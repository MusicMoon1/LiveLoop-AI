from dataclasses import dataclass
import re


@dataclass
class ChordData:
    root_notes: dict
    chord_types: dict
    chord_extensions: dict
    chord_inversions: dict


class Chord2MidiConverter:
    def __init__(self, chord_data):
        self.chord_data = chord_data
        self.root_notes = chord_data.root_notes
        self.chord_types = chord_data.chord_types
        self.chord_extensions = chord_data.chord_extensions
        self.chord_inversions = chord_data.chord_inversions

    @staticmethod
    def delace_annotation(annotation: str):
        """ Delace Chord Annotation into Root, Chord, Extension, and Inversion
        :parameter annotation: str
        :return: tuple(str, str, str, str)
        """

        # Add a period to the end of the annotation to make the regex work
        annotation += '.'

        root_pattern = r'(.*:)'
        root_match = re.search(root_pattern, annotation)
        root = root_match.group()[:-1] if root_match else None

        chord_pattern = r':(.*?)(?=[(/\.])'
        chord_match = re.search(chord_pattern, annotation)
        chord = chord_match.group()[1:] if chord_match else None

        extension_pattern = r'\((.*?)\)'
        extension_match = re.search(extension_pattern, annotation)
        extension = extension_match.group()[1:-1] if extension_match else None

        inversion_pattern = r'/(.*)'
        inversion_match = re.search(inversion_pattern, annotation)
        inversion = inversion_match.group()[1:-1] if inversion_match else None

        return root, chord, extension, inversion

    def parse_chord(self, annotation):
        """ Parse a chord annotation and return a list of MIDI notes """
        # Delace the annotation
        root, chord, extension, inversion = self.delace_annotation(annotation)

        # Get Midi Note for Root
        root_note = self.root_notes[root] if root in self.root_notes else None
        chord_notes = self.chord_types[chord] if chord in self.chord_types else [0]
        extensions = self.chord_extensions[extension] if extension in self.chord_extensions else None
        inversion = self.chord_inversions[inversion] if inversion in self.chord_inversions else None

        # Handle invalid chord
        if not root_note:
            return None

        # Combine all notes
        base_notes = [root_note + note for note in chord_notes]
        midi_notes = base_notes + extensions if extensions else base_notes

        # Handle inversion
        if inversion:
            inversion_note = root_note + inversion[0]
            notes_shifted = [note for note in midi_notes if note <= inversion_note]
            for note in notes_shifted:
                midi_notes.remove(note)
                midi_notes.append(note + 12)

        # Sanity Filter for MIDI Notes
        midi_notes = [note for note in midi_notes if 59 <= note <= 127]

        return midi_notes


# Initialize the ChordData with the note-to-MIDI mapping and chord intervals
chord_data = ChordData(
    root_notes={
        'B#': 72,
        'B': 71,
        'Bb': 70,

        'A#': 70,
        'A': 69,
        'Ab': 68,

        'Gb': 66,
        'G': 67,
        'G#': 68,

        'F#': 66,
        'F': 65,
        'Fb': 64,

        'E#': 65,
        'E': 64,
        'Eb': 63,

        'D#': 63,
        'D': 62,
        'Db': 61,

        'C#': 61,
        'C': 60,
        'Cb': 59,
    },
    chord_types={
        'maj': [0, 4, 7],
        'min': [0, 3, 7],
        'aug': [0, 4, 8],
        'dim': [0, 3, 6],

        'maj7': [0, 4, 7, 11],
        'min7': [0, 3, 7, 10],
        '7': [0, 4, 7, 10],
        'dim7': [0, 3, 6, 9],
        'hdim7': [0, 3, 6, 10],
        'minmaj7': [0, 3, 7, 11],

        'maj6': [0, 4, 7, 9],
        'min6': [0, 3, 7, 9],

        '9': [0, 7, 10, 14],
        'maj9': [0, 4, 7, 11, 14],
        'min9': [0, 3, 7, 10, 14],

        'sus4': [0, 6, 7],
        'sus2': [0, 2, 7],
    },
    chord_extensions={
        '#13': [22],
        '13': [21],
        'b13': [20],
        '#11': [18],
        '11': [17],
        'b11': [16],
        '#9': [15],
        '9': [14],
        'b9': [13],
        '#8': [13],
        '8': [12],
        'b8': [11],
        '#7': [11],
        '7': [10],
        'b7': [9],
        '#6': [9],
        '6': [8],
        'b6': [7],
        '#5': [8],
        '5': [7],
        'b5': [6],
        '#4': [6],
        '4': [5],
        'b4': [4],
        '#3': [5],
        '3': [4],
        'b3': [3],
        '#2': [3],
        '2': [2],
        'b2': [1],
        '#1': [1],
        '1': [0],
        'b1': [-1],
    },
    chord_inversions={
        '13': [21],
        '11': [17],
        '9': [14],
        '7': [10],
        '6': [9],
        '5': [7],
        '3': [4],
        '2': [3],
    }
)

chord_to_midi = Chord2MidiConverter(chord_data)
