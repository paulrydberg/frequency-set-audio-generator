#!/usr/bin/env python3
"""
Create Frequency Set Audio Generator

This script generates PEMF (or frequency set) audio based on modifiable parameters.
You can provide a comma‐separated frequency list (which may include
individual frequencies, sweeps, and per-tone durations), choose a waveform type, set the sample rate,
default dwell time, and decide whether to merge frequencies (play simultaneously) or sequence
them one after the other.

The output is saved as a WAV file by default.
"""

import argparse
import numpy as np
import scipy.io.wavfile as wav
from scipy import signal
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# --- Utility Functions ---

def fix_frequency(freq, waveform, sample_rate):
    """
    Adjust a frequency by dividing by 2 until it is below the maximum allowed for the chosen waveform.
    """
    if waveform in ["sine", "lilly"]:
        max_freq = sample_rate / 20.0
    elif waveform == "triangle":
        max_freq = sample_rate / 8.0
    elif waveform in ["pulse", "sawtooth", "reverse_sawtooth"]:
        max_freq = sample_rate / 4.0
    elif waveform == "square":
        max_freq = sample_rate / 2.0
    else:
        max_freq = sample_rate / 20.0  # fallback
    while freq > max_freq:
        freq /= 2.0
    return freq

def parse_frequency_set(freq_str, default_dwell):
    """
    Parses a frequency set string into a list of segments.
    Each segment is a dictionary:
       { 'start': float, 'end': float, 'duration': float }
    Frequency entries can be:
      - A single number (e.g., "1.2")
      - A frequency with dwell (e.g., "144=360")
      - A frequency sweep (e.g., "160-180")
      - A sweep with dwell (e.g., "520-555=60")
    Returns a list of segments.
    """
    segments = []
    parts = freq_str.split(',')
    for part in parts:
        part = part.strip()
        if not part:
            continue
        # Check for dwell specification using '='
        if '=' in part:
            freq_part, dwell_part = part.split('=')
            dwell = float(dwell_part)
        else:
            freq_part = part
            dwell = default_dwell
        # Check if this is a sweep (contains '-')
        if '-' in freq_part:
            start_str, end_str = freq_part.split('-')
            start = float(start_str)
            end = float(end_str)
        else:
            start = float(freq_part)
            end = start
        segments.append({'start': start, 'end': end, 'duration': dwell})
    return segments

def generate_tone(start_freq, end_freq, duration, sample_rate, waveform, amplitude):
    """
    Generates a tone for the given parameters.
    If start_freq != end_freq, a linear frequency sweep is applied.
    Returns a NumPy array of samples (float32).
    """
    t = np.linspace(0, duration, int(duration * sample_rate), endpoint=False)
    # Compute instantaneous phase:
    inst_phase = 2 * np.pi * (start_freq * t + 0.5 * (end_freq - start_freq) * (t**2) / duration)
    
    if waveform == "sine":
        tone = np.sin(inst_phase)
    elif waveform == "lilly":
        # "Lilly" is implemented here as a square wave with a 25% duty cycle.
        tone = signal.square(inst_phase, duty=0.25)
    elif waveform == "square":
        tone = signal.square(inst_phase)
    elif waveform == "pulse":
        # Pulse: 5% duty, positive offset only (range 0 to 1)
        sq = signal.square(inst_phase, duty=0.05)
        tone = (sq + 1) / 2  # now in range 0 to 1
    elif waveform == "sawtooth":
        tone = signal.sawtooth(inst_phase, width=1.0)  # rising ramp
    elif waveform == "reverse_sawtooth":
        tone = signal.sawtooth(inst_phase, width=0.0)  # falling ramp
    elif waveform == "triangle":
        tone = signal.sawtooth(inst_phase, width=0.5)
    else:
        print(f"Unknown waveform type: {waveform}", file=sys.stderr)
        tone = np.sin(inst_phase)
    return amplitude * tone

def merge_audio(audio_list):
    """
    Given a list of NumPy arrays (of the same length), mix them together.
    The mixed signal is the sum (scaled to avoid clipping).
    """
    if not audio_list:
        return None
    mixed = np.sum(audio_list, axis=0)
    # Normalize to avoid clipping:
    max_val = np.max(np.abs(mixed))
    if max_val > 0:
        mixed = mixed / max_val
    return mixed

# --- Audio Generation Functionality ---

