from typing import Tuple

class ReuseStrategyDecision:
    @staticmethod
    def determine_strategy(similarity: float, user_forces_generate: bool = False) -> Tuple[str, str]:
        if user_forces_generate:
            return "GENERATE", "User explicitly requested generation from scratch."
        if similarity >= 0.95:
            return "REUSE", f"High similarity ({similarity:.2f} >= 0.95): existing asset can be reused directly."
        elif similarity >= 0.75:
            return "ADAPT", f"Moderate similarity ({similarity:.2f} >= 0.75): adapt existing configuration with parameter tweaks."
        else:
            return "GENERATE", f"Low similarity ({similarity:.2f} < 0.75): generate new asset from template."
