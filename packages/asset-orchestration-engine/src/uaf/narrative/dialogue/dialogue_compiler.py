"""
UAF-81.98: Dialogue Tree Compiler & Interactive Conversation Evaluator.
Validates referential integrity of dialogue trees, evaluates prerequisites (reputation,
inventory items, world flags), resolves RPG skill checks, and applies narrative consequences.
"""

import random
from typing import Dict, List, Optional, Tuple, Any

from ..core.contracts import (
    DialogueTreeSpec,
    DialogueNode,
    DialogueChoice,
    PrerequisiteCondition,
    ConsequenceAction,
    ConditionOperator,
    ConsequenceType,
    SkillCheckAttribute,
    SkillCheckResult,
)


class DialogueTreeCompiler:
    """
    Validates and executes branching dialogue trees against player and world state.
    """

    @staticmethod
    def validate_tree_integrity(tree: DialogueTreeSpec) -> Tuple[bool, List[str]]:
        """
        Ensures that start_node exists and that all target nodes referenced by choices are present.
        """
        errors: List[str] = []

        if tree.start_node_id not in tree.nodes:
            errors.append(f"Start node '{tree.start_node_id}' does not exist in dialogue tree '{tree.tree_id}'.")

        for node_id, node in tree.nodes.items():
            for choice in node.choices:
                if choice.target_node_id not in tree.nodes:
                    errors.append(
                        f"Choice '{choice.choice_id}' in node '{node_id}' targets non-existent node '{choice.target_node_id}'."
                    )
                if choice.fallback_node_id and choice.fallback_node_id not in tree.nodes:
                    errors.append(
                        f"Choice '{choice.choice_id}' in node '{node_id}' fallback targets non-existent node '{choice.fallback_node_id}'."
                    )

        return len(errors) == 0, errors

    @staticmethod
    def evaluate_choice_prerequisites(
        choice: DialogueChoice,
        flags: Dict[str, Any],
        reputation: Dict[str, float],
        inventory: List[str],
    ) -> Tuple[bool, List[str]]:
        """
        Evaluates whether a player satisfies all conditions to select this dialogue option.
        """
        failures: List[str] = []

        for prereq in choice.prerequisites:
            key = prereq.condition_key
            op = prereq.operator
            target = prereq.target_value

            if op == ConditionOperator.EQUALS:
                actual = flags.get(key)
                if actual != target:
                    failures.append(prereq.failure_message or f"Flag '{key}' ({actual}) != {target}")

            elif op == ConditionOperator.NOT_EQUALS:
                actual = flags.get(key)
                if actual == target:
                    failures.append(prereq.failure_message or f"Flag '{key}' ({actual}) == {target}")

            elif op == ConditionOperator.GREATER_THAN:
                actual = flags.get(key, 0)
                if actual <= target:
                    failures.append(prereq.failure_message or f"Flag '{key}' ({actual}) <= {target}")

            elif op == ConditionOperator.LESS_THAN:
                actual = flags.get(key, 0)
                if actual >= target:
                    failures.append(prereq.failure_message or f"Flag '{key}' ({actual}) >= {target}")

            elif op == ConditionOperator.HAS_ITEM:
                if key not in inventory and target not in inventory:
                    failures.append(prereq.failure_message or f"Missing required item '{key}'")

            elif op == ConditionOperator.FACTION_REPUTATION_GE:
                actual_rep = reputation.get(key, 0.0)
                if actual_rep < float(target):
                    failures.append(
                        prereq.failure_message
                        or f"Insufficient reputation with faction '{key}': {actual_rep} < {target}"
                    )

        return len(failures) == 0, failures

    @staticmethod
    def resolve_skill_check(
        choice: DialogueChoice,
        player_skills: Dict[SkillCheckAttribute, int],
        deterministic: bool = True,
        seed: Optional[int] = None,
    ) -> SkillCheckResult:
        """
        Evaluates a skill check option (e.g. Persuasion, Intimidation, Technical Hack).
        """
        attr = choice.skill_check_attr or SkillCheckAttribute.PERSUASION
        diff = max(1, choice.skill_check_difficulty)
        player_lvl = player_skills.get(attr, 1)

        prob = round(player_lvl / (player_lvl + diff), 4)

        if deterministic:
            success = player_lvl >= diff
        else:
            rng = random.Random(seed) if seed is not None else random.Random()
            success = rng.random() <= prob

        return SkillCheckResult(
            attribute=attr,
            player_skill_level=player_lvl,
            difficulty=diff,
            success=success,
            probability=prob,
        )
