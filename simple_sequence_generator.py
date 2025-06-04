import numpy as np
import random


chord_formulas = {
    'maj': [0, 4, 3],
    'min': [0, 3, 4],
    'aug': [0, 4, 4],
    'dim': [0, 3, 3],
    'maj7': [4, 3, 4],
    'min7': [3, 4, 3],
    'dom7': [4, 3, 3],
    'halfdim7': [3, 3, 4],
    'dim7': [3, 3, 4],
    'minmaj7': [3, 4, 4],
    'augmaj7': [4, 4, 3],
    'augaug7th': [4, 4, 3]
}


def generate_chord_notes(root_note, chord_type):
    """ Generates a chord given a root note. """
    intervals = chord_formulas[chord_type]
    return [root_note + sum(intervals[:i]) for i in range(len(intervals))]


root_note = 60  # example root note (C=60 in MIDI)
chord_notes = {}
for chord_type in chord_formulas.keys():
    chord_notes[chord_type] = generate_chord_notes(root_note, chord_type)


# Initialize transition matrix
chords = list(chord_formulas.keys())
transition_matrix = {chord: {next_chord: 0 for next_chord in chords} for chord in chords}

# Fill transition matrix with random probabilities
# or take the ones learned from Choco: transition_matrix.pkl
for chord in chords:
    random_probs = np.random.rand(len(chords))
    random_probs /= random_probs.sum()  # Normalize so it sums to 1
    for i, next_chord in enumerate(chords):
        transition_matrix[chord][next_chord] = random_probs[i]


def next_chord(current_chord):
    """ Chooses next chords based on current chord """
    next_chords = list(transition_matrix[current_chord].keys())
    probabilities = list(transition_matrix[current_chord].values())
    return np.random.choice(next_chords, p=probabilities)


def generate_variation(melody, length=10):
    """ Generates a variation of the input notes/melody.
        Param: length -- the number of output notes """
    variation = []
    current_chord = random.choice(list(chord_formulas.keys()))
    for note in melody:
        variation.append(note)
        chord_notes = generate_chord_notes(note, current_chord)
        variation.extend(random.sample(chord_notes, min(len(chord_notes), length)))
        current_chord = next_chord(current_chord)
    return variation


input_melody = [60, 62, 64, 65, 67]  # Example input melody (MIDI notes)
output_melody = generate_variation(input_melody)  # Generate a variation of the input melody

print("Input notes:", input_melody)
print("Generated variation:", output_melody)
