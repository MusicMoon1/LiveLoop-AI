import mido
import time

# Load the MIDI file
mid = mido.MidiFile("data/midi/dummy_2bars.mid")

# Create a virtual MIDI output port
outport = mido.open_output('Python MIDI Input')  # we are sending it to the same virtual input

# Play the MIDI file in real-time
start_time = time.time()
for msg in mid.play():  # This handles real-time delays
    if not msg.is_meta:
        outport.send(msg)


"""
for track in mid.tracks:
    for msg in track:
        time.sleep(msg.time)  # Wait the appropriate time
        if not msg.is_meta:
            outport.send(msg)
"""

