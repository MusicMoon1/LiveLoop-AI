import numpy as np
import essentia.standard as es
import pickle


def transpose_notes(notes, octave=0):
    """ Transpose Notes to an Octave Above 60 """
    if min(notes) >= 60:
        return notes
    notes = [int(note) + 12 for note in notes]
    octave += 1
    return transpose_notes(notes, octave)


def estimate_pitch_melodia(audiofile):
    """ Estimate Pitch from Audio File """
    loader = es.EqloudLoader(filename=audiofile, sampleRate=44100)
    audio = loader()

    pitch_extractor = es.PredominantPitchMelodia(frameSize=2048, hopSize=128)
    pitch_values, _ = pitch_extractor(audio)
    onsets, durations, notes = es.PitchContourSegmentation(hopSize=128)(pitch_values, audio)

    return notes


def get_chord_from_audio(audiofile):
    """ Get Chord from Audio File """
    # Predict Notes
    all_notes = set(estimate_pitch_melodia(audiofile))
    # Transpose Notes so that Lowest Note is above 60
    all_notes_transposed = sorted(transpose_notes(all_notes))
    print(f'All Present Notes: {all_notes_transposed}')

    # Find Closest Chord
    chord_length = len(all_notes_transposed)
    # limit length to 4 notes
    if chord_length > 4:
        chord_length = 4
        input_chord = all_notes_transposed[:4]
    else:
        input_chord = all_notes_transposed
        chord_length = len(input_chord)

    return input_chord, chord_length


def get_weighted_distance(chord1, chord2, weight):
    """Calculate weighted Euclidean distance between two chords"""
    weighted_diff = (chord1[0] - chord2[0]) ** 2 * weight
    regular_diff = np.sum((np.array(chord1[1:]) - np.array(chord2[1:])) ** 2)
    return np.sqrt(weighted_diff + regular_diff)


def get_closest_chord(input_chord, unique_midi_chords, chord_length, weight=10.0):
    """Get closest chord from a list of unique chords, with a higher weighting on the first element"""
    # Get chords with the same length
    chords_same_length = [ch for ch in unique_midi_chords if len(ch) == chord_length]

    # Find closest chord to input
    min_distance = np.inf
    closest_chord = None
    for chord in chords_same_length:
        distance = get_weighted_distance(input_chord, chord, weight)
        if distance < min_distance:
            min_distance = distance
            closest_chord = chord

    return closest_chord


if __name__ == "__main__":

    # Testing Estimation
    file_name = 'Loop1_ragtime'
    audiofile = f"data/loops/{file_name}.aif"

    # Load the dictionary from a file
    with open('unique_midi_chords.pkl', 'rb') as f:
        unique_midi_chords = pickle.load(f)

    input_chord, chord_length = get_chord_from_audio(audiofile)

    closest_chord = get_closest_chord(input_chord, unique_midi_chords, chord_length)
    print(f'Input Chord: {input_chord} \n Most Similar Chord {closest_chord}')




