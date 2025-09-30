from pathlib import Path
from json_writer import PianoVisionJsonWriter
from midi_writer import write_midi
from note_capture import capture_notes, HandMaps  # renamed back to capture_notes for clarity

def render_sequence(
    seq_name: str,
    state_sequence,
    chords,
    fingers_used,
    *,
    tempo: float,
    maps: HandMaps,
    out_root: Path,
    seed: int,
    ts=(4, 4),
    ppq=960,
):
    """
    Render one state sequence into both a MIDI file and a PianoVision JSON file.

    Args:
        seq_name (str): Name of the sequence (used for filenames).
        state_sequence: A list of integers indexing into `chords`.
        chords: List of (pitch_a, pitch_b) tuples, one per state.
        tempo (float): Tempo in beats per minute.
        maps (HandMaps): Object describing left/right key sets and fingerings.
        out_root (Path): Root folder where the output should be written.
        seed (int): Seed identifier (used in folder/filenames).
        ts (tuple): Time signature as (numerator, denominator). Default (4, 4).
        ppq (int): MIDI pulses per quarter note. Default 960.

    Returns:
        Tuple[Path, Path]:
            - Path to the generated MIDI file
            - Path to the generated JSON file
    """

    # --- Step 1: Convert the sequence into MIDI-friendly events + JSON note dicts ---
    events, right_notes, left_notes = capture_notes(
        state_sequence, chords, fingers_used, tempo=tempo, maps=maps
    )

    # --- Step 2: Write MIDI file from captured events ---
    midi_path = write_midi(
        seq_name,
        events,
        tempo=tempo,
        seed=seed,
        out_root=out_root,
    )

    # --- Step 3: Write PianoVision JSON next to the MIDI file ---
    writer = PianoVisionJsonWriter(bpm=tempo, ts=ts, ppq=ppq)
    json_path = midi_path.with_suffix(".pv.json")
    writer.write(json_path, right_notes, left_notes, f"seed_{seed}_{seq_name}")

    return midi_path, json_path
