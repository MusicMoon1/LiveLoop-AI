import mido
from mido import Message
import time

out_port = mido.open_output("Python MIDI Input")  # open virtual MIDI port

# Define a chord (e.g. C_maj: C4, E4, G4)
notes = [60, 64, 67]

for note in notes:
    msg = Message('note_on', note=note, velocity=64)
    out_port.send(msg)
    time.sleep(0.01)

time.sleep(2)  # hold chord for 2 seconds

for note in notes:
    msg = Message('note_off', note=note, velocity=0)
    out_port.send(msg)
    time.sleep(0.01)

"""
This creates a virtual MIDI output named "Python MIDI Output".

3. Connect Max/MSP to the virtual port
In Max:
- Use a notein or midiin object
- Use a midiinfo object to see available ports
- Select "Python MIDI Output" from the list in your MIDI setup or Max device selector.
"""