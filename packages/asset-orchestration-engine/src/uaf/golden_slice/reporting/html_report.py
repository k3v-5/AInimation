"""HTML visual report generator for human-readable certification dashboards."""

from __future__ import annotations
from typing import Any, Dict
from uaf.golden_slice.certification.report import GoldenSliceCertificationReport


class HTMLReportGenerator:
    """Generates a clean, modern HTML dashboard displaying certification results."""

    @staticmethod
    def generate(report: GoldenSliceCertificationReport) -> str:
        status_color = "#22c55e" if report.is_certified else "#ef4444"
        badge_text = report.final_status

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>UAF Golden Slice Certification - {report.project_id}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 2rem; }}
        .container {{ max-width: 1000px; margin: 0 auto; background: #1e293b; border-radius: 12px; padding: 2rem; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }}
        .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 1.5rem; }}
        .badge {{ background: {status_color}; color: #ffffff; padding: 0.5rem 1.25rem; border-radius: 9999px; font-weight: bold; font-size: 1.1rem; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin: 2rem 0; }}
        .metric-card {{ background: #0f172a; padding: 1rem; border-radius: 8px; border: 1px solid #334155; text-align: center; }}
        .metric-value {{ font-size: 1.8rem; font-weight: bold; margin-top: 0.5rem; }}
        .subsystem-list {{ list-style: none; padding: 0; }}
        .subsystem-item {{ display: flex; justify-content: space-between; padding: 0.75rem 1rem; border-bottom: 1px solid #334155; }}
        .status-pass {{ color: #22c55e; font-weight: bold; }}
        .status-fail {{ color: #ef4444; font-weight: bold; }}
        .rc-banner {{ background: #3b82f6; color: white; padding: 0.75rem; border-radius: 6px; text-align: center; font-weight: bold; margin-top: 1.5rem; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1 style="margin:0;">UAF Golden Slice Certification</h1>
                <p style="margin: 0.25rem 0 0 0; color: #94a3b8;">Project: {report.project_id} | Build: {report.build_id}</p>
            </div>
            <div class="badge">{badge_text}</div>
        </div>

        <div class="metrics-grid">
            <div class="metric-card">
                <div>Target Level</div>
                <div class="metric-value" style="color:#60a5fa;">{report.target_level.value}</div>
            </div>
            <div class="metric-card">
                <div>Critical Failures</div>
                <div class="metric-value" style="color: {'#22c55e' if report.critical_failures == 0 else '#ef4444'};">{report.critical_failures}</div>
            </div>
            <div class="metric-card">
                <div>Blocking Warnings</div>
                <div class="metric-value" style="color: {'#22c55e' if report.blocking_warnings == 0 else '#ef4444'};">{report.blocking_warnings}</div>
            </div>
            <div class="metric-card">
                <div>Replay Mismatches</div>
                <div class="metric-value" style="color: {'#22c55e' if report.replay_mismatches == 0 else '#ef4444'};">{report.replay_mismatches}</div>
            </div>
        </div>

        <h3>Subsystem Verification Gates</h3>
        <ul class="subsystem-list">
            <li class="subsystem-item"><span>Generation DAG</span><span class="{'status-pass' if report.generation_passed else 'status-fail'}">{'PASS' if report.generation_passed else 'FAIL'}</span></li>
            <li class="subsystem-item"><span>Subsystem Integration</span><span class="{'status-pass' if report.integration_passed else 'status-fail'}">{'PASS' if report.integration_passed else 'FAIL'}</span></li>
            <li class="subsystem-item"><span>Automated QA Test Suites (12/12)</span><span class="{'status-pass' if report.qa_tests_passed else 'status-fail'}">{'PASS' if report.qa_tests_passed else 'FAIL'}</span></li>
            <li class="subsystem-item"><span>Performance & Frame Budget</span><span class="{'status-pass' if report.performance_compliant else 'status-fail'}">{'PASS' if report.performance_compliant else 'FAIL'}</span></li>
            <li class="subsystem-item"><span>Deterministic Replay Equivalence</span><span class="{'status-pass' if report.determinism_verified else 'status-fail'}">{'PASS' if report.determinism_verified else 'FAIL'}</span></li>
            <li class="subsystem-item"><span>Fault & Crash Recovery</span><span class="{'status-pass' if report.recovery_verified else 'status-fail'}">{'PASS' if report.recovery_verified else 'FAIL'}</span></li>
            <li class="subsystem-item"><span>Packaging & Cook Validation</span><span class="{'status-pass' if report.packaging_passed else 'status-fail'}">{'PASS' if report.packaging_passed else 'FAIL'}</span></li>
        </ul>

        {f'<div class="rc-banner">LOCKED IMMUTABLE RELEASE CANDIDATE: {report.release_candidate_tag}</div>' if report.is_immutable else ''}
    </div>
</body>
</html>
"""
        return html
