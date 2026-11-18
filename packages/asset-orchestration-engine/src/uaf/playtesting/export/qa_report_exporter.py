"""
UAF-81.96: QA Report & Telemetry Exporter.
Serializes simulation findings, archetype performance metrics, spatial heatmaps,
and softlock incident matrices to JSON, Markdown, and CSV formats.
"""

import json
import csv
import io
from pathlib import Path
from typing import List, Optional, Dict, Any

from ..core.contracts import (
    QASimulationSuiteSummary,
    PlaytestRunResult,
    HeatmapGrid2D,
    PlaytestLevelSpec,
)


class QAReportExporter:
    """
    Exports autonomous playtesting deliverables for CI/CD gates, designer inspection,
    and in-engine visualization.
    """

    @staticmethod
    def export_json(
        summary: QASimulationSuiteSummary,
        runs: Optional[List[PlaytestRunResult]] = None,
        heatmaps: Optional[List[HeatmapGrid2D]] = None,
        target_path: Optional[Path] = None,
    ) -> str:
        """
        Serializes summary and optional run details to JSON string and file.
        """
        payload: Dict[str, Any] = {
            "summary": summary.model_dump(),
            "run_count": len(runs) if runs else 0,
            "heatmaps": [h.model_dump() for h in (heatmaps or [])],
        }

        if runs:
            payload["runs"] = [
                {
                    "session_id": r.session_id,
                    "archetype": r.archetype.value,
                    "outcome": r.outcome.value,
                    "total_time_s": r.total_time_s,
                    "rooms_visited": r.rooms_visited,
                    "enemies_defeated": r.enemies_defeated,
                    "damage_dealt": r.damage_dealt,
                    "damage_taken": r.damage_taken,
                    "ammo_spent": r.ammo_spent,
                    "accuracy_achieved": r.accuracy_achieved,
                    "event_count": len(r.telemetry_events),
                }
                for r in runs
            ]

        json_str = json.dumps(payload, indent=2)
        if target_path:
            target_path = Path(target_path)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(json_str, encoding="utf-8")

        return json_str

    @staticmethod
    def export_markdown(
        summary: QASimulationSuiteSummary,
        level: Optional[PlaytestLevelSpec] = None,
        target_path: Optional[Path] = None,
    ) -> str:
        """
        Generates an executive Markdown QA Audit report.
        """
        status_badge = "✅ PASS" if summary.calibrated_successfully else "❌ FAIL"
        lines = [
            f"# UAF-81.96 Autonomous Playtesting QA Audit Report: {status_badge}",
            "",
            f"- **Total Simulation Runs:** {summary.total_runs}",
            f"- **Overall Survival Rate:** {summary.overall_survival_rate * 100:.1f}%",
            f"- **Victories:** {summary.victory_count} | **Deaths:** {summary.death_count} | **Softlocks:** {summary.softlock_count} | **Timeouts:** {summary.timeout_count}",
            "",
            "## 1. Archetype Performance Matrix",
            "",
            "| Archetype | Survival Rate |",
            "| :--- | :--- |",
        ]

        for arch, rate in summary.archetype_survival_rates.items():
            lines.append(f"| `{arch.value}` | {rate * 100:.1f}% |")

        lines.extend([
            "",
            "## 2. Identified Softlocks & Reachability Incidents",
            "",
        ])

        if not summary.identified_softlocks:
            lines.append("*Zero softlocks detected. All rooms and key-lock chains are reachable.*")
        else:
            lines.append("| Room ID | Type | Severity | Description | Remediation |")
            lines.append("| :--- | :--- | :--- | :--- | :--- |")
            for slk in summary.identified_softlocks:
                lines.append(
                    f"| `{slk.room_id}` | `{slk.softlock_type.value}` | **{slk.severity.value}** | {slk.description} | {slk.remediation_hint} |"
                )

        lines.extend([
            "",
            "## 3. Difficulty Spikes & Resource Chokepoints",
            "",
        ])

        if not summary.difficulty_spikes:
            lines.append("*No severe difficulty spikes detected. Pacing is balanced.*")
        else:
            lines.append("| Room ID | Deaths | Survival | Ammo Exhaustion | Recommendation |")
            lines.append("| :--- | :--- | :--- | :--- | :--- |")
            for spike in summary.difficulty_spikes:
                lines.append(
                    f"| `{spike.room_id}` | {spike.player_death_count} | {spike.survival_rate*100:.1f}% | {spike.ammo_exhaustion_rate*100:.1f}% | {spike.recommendation} |"
                )

        lines.append("")
        md_content = "\n".join(lines)

        if target_path:
            target_path = Path(target_path)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(md_content, encoding="utf-8")

        return md_content

    @staticmethod
    def export_telemetry_csv(
        runs: List[PlaytestRunResult],
        target_path: Optional[Path] = None,
    ) -> str:
        """
        Exports granular telemetry events across all runs to a CSV format.
        """
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "session_id",
            "archetype",
            "event_id",
            "timestamp_s",
            "event_type",
            "room_id",
            "pos_x",
            "pos_y",
            "pos_z",
            "data_json",
        ])

        for run in runs:
            for evt in run.telemetry_events:
                writer.writerow([
                    run.session_id,
                    run.archetype.value,
                    evt.event_id,
                    evt.timestamp_s,
                    evt.event_type.value,
                    evt.room_id,
                    evt.position.x,
                    evt.position.y,
                    evt.position.z,
                    json.dumps(evt.data),
                ])

        csv_str = output.getvalue()
        if target_path:
            target_path = Path(target_path)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(csv_str, encoding="utf-8")

        return csv_str

    @staticmethod
    def export_heatmap_csv(
        heatmap: HeatmapGrid2D,
        target_path: Optional[Path] = None,
    ) -> str:
        """
        Exports the 2D normalized density matrix to CSV.
        """
        output = io.StringIO()
        writer = csv.writer(output)

        for row in heatmap.cells:
            writer.writerow(row)

        csv_str = output.getvalue()
        if target_path:
            target_path = Path(target_path)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(csv_str, encoding="utf-8")

        return csv_str
