import os
import json
import threading
from typing import Dict, Any, List, Optional
from ..core.strategy_models import StrategyRecord
from ..core.learning_models import StrategyOutcome, LearningEvent, StrategyOptimizationProfile

class StrategyLearningStore:
    """Thread-safe transactional JSON persistence for strategies, outcomes, and profiles."""

    def __init__(self, persistence_path: Optional[str] = None):
        self.persistence_path = persistence_path or r"E:\Darx_Proyect\Saved\StrategyLearning\darx_strategy_learning_store.json"
        self._strategies: Dict[str, StrategyRecord] = {}
        self._outcomes: List[StrategyOutcome] = []
        self._events: List[LearningEvent] = []
        self._profiles: Dict[str, StrategyOptimizationProfile] = {}
        self._lock = threading.RLock()
        self._init_default_profiles()
        self.load_from_disk()

    def _init_default_profiles(self):
        self._profiles["BALANCED"] = StrategyOptimizationProfile.balanced()
        self._profiles["QUALITY_FIRST"] = StrategyOptimizationProfile.quality_first()
        self._profiles["PERFORMANCE_FIRST"] = StrategyOptimizationProfile.performance_first()

    def store_strategy(self, strategy: StrategyRecord):
        with self._lock:
            self._strategies[strategy.strategy_id] = strategy
            self.save_to_disk()

    def get_strategy(self, strategy_id: str) -> Optional[StrategyRecord]:
        with self._lock:
            return self._strategies.get(strategy_id)

    def list_strategies(self) -> List[StrategyRecord]:
        with self._lock:
            return list(self._strategies.values())

    def store_outcome(self, outcome: StrategyOutcome):
        with self._lock:
            self._outcomes.append(outcome)
            self.save_to_disk()

    def list_outcomes(self) -> List[StrategyOutcome]:
        with self._lock:
            return list(self._outcomes)

    def store_event(self, event: LearningEvent):
        with self._lock:
            self._events.append(event)
            self.save_to_disk()

    def list_events(self) -> List[LearningEvent]:
        with self._lock:
            return list(self._events)

    def save_to_disk(self):
        if not self.persistence_path:
            return
        os.makedirs(os.path.dirname(self.persistence_path), exist_ok=True)
        with self._lock:
            data = {
                "strategies": {k: v.to_dict() for k, v in self._strategies.items()},
                "outcomes": [o.to_dict() for o in self._outcomes],
                "events": [e.to_dict() for e in self._events],
                "profiles": {k: v.to_dict() for k, v in self._profiles.items()}
            }
            tmp_path = self.persistence_path + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(tmp_path, self.persistence_path)

    def load_from_disk(self):
        if not self.persistence_path or not os.path.exists(self.persistence_path):
            return
        if os.path.getsize(self.persistence_path) == 0:
            return
        with self._lock:
            try:
                with open(self.persistence_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for k, v in data.get("strategies", {}).items():
                        self._strategies[k] = StrategyRecord.from_dict(v)
                    for o in data.get("outcomes", []):
                        self._outcomes.append(StrategyOutcome.from_dict(o))
                    for k, p in data.get("profiles", {}).items():
                        self._profiles[k] = StrategyOptimizationProfile(**p)
            except Exception as e:
                print(f"[StrategyLearningStore] Warning loading store: {e}")
