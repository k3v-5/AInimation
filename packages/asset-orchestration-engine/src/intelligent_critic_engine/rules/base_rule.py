from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple
from ..core.critic_types import CausalCategory
from ..core.critic_schema import CriticDiagnosis, CriticConfiguration

class ICriticRule(ABC):
    @property
    @abstractmethod
    def rule_id(self) -> str:
        pass

    @property
    @abstractmethod
    def category(self) -> CausalCategory:
        pass

    @abstractmethod
    def evaluate(
        self,
        context: Dict[str, Any],
        config: CriticConfiguration
    ) -> List[CriticDiagnosis]:
        pass
