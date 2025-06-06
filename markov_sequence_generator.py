import jams
import os
import pickle
import numpy as np
import random

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
    """ --- Compute Transition Chain for Markov Chain ---
    Parameters:
        sequence (np.ndarray): Sequence (e.g. notes from a chord progression)
        m_order (int): Order for Markov Chain
    Returns:
        transition_states (dict): Transition States
    """
    transition_states = {}  # init dict for transition states

    # iterate through sequence
    for i in range(m_order, len(sequence)):
        current_state = tuple(sequence[i])   # get current state
        # Get n previous states
        prev_states = sequence[i - m_order:i]
        prev_states = tuple([tuple(s) for s in prev_states])
        # Create Key if not existant
        if prev_states not in transition_states:
            transition_states[prev_states] = [current_state]
        # Add Current Value to Key if already occured
        else:
            transition_states[prev_states].append(current_state)

    return transition_states


def generate_new_sequence_oldest(start=None, transition_states=None, size=100):
    """ --- Generate New Sequence from Transition States ---
    Parameters:
        start (tuple): input/starting chord, e.g. (60, 64, 67)
        transition_states (dict): Transition States
        size (int): Output Size
    Returns:
        new_sequence (np.ndarray): New Sequence (i.e. notes)
    Example:
        ((63, 67, 70, 72), (63, 67, 70, 74), (63, 67, 70, 72), (64, 67, 70)): [(65, 68, 72, 75), (65, 68, 72, 75), (65, 68, 72, 75)]
        left side: last 4 chords in the sequence. right side: the next chord that followed
        So: in the pre-learned data, when the last 4 chords in the sequence were that (left),
        the next chord was always (65, 68, 72, 75), and that happened 3 times in that data.
        If the right side was: [(65, 68, 72, 75), (70, 74, 77, 80)], then each chord would have 50% chance of being chosen
        Thus: probabilites are encoded by repetition / inferred through random sampling with repetition
        So: Looking for keys that match the given start chord ensures the generated sequence begins in a musically meaningful way
        that connects to the trained data.
        If a tuple appears several times in the keys, it was just part of the musical phrase's pattern.
        Also: each key is a sequence of 4 chords -- means a 4th order Markov Chain
    """
    # Get Starting Point
    if not start:
        # start = next(iter(transition_states))
        start = list(transition_states)[np.random.randint(len(list(transition_states)))]
    else:
        # Normalize start to be a list of tuples, even if it's just one
        if isinstance(start, tuple):
            start = [start]
        # Start with Sequence starting with input/start chord
        # Get first states of transition states
        starting_states = [key for key in transition_states.keys() if key[0] == start]
        # randomly choose one from possible states: repeating entries increase their probability of being chosen
        start = starting_states[np.random.randint(0, len(starting_states))]

    # Initialise New Sequence with starting points/chords
    new_sequence = list(start)

    # Generate Sequence
    for _ in range(size):
        # Get Current State(s): Use the latest m_order (e.g. 4) elements of the sequence
        # In first iteration, this will be the same as "start"
        current_state = new_sequence[-len(start):]
        # Get potential next state(s)
        if tuple(current_state) in list(transition_states.keys()):  # in first iter, this will always be true
            potential_next_states = transition_states[tuple(current_state)]
        else:
            # If State does not exist, lower the order
            potential_next_states = get_lower_order_state(transition_states, current_state)
        # Pick Random State from Potential States
        next_state = potential_next_states[np.random.randint(0, len(potential_next_states))]
        # Append Next State to Sequence
        new_sequence.append(next_state)
        if len(new_sequence) == size:
            print(f"New sequence reached size {size} as defined. Stopping generation.")
            break

    return [list(s) for s in new_sequence]


def generate_new_sequence_old2(start=None, transition_states=None, size=100):
    """ Generate a new sequence from a Markov chain of chord transitions.
    Parameters:
        start (tuple or list of tuples): Starting chord or sequence of chords.
        transition_states (dict): Transition states of the Markov chain.
        size (int): Desired length of generated sequence.
    Returns:
        list of lists: New generated sequence.
    """
    # Convert to list if start is a single tuple
    if start is None:
        start = list(transition_states)[np.random.randint(len(transition_states))]
    elif isinstance(start, tuple):
        # Look for starting sequences where the first chord matches
        candidates = [key for key in transition_states if key[0] == start]
        if not candidates:
            raise ValueError(f"No transitions starting with chord {start}")
        start = list(candidates[np.random.randint(0, len(candidates))])
    elif isinstance(start, list):
        # Ensure all elements are tuples (e.g., chords)
        if not all(isinstance(chord, tuple) for chord in start):
            raise ValueError("If start is a list, it must contain tuples.")
    else:
        raise TypeError("start must be None, a tuple, or a list of tuples.")

    new_sequence = list(start)

    for _ in range(size):
        # Use the latest m-order chords (length of key)
        m_order = len(list(transition_states.keys())[0])  # assumes consistent order
        current_state = tuple(new_sequence[-m_order:])
        
        if current_state in transition_states:
            potential_next_states = transition_states[current_state]
        else:
            potential_next_states = get_lower_order_state(transition_states, list(current_state))
        
        next_state = potential_next_states[np.random.randint(0, len(potential_next_states))]
        new_sequence.append(next_state)

        if len(new_sequence) >= size:
            print(f"New sequence reached size {size}.")
            break

    return [list(s) for s in new_sequence]


