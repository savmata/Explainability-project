class SelectiveMismatchDetector:
    """
    Detects items intentionally left out.
    Always fires on a skip, since the user will notice the item
    remaining on the counter and needs to know why.
    """
    # items that should always be excluded — robot knows these
    HANDWASH_ONLY = {"cast_iron_pan", "wooden_spoon", "copper_pot"}
    MAX_HEIGHT_CM = 30  # items taller than this don't fit

    def check(
        self,
        intention: "IntentionResult",
        context: WorldContext
    ) -> Optional[MismatchEvent]:

        if not intention.skip:
            return None

        b = intention.belief

        # determine severity by whether the skip is expected or surprising
        known_exclusion = b.name in self.HANDWASH_ONLY
        severity = Severity.LOW if known_exclusion else Severity.HIGH

        return MismatchEvent(
            category=MismatchCategory.SELECTIVE,
            severity=severity,
            belief=b,
            desire=intention.desire,
            intention=intention,
            description=(
                f"{b.name} left out "
                f"({'handwash only' if known_exclusion else intention.reasoning})"
            )
        )
