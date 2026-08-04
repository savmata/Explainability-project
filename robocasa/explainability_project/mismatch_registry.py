class MismatchRegistry:
    def __init__(self):
        self.spatial = SpatialMismatchDetector()
        self.selective = SelectiveMismatchDetector()
        self.sequential = SequentialMismatchDetector()
        self.temporal = TemporalMismatchDetector()

    def check_all(
        self,
        intention: "IntentionResult",
        context: WorldContext
    ) -> list[MismatchEvent]:

        results = []
        for detector in [
            self.spatial, self.selective,
            self.sequential, self.temporal
        ]:
            event = detector.check(intention, context)
            if event is not None:
                results.append(event)
        return results
