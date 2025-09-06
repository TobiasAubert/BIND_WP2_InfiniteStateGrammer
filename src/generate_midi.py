from midiutil import MIDIFile
import generate_states
from pathlib import Path
import load_sequences


pitches_left = {"C4": 60, "D4": 62, "E4": 64, "F4": 65, "G4": 67,}
pitches_right = {"C5": 72, "D5": 73, "E5": 74, "F5": 75, "G5": 76}

states = generate_states.generate_states(pitches_left,pitches_right, seed=1)

here = Path(__file__).parent
folder = here.parent / "src" / "state_sequences"
state_sequences = load_sequences.load_sequences(folder)

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

print(states[1])

def generate_midis(tempo = tempo, time = time, states = None, state_sequences = None, pitches_left = pitches_left):
    states, seed = states
    # states = states[0]
    # seed = states[-1]

    for name, state_sequence in state_sequences.items():
        for d in state_sequence:
            a,b = states[d]
            for pitch in (a,b):
                if a in pitches_left.values():
                    mf.addNote(0, channel=0, pitch=pitch, time=time, duration=1, volume=100)
                else:
                    mf.addNote(1, channel=0, pitch=pitch, time=time, duration=1, volume=100)
            
            time +=1

        # Save file
        save_midi(mf,seed, name)


def save_midi(mf, seed, name):
    here = Path(__file__).parent
    base_folder= here.parent / "generated_midis"
    
    seed_folder = base_folder / f"seed_{seed}"
    seed_folder.mkdir(parents=True,exist_ok=True) # create folder if missing

    #Full path for the midi file
    file_path = seed_folder / f"seed_{seed}_{name}.mid"

    with open(file_path, "wb") as output_file:
        mf.writeFile(output_file)

generate_midis(states=states, state_sequences=state_sequences)