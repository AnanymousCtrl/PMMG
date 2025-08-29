import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
import music21 as m21
import pretty_midi
import os
from collections import Counter

class MusicGenerator:
    def __init__(self):
        self.model = None
        self.sequence_length = 32
        self.note_range = 128  # MIDI note range
        self.vocab_size = self.note_range + 1  # +1 for rest
        
    def load_maestro_data(self, max_files=100):
        """Load and preprocess MAESTRO MIDI files"""
        dataset_path = "../maestro-v3.0.0-midi/maestro-v3.0.0"
        midi_files = []
        
        for root, dirs, files in os.walk(dataset_path):
            for file in files:
                if file.endswith('.midi'):
                    midi_files.append(os.path.join(root, file))
        
        # Limit to max_files for demonstration
        midi_files = midi_files[:max_files]
        
        sequences = []
        for file_path in midi_files:
            try:
                midi_data = pretty_midi.PrettyMIDI(file_path)
                for instrument in midi_data.instruments:
                    notes = []
                    for note in instrument.notes:
                        # Convert to note numbers and durations
                        notes.append({
                            'pitch': note.pitch,
                            'start': note.start,
                            'end': note.end,
                            'velocity': note.velocity
                        })
                    if notes:
                        sequences.append(notes)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
        
        return sequences
    
    def create_training_data(self, sequences):
        """Create training data from note sequences"""
        X = []
        y = []
        
        for seq in sequences:
            if len(seq) > self.sequence_length:
                for i in range(len(seq) - self.sequence_length):
                    input_seq = seq[i:i + self.sequence_length]
                    target_note = seq[i + self.sequence_length]
                    
                    # Convert to numerical representation
                    input_notes = [note['pitch'] for note in input_seq]
                    target_pitch = target_note['pitch']
                    
                    X.append(input_notes)
                    y.append(target_pitch)
        
        return np.array(X), np.array(y)
    
    def build_model(self):
        """Build LSTM model for music generation"""
        model = Sequential([
            LSTM(256, input_shape=(self.sequence_length, 1), return_sequences=True),
            Dropout(0.3),
            LSTM(256),
            Dropout(0.3),
            Dense(128, activation='relu'),
            Dense(self.vocab_size, activation='softmax')
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def train_model(self, X, y, epochs=5, batch_size=64):
        """Train the music generation model"""
        # Reshape data for LSTM
        X = X.reshape((X.shape[0], X.shape[1], 1))
        
        # Normalize data
        X = X / self.note_range
        
        # Build and train model
        self.model = self.build_model()
        
        history = self.model.fit(
            X, y,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.2,
            verbose=1
        )
        
        return history
    
    def generate_music(self, seed_sequence=None, length=50, temperature=0.8):
        """Generate new music using the trained model"""
        if seed_sequence is None:
            # Create a random seed sequence
            seed_sequence = np.random.randint(0, self.note_range, self.sequence_length)
        else:
            seed_sequence = seed_sequence[-self.sequence_length:]
        
        generated_notes = list(seed_sequence)
        
        for _ in range(length):
            # Prepare input sequence
            input_seq = np.array(generated_notes[-self.sequence_length:])
            input_seq = input_seq.reshape((1, self.sequence_length, 1)) / self.note_range
            
            # Predict next note
            predictions = self.model.predict(input_seq, verbose=0)[0]
            
            # Apply temperature
            predictions = np.log(predictions) / temperature
            exp_preds = np.exp(predictions)
            predictions = exp_preds / np.sum(exp_preds)
            
            # Sample from distribution
            next_note = np.random.choice(self.vocab_size, p=predictions)
            
            generated_notes.append(next_note)
        
        return generated_notes[self.sequence_length:]  # Return only new notes
    
    def notes_to_music21(self, notes, tempo=120, duration=0.5):
        """Convert generated notes to music21 stream"""
        stream = m21.stream.Stream()
        stream.append(m21.tempo.MetronomeMark(number=tempo))
        
        for note_num in notes:
            if note_num < self.note_range:  # Valid MIDI note
                note = m21.note.Note()
                note.pitch.midi = note_num
                note.duration.quarterLength = duration
                stream.append(note)
            else:  # Rest
                rest = m21.note.Rest()
                rest.duration.quarterLength = duration
                stream.append(rest)
        
        return stream

# Simple generator for demonstration (without training)
class SimpleMusicGenerator:
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
