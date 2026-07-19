_ARCHETYPE_MULTIPLIERS = {
    "Two-Way Wing": 1.25,
    "Floor-Spacing Rim Protector": 1.20,
    "High-Volume Playmaker": 1.15,
    "Traditional Low-Volume Big": 0.85,
    "Unknown": 1.0,  # explicit sentinel for players not yet classified into an archetype
}

def get_archetype_multiplier(archetype: str) -> float:
    """Classifies players into discrete structural bins and returns a premium/discount multiplier.

    Only recognized archetype labels (plus the explicit "Unknown" sentinel) are
    accepted. A typo (e.g. "Two Way Wing" missing the hyphen) would otherwise
    silently fall through to a neutral 1.0x multiplier, masking a data-entry
    error instead of surfacing it.
    """
    if archetype not in _ARCHETYPE_MULTIPLIERS:
        raise ValueError(
            f"Unrecognized archetype {archetype!r}. Must be one of "
            f"{sorted(_ARCHETYPE_MULTIPLIERS)} (use 'Unknown' for unclassified players)."
        )
    return _ARCHETYPE_MULTIPLIERS[archetype]