def generate_audio(frequencies, waveform, audio_format, sample_rate, dwell, merge_frequencies, output):
    """
    Generates the Frequency Set audio based on the provided parameters.
    """
    # Parse frequency set.
    segments = parse_frequency_set(frequencies, dwell)
    print("Parsed Frequency Segments:")
    for seg in segments:
        print(f"  Start: {seg['start']} Hz, End: {seg['end']} Hz, Duration: {seg['duration']} sec")
    
    # Adjust segments to meet maximum frequency requirements.
    fixed_segments = []
    for seg in segments:
        fixed_start = fix_frequency(seg['start'], waveform, sample_rate)
        fixed_end = fix_frequency(seg['end'], waveform, sample_rate)
        if fixed_start != seg['start'] or fixed_end != seg['end']:
            print(f"Adjusted frequency from {seg['start']}-{seg['end']} Hz to {fixed_start}-{fixed_end} Hz due to sample rate limits.")
        fixed_segments.append({'start': fixed_start, 'end': fixed_end, 'duration': seg['duration']})
    
    # Generate tones based on merge option.
    if merge_frequencies:
        # Use the dwell of the first segment as common duration.
        common_duration = fixed_segments[0]['duration']
        merged_tones = []
        for seg in fixed_segments:
            tone = generate_tone(seg['start'], seg['end'], common_duration, sample_rate, waveform, amplitude=1.0)
            merged_tones.append(tone)
        merged = merge_audio(merged_tones)
        final_audio = (merged * 32767).astype(np.int16)
    else:
        audio_segments = []
        for seg in fixed_segments:
            tone = generate_tone(seg['start'], seg['end'], seg['duration'], sample_rate, waveform, amplitude=1.0)
            tone_scaled = tone * 32767
            audio_segments.append(tone_scaled.astype(np.int16))
        final_audio = np.concatenate(audio_segments)
    
    # Save the output as WAV (conversion to other formats could be added later).
    wav.write(output, sample_rate, final_audio)
    print(f"Generated audio saved to {output}")

# --- Tkinter GUI ---

class GeneratorUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Create Frequency Set Audio")
        self.geometry("700x400")
        self.create_widgets()

    def create_widgets(self):
        # Frequency set entry.
        tk.Label(self, text="Frequencies (comma separated):").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.freq_entry = tk.Entry(self, width=60)
        self.freq_entry.insert(0, "144,160,1.2,520,10,10000,304")
        self.freq_entry.grid(row=0, column=1, padx=10, pady=5)

        # Waveform OptionMenu.
        tk.Label(self, text="Waveform:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.waveform_var = tk.StringVar(value="pulse")
        waveform_options = ["pulse", "lilly", "square", "sawtooth", "reverse_sawtooth", "triangle", "sine"]
        self.waveform_menu = ttk.OptionMenu(self, self.waveform_var, self.waveform_var.get(), *waveform_options)
        self.waveform_menu.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # Audio format.
        tk.Label(self, text="Audio Format:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.audio_format_var = tk.StringVar(value="WAV")
        audio_format_options = ["WAV", "MP3", "FLAC", "ALAC"]
        self.audio_format_menu = ttk.OptionMenu(self, self.audio_format_var, self.audio_format_var.get(), *audio_format_options)
        self.audio_format_menu.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        # Sample rate.
        tk.Label(self, text="Sample Rate (Hz):").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.sample_rate_var = tk.IntVar(value=48000)
        sample_rate_options = [48000, 96000, 192000, 384000, 576000]
        self.sample_rate_menu = ttk.OptionMenu(self, self.sample_rate_var, self.sample_rate_var.get(), *sample_rate_options)
        self.sample_rate_menu.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        # Dwell time.
        tk.Label(self, text="Default Dwell (sec):").grid(row=4, column=0, sticky="w", padx=10, pady=5)
        self.dwell_entry = tk.Entry(self, width=20)
        self.dwell_entry.insert(0, "180")
        self.dwell_entry.grid(row=4, column=1, padx=10, pady=5, sticky="w")

        # Merge frequencies checkbutton.
        self.merge_var = tk.BooleanVar(value=False)
        self.merge_check = tk.Checkbutton(self, text="Merge Frequencies (Simultaneous)", variable=self.merge_var)
        self.merge_check.grid(row=5, column=1, padx=10, pady=5, sticky="w")

        # Output filename.
        tk.Label(self, text="Output File Name:").grid(row=6, column=0, sticky="w", padx=10, pady=5)
        self.output_entry = tk.Entry(self, width=60)
        self.output_entry.insert(0, "output.wav")
        self.output_entry.grid(row=6, column=1, padx=10, pady=5)

        # Generate Button.
        self.generate_button = tk.Button(self, text="Generate Audio", command=self.generate_audio)
        self.generate_button.grid(row=7, column=0, columnspan=2, pady=20)

    def generate_audio(self):
        try:
            generate_audio(
                frequencies=self.freq_entry.get(),
                waveform=self.waveform_var.get(),
                audio_format=self.audio_format_var.get(),
                sample_rate=int(self.sample_rate_var.get()),
                dwell=float(self.dwell_entry.get()),
                merge_frequencies=self.merge_var.get(),
                output=self.output_entry.get()
            )
            messagebox.showinfo("Audio Generated", f"Audio successfully generated and saved to: {self.output_entry.get()}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

def main_gui():
    app = GeneratorUI()
    app.mainloop()

if __name__ == '__main__':
    main_gui()