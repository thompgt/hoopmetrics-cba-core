"""Heuristic mapping from real per-game box-score stats to the engine's
simulated valuation inputs (box_plus_minus, on_off, epm) and archetype
label.

engine_gateway.evaluate_player already treats its box_plus_minus/on_off/epm
inputs as a "simulated" model rather than official advanced stats (see
README), so these estimators just need to be a deterministic, documented
approximation from real box-score counting stats -- not a real BPM/RAPM/EPM
implementation. on_off and epm are each derived as a fixed proportional
variant of the estimated box_plus_minus, since no real on/off or predictive
data is available here.
"""

_ARCHETYPES = (
    "Two-Way Wing", "Floor-Spacing Rim Protector", "High-Volume Playmaker", "Traditional Low-Volume Big",
)


def estimate_box_plus_minus(pts: float, reb: float, ast: float, stl: float, blk: float) -> float:
    return (pts * 0.3) + (reb * 0.25) + (ast * 0.35) + (stl * 1.0) + (blk * 0.9) - 8.0


def estimate_on_off(box_plus_minus: float) -> float:
    return box_plus_minus * 0.85


def estimate_epm(box_plus_minus: float, ast: float) -> float:
    value = (box_plus_minus * 1.05) + (ast * 0.05)
    return max(-15.0, min(15.0, value))


def classify_archetype_from_stats(pts: float, reb: float, ast: float, stl: float, blk: float) -> str:
    if ast >= 6.5:
        return "High-Volume Playmaker"
    if blk >= 1.0 and reb >= 9:
        return "Floor-Spacing Rim Protector"
    if reb >= 8 and ast < 4 and blk < 0.8:
        return "Traditional Low-Volume Big"
    if (stl + blk) >= 1.5 and pts >= 20:
        return "Two-Way Wing"
    return "Unknown"
