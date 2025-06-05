import pickle
import os

from estimate_notes import estimate_pitch_melodia, get_chord_from_notes, get_closest_chord, get_notes_from_MIDI
from markov_sequence_generator import generate_new_sequence
from create_midi import create_midi_file

""" Runs pitch estimation from audio, chord sequence generation and MIDI file creation """


def load_data():
    """ Loads and returns:
        a) the list of unique MIDI chords
        b) the pre-computed transition matrix for chord sequences """

    with open('unique_midi_chords.pkl', 'rb') as f:
        unique_midi_chords = pickle.load(f)

    with open('transition_matrix.pkl', 'rb') as f:
        transition_matrix = pickle.load(f)

    return unique_midi_chords, transition_matrix


def main_process(unique_midi_chords, transition_matrix, file_name, input_type):
    print(f"Processing {file_name}")

    # Get chord from [input_type] ##### this is where we should get audio input from MAX via OSC
    if "audio" in input_type:
        all_notes = estimate_pitch_melodia(file_name)  # estimate active notes
    elif "midi" in input_type:
        all_notes = get_notes_from_MIDI(file_name)  # read active notes from MIDI file
    input_chord, chord_length = get_chord_from_notes(all_notes)

    # Get Closest Chord
    closest_chord, distance = get_closest_chord(input_chord, unique_midi_chords, chord_length, weight=100.0)
    print(f"Input chord: {input_chord}, chord length: {chord_length}\nMost similar chord: {closest_chord}, distance: {distance}")

    # Settings for new sequence
    chord_duration = 2
    out_size = 8
    out_size = chord_length * 2  # e.g. if 2 input chords, create 4 output chords
    # but chord_length is not number of chords, just number of notes in chord
    # in sequence generation, this number is used to count the tuples (which are chords)

    # Generate New Sequence
    new_sequence = generate_new_sequence(closest_chord, transition_matrix, size=out_size)
    create_midi_file(new_sequence, chord_duration=chord_duration, file_name=file_name)


def main():
    unique_midi_chords, transition_matrix = load_data()

    ### SELECT BLOCK ###

    ### FOR AUDIO FILES
    # Process all files in the directory (this contained simple melody loops)
    input_type = "audio"
    print("### Estimating pitches with Essentia")
    # loops_path = "data/loops"  # e.g. "Loop1_ragtime"
    # file_names = os.listdir(loops_path)
    # for file_name in file_names:
    #     main_process(unique_midi_chords, transition_matrix, file_name, input_type)
    file_name = "data/wav/c_e_fsharp.wav"
    #main_process(unique_midi_chords, transition_matrix, file_name, input_type)

    ### FOR MIDI FILES
    input_type = "midi"
    print("### Reading notes from MIDI")
    file_name = "data/midi/c_e_fsharp.mid"
    main_process(unique_midi_chords, transition_matrix, file_name, input_type)


if __name__ == "__main__":
    main()
