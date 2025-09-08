from pathlib import Path
import itertools
import random

import generate_states
import load_sequences
from midi_writer import render_sequence_to_midi

# --- config (easy to tweak / pass via CLI later)
TEMPO = 120
SEED  = 13

# --- pitches
pitches_left  = {"C4": 60, "D4": 62, "E4": 64, "F4": 65, "G4": 67}
pitches_right = {"C5": 72, "D5": 74, "E5": 76, "F5": 77, "G5": 79}

def main():
    here = Path(__file__).parent                    
    sequences_folder = here / "state_sequences"     
    out_root = here.parent / "generated_midis"

    # generate dyads + seed (your function should return (dyads, seed))
    dyads, seed = generate_states.generate_states(
        pitches_left, pitches_right, seed=SEED
    )

    # load all text sequences into a dict: {"Block_1": [..], ...}
    state_sequences = load_sequences.load_sequences(sequences_folder)

    # render each sequence to its own MIDI file
    for name, seq in state_sequences.items():
        path = render_sequence_to_midi(
            seq_name=name,
            dyads=dyads,
            state_sequence=seq,
            pitches_left=pitches_left,
            pitches_right=pitches_right,
            tempo=TEMPO,
            seed=seed,
            out_root=out_root,
            write_json= True
        )
        

if __name__ == "__main__":
    main()