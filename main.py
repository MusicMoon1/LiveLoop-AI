import pickle
import os

from estimate_notes import get_chord_from_audio, get_closest_chord
from markov_sequence_generator import generate_new_sequence, create_midi_file

""" Runs Estimation, Chord Sequence Generation and MIDI File Creation """


def load_data():
    # Load List of Chords
    with open('unique_midi_chords.pkl', 'rb') as f:
        unique_midi_chords = pickle.load(f)

    # Load Transition Matrix
    with open('transition_matrix.pkl', 'rb') as f:
        transition_matrix = pickle.load(f)

    return unique_midi_chords, transition_matrix


def main_process(unique_midi_chords, transition_matrix, file_name='Loop1_ragtime'):
    # Set Up Input
    print("Processing ", file_name)
    audiofile = f"data/loops/{file_name}"

    # Get Chord from Audio
    input_chord, chord_length = get_chord_from_audio(audiofile)

    # Get Closest Chord
    closest_chord = get_closest_chord(input_chord, unique_midi_chords, chord_length, weight=100.0)
    print(f'Input Chord: {input_chord} \n Most Similar Chord {closest_chord}')

    # New Sequence Settings
    chord_duration = 2
    out_size = 8

    # Generate New Sequence
    new_sequence = generate_new_sequence(closest_chord, transition_matrix, size=out_size)
    create_midi_file(new_sequence, chord_duration=chord_duration, file_name=file_name)


def main():
    """ Runs Estimation, Chord Sequence Generation and MIDI File Creation """
    unique_midi_chords, transition_matrix = load_data()

    # Process all files in the directory
    loops_path = "data/loops"
    file_names = os.listdir(loops_path)

    for file_name in file_names:
        main_process(unique_midi_chords, transition_matrix, file_name=file_name)


if __name__ == "__main__":
    main()
