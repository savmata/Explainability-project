class SpatialMismatchDetector:
    """
    Detects placement in an unexpected location.
    Expected rack is derived from object properties:
      glass/fragile -> top rack
      large/heavy   -> bottom rack
      cutlery       -> basket
    """
    RACK_RULES = {
        "glass":    "top",
        "ceramic":  "bottom",
        "metal":    "basket",
        "plastic":  "top",
    }

    def check(
        self,
        intention: "IntentionResult",
        context: WorldContext
    ) -> Optional[MismatchEvent]:

        b = intention.belief
        expected = self.RACK_RULES.get(b.material, b.expected_rack)
        actual = intention.target_rack

        if intention.skip or actual == expected:
            return None

        severity = Severity.HIGH if b.fragile else Severity.MEDIUM

        return MismatchEvent(
            category=MismatchCategory.SPATIAL,
            severity=severity,
            belief=b,
            desire=intention.desire,
            intention=intention,
            description=(
                f"{b.name} placed on {actual} rack "
                f"(expected: {expected})"
            )
        )
