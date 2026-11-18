"""
Universal Gameplay Validator for UAF-81.58.
Enforces multi-factor quality scoring, category rules, and non-negotiable Hard Fail conditions.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set
import re
from ..models.definition import (
    GameplayState,
    QuestState,
    CurrencyType,
)


@dataclass
class GameplayValidationReport:
    is_valid: bool = True
    quality_score: float = 100.0
    passed_checks: List[str] = field(default_factory=list)
    failed_checks: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "quality_score": round(self.quality_score, 2),
            "passed_checks": list(self.passed_checks),
            "failed_checks": list(self.failed_checks),
            "warnings": list(self.warnings),
            "details": dict(self.details),
        }


class UniversalGameplayValidator:
    """
    Quality gate & structural validator for UAF-81.58 Gameplay Assets.
    """

    WINDOWS_DRIVE_PATTERN = re.compile(r"^[A-Za-z]:[/\\]")

    @classmethod
    def validate_gameplay_state(
        cls,
        state: GameplayState,
        export_path: Optional[str] = None,
    ) -> GameplayValidationReport:
        report = GameplayValidationReport()
        deductions = 0.0

        # --- 1. HARD FAIL: PATH PURITY ---
        if export_path and cls.WINDOWS_DRIVE_PATTERN.match(export_path):
            report.is_valid = False
            report.failed_checks.append(f"HARD_FAIL: Machine-dependent path detected: {export_path}")
            report.quality_score = 0.0
            return report

        for e_id in state.entities:
            if cls.WINDOWS_DRIVE_PATTERN.match(e_id):
                report.is_valid = False
                report.failed_checks.append(f"HARD_FAIL: Machine-dependent entity identifier: {e_id}")
                report.quality_score = 0.0
                return report

        report.passed_checks.append("CHECK_PATH_PURITY")

        # --- 2. HARD FAIL: NO ORPHAN DATA (Quests without objectives) ---
        for q in state.quests.values():
            if not q.objectives:
                report.is_valid = False
                report.failed_checks.append(f"HARD_FAIL: Quest {q.quest_id} has 0 objectives.")
                report.quality_score = 0.0
                return report
        report.passed_checks.append("CHECK_QUEST_OBJECTIVES_INTEGRITY")

        # --- 3. HARD FAIL: DIALOGUE GRAPH SANITY ---
        for diag in state.dialogues.values():
            if diag.root_node_id not in diag.nodes:
                report.is_valid = False
                report.failed_checks.append(f"HARD_FAIL: Dialogue {diag.dialogue_id} root node '{diag.root_node_id}' missing.")
                report.quality_score = 0.0
                return report
            for n_id, node in diag.nodes.items():
                for choice in node.choices:
                    if choice.target_node_id not in diag.nodes:
                        report.is_valid = False
                        report.failed_checks.append(
                            f"HARD_FAIL: Dialogue choice in node '{n_id}' references undefined target '{choice.target_node_id}'."
                        )
                        report.quality_score = 0.0
                        return report
        report.passed_checks.append("CHECK_DIALOGUE_GRAPH_SANITY")

        # --- 4. HARD FAIL: WALLET BALANCE PURITY ---
        for entity in state.entities.values():
            for c_type, bal in entity.wallet.balances.items():
                if bal < 0:
                    report.is_valid = False
                    report.failed_checks.append(
                        f"HARD_FAIL: Negative balance {bal} for {c_type.value} on entity {entity.entity_id}."
                    )
                    report.quality_score = 0.0
                    return report

        for merchant in state.merchants.values():
            for c_type, bal in merchant.wallet.balances.items():
                if bal < 0:
                    report.is_valid = False
                    report.failed_checks.append(
                        f"HARD_FAIL: Negative balance {bal} for merchant {merchant.merchant_id}."
                    )
                    report.quality_score = 0.0
                    return report
        report.passed_checks.append("CHECK_CURRENCY_BOUNDS")

        # --- 5. HARD FAIL: DUPLICATE TRANSACTION IDS ---
        tx_seen: Set[str] = set()
        for tx in state.transactions:
            if tx.transaction_id in tx_seen:
                report.is_valid = False
                report.failed_checks.append(f"HARD_FAIL: Duplicate transaction ID: {tx.transaction_id}")
                report.quality_score = 0.0
                return report
            tx_seen.add(tx.transaction_id)
        report.passed_checks.append("CHECK_TRANSACTION_IDEMPOTENCY")

        # --- 6. HARD FAIL: CIRCULAR SKILL PREREQUISITES ---
        for tree in state.skill_trees.values():
            for s_id, s_node in tree.skills.items():
                visited = set()
                curr = s_node
                while curr and curr.prerequisites:
                    p_id = curr.prerequisites[0]
                    if p_id in visited:
                        report.is_valid = False
                        report.failed_checks.append(f"HARD_FAIL: Circular skill prerequisite cycle at {p_id}")
                        report.quality_score = 0.0
                        return report
                    visited.add(p_id)
                    curr = tree.skills.get(p_id)
        report.passed_checks.append("CHECK_SKILL_TREE_DAG")

        # --- 7. WARNINGS & DEDUCTIONS ---
        for entity in state.entities.values():
            if entity.health < 0.0:
                report.warnings.append(f"Entity {entity.entity_id} has negative health: {entity.health}")
                deductions += 5.0

            for it in entity.inventory.items:
                if it.quantity < 0:
                    report.warnings.append(f"Item {it.instance_id} has negative quantity: {it.quantity}")
                    deductions += 5.0
                if it.definition_id not in state.items:
                    report.warnings.append(f"Item {it.instance_id} references undefined item {it.definition_id}")
                    deductions += 5.0

        for unlock in state.world_unlocks.values():
            if unlock.is_unlocked:
                for req_f in unlock.required_flags:
                    if not state.world_flags.get(req_f, False):
                        report.warnings.append(f"Unlock {unlock.unlock_id} marked unlocked but missing required flag {req_f}")
                        deductions += 5.0

        report.quality_score = max(0.0, 100.0 - deductions)
        return report
