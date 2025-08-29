import streamlit as st
import numpy as np
import pandas as pd
import os
import random
from pathlib import Path
import pretty_midi
import music21 as m21
import librosa
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import time
from model import MusicGenerator, SimpleMusicGenerator

# Set page config
st.set_page_config(
    page_title="Music Generation App",
    page_icon="🎵",
    layout="wide"
)

# Title and description
st.title("🎵 AI Music Generator")
st.markdown("""
This app generates music using AI models trained on the MAESTRO dataset. 
You can generate new musical compositions and listen to them directly in the browser.
""")

# Sidebar for controls
st.sidebar.header("Generation Settings")

# Function to load and analyze MAESTRO dataset
def analyze_maestro_dataset():
    """Analyze the MAESTRO dataset and return statistics"""
    dataset_path = "../maestro-v3.0.0-midi/maestro-v3.0.0"
    
    if not os.path.exists(dataset_path):
        st.warning("MAESTRO dataset not found. Please ensure the dataset is in the correct location.")
        return None
    
    midi_files = []
    for root, dirs, files in os.walk(dataset_path):
        for file in files:
            if file.endswith('.midi'):
                midi_files.append(os.path.join(root, file))
    
    return {
        'total_files': len(midi_files),
        'file_paths': midi_files[:10]  # First 10 files for demo
    }

# Function to generate simple music (placeholder for actual model)
def generate_simple_music(duration=30, tempo=120):
    """Generate a simple musical sequence"""
    # Create a simple melody using random notes
    notes = ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5']
    rhythm = [0.5, 0.5, 1.0, 0.5, 0.5, 1.0, 2.0]
    
    # Create a stream
    stream = m21.stream.Stream()
    stream.append(m21.tempo.MetronomeMark(number=tempo))
    
    current_time = 0
    while current_time < duration:
        note_name = random.choice(notes)
        note_duration = random.choice(rhythm)
        
        note = m21.note.Note(note_name)
        note.duration.quarterLength = note_duration
        stream.append(note)
        
        current_time += note_duration
    
    return stream

# Function to convert music21 stream to MIDI bytes
def stream_to_midi_bytes(stream):
    """Convert music21 stream to MIDI bytes"""
    midi_file = BytesIO()
    stream.write('midi', fp=midi_file)
    midi_file.seek(0)
    return midi_file

# Function to create download link for MIDI file
def get_midi_download_link(midi_bytes, filename="generated_music.mid"):
    """Generate a download link for MIDI file"""
    b64 = base64.b64encode(midi_bytes.read()).decode()
    href = f'<a href="data:audio/midi;base64,{b64}" download="{filename}">Download MIDI file</a>'
    return href

# Initialize models
@st.cache_resource
def load_models():
    return {
        'simple': SimpleMusicGenerator(),
        'advanced': MusicGenerator()
    }

