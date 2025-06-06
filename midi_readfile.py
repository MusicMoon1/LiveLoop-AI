import mido
import time

"""
This script simulates receiving MIDI messages and analyzes notes over two bars.
It assumes a MIDI file with two bars at 120 BPM, where each bar is 4 beats long (4/4 meter).
The script collects note events and analyzes them in two defined windows.
"""

mid = mido.MidiFile("data/midi/dummy_2bars.mid")  # load midi file

note_states = {}
events = []
start_time = time.time()

print("Starting MIDI playback simulation...")
for msg in mid.play():  # simulates real-time playback
    now = time.time()
    elapsed = now - start_time

    if msg.type == "note_on" and msg.velocity > 0:
        note_states[msg.note] = (elapsed, msg.velocity)
    elif (msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0)) and msg.note in note_states:
        on_time, velocity = note_states.pop(msg.note)
        events.append((msg.note, on_time, elapsed))
print("Finished playback. Analyzing windows & notes...")

# analysis windows
BEAT_DURATION = 0.5  # 120 BPM
WINDOWS = [
    (0, 2 * BEAT_DURATION),  # beats 1-3
    (2 * BEAT_DURATION, 4 * BEAT_DURATION + BEAT_DURATION)  # beats 3-1 (next bar)
]

def get_notes_in_window(events, start, end):
    notes = set()
    for note, on_time, off_time in events:
        if on_time < end and off_time > start:
            if not (on_time == end or off_time == start):  # edge case: starts exactly at end or ends exactly at start
                notes.add(note)
    return notes

window1_notes = get_notes_in_window(events, *WINDOWS[0])
window2_notes = get_notes_in_window(events, *WINDOWS[1])

print(f"Notes active during beats 1-3 (Bar 1): {sorted(window1_notes)}")
print(f"Notes active during beats 3-1 (Bar 1 → Bar 2): {sorted(window2_notes)}")
