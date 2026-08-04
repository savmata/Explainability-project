class SequentialMismatchDetector:
    """
    Detects when the robot loads items out of the expected order.

    'Expected order' is defined as:
      1. The order items appear left-to-right on the counter, OR
      2. The order the user manually arranged them before the robot ran.

    The robot may deviate to optimise spray coverage or avoid
    blocking a slot — this should always be explained.
    """

    def __init__(self):
        # track which items we've seen, in the order we encounter them
        self._expected_sequence: list[str] = []
        self._loaded_sequence:   list[str] = []

    def register_expected_order(self, item_names: list[str]):
        """Call once at episode start with counter items left→right."""
        self._expected_sequence = list(item_names)

    def check(
        self,
        intention: "IntentionResult",
        context: WorldContext
    ) -> Optional[MismatchEvent]:

        if intention.skip:
            return None

        b = intention.belief
        self._loaded_sequence.append(b.name)

        # index in expected vs actual position
        n_loaded = len(self._loaded_sequence)
        if n_loaded > len(self._expected_sequence):
            return None  # more items than expected — handle elsewhere

        expected_next = self._expected_sequence[n_loaded - 1]
        actual_next = b.name

        if actual_next == expected_next:
            return None

        return MismatchEvent(
            category=MismatchCategory.SEQUENTIAL,
            severity=Severity.MEDIUM,
            belief=b,
            desire=intention.desire,
            intention=intention,
            description=(
                f"loaded {actual_next} at position {n_loaded} "
                f"(expected {expected_next})"
            )
        )
