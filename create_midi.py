from music21 import stream, chord, meter


def create_midi_file(new_sequence_midi: list[list[int]], chord_duration: float = 2, file_name='midi') -> None:
    """ Create MIDI File from List of MIDI Notes """
    score = stream.Score()  # create a music21 score
    time_signature = meter.TimeSignature('4/4')  # define a 4/4 time signature
    score.append(time_signature)

    # Iterate over the list of MIDI chords and add them to a part for the chords
    chord_part = stream.Part()  # Create part for the chords
    for midi_notes in new_sequence_midi:
        # Create a chord from the MIDI notes
        m21_chord = chord.Chord(midi_notes)
        m21_chord.duration.quarterLength = chord_duration
        chord_part.append(m21_chord)  # Add the chord to the part
    score.append(chord_part)  # Add the chord part to the score

    # Save the score to a MIDI file
    midi_file_path = f"{file_name}_new.mid"
    try:
        score.write("midi", fp=midi_file_path)
    except Exception as e:
        print(f"Error saving MIDI file: {e}")
        return
    print(f"MIDI file saved to {midi_file_path}.")
