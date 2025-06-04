import numpy as np
import essentia.standard as es
import pickle
import pretty_midi as pm


def transpose_notes(notes, octave=0):
    """ Transpose Notes to an Octave Above 60 """
    if min(notes) >= 60:
        return notes
    notes = [int(note) + 12 for note in notes]
    octave += 1
    return transpose_notes(notes, octave)


def estimate_pitch_melodia(audiofile):
    """ Estimate Pitches from Audio File """
    loader = es.EqloudLoader(filename=audiofile, sampleRate=44100)
    audio = loader()

    pitch_extractor = es.PredominantPitchMelodia(frameSize=2048, hopSize=128)
    pitch_values, _ = pitch_extractor(audio)
    onsets, durations, notes = es.PitchContourSegmentation(hopSize=128)(pitch_values, audio)

    return set(notes)


def get_chord_from_notes(all_notes):
    """ Get Chord from a SET of notes """
    # Transpose Notes so that Lowest Note is above 60
    all_notes_transposed = sorted(transpose_notes(all_notes))
    print(f'All present notes transposed: {all_notes_transposed}')

    # Find Closest Chord
    chord_length = len(all_notes_transposed)

    # Chord Limit to Triad
    chord_lim = 3

    # limit length to n notes
    if chord_length > chord_lim:
        chord_length = chord_lim
        input_chord = all_notes_transposed[:chord_lim]
    else:
        input_chord = all_notes_transposed
        chord_length = len(input_chord)

    return input_chord, chord_length


def get_weighted_distance(chord1, chord2, weight):
    """ Calculates weighted Euclidean distance between two chords, assuming the first two notes are more important """
    chord1 = np.array(chord1)
    chord2 = np.array(chord2)

    weighted_diff = ((chord1[0] - chord2[0]) * weight) ** 2 + ((chord1[1] - chord2[1]) * weight) ** 2
    regular_diff = np.sum((chord1[2:] - chord2[2:]) ** 2)
    return np.sqrt(weighted_diff + regular_diff)


def get_closest_chord(input_chord, unique_midi_chords, chord_length, weight=10.0):
    """ --- Get closest chord from a list of unique chords, with a higher weighting on the first element ---
    # NOTE: some separate ideas here
    # a) consider using cosine similarity in get_weighted_distance()
    # b) consider returning all chords with a distance below a certain threshold to pick from the closest ones
    """

    # Get chords with the same length
    chords_same_length = [ch for ch in unique_midi_chords if len(ch) == chord_length]

    # Find closest chord to input
    min_distance = np.inf
    closest_chord = None
    for chord in chords_same_length:
        distance = get_weighted_distance(input_chord, chord, weight)
        print(f"Comparing input chord {input_chord} with chord {chord} -- distance: {distance}")
        if distance < min_distance:
            min_distance = distance
            closest_chord = chord

    return closest_chord, min_distance


def get_notes_from_MIDI(midi_file):
    """ Get set/list of active notes from a MIDI file """
    midi_data = pm.PrettyMIDI(midi_file)
    piano_roll = midi_data.get_piano_roll()

    # plt.imshow(piano_roll, aspect='auto', origin='lower', cmap='gray_r')
    # plt.xlabel('Time')
    # plt.ylabel('Pitch')
    # plt.title('Piano Roll -- close this to proceed')
    # plt.show()

    active_notes = []
    for row_idx in range(piano_roll.shape[0]):
        if np.any(piano_roll[row_idx] > 0):
            active_notes.append(row_idx)
    print(f"Active notes in {midi_file}: {active_notes}")

    return set(active_notes)


def test_estimation_audiofile(unique_midi_chords):
    """ --- Test chord estimation from an audio file ---
    Loads audio file, estimates active pitches/notes, and then estimates the chord played """
    
    file_name = "Loop1_ragtime"
    audiofile = f"data/loops/{file_name}.aif"

    all_notes = estimate_pitch_melodia(audiofile)  # predict active notes
    input_chord, chord_length = get_chord_from_notes(all_notes)  # estimate chord

    closest_chord = get_closest_chord(input_chord, unique_midi_chords, chord_length)
    print(f"Input chord: {input_chord}, chord length: {chord_length}\nMost similar chord: {closest_chord}")


def test_estimation_midifile(unique_midi_chords):
    """ --- Test chord estimation from a MIDI file --- 
    Loads MIDI file, reads all active pitches/notes, and then estimates the chord played """
    
    midi_file = "data/midi/c_e_fsharp.mid"
    #midi_file = "data/midi/chord_progression.mid"

    active_notes_set = get_notes_from_MIDI(midi_file)
    input_chord, chord_length = get_chord_from_notes(active_notes_set)  # estimate chord

    closest_chord, min_distance = get_closest_chord(input_chord, unique_midi_chords, chord_length)
    print(f"Input chord: {input_chord}, chord length: {chord_length}\nMost similar chord: {closest_chord}, distance: {min_distance}")


if __name__ == "__main__":
    # Load the unique MIDI chords dictionary from file
    with open('unique_midi_chords.pkl', 'rb') as f:
        unique_midi_chords = pickle.load(f)

    #test_estimation_audiofile(unique_midi_chords)
    test_estimation_midifile(unique_midi_chords)
