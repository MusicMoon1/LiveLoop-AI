import mido
import time


### parameters
BPM = 120
BEAT_DURATION = 60 / BPM  # @120bpm: 0.5s per beat
BAR_DURATION = 4 * BEAT_DURATION  # @120bpm: 2s per bar
WINDOWS = [
    (0, 2 * BEAT_DURATION),  # duration: beat 1 to 3 (bar 1)
    (2 * BEAT_DURATION, BAR_DURATION + BEAT_DURATION)  # duration: beat 3 to beat 1 of bar 2
]


### receive MIDI
note_states = {}  # active notes: note -> (on_time, velocity)
events = []  # finished notes: list of (note, on_time, off_time)

start_time = None
in_port = mido.open_input("Python MIDI Input", virtual=True)
print("Waiting for incoming 2-bar MIDI...")
while True:
    msg = in_port.receive()

    now = time.time()
    if start_time is None:
        start_time = now
        print("Starting recording...")

    elapsed = now - start_time

    if msg.type == "note_on" and msg.velocity > 0:
        note_states[msg.note] = (elapsed, msg.velocity)

    elif (msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0)) and msg.note in note_states:
        on_time, velocity = note_states.pop(msg.note)
        events.append((msg.note, on_time, elapsed))

    # Stop analyzing after 2 bars (4 seconds at 120 bpm)
    if elapsed >= 2 * BAR_DURATION:
        print("Done recording. Analyzing windows...")
        break


def get_notes_in_window(events, start, end):
    notes = set()
    for note, on_time, off_time in events:
        # If any part of the note duration overlaps with the window
        if on_time < end and off_time > start:
            notes.add(note)
    return notes

window1_notes = get_notes_in_window(events, *WINDOWS[0])
window2_notes = get_notes_in_window(events, *WINDOWS[1])

print(f"Notes active during beat 1-3 (Bar 1): {sorted(window1_notes)}")
print(f"Notes active during beat 3-1 (Bar 1 → Bar 2): {sorted(window2_notes)}")
