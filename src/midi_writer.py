from json_writer import PianoVisionJsonWriter  # the class we made earlier
from pathlib import Path
from midiutil import MIDIFile


def render_sequence_to_midi(seq_name, dyads, state_sequence,
                             pitches_left, pitches_right,
                             tempo, seed, out_root, write_json=True):

    # --- MIDI setup (unchanged) ---
    mf = MIDIFile(2)  # 0 = right, 1 = left
    mf.addTrackName(1, 0, "Left");  mf.addTempo(1, 0, tempo)
    mf.addTrackName(0, 0, "Right"); mf.addTempo(0, 0, tempo)

    # For fast membership checks
    LH_KEYS = sorted(pitches_left.values())
    RH_KEYS = sorted(pitches_right.values())

    #Fingering mapping
    # Left hand: C3..G3 (MIDI 48–55), fingers 5–1, thumb = 1
    LH_FINGERS = {
        LH_KEYS[0]: 5,  # C3
        LH_KEYS[1]: 4,  # D3
        LH_KEYS[2]: 3,  # E3
        LH_KEYS[3]: 2,  # F3
        LH_KEYS[4]: 1,  # G3
    }

    # Right hand: C4..G4 (MIDI 60–67), fingers 1–5, thumb = 1
    RH_FINGERS = {
        RH_KEYS[0]: 1,  # C4
        RH_KEYS[1]: 2,  # D4
        RH_KEYS[2]: 3,  # E4
        RH_KEYS[3]: 4,  # F4
        RH_KEYS[4]: 5,  # G4
    }

    # --- JSON note capture ---
    right_notes, left_notes = [], []
    spb = 60.0 / float(tempo)   # seconds per beat

    t_beats = 0.0
    for d in state_sequence:
        a, b = dyads[d]  # two MIDI pitches
        for pitch in (a, b):
            track = 1 if pitch in LH_KEYS else 0

            # MIDI note (time/duration are in BEATS)
            mf.addNote(track, 0, int(pitch), float(t_beats), 1.0, 100)

            # JSON note (start/duration are in SECONDS)
            note_dict = {
                "midi": int(pitch),
                "start": round(t_beats * spb, 6),
                "duration": round(1.0 * spb, 6),   # quarter note = 1 beat
                "velocity": round(100 / 127.0, 6),
                "finger": LH_FINGERS.get(int(pitch)) if track == 1 else RH_FINGERS.get(int(pitch))
            }
            if track == 1:
                left_notes.append(note_dict)
            else:
                right_notes.append(note_dict)

        t_beats += 1.0

    # --- Save MIDI ---
    seed_dir = out_root / f"seed_{seed}"
    seed_dir.mkdir(parents=True, exist_ok=True)
    midi_path = seed_dir / f"seed_{seed}_{seq_name}.mid"
    with open(midi_path, "wb") as out:
        mf.writeFile(out)

    # --- Save PianoVision JSON next to the MIDI ---
    if write_json:
        writer = PianoVisionJsonWriter(bpm=tempo, ts=(4,4), ppq=960)
        json_path = midi_path.with_suffix(".pv.json") 
        writer.write(json_path, right_notes, left_notes, f"seed_{seed}_{seq_name}")

    return midi_path

