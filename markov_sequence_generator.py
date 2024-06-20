import jams
import os
import pickle
import numpy as np

from music21 import stream, chord, meter
from chord_to_midi import chord_to_midi


def load_file_list(path):
    """ Load list of files from a directory """
    return [file for file in os.listdir(path) if file.endswith(".jams")]


def get_chord_progression(file: str = None) -> list[str]:
    """ Return chord progression from a single file """
    audio_jams = jams.load(f'data/jams/{file}', validate=False)
    chord_progressions = [chord[2] for chord in audio_jams.annotations[0]['data']]
    return chord_progressions


def get_progressions(files: list[str] = None) -> list[list[str]]:
    """ Return chord progressions from all files """
    all_chord_progressions = []
    for file in files:
        all_chord_progressions.append(get_chord_progression(file))
    return all_chord_progressions


def compute_transition_chain(sequence, m_order=2):
    """
    ---- Compute Transition Chain for Markov Chain ----
    Parameters:
        sequence (np.ndarray): Sequence
        m_order (int): Order for Markov Chain
    Returns:
        transition_states (dict): Transition States
    """
    # Initialise Transition States Dict
    transition_states = {}
    # Iterate Through Sequence
    for i in range(m_order, len(sequence)):
        # Get Current State
        current_state = tuple(sequence[i])
        # Get n Previous States
        prev_states = sequence[i - m_order:i]
        prev_states = tuple([tuple(s) for s in prev_states])
        # Create Key if not existant
        if prev_states not in transition_states:
            transition_states[prev_states] = [current_state]
        # Add Current Value to Key if already occured
        else:
            transition_states[prev_states].append(current_state)

    return transition_states


def generate_new_sequence(start=None, transition_states=None, size=100):
    """
    ---- Generate New Sequence from Transition States ----
    Parameters:
        transition_states (dict): Transition States
        size (int): Output Size
    Returns:
        new_sequence (np.ndarray): New Sequence
    """
    # Get Starting Point
    # start = next(iter(transition_states))
    if not start:
        start = list(transition_states)[np.random.randint(len(list(transition_states)))]

    # Start with Sequence starting with start chord
    # Get first states of transition states
    starting_states = [key for key in transition_states.keys() if key[0] == start]
    start = starting_states[np.random.randint(0, len(starting_states))]

    # Initialise New Sequence with starting points
    new_sequence = list(start)

    # Generate Sequence
    for _ in range(size):
        # Get Current State
        current_state = new_sequence[-len(start):]
        # Get Next State
        if tuple(current_state) in list(transition_states.keys()):
            potential_next_states = transition_states[tuple(current_state)]
        else:
            # If State does not exist Lower Order
            potential_next_states = get_lower_order_state(transition_states, current_state)
        # Pick Random State from Potential States
        next_state = potential_next_states[np.random.randint(0, len(potential_next_states))]
        # Append Next State to Sequence
        new_sequence.append(next_state)

    return [list(s) for s in new_sequence]


def get_lower_order_state(transition_states, current_state):
    """
    ---- Recursively Get Lower Order Transition States ----
    Parameters:
        transition_states (dict): Original Order Transition States
        current_state (tuple): Current State
    Returns:
        Values for Reduced Order Transition States
    """
    # Ensure that original dict is not changed (otherwise truncated outside of function)
    higher_order_states = dict(transition_states)

    if tuple(current_state) in list(higher_order_states.keys()):
        # print(f"found lower order state of {len(current_state)}")
        return higher_order_states[tuple(current_state)]
    else:
        lower_order_states = {}
        for key, value in higher_order_states.items():
            # Truncate the first element of the key tuple
            truncated_key = key[1:]
            # Check if the truncated key is already in the lower order states
            if truncated_key not in lower_order_states:
                lower_order_states[truncated_key] = value
            else:
                lower_order_states[truncated_key] += value
        # Recursively call the function with the lower order states
        return get_lower_order_state(lower_order_states, current_state[1:])


def chords_to_midi_notes(new_sequence: list[str]) -> list[list[int]]:
    """ Convert List of Chords to List of MIDI Notes """
    new_sequence_midi = []
    for chord_notation in new_sequence:
        chord_midi = chord_to_midi.parse_chord(annotation=chord_notation)
        if chord_midi and len(chord_midi) >= 3:
            new_sequence_midi.append(chord_midi)
    return new_sequence_midi


def get_unique_midi_chords(chord_progressions_all: list[str]) -> tuple[list[str], dict[str, int], dict[int, str]]:
    """ Get unique chords and create a mapping between chord notation and index """
    unique_chords = list(set(chord_progressions_all))
    chtoi = {ch: i for i, ch in enumerate(unique_chords)}
    itoch = {v: k for k, v in chtoi.items()}
    return unique_chords, chtoi, itoch


def create_midi_file(new_sequence_midi: list[list[int]], chord_duration: float = 2, file_name='midi') -> None:
    """ Create MIDI File from List of MIDI Notes """
    # Create a music21 score
    score = stream.Score()
    # Define a 4/4 time signature
    time_signature = meter.TimeSignature('4/4')
    score.append(time_signature)

    # Create a part for the chords
    chord_part = stream.Part()

    # Iterate over the list of MIDI chords and add them to the part
    for midi_notes in new_sequence_midi:
        # Create a chord from the MIDI notes
        m21_chord = chord.Chord(midi_notes)
        m21_chord.duration.quarterLength = chord_duration
        # Add the chord to the part
        chord_part.append(m21_chord)

    # Add the part to the score
    score.append(chord_part)

    # Save the score to a MIDI file
    midi_file_path = f'data/midi/{file_name}.mid'
    score.write('midi', fp=midi_file_path)
    print(f"MIDI file saved to {midi_file_path}")


def generate_transition_matrix(data_path, m_order: int = 3) -> None:
    """ Parse Choco Chord Data into Transition Matrix and write to file """

    # Define path to jams files
    files = load_file_list(data_path)

    # Retrieve chord progressions from all files
    chord_progressions = get_progressions(files)
    chord_progressions_all = [
        item for sublist in chord_progressions for item in sublist
        if isinstance(item, str)
    ]

    chord_progressions_notes = chords_to_midi_notes(chord_progressions_all)

    # Save Set of Unique Chords
    unique_midi_chords = set([tuple(ch) for ch in chord_progressions_notes])
    with open('unique_midi_chords.pkl', 'wb') as f:
        pickle.dump(unique_midi_chords, f)

    # Generate New Sequence based on Markov Chain
    transition_matrix = compute_transition_chain(chord_progressions_notes, m_order=m_order)

    # Save the dictionary to a file
    with open('transition_matrix.pkl', 'wb') as f:
        pickle.dump(transition_matrix, f)


def main():
    """ Runs Estimation, Chord Sequence Generation and MIDI File Creation """

    # Settings for Markov Chain
    m_order = 2                 # Order for Markov Chain
    path = "data/jams"          # Path to Jams

    # Learn Chord Progressions for Markov Chain
    generate_transition_matrix(path, m_order=m_order)

    print('Saved Transition Matrix and Unique Chords to transition_matrix.pkl and unique_midi_chords.pkl')


if __name__ == "__main__":
    main()


