def get_archetype_multiplier(archetype: str) -> float:
    """Classifies players into discrete structural bins and returns a premium/discount multiplier."""
    multipliers = {
        "Two-Way Wing": 1.25,
        "Floor-Spacing Rim Protector": 1.20,
        "High-Volume Playmaker": 1.15,
        "Traditional Low-Volume Big": 0.85
    }
    return multipliers.get(archetype, 1.0)
