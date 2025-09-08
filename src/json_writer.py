# json_writer.py
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple

def _build_measures(bpm: float, ts: Tuple[int, int], song_len: float, ppq: int):
    ts_num, ts_den = ts
    spb = 60.0 / bpm
    beats_per_measure = ts_num * (4.0 / ts_den)
    spm = spb * beats_per_measure

    measures = []
    t = 0.0
    i = 0
    while t < song_len - 1e-9 or i == 0:  # ensure at least one row
        measures.append({
            "time": round(t, 12),
            "timeSignature": [ts_num, ts_den],
            "ticksPerMeasure": ppq * beats_per_measure,
            "ticksStart": i * ppq * beats_per_measure,
            "totalTicks": ppq * beats_per_measure,
            "type": 0 if i == 0 else 2
        })
        i += 1
        t = round(i * spm, 12)
    return measures, spm

def _group_tracks_v2(notes: List[Dict[str, Any]], hand_prefix: str,
                     bpm: float, ts: Tuple[int, int], ppq: int):
    ts_num, ts_den = ts
    spb = 60.0 / bpm
    beats_per_measure = ts_num * (4.0 / ts_den)
    spm = spb * beats_per_measure

    buckets: Dict[int, List[Dict[str, Any]]] = {}
    for i, n in enumerate(notes):
        m_idx = int(n["start"] // spm)
        entry = {
            "note": n["midi"],
            "durationTicks": int(round(n["duration"] / spb * ppq)),
            "noteOffVelocity": n["velocity"],
            "ticksStart": int(round(n["start"] / spb * ppq)),
            "velocity": n["velocity"],
            "measureBars": round((n["start"] / spb) / ts_num, 6),
            "duration": n["duration"],
            "noteName": None, "octave": None, "notePitch": None,
            "start": n["start"],
            "end": n["start"] + n["duration"],
            "noteLengthType": "quarter",
            "group": -1,
            "measureInd": m_idx,
            "noteMeasureInd": 0,
            "id": f"{hand_prefix}{i}",
            "finger": n.get("finger"),
            "smp": None
        }
        buckets.setdefault(m_idx, []).append(entry)

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
    def __init__(self, bpm: float, ts=(4, 4), ppq=960):
        self.bpm = float(bpm)
        self.ts = ts
        self.ppq = int(ppq)

    def build_json(self, right_notes: List[Dict[str, Any]], left_notes: List[Dict[str, Any]]) -> Dict[str, Any]:
        # right_notes/left_notes: dicts with midi, start(s), duration(s), velocity(0..1), finger(optional)
        song_len = self._song_length(right_notes, left_notes)
        measures, _ = _build_measures(self.bpm, self.ts, song_len, self.ppq)

        return {
            "supportingTracks": self._supporting_tracks(right_notes, left_notes),
            "start_time": 0,
            "song_length": round(song_len, 6),
            "resolution": self.ppq,
            "tempos": [{"bpm": self.bpm, "ticks": 0, "time": 0}],
            "keySignatures": [],
            "timeSignatures": [{"measures": 0, "ticks": 0, "timeSignature": [self.ts[0], self.ts[1]]}],
            "measures": measures,
            "tracksV2": {
                "right": _group_tracks_v2(right_notes, "r", self.bpm, self.ts, self.ppq),
                "left":  _group_tracks_v2(left_notes,  "l", self.bpm, self.ts, self.ppq)
            },
            "original": {"header": {
                "keySignatures": [], "meta": [], "name": "",
                "ppq": self.ppq, "tempos": [{"bpm": self.bpm, "ticks": 0}], "timeSignatures": []
            }}
        }

    def write(self, path: Path, right_notes: List[Dict[str, Any]], left_notes: List[Dict[str, Any]]) -> None:
        payload = self.build_json(right_notes, left_notes)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    def _song_length(self, right_notes: List[Dict[str, Any]], left_notes: List[Dict[str, Any]]) -> float:
        return max((n["start"] + n["duration"] for n in (right_notes + left_notes)), default=0.0)

    def _supporting_tracks(self, right_notes: List[Dict[str, Any]], left_notes: List[Dict[str, Any]]):
        return [
            {"notes": [{"midi": n["midi"], "time": n["start"], "velocity": n["velocity"], "duration": n["duration"]} for n in left_notes],
             "myInstrument": -5, "theirInstrument": 0},
            {"notes": [{"midi": n["midi"], "time": n["start"], "velocity": n["velocity"], "duration": n["duration"]} for n in right_notes],
             "myInstrument": -5, "theirInstrument": 0},
        ]
