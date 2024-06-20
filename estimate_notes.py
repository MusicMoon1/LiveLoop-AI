import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import essentia.standard as es

from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH


def inputaudio(audiofile):
    samples, sr = librosa.load(audiofile)
    return samples, sr


def cqt(samples, sr):
    cqt = librosa.cqt(y=samples, sr=sr, bins_per_octave=12)
    return cqt


def plot(cqt):
    fig, ax = plt.subplots()
    img = librosa.display.specshow(librosa.amplitude_to_db(cqt, ref=np.max),
                                    sr=sr, x_axis='time', y_axis='cqt_note', ax=ax)
    ax.set_title('CQT -- close this to proceed')
    fig.colorbar(img, ax=ax, format="%+2.0f dB")

    plt.tight_layout()
    plt.show()


def active_notes(midi_data):
    """ Gets list of active notes from the midi piano roll. """
    piano_roll = midi_data.get_piano_roll()

    plt.imshow(piano_roll, aspect='auto', origin='lower', cmap='gray_r')
    plt.xlabel('Time')
    plt.ylabel('Pitch')
    plt.title('Piano Roll -- close this to proceed')
    plt.show()
    active_notes = []
    for row_idx in range(piano_roll.shape[0]):
        if np.any(piano_roll[row_idx] > 0):
            active_notes.append(row_idx)
    print(f"active notes in this loop: {active_notes}")


def transpose_notes(notes, octave=0):
    if min(notes) >= 60:
        return notes
    notes = [int(note) + 12 for note in notes]
    octave += 1
    return transpose_notes(notes, octave)


def estimate_pitch_basic(audio):
    model_output, midi_data, note_events = predict(audio)
    # Get All Notes Played as Midi Notes
    all_notes = []
    for instrument in midi_data.instruments:
        for note in instrument.notes:
            all_notes.append(note.pitch)
    return all_notes


def estimate_pitch_melodia(audiofile):
    # Load File
    loader = es.EqloudLoader(filename=audiofile, sampleRate=44100)
    audio = loader()

    pitch_extractor = es.PredominantPitchMelodia(frameSize=2048, hopSize=128)
    pitch_values, _ = pitch_extractor(audio)
    # pitch_times = np.linspace(0.0, len(audio) / 44100.0, len(pitch_values))
    onsets, durations, notes = es.PitchContourSegmentation(hopSize=128)(pitch_values, audio)

    return notes


if __name__ == "__main__":
    # audiofile = "61228__the-sacha-rush__piano1.wav"
    audiofile = "data/loops/Loop1_anahata.aif"
    # Predict Notes

    all_notes = set(estimate_pitch_melodia(audiofile))
    # Transpose Notes so that Lowest Note is above 60
    all_notes_transposed = transpose_notes(all_notes)

    print(f'All Present Notes: {all_notes}')



