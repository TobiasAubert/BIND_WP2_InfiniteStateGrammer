from pathlib import Path
from midiutil import MIDIFile

def render_sequence_to_midi(seq_name, dyads, state_sequence, pitches_left, tempo, seed, out_root: Path):
    mf = MIDIFile(2)                      # 0=left, 1=right
    mf.addTrackName(0, 0, "Left");  mf.addTempo(0, 0, tempo)
    mf.addTrackName(1, 0, "Right"); mf.addTempo(1, 0, tempo)

    t = 0
    for d in state_sequence:
        a, b = dyads[d]
        for pitch in (a, b):
            track = 0 if pitch in pitches_left.values() else 1
            mf.addNote(track, 0, pitch, t, 1, 100)
        t += 1

    seed_dir = out_root / f"seed_{seed}"
    seed_dir.mkdir(parents=True, exist_ok=True)
    path = seed_dir / f"seed_{seed}_{seq_name}.mid"
    with open(path, "wb") as out:
        mf.writeFile(out)
    return path