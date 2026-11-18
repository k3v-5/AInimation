import time
from typing import Dict, Any, List, Optional
from ..core.evaluation_types import (
    EvaluationDimension, DefectSeverity, DefectStatus, BenchmarkStatus, AcceptanceDecision
)
from ..models.evaluation_models import (
    EvaluationBenchmark, DimensionScore, EvaluationProfile, EvaluationDefect
)
from ..profiles.default_profiles import ProfileRegistry, create_weapon_profile
from ..metrics.dimension_evaluators import DimensionEvaluator
from ..comparison.ab_comparison import ABComparisonEngine, ABComparisonResult
from ..regression.regression_detector import RegressionDetector, RegressionReport
from ..persistence.evaluation_store import EvaluationStore, BenchmarkCorruptedError, BenchmarkFinalizedImmutableError
from ..persistence.governance_guard import EvaluationGovernanceGuard, EvaluationPermissionDeniedError
from ..integration.knowledge_graph_bridge import KnowledgeGraphEvaluationBridge

class EvaluationBenchmarkAPI:
    """
    Unified public facade for the Evaluation Benchmark System (Phase 75).
    """
    def __init__(self, persistence_path: Optional[str] = None):
        self.store = EvaluationStore(persistence_path)
        self.profiles = ProfileRegistry()
        self.evaluators = DimensionEvaluator()
        self.comparison = ABComparisonEngine()
        self.regression = RegressionDetector()
        self.governance = EvaluationGovernanceGuard()
        self.kg_bridge = KnowledgeGraphEvaluationBridge()

    def create_benchmark(
        self,
        benchmark_id: str,
        asset_semantic_id: str,
        candidate_id: str,
        profile_id: str = "PROFILE_WEAPON_DARX",
        reference_id: Optional[str] = None,
        baseline_id: Optional[str] = None,
        job_id: Optional[str] = None,
        agent_id: Optional[str] = "agent.visual.critic"
    ) -> EvaluationBenchmark:
        profile = self.profiles.get_profile(profile_id) or create_weapon_profile()
        bench = EvaluationBenchmark(
            benchmark_id=benchmark_id,
            project_id="DarX",
            asset_semantic_id=asset_semantic_id,
            candidate_id=candidate_id,
            reference_id=reference_id,
            baseline_id=baseline_id,
            evaluation_profile=profile,
            job_id=job_id,
            agent_id=agent_id
        )
        return self.store.store_benchmark(bench)

    def evaluate_asset(
        self,
        asset_semantic_id: str,
        candidate_id: str,
        asset_data: Dict[str, Any],
        profile_id: str = "PROFILE_WEAPON_DARX",
        reference_data: Optional[Dict[str, Any]] = None,
        baseline_id: Optional[str] = None,
        benchmark_id: Optional[str] = None,
        job_id: Optional[str] = None,
        agent_id: Optional[str] = "agent.visual.critic"
    ) -> EvaluationBenchmark:
        b_id = benchmark_id or f"BENCH_{int(time.time()*1000)%100000}"
        profile = self.profiles.get_profile(profile_id) or create_weapon_profile()

        dim_scores = DimensionEvaluator.evaluate_all(asset_data, profile.minimum_dimension_scores, reference_data)
        
        bench = EvaluationBenchmark(
            benchmark_id=b_id,
            project_id="DarX",
            asset_semantic_id=asset_semantic_id,
            candidate_id=candidate_id,
            baseline_id=baseline_id,
            evaluation_profile=profile,
            dimension_scores=dim_scores,
            metrics=asset_data,
            job_id=job_id,
            agent_id=agent_id,
            status=BenchmarkStatus.IN_PROGRESS
        )
        bench.calculate_global_score()
        return self.store.store_benchmark(bench)

    def evaluate_dimension(
        self,
        dimension: EvaluationDimension,
        asset_data: Dict[str, Any],
        spec_data: Optional[Dict[str, Any]] = None
    ) -> DimensionScore:
        all_scores = DimensionEvaluator.evaluate_all(asset_data, spec_data)
        return all_scores.get(dimension, DimensionScore(dimension=dimension))

    def calculate_score(self, benchmark: EvaluationBenchmark) -> float:
        benchmark.calculate_global_score()
        return benchmark.weighted_score

    def compare_assets(self, candidate_a: EvaluationBenchmark, candidate_b: EvaluationBenchmark) -> ABComparisonResult:
        return self.comparison.compare_benchmarks(candidate_a, candidate_b)

    def compare_to_baseline(self, candidate: EvaluationBenchmark, baseline: EvaluationBenchmark) -> RegressionReport:
        return self.regression.detect_regressions(candidate, baseline)

    def detect_regressions(self, candidate: EvaluationBenchmark, baseline: EvaluationBenchmark) -> RegressionReport:
        return self.regression.detect_regressions(candidate, baseline)

    def get_benchmark(self, benchmark_id: str) -> Optional[EvaluationBenchmark]:
        return self.store.get_benchmark(benchmark_id)

    def list_benchmarks(self, asset_semantic_id: Optional[str] = None) -> List[EvaluationBenchmark]:
        return self.store.list_benchmarks(asset_semantic_id)

    def get_metrics(self, benchmark_id: str) -> Dict[str, Any]:
        bench = self.get_benchmark(benchmark_id)
        return bench.metrics if bench else {}

    def get_defects(self, benchmark_id: str) -> List[EvaluationDefect]:
        bench = self.get_benchmark(benchmark_id)
        return bench.defects if bench else []

    def get_evidence(self, benchmark_id: str) -> Dict[str, Any]:
        bench = self.get_benchmark(benchmark_id)
        return bench.evidence if bench else {}

    def finalize_benchmark(self, benchmark_id: str, agent_id: str = "agent.visual.critic") -> EvaluationBenchmark:
        bench = self.get_benchmark(benchmark_id)
        if not bench:
            raise KeyError(f"Benchmark {benchmark_id} not found.")
        self.governance.validate_evaluation_access(agent_id)
        bench.status = BenchmarkStatus.FINALIZED
        bench.completed_at = time.time()
        bench.calculate_global_score()
        saved = self.store.store_benchmark(bench, allow_finalize=True)
        # Sync to knowledge graph
        try:
            self.kg_bridge.sync_benchmark_to_graph(saved)
        except Exception as e:
            print(f"[EvaluationAPI] Note syncing to graph: {e}")
        return saved

    def reproduce_benchmark(self, benchmark_id: str, asset_data: Dict[str, Any]) -> EvaluationBenchmark:
        original = self.get_benchmark(benchmark_id)
        if not original:
            raise KeyError(f"Original benchmark {benchmark_id} not found.")
        repro_id = f"REPRO_{benchmark_id}"
        repro = self.evaluate_asset(
            asset_semantic_id=original.asset_semantic_id,
            candidate_id=f"repro_{original.candidate_id}",
            asset_data=asset_data,
            profile_id=original.evaluation_profile.profile_id,
            benchmark_id=repro_id
        )
        return repro

    def generate_benchmark_report(self, benchmark_id: str) -> str:
        bench = self.get_benchmark(benchmark_id)
        if not bench:
            return f"Benchmark {benchmark_id} not found."
        
        lines = [
            "=" * 60,
            f"F75 BENCHMARK REPORT: {bench.benchmark_id}",
            "=" * 60,
            f"Asset: {bench.asset_semantic_id}",
            f"Candidate: {bench.candidate_id}",
            f"Baseline: {bench.baseline_id or 'None'}",
            f"Profile: {bench.evaluation_profile.name} (v{bench.evaluation_profile.version})",
            "",
            f"Global Score: {round(bench.weighted_score * 100, 2)} / 100 ({round(bench.weighted_score, 4)})",
            f"Confidence: {round(bench.confidence, 4)}",
            f"Acceptance: {bench.acceptance.value}",
            "",
            "DIMENSION BREAKDOWN:"
        ]
        for dim, ds in bench.dimension_scores.items():
            lines.append(f" - {dim.value:<22}: {round(ds.score, 4)} (weight: {ds.weight})")

        lines.append("")
        lines.append(f"DEFECTS DETECTED: {len(bench.defects)}")
        for d in bench.defects:
            lines.append(f" * [{d.severity.value}] {d.dimension.value}: {d.description}")

        lines.append("=" * 60)
        return "\n".join(lines)

    def get_statistics(self) -> Dict[str, Any]:
        all_b = self.list_benchmarks()
        if not all_b:
            return {"total_benchmarks": 0, "average_score": 0.0, "acceptance_rate": 0.0}
        
        avg_score = sum(b.weighted_score for b in all_b) / len(all_b)
        approved_count = sum(1 for b in all_b if b.acceptance == AcceptanceDecision.APPROVED)
        return {
            "total_benchmarks": len(all_b),
            "average_score": round(avg_score, 4),
            "acceptance_rate": round(approved_count / len(all_b), 4),
            "best_score": round(max(b.weighted_score for b in all_b), 4),
            "worst_score": round(min(b.weighted_score for b in all_b), 4)
        }
