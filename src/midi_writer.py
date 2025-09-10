from pathlib import Path
from typing import Dict, Any, Sequence, Tuple
from midiutil import MIDIFile

def write_midi(
    seq_name: str,
    events: Sequence[Dict[str, Any]],
    *,
    tempo: float,
    seed: int,
    out_root: Path,
    track_names: Tuple[str, ...] = ("Right", "Left"),
    channel: int = 0,
) -> Path:
    """
    Write a MIDI file from note 'events'.

    Args:
        seq_name (str): Name of the sequence (used in the file name).
        events (Sequence[Dict[str, Any]]): List of note events. Each event must have:
            - track (int): Which MIDI track the note belongs to (0=right, 1=left).
            - pitch (int): MIDI note number (0–127).
            - start_beats (float): Start time in beats.
            - duration_beats (float): Note duration in beats.
            - velocity (int): MIDI velocity (0–127).
        tempo (float): Tempo in beats per minute (BPM).
        seed (int): Random seed or sequence ID (used in folder/file name).
        out_root (Path): Root folder where files should be saved.
        track_names (Tuple[str, ...]): Optional names for tracks (defaults: "Right", "Left").
        channel (int): MIDI channel number (default 0).

    Returns:
        Path: Path to the written `.mid` file.
    """

    # --- Setup ---
    # Ensure we have enough tracks: take the maximum track index in events + 1,
    # and compare with the number of names in track_names.
    num_tracks = max(max(e["track"] for e in events) + 1, len(track_names))

    # Create a MIDIFile with the right number of tracks.
    mf = MIDIFile(
        numTracks=num_tracks,
        removeDuplicates=False,  # allow duplicate events if any
        deinterleave=False,      # keep track events as given
        file_format=1,           # type-1 MIDI: multi-track file
    )

    # --- Add track metadata ---
    for t in range(num_tracks):
        # Use provided track name if available, otherwise fallback to "Track N"
        name = track_names[t] if t < len(track_names) else f"Track {t}"
        mf.addTrackName(t, 0, name)
        mf.addTempo(t, 0, float(tempo))  # set tempo at start of track

    # --- Add note events ---
    for e in events:
        t = int(e["track"])             # which track
        p = int(e["pitch"])             # MIDI pitch
        start = float(e["start_beats"]) # start time in beats
        dur = float(e["duration_beats"])# duration in beats
        vel = int(e["velocity"])        # velocity (0–127)

        # Add the note event to the MIDI track
        mf.addNote(t, channel, p, start, dur, vel)

    # --- Save MIDI file ---
    # Create folder for this seed (e.g. "seed_4")
    seed_dir = out_root / f"seed_{seed}"
    seed_dir.mkdir(parents=True, exist_ok=True)

    # Build output path (e.g. "seed_4_Block_1.mid")
    midi_path = seed_dir / f"seed_{seed}_{seq_name}.mid"

    # Write binary MIDI file
    with open(midi_path, "wb") as fh:
        mf.writeFile(fh)

    return midi_path
