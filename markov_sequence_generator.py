import jams
import os
import numpy as np
from music21 import stream, chord, note, meter
from chord_to_midi import chord_to_midi


def load_file_list(path):
    # Path is folder containing all the jams files
    return [file for file in os.listdir(path) if file.endswith(".jams")]


def get_chord_progression(file: str = None) -> list[str]:
    """ Return chord progression from a single file """
    audio_jams = jams.load(f'data/jams/{file}', validate=False)
    chord_progressions = [chord[2] for chord in audio_jams.annotations[0]['data']]
    return chord_progressions


def get_progressions(files: list[str] = None) -> list[list[str]]:
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
        current_state = sequence[i]
        # Get n Previous States
        prev_states = sequence[i - m_order:i]
        # Create Key if not existant
        if tuple(prev_states) not in transition_states:
            transition_states[tuple(prev_states)] = [current_state]
        # Add Current Value to Key if already occured
        else:
            transition_states[tuple(prev_states)].append(current_state)

    return transition_states


def generate_new_sequence(transition_states, size=100):
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
    start = list(transition_states)[np.random.randint(len(list(transition_states)))]
    # Initialise New Sequence with starting points
    new_sequence = list(start)

    no_matching_state = 0
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
            no_matching_state += 1
        # Pick Random State from Potential States
        next_state = potential_next_states[np.random.randint(0, len(potential_next_states))]
        # Append Next State to Sequence
        new_sequence.append(next_state)

    print("found no matching state for {} states".format(no_matching_state))

    return new_sequence


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
        new_sequence_midi.append(chord_to_midi.parse_chord(annotation=chord_notation))
    return new_sequence_midi


def create_midi_file(new_sequence_midi: list[list[int]], chord_duration: float = 2) -> None:
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
    midi_file_path = 'chord_progression.mid'
    score.write('midi', fp=midi_file_path)
    print(f"MIDI file saved to {midi_file_path}")


def main():
    # Define path to jams files
    m_order = 2
    path = "data/jams"
    files = load_file_list(path)

    # Retrieve chord progressions from all files
    chord_progressions = get_progressions(files)
    chord_progressions_all = [
        item for sublist in chord_progressions for item in sublist
        if isinstance(item, str)
    ]

    # Get unique chords and create a mapping between chord notation and index
    unique_chords = set(chord_progressions_all)
    chtoi = {ch: i for i, ch in enumerate(unique_chords)}
    itoch = {v: k for k, v in chtoi.items()}

    # Generate New Sequence based on Markov Chain
    transition_matrix = compute_transition_chain(chord_progressions_all, m_order=m_order)
    new_sequence = generate_new_sequence(transition_matrix, size=128)

    # Convert Chords to MIDI Notes
    new_sequence_midi = chords_to_midi_notes(new_sequence)

    # Create MIDI File
    create_midi_file(new_sequence_midi, chord_duration=2)


if __name__ == "__main__":
    main()
