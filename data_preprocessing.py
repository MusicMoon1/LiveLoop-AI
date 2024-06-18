import jams
import os


def load_file_list(path):
    # Path is folder containing all the jams files
    return [file for file in os.listdir(path) if file.endswith(".jams")]


def get_chord_progression(file: str = None) -> list[str]:
    """ Return chord progression from a single file """
    audio_jams = jams.load(f'data/jams/{file}', validate=False)
    # chord_progressions = [chord for chord in audio_jams.annotations[0]['data']]
    chord_progressions = [chord[2] for chord in audio_jams.annotations[0]['data']]
    return chord_progressions


def get_progressions(files: list[str] = None) -> list[list[str]]:
    all_chord_progressions = []
    for file in files:
        all_chord_progressions.append(get_chord_progression(file))
    return all_chord_progressions


def get_notes_for_chords(chord_progressions: list[list[str]]) -> list[list[str]]:
    # Get notes for each chord
    # Alvero you could fill in this function here :)
    pass


def main():
    path = "data/jams"
    files = load_file_list(path)
    chord_progressions = get_progressions(files)
    chord_progressions_notes = [get_notes_for_chords(chord_progression) for chord_progression in chord_progressions]


if __name__ == "__main__":
    main()
