import os
import json
import threading
from typing import Dict, List, Optional
from ..models.evaluation_models import EvaluationBenchmark
from ..core.evaluation_types import BenchmarkStatus

class BenchmarkCorruptedError(Exception):
    """Raised when an EvaluationBenchmark fails cryptographic integrity verification."""
    pass

class BenchmarkFinalizedImmutableError(Exception):
    """Raised when attempting to modify a finalized/immutable benchmark."""
    pass

class EvaluationStore:
    """Persistent and verifiable storage for EvaluationBenchmark records."""
    def __init__(self, persistence_path: Optional[str] = None):
        self._benchmarks: Dict[str, EvaluationBenchmark] = {}
        self._lock = threading.RLock()
        self.persistence_path = persistence_path or r"E:\Darx_Proyect\Saved\Evaluation\darx_benchmarks.json"

        if self.persistence_path and os.path.exists(self.persistence_path):
            self.load_from_disk()

    def store_benchmark(self, benchmark: EvaluationBenchmark, allow_finalize: bool = False) -> EvaluationBenchmark:
        with self._lock:
            existing = self._benchmarks.get(benchmark.benchmark_id)
            if existing and existing.status == BenchmarkStatus.FINALIZED and not allow_finalize:
                raise BenchmarkFinalizedImmutableError(
                    f"Benchmark {benchmark.benchmark_id} is FINALIZED and immutable. Create a new version."
                )

            benchmark.content_hash = benchmark.compute_hash()
            self._benchmarks[benchmark.benchmark_id] = benchmark
            self.save_to_disk()
            return benchmark

    def get_benchmark(self, benchmark_id: str) -> Optional[EvaluationBenchmark]:
        with self._lock:
            bench = self._benchmarks.get(benchmark_id)
            if bench and not bench.verify_integrity():
                raise BenchmarkCorruptedError(f"Benchmark {benchmark_id} corrupted on disk (hash mismatch).")
            return bench

    def list_benchmarks(self, asset_semantic_id: Optional[str] = None) -> List[EvaluationBenchmark]:
        with self._lock:
            results = list(self._benchmarks.values())
            if asset_semantic_id:
                results = [b for b in results if b.asset_semantic_id == asset_semantic_id]
            return results

    def save_to_disk(self):
        if not self.persistence_path:
            return
        os.makedirs(os.path.dirname(self.persistence_path), exist_ok=True)
        with self._lock:
            data = {k: v.to_dict() for k, v in self._benchmarks.items()}
            with open(self.persistence_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

    def load_from_disk(self):
        if not self.persistence_path or not os.path.exists(self.persistence_path):
            return
        if os.path.getsize(self.persistence_path) == 0:
            return
        with self._lock:
            try:
                with open(self.persistence_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._benchmarks = {}
                    for k, v in data.items():
                        bench = EvaluationBenchmark.from_dict(v)
                        if not bench.verify_integrity():
                            raise BenchmarkCorruptedError(f"Benchmark {k} failed cryptographic integrity verification.")
                        self._benchmarks[k] = bench
            except BenchmarkCorruptedError:
                raise
            except Exception as e:
                print(f"[EvaluationStore] Warning loading benchmarks: {e}")
