class TemporalMismatchDetector:
    """
    Detects unexpected pauses in execution.

    A pause is defined as: no completed placement action for
    more than `pause_threshold` consecutive timesteps.

    Fires once per pause episode (not every step), and resets
    when the robot resumes.
    """

    def __init__(self, pause_threshold: int = 50):
        self.pause_threshold = pause_threshold
        self._pause_fired = False   # prevent repeated firing for same pause

    def check(
        self,
        intention: "IntentionResult",
        context: WorldContext
    ) -> Optional[MismatchEvent]:

        steps_since_action = context.current_step - context.last_action_step
        currently_paused = steps_since_action > self.pause_threshold

        # robot resumed — reset so next pause can fire
        if not currently_paused:
            self._pause_fired = False
            return None

        # already reported this pause — don't repeat
        if self._pause_fired:
            return None

        self._pause_fired = True

        return MismatchEvent(
            category=MismatchCategory.TEMPORAL,
            severity=Severity.HIGH,
            belief=intention.belief,
            desire=intention.desire,
            intention=intention,
            description=(
                f"robot paused for {steps_since_action} steps "
                f"({intention.reasoning})"
            )
        )