# Main app logic
def main():
    models = load_models()
    
    # Dataset analysis
    dataset_info = analyze_maestro_dataset()
    
    if dataset_info:
        st.sidebar.success(f"MAESTRO dataset loaded: {dataset_info['total_files']} MIDI files found")
        
        # Display sample files
        with st.expander("View Sample MIDI Files"):
            for i, file_path in enumerate(dataset_info['file_paths']):
                st.write(f"{i+1}. {os.path.basename(file_path)}")
    
    # Generation parameters
    st.sidebar.subheader("Generation Parameters")
    model_type = st.sidebar.selectbox(
        "Model Type",
        options=["Simple Markov", "LSTM (Advanced)"],
        index=0,
        help="Simple Markov: Fast generation using rule-based transitions\nLSTM: Neural network model (requires training)"
    )
    
    duration = st.sidebar.slider("Duration (seconds)", 10, 120, 30)
    tempo = st.sidebar.slider("Tempo (BPM)", 60, 200, 120)
    complexity = st.sidebar.select_slider("Complexity", options=["Simple", "Medium", "Complex"], value="Medium")
    
    # Training section for advanced model
    if model_type == "LSTM (Advanced)":
        st.sidebar.markdown("---")
        st.sidebar.subheader("Model Training")
        if st.sidebar.button("🔄 Train Model", help="Train the LSTM model on MAESTRO dataset"):
            with st.spinner("Training model... This may take several minutes."):
                try:
                    generator = models['advanced']
                    sequences = generator.load_maestro_data(max_files=50)
                    X, y = generator.create_training_data(sequences)
                    history = generator.train_model(X, y, epochs=20, batch_size=32)
                    st.sidebar.success("Model trained successfully!")
                except Exception as e:
                    st.sidebar.error(f"Training failed: {str(e)}")
    
    # Generate button
    if st.sidebar.button("🎹 Generate Music", type="primary"):
        with st.spinner("Generating music..."):
            try:
                if model_type == "Simple Markov":
                    # Use simple Markov model
                    generator = models['simple']
                    melody_length = max(20, duration * 2)  # Adjust length based on duration
                    melody = generator.generate_melody(length=melody_length)
                    music_stream = generator.generate_music21_stream(melody, tempo=tempo)
                else:
                    # Use advanced LSTM model (or fallback to simple if not trained)
                    generator = models['advanced']
                    if generator.model is None:
                        st.warning("LSTM model not trained yet. Using simple model instead.")
                        simple_gen = models['simple']
                        melody = simple_gen.generate_melody(length=30)
                        music_stream = simple_gen.generate_music21_stream(melody, tempo=tempo)
                    else:
                        # Generate with LSTM
                        generated_notes = generator.generate_music(length=50, temperature=0.8)
                        music_stream = generator.notes_to_music21(generated_notes, tempo=tempo)
                
                # Convert to MIDI
                midi_bytes = stream_to_midi_bytes(music_stream)
                
                # Display music
                st.subheader("🎼 Generated Music")
                
                # Show music notation
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Music Notation:**")
                    # Create a simple visualization of the notes
                    fig, ax = plt.subplots(figsize=(10, 4))
                    
                    # Extract note information for visualization
                    notes = []
                    times = []
                    current_time = 0
                    for element in music_stream:
                        if isinstance(element, m21.note.Note):
                            notes.append(element.pitch.midi)
                            times.append(current_time)
                            current_time += element.duration.quarterLength
                        elif isinstance(element, m21.note.Rest):
                            current_time += element.duration.quarterLength
                    
                    ax.plot(times, notes, 'o-', markersize=8)
                    ax.set_xlabel('Time (beats)')
                    ax.set_ylabel('MIDI Note Number')
                    ax.set_title('Generated Melody')
                    ax.grid(True, alpha=0.3)
                    st.pyplot(fig)
                
                with col2:
                    st.write("**MIDI Information:**")
                    
                    # Display basic info
                    st.write(f"Model: {model_type}")
                    st.write(f"Duration: {duration} seconds")
                    st.write(f"Tempo: {tempo} BPM")
                    note_count = len([e for e in music_stream if isinstance(e, m21.note.Note)])
                    st.write(f"Number of notes: {note_count}")
                    
                    # Download link
                    st.markdown(get_midi_download_link(midi_bytes), unsafe_allow_html=True)
                
                # Show actual music notation
                st.write("**Sheet Music Preview:**")
                music_xml = music_stream.write('musicxml')
                st.text("MusicXML generated - would display sheet music here with proper rendering")
                
            except Exception as e:
                st.error(f"Error generating music: {str(e)}")
                st.info("Falling back to simple music generation...")
                # Fallback to simple generation
                music_stream = generate_simple_music(duration, tempo)
                midi_bytes = stream_to_midi_bytes(music_stream)
                
                st.subheader("🎼 Generated Music (Fallback)")
                st.write("Simple melody generated as fallback")
                st.markdown(get_midi_download_link(midi_bytes), unsafe_allow_html=True)
    
    # Information section
    st.sidebar.markdown("---")
    st.sidebar.info("""
    **About this app:**
    - Uses the MAESTRO dataset for music generation
    - Two model types: Simple Markov and LSTM neural network
    - Generates MIDI files that can be downloaded
    - Real-time music visualization
    """)

if __name__ == "__main__":
    main()
