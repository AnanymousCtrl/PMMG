# 🎵 AI Music Generator - Streamlit App

A Streamlit application for generating music using AI models trained on the MAESTRO dataset.

## Features

- 🎹 Generate musical compositions using AI
- 🎼 Visualize generated music with notation plots
- 📥 Download generated MIDI files
- ⚙️ Customizable generation parameters (duration, tempo, complexity)
- 🎧 Audio playback capabilities (with proper setup)

## Prerequisites

- Python 3.8+
- MAESTRO dataset (should be located in the parent directory as `maestro-v3.0.0-midi`)

## Installation

1. Clone or navigate to this directory
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Running the Application

1. Ensure the MAESTRO dataset is available in the parent directory:
   ```
   ../maestro-v3.0.0-midi/maestro-v3.0.0/
   ```

2. Run the Streamlit app:

```bash
streamlit run app.py
```

3. Open your browser and navigate to the URL shown in the terminal (typically `http://localhost:8501`)

## Usage

1. **Adjust Parameters**: Use the sidebar sliders to set:
   - Duration (10-120 seconds)
   - Tempo (60-200 BPM)
   - Complexity level

2. **Generate Music**: Click the "Generate Music" button to create a new composition

3. **View Results**: 
   - See the music notation visualization
   - Download the MIDI file
   - Listen to the generated music

## File Structure

```
music_generator_app/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Dataset Information

This app uses the [MAESTRO dataset](https://magenta.tensorflow.org/datasets/maestro) which contains over 200 hours of virtuosic piano performances. The dataset includes:
- MIDI files with precise note timing
- Audio recordings
- Performance metadata

## Technical Details

- **Backend**: Python with Streamlit for the web interface
- **Music Processing**: music21 library for music analysis and generation
- **MIDI Handling**: pretty_midi for MIDI file operations
- **Visualization**: Matplotlib for music notation plots

## Extending the App

To add more sophisticated music generation capabilities:

1. **Integrate Pre-trained Models**: Use models like Google's Magenta or OpenAI's MuseNet
2. **Add Audio Playback**: Implement proper audio conversion from MIDI to WAV/MP3
3. **Style Transfer**: Add options for different musical styles
4. **Real-time Generation**: Implement streaming music generation

## Troubleshooting

**Common Issues:**

1. **Dataset not found**: Ensure the MAESTRO dataset is in the correct location
2. **Dependency issues**: Use Python 3.8+ and install all requirements
3. **MIDI playback**: Audio playback requires additional audio libraries

**For audio playback**, you might need to install:

```bash
pip install fluidsynth
# And ensure you have a soundfont file for proper audio rendering
```

## License

This project is for educational and demonstration purposes. The MAESTRO dataset is provided by Google Magenta under the CC BY-NC-SA 4.0 license.

## Contributing

Feel free to fork this project and add your own music generation models or features!
