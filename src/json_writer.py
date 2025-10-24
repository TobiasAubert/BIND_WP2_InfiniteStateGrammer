import json
from pathlib import Path
from typing import List, Dict, Any, Tuple

def _build_measures(bpm: float, ts: Tuple[int, int], song_len: float, ppq: int):
    """
    Build a list of measure objects for the given song length.

    Args:
        bpm: Tempo in beats per minute.
        ts:  Time signature as (numerator, denominator).
        song_len: Total song length in seconds.
        ppq: Pulses per quarter note (MIDI resolution).

    Returns:
        measures: List of measure dicts with timing + tick info.
        spm: Seconds per measure.
    """
    ts_num, ts_den = ts
    spb = 60.0 / bpm                       # seconds per beat
    beats_per_measure = ts_num * (4.0 / ts_den)
    spm = spb * beats_per_measure          # seconds per measure

    measures = []
    t = 0.0
    i = 0
    # Keep building until the last measure covers the song length
    while t < song_len - 1e-9 or i == 0:  # ensure at least one measure
        measures.append({
            "time": round(t, 12),
            "timeSignature": [ts_num, ts_den],
            "ticksPerMeasure": ppq * beats_per_measure,
            "ticksStart": i * ppq * beats_per_measure,
            "totalTicks": ppq * beats_per_measure,
            "type": 0 if i == 0 else 2   # 0 = start, 2 = normal
        })
        i += 1
        t = round(i * spm, 12)
    return measures, spm


