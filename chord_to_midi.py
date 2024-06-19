from dataclasses import dataclass
import re


@dataclass
class ChordData:
    note_to_midi: dict
    chord_intervals: dict
    chord_extensions: dict


class Chord2MidiConverter:
    def __init__(self, chord_data):
        self.chord_data = chord_data
        self.note_to_midi = chord_data.note_to_midi
        self.chord_intervals = chord_data.chord_intervals
        self.chord_extensions = chord_data.chord_extensions

    # Function to get the MIDI note number of a root note
    def get_root_midi(self, root):
        if root in chord_data.note_to_midi:
            return chord_data.note_to_midi[root]
        else:
            raise ValueError(f"Unsupported root note: {root}")

    # Function to parse the chord annotation and return MIDI notes
    def parse_chord(self, annotation):
        # Regex pattern to parse the chord annotation
        pattern = r"([A-G][b#]?)(:[a-zA-Z0-9]+)?(\([b#]?[0-9]+\))?(\/[0-9]+)?"
        match = re.match(pattern, annotation)

        if not match:
            # raise ValueError(f"Invalid chord annotation: {annotation}")
            print(f"Invalid chord annotation: {annotation} - skipping")
            return []

        root = match.group(1)
        chord_type = match.group(2)[1:] if match.group(2) else 'maj'
        extensions = match.group(3)[1:-1].split(',') if match.group(3) else []
        inversion = int(match.group(4)[1:]) if match.group(4) else None

        root_note = self.get_root_midi(root)
        base_notes = [root_note + interval for interval in chord_data.chord_intervals.get(chord_type, [])]

        # Handle extensions
        for ext in extensions:
            alteration = 0
            if ext.startswith('b'):
                alteration = -1
                ext = ext[1:]
            elif ext.startswith('#'):
                alteration = 1
                ext = ext[1:]

            ext = int(ext)
            base_notes.append(root_note + ext + alteration)

        # Handle inversion
        if inversion:
            base_notes = base_notes[inversion:] + base_notes[:inversion]

        return base_notes


# Initialize the ChordData with the note-to-MIDI mapping and chord intervals
chord_data = ChordData(
    note_to_midi={
        'Cb': 59, 'C': 60, 'C#': 61,
        'Db': 61, 'D': 62, 'D#': 63,
        'Eb': 63, 'E': 64, 
        'F': 65, 'F#': 66, 
        'Gb': 66, 'G': 67, 'G#': 68, 
        'Ab': 68, 'A': 69, 'A#': 70, 
        'Bb': 70, 'B': 71
    },
    chord_intervals={
        'maj': [0, 4, 7],
        'min': [0, 3, 7],
        'dim': [0, 3, 6],
        'aug': [0, 4, 8],
        'aug(b7)': [0, 4, 8, 11],  # same as 7(#5,*5)
        'maj7': [0, 4, 7, 11],
        'min7': [0, 3, 7, 10],
        'minmaj7': [0, 3, 7, 11],
        '7': [0, 4, 7, 10],  # same as b7
        '9': [0, 4, 7, 10, 14],
        '11': [0, 4, 7, 10, 14, 17],
        '13': [0, 4, 7, 10, 14, 17, 21],
        'maj6': [0, 4, 7, 9],
        'b6': [0, 4, 7, 8],
        'b3': [0, 2, 4, 7],
        '#9': [0, 4, 7, 15],
        'dim7': [0, 3, 6, 9],
        'min6': [0, 3, 7, 9],
        'maj9': [0, 4, 7, 11, 14],
        'min9': [0, 3, 7, 10, 14],
        'min11': [0, 3, 7, 10, 14, 17],
        'min13': [0, 3, 7, 10, 14, 17, 21],
        'sus4': [0, 5, 7],
        'sus2': [0, 2, 7],
        '7sus4': [0, 5, 7, 10],
        '7sus2': [0, 2, 7, 10],
        '7b5': [0, 4, 6, 10],
        '7#5': [0, 4, 8, 10],
        '7b9': [0, 4, 7, 10, 13],
        '#4': [0, 6, 7],
        '7(#9)': [0, 4, 7, 10, 15],
        'hdim': [0, 3, 6, 10],
    },
    chord_extensions={
        'b7': [10],
        'b6': [8],
        'b3': [2],
        '#9': [15],
        '#5': [8],
        '*5': [8],
    }
)

chord_to_midi = Chord2MidiConverter(chord_data)
