from typing import Dict, Any, List
from ...evaluation.models.evaluation_models import EvaluationBenchmark, AcceptanceDecision, DefectSeverity
from ..core.failure_models import FailureRecord
from ..core.failure_types import FailureType, FailureSeverity, FailureStatus

class ValidationFailureDetector:
    """Converts F75 EvaluationBenchmark results into structured FailureRecords."""

    @staticmethod
    def from_benchmark(benchmark: EvaluationBenchmark) -> List[FailureRecord]:
        records = []
        if benchmark.acceptance == AcceptanceDecision.REJECTED:
            for defect in benchmark.defects:
                f_type = FailureType.BENCHMARK_ERROR
                is_crit = getattr(defect, "severity", None) == DefectSeverity.CRITICAL or getattr(defect, "is_critical", False)
                sev = FailureSeverity.CRITICAL if is_crit else FailureSeverity.ERROR
                dim_str = defect.dimension.value.upper() if hasattr(defect.dimension, "value") else str(defect.dimension).upper()
                dim_val = defect.dimension.value if hasattr(defect.dimension, "value") else str(defect.dimension)
                
                if "SCALE" in dim_str or "TRANSFORM" in dim_str:
                    f_type = FailureType.SCALE_ERROR
                elif "MATERIAL" in dim_str or "SHADER" in dim_str:
                    f_type = FailureType.MATERIAL_ERROR
                elif "UV" in dim_str:
                    f_type = FailureType.UV_ERROR
                elif "LOD" in dim_str:
                    f_type = FailureType.LOD_ERROR
                elif "COLLISION" in dim_str:
                    f_type = FailureType.COLLISION_ERROR

                exp = getattr(defect, "expected_value", getattr(defect, "expected_state", {"description": defect.description}))
                act = getattr(defect, "actual_value", getattr(defect, "actual_state", defect.evidence if hasattr(defect, "evidence") else {}))
                rec = FailureRecord(
                    failure_id=f"FAIL_VAL_{benchmark.benchmark_id}_{defect.defect_id}",
                    semantic_id=benchmark.asset_semantic_id,
                    job_id=benchmark.job_id,
                    pipeline_phase="EVALUATION",
                    pipeline_stage="BENCHMARK",
                    operation="EVALUATE_ASSET",
                    failure_type=f_type,
                    failure_category=dim_val,
                    severity=sev,
                    status=FailureStatus.DETECTED,
                    message=defect.description,
                    expected_state={"expected": exp},
                    actual_state={"actual": act}
                )
                records.append(rec)

            if not records:
                # Global benchmark rejection without specific itemized defect
                rec = FailureRecord(
                    failure_id=f"FAIL_VAL_{benchmark.benchmark_id}_GLOBAL",
                    semantic_id=benchmark.asset_semantic_id,
                    job_id=benchmark.job_id,
                    pipeline_phase="EVALUATION",
                    pipeline_stage="BENCHMARK",
                    operation="EVALUATE_ASSET",
                    failure_type=FailureType.BENCHMARK_ERROR,
                    failure_category="BENCHMARK",
                    severity=FailureSeverity.ERROR,
                    status=FailureStatus.DETECTED,
                    message=f"Benchmark score {round(benchmark.weighted_score, 4)} below required threshold"
                )
                records.append(rec)

        return records
