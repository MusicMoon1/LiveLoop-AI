import mido
from mido import MidiFile, MidiTrack, Message, MetaMessage


### settings
BPM = 120
BEAT_DURATION = 60 / BPM  # seconds per beat
TICKS_PER_BEAT = 480  # standard resolution
BAR_BEATS = 4
TOTAL_BARS = 2


### create MIDI file
mid = MidiFile(ticks_per_beat=TICKS_PER_BEAT)
track = MidiTrack()
mid.tracks.append(track)
track.append(MetaMessage("set_tempo", tempo=mido.bpm2tempo(BPM)))  # set tempo


### add notes
# Bar 1 -- beat 1: C_maj; beat 3: G_maj
track.append(Message("note_on", note=60, velocity=64, time=0))  # C
track.append(Message("note_on", note=64, velocity=64, time=0))  # E
track.append(Message("note_on", note=67, velocity=64, time=0))  # G
track.append(Message("note_off", note=60, velocity=64, time=TICKS_PER_BEAT * 2))  # beat 3
track.append(Message("note_off", note=64, velocity=64, time=0))
track.append(Message("note_off", note=67, velocity=64, time=0))

track.append(Message("note_on", note=55, velocity=64, time=0))  # G
track.append(Message("note_on", note=59, velocity=64, time=0))  # B
track.append(Message("note_on", note=62, velocity=64, time=0))  # D
track.append(Message("note_off", note=55, velocity=64, time=TICKS_PER_BEAT * 2))  # end of bar
track.append(Message("note_off", note=59, velocity=64, time=0))
track.append(Message("note_off", note=62, velocity=64, time=0))

# Bar 2 -- beat 1: D_min
track.append(Message("note_on", note=62, velocity=64, time=0))  # D
track.append(Message("note_on", note=65, velocity=64, time=0))  # F
track.append(Message("note_on", note=69, velocity=64, time=0))  # A
track.append(Message("note_off", note=62, velocity=64, time=TICKS_PER_BEAT * 4))  # whole bar
track.append(Message("note_off", note=65, velocity=64, time=0))
track.append(Message("note_off", note=69, velocity=64, time=0))


### save MIDI file
file_name = "data/midi/dummy_2bars.mid"
try:
    mid.save(f"{file_name}")
except Exception as e:
    print(f"Error saving MIDI file: {e}")
print(f"MIDI file {file_name} saved.")