def generate_new_sequence_old1(start=None, transition_states=None, size=100):
    """
    Generate a new sequence using the given Markov transition states.
    
    Parameters:
        start (list/tuple): optional list of chords to begin with, e.g. [(60, 64, 67), (62, 65, 69)]
        transition_states (dict): transition mapping
        size (int): desired length of output sequence

    Returns:
        list: new sequence of chords
    """
    import numpy as np

    keys = list(transition_states.keys())

    # Normalize start input
    if start is None:
        # No input — pick a random state
        start = list(keys[np.random.randint(len(keys))])
    elif isinstance(start[0], int):
        # Single chord (like (60, 64, 67)), wrap it in a list
        start = [start]

    # Try to find a full sequence match
    for i in range(len(start), 0, -1):
        subseq = tuple(start[-i:])  # Try last i chords
        if subseq in transition_states:
            start = list(subseq)
            break
    else:
        # No matching key found — fallback
        print("Warning: No matching state found for start sequence.")
        # At least ensure all chords appear somewhere
        found = [ch for ch in start if any(ch in key for key in keys)]
        if found:
            start = [found[0]]
        else:
            # Fallback to random
            start = list(keys[np.random.randint(len(keys))])

    # Start generating
    new_sequence = list(start)

    for _ in range(size):
        current_state = tuple(new_sequence[-len(start):])
        if current_state in transition_states:
            options = transition_states[current_state]
        else:
            options = get_lower_order_state(transition_states, list(current_state))
        next_chord = options[np.random.randint(len(options))]
        new_sequence.append(next_chord)

    return [list(chord) for chord in new_sequence]


def generate_new_sequence(start=None, transition_states=None, size=100):
    """
    Generate a new sequence from transition states, optionally seeded with a multi-chord start phrase.
    Parameters:
        start (list[tuple]): starting sequence of chords (e.g. [(60, 64, 67), (62, 65, 69)])
        transition_states (dict): the Markov model
        size (int): length of sequence to generate
    Returns:
        new_sequence (list[list]): generated note sequence
    """
    if not start:
        start = list(transition_states)[np.random.randint(len(transition_states))]
    else:
        # Ensure start is a tuple of tuples
        if isinstance(start[0], int):
            # Single chord passed as a tuple like (60, 64, 67)
            start = [start]
        start_tuple = tuple(start)
        
        # Try to find an exact match in transition states
        if start_tuple in transition_states:
            pass  # exact start sequence found
        else:
            # Try to find a matching sequence ending with the first chord
            fallback_states = [key for key in transition_states if key[-1] == start[0]]
            if fallback_states:
                start_tuple = fallback_states[np.random.randint(0, len(fallback_states))]
            else:
                # Absolute fallback: pick a random key
                start_tuple = list(transition_states)[np.random.randint(len(transition_states))]

    # Initialize new sequence
    new_sequence = list(start_tuple)

    for _ in range(size):
        current_state = tuple(new_sequence[-len(start_tuple):])
        if current_state in transition_states:
            potential_next_states = transition_states[current_state]
        else:
            potential_next_states = get_lower_order_state(transition_states, list(current_state))
        
        if not potential_next_states:
            break

        next_state = potential_next_states[np.random.randint(len(potential_next_states))]
        new_sequence.append(next_state)

        if len(new_sequence) >= size:
            break

    return [list(chord) for chord in new_sequence]


def get_lower_order_state(transition_states, current_state): 
    """ --- Recursively Get Lower Order Transition States ---
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
    ch2i = {ch: i for i, ch in enumerate(unique_chords)}
    i2ch = {v: k for k, v in ch2i.items()}
    return unique_chords, ch2i, i2ch


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
    """ Computes unique chords and the transition chain/matrix """

    # Settings for Markov Chain
    m_order = 4

    # Learn Chord Progressions for Markov Chain
    generate_transition_matrix("data/jams", m_order=m_order)

    print('Saved Transition Matrix and Unique Chords to transition_matrix.pkl and unique_midi_chords.pkl')


if __name__ == "__main__":
    main()
