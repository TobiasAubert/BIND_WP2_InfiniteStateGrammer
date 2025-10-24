from pathlib import Path
import sys

import generate_states
import load_sequences

from note_capture import build_default_maps, capture_notes
from midi_writer import write_midi
from json_writer import PianoVisionJsonWriter
from renderer import render_sequence
import sys

# --- config (easy to tweak / pass via CLI later)
TEMPO = 120
SEED  = 20
FINGERS_USED = 2  # how many fingers per hand to use (for chord generation)
SCROLL_SPEED = 20.0  # visual scroll speed multiplier for PianoVision JSON (>1 = faster visuals)
# how many chords to generate of each type (must sum to 9)
CHORDS_LEFT_HAND = 2 # how many only left hand chords as states ()
CHORDS_RIGHT_HAND = 2 # how many only right hand chords as states
CHORDS_CROSS_HAND = 5 # how many cross hand chords as states

# --- pitches (note: your LH is higher than RH here; that's fine if intentional)
pitches_left  = {"C4": 60, "D4": 62, "E4": 64, "F4": 65, "G4": 67}
pitches_right = {"C5": 72, "D5": 74, "E5": 76, "F5": 77, "G5": 79}

def main():
    here = Path(__file__).parent
    sequences_folder = here / "state_sequences"
    out_root = here.parent / "generated_midis"

    # Validation
    if CHORDS_LEFT_HAND + CHORDS_RIGHT_HAND + CHORDS_CROSS_HAND != 9:
        sys.exit("Error: CHORDS_LEFT_HAND + CHORDS_RIGHT_HAND + CHORDS_CROSS_HAND must sum to 9!")
    if FINGERS_USED > 10:
        sys.exit("Error: FINGERS_USED cannot be more than 10! most people only have 10")
    if FINGERS_USED < 1:
        sys.exit("Error: FINGERS_USED must be at least 1!")

    # 1) chords + seed (generate_states now returns both chords and a human-readable list)
    chords, states_listed = generate_states.generate_states(
        pitches_left,
        pitches_right,
        n_left=CHORDS_LEFT_HAND,
        n_right=CHORDS_RIGHT_HAND,
        n_cross=CHORDS_CROSS_HAND,
        fingers_used=FINGERS_USED,
        seed=SEED,
    )

    # write states list once per seed 
    generate_states.write_states_file(out_root, states_listed, SEED)

    # 2) build maps (hand routing + optional fingerings)
    maps = build_default_maps(pitches_left, pitches_right)
    
    # 3) load sequences
    state_sequences = load_sequences.load_sequences(sequences_folder)

    # 4) render each sequence
    for name, seq in state_sequences.items():
        render_sequence(
            seq_name=name,
            state_sequence=seq,
            chords=chords,
            fingers_used=FINGERS_USED,
            tempo=TEMPO,
            scroll_speed=SCROLL_SPEED,
            maps=maps,
            out_root=out_root,
            seed=SEED,
        )

if __name__ == "__main__":
    main()
