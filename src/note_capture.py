from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple, Set, Any

# A mapping of which pitches belong to each hand,
# and which finger numbers (1–5) should be assigned to those pitches.
@dataclass(frozen=True)
class HandMaps:
    lh_fingers: Dict[int, int]  # pitch -> finger for left hand (5 = pinky … 1 = thumb)
    rh_fingers: Dict[int, int]  # pitch -> finger for right hand (1 = thumb … 5 = pinky)
    lh_keys: Set[int]           # set of MIDI pitches that belong to the left hand
    rh_keys: Set[int]           # set of MIDI pitches that belong to the right hand


def build_default_maps(pitches_left: Dict[str, int],
                       pitches_right: Dict[str, int]) -> HandMaps:
    """
    Build default key sets and simple finger maps for each hand,
    based on the given pitch dictionaries.

    Args:
        pitches_left:  Dict mapping note names (e.g. "C3") to MIDI numbers for the left hand range.
        pitches_right: Dict mapping note names (e.g. "C4") to MIDI numbers for the right hand range.

    Returns:
        HandMaps with:
          - finger mappings (pitch -> finger number)
          - sets of pitches for left and right hand
    """
    # Sort the given pitches (by MIDI number)
    lh_keys_sorted = sorted(int(v) for v in pitches_left.values())
    rh_keys_sorted = sorted(int(v) for v in pitches_right.values())

    # Build left-hand fingering if there are at least 5 keys
    lh_fingers = {}
    if len(lh_keys_sorted) >= 5:
        # Assign fingers 5–1 across the first 5 sorted keys
        lh_fingers = {
            lh_keys_sorted[0]: 5,
            lh_keys_sorted[1]: 4,
            lh_keys_sorted[2]: 3,
            lh_keys_sorted[3]: 2,
            lh_keys_sorted[4]: 1,
        }

    # Build right-hand fingering if there are at least 5 keys
    rh_fingers = {}
    if len(rh_keys_sorted) >= 5:
        # Assign fingers 1–5 across the first 5 sorted keys
        rh_fingers = {
            rh_keys_sorted[0]: 1,
            rh_keys_sorted[1]: 2,
            rh_keys_sorted[2]: 3,
            rh_keys_sorted[3]: 4,
            rh_keys_sorted[4]: 5,
        }

    return HandMaps(
        lh_fingers=lh_fingers,
        rh_fingers=rh_fingers,
        lh_keys=set(lh_keys_sorted),
        rh_keys=set(rh_keys_sorted),
    )


def capture_notes(
    state_sequence: Sequence[int],
    dyads: Sequence[Tuple[int, int]],
    tempo: float,
    maps: HandMaps,
    *,
    start_beat: float = 0.0,
    step_beats: float = 1.0,
    velocity: int = 100,
    channel: int = 0,   # kept for convenience if you later write to a MIDIFile
) -> Tuple[List[Dict[str, Any]], List[dict], List[dict], float]:
    """
    Convert a sequence of dyad indices into MIDI-friendly events and JSON note dicts.

    Args:
        state_sequence: Sequence of indices selecting dyads (pairs of pitches).
        dyads: List of (pitch_a, pitch_b) pairs. Each state_sequence element indexes into this list.
        tempo: Tempo in beats per minute.
        maps: HandMaps object describing left/right hand keys and finger numbers.
        start_beat: Starting beat offset (default = 0.0).
        step_beats: Duration of each dyad in beats (default = 1.0).
        velocity: MIDI velocity (0–127).
        channel: MIDI channel (default = 0).

    Returns:
        events:      List of MIDI-friendly note events (beats, track, pitch, velocity).
        right_notes: List of PianoVision-style note dicts for right hand (in seconds).
        left_notes:  List of PianoVision-style note dicts for left hand (in seconds).
        end_beat:    The final beat position after processing the sequence.
    """
    events: List[Dict[str, Any]] = []
    right_notes: List[dict] = []
    left_notes: List[dict] = []

    # Seconds per beat
    spb = 60.0 / float(tempo)
    # Current time in beats
    t_beats = float(start_beat)
    # Velocity scaled to 0..1 for JSON
    vel_float = round(velocity / 127.0, 6)

    # Iterate over sequence of dyad indices
    for d in state_sequence:
        a, b = dyads[d]  # two pitches in the dyad
        for pitch in (a, b):
            p = int(pitch)
            # Decide which track/hand this pitch belongs to
            track = 1 if p in maps.lh_keys else 0

            # --- MIDI-friendly event (timings in beats) ---
            events.append({
                "track": track,
                "channel": channel,
                "pitch": p,
                "start_beats": t_beats,
                "duration_beats": step_beats,
                "velocity": int(velocity),
            })

            # --- JSON-friendly note dict (timings in seconds) ---
            note_dict = {
                "midi": p,
                "start": round(t_beats * spb, 6),
                "duration": round(step_beats * spb, 6),
                "velocity": vel_float,  # scaled velocity
                "finger": (
                    maps.lh_fingers.get(p)
                    if track == 1
                    else maps.rh_fingers.get(p)
                ),
            }
            (left_notes if track == 1 else right_notes).append(note_dict)

        # Advance by one step (duration in beats)
        t_beats += step_beats

    # Return events, JSON note dicts
    return events, right_notes, left_notes
