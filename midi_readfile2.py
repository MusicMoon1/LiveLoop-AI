import mido
from mido import MidiFile, merge_tracks, tick2second
from collections import namedtuple


# Constants
filename = "data/midi/dummy_2bars.mid"
BPM = 120
DEFAULT_TEMPO = mido.bpm2tempo(BPM)  # in microseconds per beat, should be 500000 @120bpm
DELTA = 0.06  # 60 ms
WINDOWS = [(0, 2),
           (2, 4),
           (4, 6),
           (6, 8)]

# --- Data Structures ---
NoteEvent = namedtuple('NoteEvent', ['note', 'start', 'end'])


# --- Step 1: Parse MIDI with accurate timing ---
mid = MidiFile(filename)
ticks_per_beat = mid.ticks_per_beat
tempo = DEFAULT_TEMPO

absolute_time = 0
current_tick = 0
tempo_map = [(0, tempo)]  # [(tick, tempo)]
note_starts = {}          # note -> start_time
note_events = []          # list of NoteEvent


######## !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
### for msg in mid:  # ASSUMES MERGED tracks!! This is SUPER IMPORTANT for the msg times!!!!!!
######## !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
merged = merge_tracks(mid.tracks)
for msg in merged:
    current_tick += msg.time
    if msg.type == 'set_tempo':
        tempo = msg.tempo
        tempo_map.append((current_tick, tempo))
    
    time_sec = tick2second(current_tick, ticks_per_beat, tempo)
    
    if msg.type == 'note_on' and msg.velocity > 0:
        note_starts[msg.note] = time_sec
    elif (msg.type == 'note_off') or (msg.type == 'note_on' and msg.velocity == 0):
        if msg.note in note_starts:
            note_events.append(NoteEvent(
                note=msg.note,
                start=note_starts[msg.note],
                end=time_sec
            ))
            del note_starts[msg.note]


# --- Step 2: Convert beats to seconds ---
def beat_to_seconds(beat):
    # ticks = beat * ticks_per_beat
    # last_tick = 0
    # last_tempo = DEFAULT_TEMPO
    # total_seconds = 0

    # for i, (tick, tempo) in enumerate(tempo_map):
    #     if tick >= ticks:
    #         break
    #     delta_ticks = tick - last_tick
    #     total_seconds += tick2second(delta_ticks, ticks_per_beat, last_tempo)
    #     last_tick = tick
    #     last_tempo = tempo

    # remaining_ticks = ticks - last_tick
    # total_seconds += tick2second(remaining_ticks, ticks_per_beat, last_tempo)
    ticks = beat * ticks_per_beat
    seconds = tick2second(ticks, ticks_per_beat, DEFAULT_TEMPO)
    return seconds


# --- Step 3: Analyze each window ---
def notes_active_in_window(start_beat, end_beat):
    start_sec = beat_to_seconds(start_beat)
    end_sec = beat_to_seconds(end_beat)
    active = set()
    for note in note_events:
        # Note is active if any part of it overlaps the window
        if not (note.end <= start_sec or note.start >= end_sec):
            active.add(note.note)
    return sorted(active)


# --- Step 4: Output results ---
for i, (b_start, b_end) in enumerate(WINDOWS):
    notes = notes_active_in_window(b_start+DELTA, b_end-DELTA)
    print(f"Window {i+1}: beats {b_start:.2f} - {b_end:.2f} → notes: {notes}")