def _group_tracks_v2(notes: List[Dict[str, Any]], hand_prefix: str,
                     bpm: float, ts: Tuple[int, int], ppq: int):
    """
    Group notes into measure-based chunks for PianoVision.

    Args:
        notes: List of note dicts (with midi, start, duration, velocity).
        hand_prefix: "r" or "l" (used to build note IDs).
        bpm: Tempo in beats per minute.
        ts:  Time signature as (numerator, denominator).
        ppq: Pulses per quarter note.

    Returns:
        chunks: List of measure chunks, each containing notes + metadata.
    """
    ts_num, ts_den = ts
    spb = 60.0 / bpm
    beats_per_measure = ts_num * (4.0 / ts_den)
    spm = spb * beats_per_measure

    # Group notes by measure index
    buckets: Dict[int, List[Dict[str, Any]]] = {}
    for i, n in enumerate(notes):
        m_idx = int(n["start"] // spm)   # which measure this note starts in
        entry = {
            "note": n["midi"],
            "durationTicks": int(round(n["duration"] / spb * ppq)),
            "noteOffVelocity": n["velocity"],   # currently same as note-on velocity
            "ticksStart": int(round(n["start"] / spb * ppq)),
            "velocity": n["velocity"],
            "measureBars": round((n["start"] / spb) / ts_num, 6),
            "duration": n["duration"],
            "noteName": None, "octave": None, "notePitch": None,  # placeholders
            "start": n["start"],
            "end": n["start"] + n["duration"],
            "noteLengthType": "quarter",  # not computed, fixed as "quarter"
            "group": -1,
            "measureInd": m_idx,
            "noteMeasureInd": 0,
            "id": f"{hand_prefix}{i}",   # e.g. r0, r1, l0, l1 …
            "finger": n.get("finger"),
            "smp": None
        }
        buckets.setdefault(m_idx, []).append(entry)

    # Convert grouped notes into chunk objects
    chunks: List[Dict[str, Any]] = []
    for m_idx in sorted(buckets.keys()):
        start = m_idx * spm
        end = start + spm
        chunk_notes = buckets[m_idx]
        chunks.append({
            "direction": "down",
            "time": round(start, 12),
            "timeEnd": round(end, 12),
            "timeSignature": [ts_num, ts_den],
            "notes": chunk_notes,
            "max": max(e["note"] for e in chunk_notes),
            "min": min(e["note"] for e in chunk_notes),
            "measureTicksStart": m_idx * ppq * beats_per_measure,
            "measureTicksEnd": (m_idx + 1) * ppq * beats_per_measure,
            "rests": [],
            "groups": []
        })
    return chunks


class PianoVisionJsonWriter:
    """
    Build and write PianoVision-compatible JSON from note dicts.

    Expects right_notes / left_notes with fields:
      - midi: MIDI pitch number
      - start: start time in seconds
      - duration: duration in seconds
      - velocity: float 0..1
      - finger: (optional) finger number
    """

    def __init__(self, bpm: float, ts=(4, 4), ppq=960, visual_speed: float = 1.0):
        """
        visual_speed: multiplier for the visual scroll speed. Values >1.0 make visuals
        move faster (notes appear/finish sooner), values <1.0 make visuals slower.

        Internally this writer scales the note 'start' and 'duration' times by 1/visual_speed
        when producing the JSON. The MIDI tempo (bpm) is left unchanged so audio playback
        remains the same while visuals can be sped up or slowed down independently.
        """
        self.bpm = float(bpm)
        self.ts = ts
        self.ppq = int(ppq)
        # store visual speed multiplier (>1 speeds up visuals)
        self.visual_speed = float(visual_speed) if visual_speed and visual_speed > 0 else 1.0

    def build_json(self, right_notes: List[Dict[str, Any]],
                   left_notes: List[Dict[str, Any]],
                   name: str = "unknown") -> Dict[str, Any]:
        """
        Construct the full PianoVision JSON payload (as a dict).
        """
        # Apply visual speed scaling to notes without mutating the originals.
        # A visual_speed > 1.0 results in shorter visual times (faster scroll).
        scale = 1.0 / self.visual_speed
        def _scale_notes(notes):
            return [
                {**n, "start": n["start"] * scale, "duration": n["duration"] * scale}
                for n in notes
            ]

        scaled_right = _scale_notes(right_notes)
        scaled_left = _scale_notes(left_notes)

        song_len = self._song_length(scaled_right, scaled_left)
        measures, _ = _build_measures(self.bpm, self.ts, song_len, self.ppq)

        return {
            # include original supportingTracks times? use scaled notes so visuals match tracksV2
            "supportingTracks": self._supporting_tracks(scaled_right, scaled_left),
            "start_time": 0,
            "song_length": round(song_len, 6),
            "resolution": self.ppq,
            "tempos": [{"bpm": self.bpm, "ticks": 0, "time": 0}],
            "keySignatures": [],
            "timeSignatures": [
                {"measures": 0, "ticks": 0,
                 "timeSignature": [self.ts[0], self.ts[1]]}
            ],
            "measures": measures,
            "tracksV2": {
                "right": _group_tracks_v2(scaled_right, "r", self.bpm, self.ts, self.ppq),
                "left":  _group_tracks_v2(scaled_left,  "l", self.bpm, self.ts, self.ppq)
            },
            "original": {"header": {
                "keySignatures": [], "meta": [], "name": "",
                "ppq": self.ppq,
                "tempos": [{"bpm": self.bpm, "ticks": 0}],
                "timeSignatures": []
            }},
            "name": name,
            # Informational: visual_speed controls how fast visuals run relative to audio.
            "visual_speed": self.visual_speed,
        }

    def write(self, path: Path,
              right_notes: List[Dict[str, Any]],
              left_notes: List[Dict[str, Any]],
              name: str) -> None:
        """
        Write the JSON payload to disk at the given path.
        """
        payload = self.build_json(right_notes, left_notes, name)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    def _song_length(self,
                     right_notes: List[Dict[str, Any]],
                     left_notes: List[Dict[str, Any]]) -> float:
        """
        Compute song length in seconds as max(start + duration) across all notes.
        """
        return max((n["start"] + n["duration"]
                    for n in (right_notes + left_notes)),
                   default=0.0)

    def _supporting_tracks(self,
                           right_notes: List[Dict[str, Any]],
                           left_notes: List[Dict[str, Any]]):
        """
        Build the 'supportingTracks' field expected by PianoVision.

        Each supporting track has a minimal set of note data (midi, time, velocity, duration).
        """
        return [
            {"notes": [
                {"midi": n["midi"], "time": n["start"],
                 "velocity": n["velocity"], "duration": n["duration"]}
                for n in left_notes
             ],
             "myInstrument": -5, "theirInstrument": 0},
            {"notes": [
                {"midi": n["midi"], "time": n["start"],
                 "velocity": n["velocity"], "duration": n["duration"]}
                for n in right_notes
             ],
             "myInstrument": -5, "theirInstrument": 0},
        ]
