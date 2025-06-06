import mido
from mido import MidiFile, tick2second
from collections import namedtuple

# ------------------------
# Config
# ------------------------
filename = "data/midi/dummy_2bars.mid"
DELTA = 0.06  # 60 ms tolerance
BEAT_WINDOWS = [(0, 2 - DELTA), (2 + DELTA, 4 - DELTA), (4 + DELTA, 6 - DELTA), (6 + DELTA, 8 - DELTA)]

# ------------------------
# Step 1: Load MIDI
# ------------------------
mid = MidiFile(filename)
ticks_per_beat = mid.ticks_per_beat
DEFAULT_TEMPO = 500000  # microseconds per beat

# ------------------------
# Step 2: Build absolute time map
# ------------------------
tempo = DEFAULT_TEMPO
tempo_changes = [(0, tempo)]
note_starts = {}
note_events = []

NoteEvent = namedtuple('NoteEvent', ['note', 'start', 'end'])

absolute_tick = 0
absolute_sec = 0

for msg in mid:
    delta_sec = tick2second(msg.time, ticks_per_beat, tempo)
    absolute_sec += delta_sec
    absolute_tick += msg.time

    if msg.type == 'set_tempo':
        tempo = msg.tempo
        tempo_changes.append((absolute_tick, tempo))

    if msg.type == 'note_on' and msg.velocity > 0:
        note_starts[msg.note] = absolute_sec
    elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
        if msg.note in note_starts:
            note_events.append(NoteEvent(note=msg.note, start=note_starts[msg.note], end=absolute_sec))
            del note_starts[msg.note]

# ------------------------
# Step 3: Beat → Seconds conversion
# ------------------------
def beat_to_seconds(beat):
    ticks = beat * ticks_per_beat
    total_sec = 0
    last_tick = 0
    tempo = DEFAULT_TEMPO

    for i in range(len(tempo_changes)):
        tick_i, tempo_i = tempo_changes[i]
        if tick_i >= ticks:
            break
        next_tick = tempo_changes[i + 1][0] if i + 1 < len(tempo_changes) else ticks
        dticks = min(ticks, next_tick) - tick_i
        total_sec += tick2second(dticks, ticks_per_beat, tempo_i)
        last_tick = tick_i
        tempo = tempo_i

    if ticks > last_tick:
        dticks = ticks - last_tick
        total_sec += tick2second(dticks, ticks_per_beat, tempo)

    return total_sec

# ------------------------
# Step 4: Active note detection per window
# ------------------------
def get_notes_in_window(start_beat, end_beat):
    start_time = beat_to_seconds(start_beat)
    end_time = beat_to_seconds(end_beat)
    active_notes = set()

    for note in note_events:
        # If note overlaps window
        if not (note.end <= start_time or note.start >= end_time):
            active_notes.add(note.note)

    return sorted(active_notes)

# ------------------------
# Step 5: Run analysis
# ------------------------
for i, (b_start, b_end) in enumerate(BEAT_WINDOWS):
    notes = get_notes_in_window(b_start, b_end)
    print(f"Window {i+1}: Beats {b_start:.2f} → {b_end:.2f} → Notes: {notes}")
