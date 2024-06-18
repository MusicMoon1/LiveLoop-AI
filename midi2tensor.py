from mido import MidiFile
import numpy as np

def midi_to_piano_roll(midi_path, time_step=0.05):
    midi = MidiFile(midi_path)
    max_time = max(trk[-1].time for trk in midi.tracks)
    num_time_steps = int(max_time // time_step) + 1
    piano_roll = np.zeros((128, num_time_steps))

    current_time = 0
    for track in midi.tracks:
        for msg in track:
            current_time += msg.time
            if msg.type == 'note_on' and msg.velocity > 0:
                t = int(current_time // time_step)
                piano_roll[msg.note, t] = msg.velocity
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                t = int(current_time // time_step)
                piano_roll[msg.note, t] = 0

    return piano_roll


if __name__ == "__main__":
    path = 'data/test_melody.mid'
    piano_roll = midi_to_piano_roll(path)
    print(piano_roll.shape)