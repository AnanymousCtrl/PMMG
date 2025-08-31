import streamlit as st
import numpy as np
import os
import random
import music21 as m21
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# Set page config
st.set_page_config(
    page_title="Meditation Music Generator",
    page_icon="🎵",
    layout="wide"
)

# Title and description
st.title("🎵 Meditation Music Generator")
st.markdown("""
This app generates simple music compositions using the MAESTRO dataset as inspiration.
You can generate musical sequences and download them as MIDI files.
""")

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

# music generator using Markov-like transitions
class MediMusicGenerator:
    def __init__(self):
        self.common_notes = [60, 62, 64, 65, 67, 69, 71, 72]  # C Major scale
        self.transitions = {
            60: [62, 64, 67],  # C -> D, E, G
            62: [64, 65, 67],   # D -> E, F, G
            64: [65, 67, 69],   # E -> F, G, A
            65: [67, 69, 72],   # F -> G, A, C
            67: [69, 71, 72],   # G -> A, B, C
            69: [71, 72, 60],   # A -> B, C, C
            71: [72, 60, 62],   # B -> C, C, D
            72: [60, 62, 64]    # C -> C, D, E
        }
    
    def generate_melody(self, length=20, start_note=60):
        """Generate a simple melody using Markov-like transitions"""
        melody = [start_note]
        current_note = start_note
        
        for _ in range(length - 1):
            if current_note in self.transitions:
                next_note = random.choice(self.transitions[current_note])
            else:
                next_note = random.choice(self.common_notes)
            
            melody.append(next_note)
            current_note = next_note
        
        return melody
    
    def generate_music21_stream(self, melody, tempo=120, duration=0.5):
        """Convert melody to music21 stream"""
        stream = m21.stream.Stream()
        stream.append(m21.tempo.MetronomeMark(number=tempo))
        
        for note_num in melody:
            note = m21.note.Note()
            note.pitch.midi = note_num
            note.duration.quarterLength = duration
            stream.append(note)
        
        return stream

# Function to convert music21 stream to MIDI bytes
def stream_to_midi_bytes(stream):
    """Convert music21 stream to MIDI bytes"""
    import tempfile
    import os
    
    # Create a temporary file with a unique name
    temp_file = tempfile.NamedTemporaryFile(suffix='.mid', delete=False)
    temp_file.close()
    
    try:
        # Write to the file
        stream.write('midi', fp=temp_file.name)
        
        # Read the file back into bytes
        with open(temp_file.name, 'rb') as f:
            midi_bytes = BytesIO(f.read())
        
        midi_bytes.seek(0)
        return midi_bytes
        
    finally:
        # Clean up - ensure file is closed before deleting
        try:
            os.unlink(temp_file.name)
        except:
            pass

# Function to create download link for MIDI file
def get_midi_download_link(midi_bytes, filename="generated_music.mid"):
    """Generate a download link for MIDI file"""
    b64 = base64.b64encode(midi_bytes.read()).decode()
    href = f'<a href="data:audio/midi;base64,{b64}" download="{filename}">Download MIDI file</a>'
    return href

# Function to generate WAV audio from melody using pure Python synthesis
def generate_wav_from_melody(melody, tempo=120, sample_rate=44100):
    """Generate WAV audio from melody using sine wave synthesis"""
    import numpy as np
    from scipy.io import wavfile
    
    # MIDI note to frequency conversion
    def midi_to_freq(note):
        return 440.0 * (2.0 ** ((note - 69) / 12.0))
    
    # Duration per note in seconds (quarter note = 60/tempo seconds)
    note_duration = 60.0 / tempo  # seconds per quarter note
    duration_per_note = note_duration  # each note is a quarter note
    
    # Generate audio samples
    samples = []
    
    for note in melody:
        frequency = midi_to_freq(note)
        # Generate sine wave for this note
        t = np.linspace(0, duration_per_note, int(sample_rate * duration_per_note), endpoint=False)
        note_samples = 0.5 * np.sin(2 * np.pi * frequency * t)
        
        # Apply simple envelope (attack, decay)
        envelope = np.ones_like(note_samples)
        attack_samples = int(0.1 * len(envelope))
        decay_samples = int(0.2 * len(envelope))
        
        # Attack
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        # Decay
        envelope[-decay_samples:] = np.linspace(1, 0, decay_samples)
        
        note_samples *= envelope
        samples.extend(note_samples)
    
    # Convert to 16-bit PCM
    audio_data = np.array(samples)
    audio_data = np.int16(audio_data * 32767)
    
    # Create WAV file in memory
    import io
    wav_buffer = io.BytesIO()
    wavfile.write(wav_buffer, sample_rate, audio_data)
    wav_buffer.seek(0)
    
    return wav_buffer.getvalue()

