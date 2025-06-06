import mido
import time
import markov_main as mkv
from estimate_notes import get_chord_from_notes, get_closest_chord
from datetime import datetime


BPM = 120
BEATS_PER_BAR = 4
TOTAL_BARS = 2
SECONDS_PER_BEAT = 60 / BPM  # 0.5s
TOTAL_DURATION = SECONDS_PER_BEAT * BEATS_PER_BAR * TOTAL_BARS
DELTA = 0.0  # 0.02 = 20 ms

timeout_seconds = 10
wait_start = time.time()

print("If notes are not recorded properly, check delta time for the analysis windows.")
print("Waiting for first MIDI event...")
in_port = mido.open_input("Python MIDI Input", virtual=True)  # creates virtual input
while True:
    msg = in_port.poll()
    if msg:
        print(f"Received first MIDI msg: {msg}")
        start_time = time.time()  # start timing now
        note_events = [(0, msg)]  # timestamp 0 relative to first event
        break
    if time.time()-wait_start > timeout_seconds:
        print(f"No MIDI input after {timeout_seconds} seconds, exiting.")
        exit()
    time.sleep(0.001)  # avoid busy waiting

# record for 2 bars
print(f"Started recording for {TOTAL_DURATION} seconds...")
while time.time()-start_time < TOTAL_DURATION:
    msg = in_port.poll()
    if msg and msg.type in ["note_on", "note_off"]:
        note_events.append((time.time()-start_time, msg))  # timestamp relative to bar start
        print(f"Received msg: {msg}")
print("Finished recording.")


# Process the data
def get_notes_between(start_beat, end_beat):
    """ Return all note_on messages that started between two beats. """
    start_sec = start_beat * SECONDS_PER_BEAT
    end_sec = end_beat * SECONDS_PER_BEAT

    active_notes = set()
    for t, msg in note_events:
        if start_sec <= t < end_sec:
            if msg.type == "note_on" and msg.velocity > 0:
                active_notes.add(msg.note)
            elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                active_notes.discard(msg.note)
    return active_notes


### define beat windows
windows = [
    (0, 2),   # Bar 1 beat 1 to 3
    (2, 4),   # Bar 1 beat 3 to bar 2 beat 1
    (4, 6),   # Bar 2 beat 1 to 3
    (6, 8),   # Bar 2 beat 3 to end
]

### analyze windows
chords = []
for i, (start, end) in enumerate(windows):
    notes = get_notes_between(start+DELTA, end-DELTA)
    print(f"Window {i+1}: beats {start}-{end} → notes: {sorted(notes)}")
    if notes:  # set is not empty, a.k.a. notes were played in this window
        if len(notes) >= 3:
            chords.append(notes)
print(f"chords: {chords}")

### start markov sequence generation
unique_midi_chords, transition_matrix = mkv.load_data()
chords_refined = []
for chord in chords:
    input_chord, chord_length = get_chord_from_notes(chord)
    closest_chord, distance = get_closest_chord(input_chord, unique_midi_chords, chord_length, weight=100.0)
    chords_refined.append(closest_chord)
if not chords_refined:
    print("No chords(_refined) detected! Generating from random start...")
else:
    print(f"chords_refined: {chords_refined}")

new_chord_sequence = mkv.generate_new_sequence(chords_refined, transition_matrix, size=len(chords_refined)*2)
print(f"Generated chord sequence: {new_chord_sequence}")

currdate = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"data/midi/{currdate}_markov_out.mid"
mkv.create_midi_file(new_chord_sequence, chord_duration=2, file_name=filename)
