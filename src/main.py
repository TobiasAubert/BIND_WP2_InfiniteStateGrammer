from pathlib import Path

import generate_states
import load_sequences

from note_capture import build_default_maps, capture_notes
from midi_writer import write_midi
from json_writer import PianoVisionJsonWriter
from renderer import render_sequence

# --- config (easy to tweak / pass via CLI later)
TEMPO = 120
SEED  = 10

# --- pitches (note: your LH is higher than RH here; that's fine if intentional)
pitches_left  = {"C4": 60, "D4": 62, "E4": 64, "F4": 65, "G4": 67}
pitches_right = {"C5": 72, "D5": 74, "E5": 76, "F5": 77, "G5": 79}

def main():
    here = Path(__file__).parent
    sequences_folder = here / "state_sequences"
    out_root = here.parent / "generated_midis"

    # 1) dyads + seed
    dyads, seed = generate_states.generate_states(
        pitches_left, pitches_right, seed=SEED
    )

    # 2) build maps (hand routing + optional fingerings)
    maps = build_default_maps(pitches_left, pitches_right)

    # 3) load sequences
    state_sequences = load_sequences.load_sequences(sequences_folder)

    # 4) render each sequence
    for name, seq in state_sequences.items():
        render_sequence(
            seq_name=name,
            state_sequence=seq,
            dyads=dyads,
            tempo=TEMPO,
            maps=maps,
            out_root=out_root,
            seed=SEED,)
        
if __name__ == "__main__":
    main()