# Function to create download link for WAV file
def get_wav_download_link(wav_bytes, filename="generated_music.wav"):
    """Generate a download link for WAV file"""
    if wav_bytes:
        b64 = base64.b64encode(wav_bytes).decode()
        href = f'<a href="data:audio/wav;base64,{b64}" download="{filename}">Download WAV file</a>'
        return href
    return "WAV generation not available"

# Function to create audio player for WAV
def get_wav_audio_player(wav_bytes):
    """Create HTML audio player for WAV file"""
    if wav_bytes:
        b64 = base64.b64encode(wav_bytes).decode()
        audio_html = f'''
        <audio controls>
            <source src="data:audio/wav;base64,{b64}" type="audio/wav">
            Your browser does not support the audio element.
        </audio>
        '''
        return audio_html
    return "Audio playback not available"

# Main app logic
def main():
    generator = MediMusicGenerator()
    
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
    duration = st.sidebar.slider("Number of notes", 10, 50, 20)
    tempo = st.sidebar.slider("Tempo (BPM)", 60, 200, 120)
    start_note = st.sidebar.selectbox("Starting note", 
                                     options=["C4 (60)", "D4 (62)", "E4 (64)", "F4 (65)", "G4 (67)", "A4 (69)", "B4 (71)", "C5 (72)"],
                                     index=0)
    
    # Parse start note
    start_note_midi = int(start_note.split("(")[1].split(")")[0])
    
    # Generate button
    if st.sidebar.button("🎹 Generate Music", type="primary"):
        with st.spinner("Generating music..."):
            try:
                # Generate music
                melody = generator.generate_melody(length=duration, start_note=start_note_midi)
                music_stream = generator.generate_music21_stream(melody, tempo=tempo)
                
                # Convert to MIDI
                midi_bytes = stream_to_midi_bytes(music_stream)
                
                # Display music
                st.subheader("🎼 Generated Music")
                
                # Show music notation
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Music Visualization:**")
                    # Create a simple visualization of the notes
                    fig, ax = plt.subplots(figsize=(10, 4))
                    
                    # Extract note information for visualization
                    times = list(range(len(melody)))
                    
                    ax.plot(times, melody, 'o-', markersize=8)
                    ax.set_xlabel('Note Position')
                    ax.set_ylabel('MIDI Note Number')
                    ax.set_title('Generated Melody')
                    ax.grid(True, alpha=0.3)
                    st.pyplot(fig)
                
                with col2:
                    st.write("**MIDI Information:**")
                    
                    # Display basic info
                    st.write(f"Number of notes: {duration}")
                    st.write(f"Tempo: {tempo} BPM")
                    st.write(f"Starting note: MIDI {start_note_midi}")
                    
                    # Show the melody
                    st.write("**Generated Notes:**")
                    note_names = [m21.note.Note(n).nameWithOctave for n in melody[:10]]  # Show first 10 notes
                    st.write(", ".join(note_names) + ("..." if len(melody) > 10 else ""))
                    
                    # Download link
                    st.markdown(get_midi_download_link(midi_bytes), unsafe_allow_html=True)
                
                # Generate WAV audio using pure Python synthesis
                st.write("---")
                st.subheader("🎧 Audio Playback")
                
                # Generate WAV from melody directly
                wav_bytes = generate_wav_from_melody(melody, tempo)
                
                if wav_bytes:
                    # Audio player
                    st.write("**Listen to your music:**")
                    st.markdown(get_wav_audio_player(wav_bytes), unsafe_allow_html=True)
                    
                    # WAV download link
                    st.write("**Download audio:**")
                    st.markdown(get_wav_download_link(wav_bytes), unsafe_allow_html=True)
                else:
                    st.info("WAV audio generation failed")
                
                # Show some music theory info
                st.write("---")
                st.subheader("🎵 Music Theory Info")
                unique_notes = set(melody)
                st.write(f"Unique notes used: {len(unique_notes)}")
                st.write(f"Range: {min(unique_notes)} - {max(unique_notes)}")
                
                # Show scale information
                scale_notes = sorted(unique_notes)
                st.write(f"Notes in scale: {', '.join(str(n) for n in scale_notes)}")
                
            except Exception as e:
                st.error(f"Error generating music: {str(e)}")
                import traceback
                st.text(traceback.format_exc())
    
    # Information section
    st.sidebar.markdown("---")
    st.sidebar.info("""
    **About this app:**
    - Uses the MAESTRO dataset for inspiration
    - Simple Markov chain music generation
    - Generates MIDI files that can be downloaded
    - Real-time music visualization
    """)

if __name__ == "__main__":
    main()
