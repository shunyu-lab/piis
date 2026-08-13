"""Reserved. V0.6 will implement fact checking without promoting model output to truth."""

from piis.models.claim import Claim


class FactChecker:
    def check(self, claim: Claim) -> None:
        raise NotImplementedError("Fact checking is not part of V0.1.")
