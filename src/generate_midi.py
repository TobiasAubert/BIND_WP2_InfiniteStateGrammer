from midiutil import MIDIFile

# create a MIDI file with one track
mf = MIDIFile(2) # two tracks (Left 0 and Right 1)

tempo = 120
time = 0    # start at the beginning

# Track 0 left hand
mf.addTrackName(0, time, "Left Track")
mf.addTempo(0, time, tempo)

# Track 1 right hand
mf.addTrackName(1, time, "Right Track")
mf.addTempo(1, time, tempo)


# Aufwärmen
# Prestest
# Block 1 -8
# Posttest

def generate_midis(pitches = pitches, tempo = tempo, time = time, states = None, transitions = None):
    pass


# Example notes:
# Right hand (C4, E4, G4 chord)
mf.addNote(0, channel=0, pitch=60, time=0, duration=1, volume=100)
mf.addNote(0, channel=0, pitch=64, time=0, duration=1, volume=100)
mf.addNote(0, channel=0, pitch=67, time=0, duration=1, volume=100)

# Left hand (C3 bass note)
mf.addNote(1, channel=0, pitch=48, time=0, duration=1, volume=100)

# Save file
with open("piano_piece.mid", "wb") as output_file:
    mf.writeFile(output_file)