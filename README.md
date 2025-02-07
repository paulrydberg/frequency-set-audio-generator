# Create Frequency Set Audio Generator

This Python script generates Pulsed Electromagnetic Field (PEMF) or frequency set audio based on user-defined parameters. Users can input a list of frequencies (including individual tones, sweeps, and per-tone durations), select a waveform type, set the sample rate, specify default dwell time, add metadata, and choose whether to merge frequencies (play simultaneously) or sequence them consecutively. The output is saved as a WAV file by default.

## Features

- **Frequency Input**: Accepts a comma-separated list of frequencies, including:
  - Single frequencies (e.g., `144`)
  - Frequency sweeps (e.g., `160-180`)
  - Frequencies with specific dwell times (e.g., `144=360`)
  - Sweeps with dwell times (e.g., `520-555=60`)

- **Waveform Selection**: Supports various waveform types:
  - Sine
  - Lilly (implemented as a square wave with a 25% duty cycle)
  - Square
  - Pulse (5% duty cycle, positive offset)
  - Sawtooth
  - Reverse Sawtooth
  - Triangle

- **Sample Rate**: Configurable sample rates, including:
  - 48,000 Hz
  - 96,000 Hz
  - 192,000 Hz
  - 384,000 Hz
  - 576,000 Hz

- **Dwell Time**: Set a default duration for each frequency if not specified individually.

- **Frequency Merging**: Choose to merge frequencies to play simultaneously or sequence them one after the other.

## Requirements

- Python 3.x
- Conda

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/paulrydberg/frequency-set-audio-generator.git
   cd frequency-set-audio-generator
   ```

2. **Create a new environment with Python 3.9**:
   ```bash
   conda create --name pemf python=3.9 -y
   ```

3. **Activate the environment**:
   ```bash
   conda activate pemf
   ```

4. **Install numpy and scipy via conda**:
   ```bash
   conda install numpy scipy -y
   ```

5. **Install pydub via pip**:
   ```bash
   pip install pydub
   ```

6. **Install ffmpeg via conda-forge (required by pydub)**:
   ```bash
   conda install -c conda-forge ffmpeg -y
   ```

## Usage

Run the script to launch the GUI:

```bash
python3 app.py
```

### GUI Instructions

1. **Frequencies**: Enter a comma-separated list of frequencies. Examples:
   - Single frequency: `144`
   - Frequency sweep: `160-180`
   - Frequency with dwell time: `144=360`
   - Sweep with dwell time: `520-555=60`

2. **Waveform**: Select the desired waveform type from the dropdown menu.

3. **Audio Format**: Currently, WAV, MP3, FLAC, and ALAC formats are supported.

4. **Sample Rate**: Choose the sample rate from the available options.

5. **Default Dwell**: Enter the default duration (in seconds) for each frequency if not specified individually.

6. **Merge Frequencies**: Check this box to play all frequencies simultaneously; leave unchecked to play them sequentially.

7. **Output File Name**: Specify the name of the output file (e.g., `output.wav`).

8. **Generate Audio**: Click the "Generate Audio" button to create and save the audio file.

## Example

To generate an audio file with the following parameters:

- Frequencies: `144,160-180=60,1.2,520-555=120`
- Waveform: `pulse`
- Sample Rate: `48000 Hz`
- Default Dwell: `180 seconds`

Set the parameters in the GUI accordingly and click "Generate Audio." The output will be saved as specified (e.g., `output.wav`).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

This script utilizes the following Python libraries:

- [NumPy](https://numpy.org/)
- [SciPy](https://scipy.org/)
- [Tkinter](https://docs.python.org/3/library/tkinter.html)

For more information on audio signal processing in Python, refer to resources like [Audio Signal Processing in Python](https://github.com/mgeier/python-audio/blob/master/README.md). 