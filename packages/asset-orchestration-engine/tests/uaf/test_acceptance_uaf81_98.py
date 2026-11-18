"""
Acceptance Test Suite for UAF-81.98: Procedural Quest Graph, Branching Narrative & Dialogue Trees.
Validates DAG acyclicity via Kahn's algorithm, mutually exclusive faction branch resolution,
dialogue tree referential integrity, prerequisite evaluation (reputation, items, flags),
RPG skill check calculations, transactional world state snapshots/rollback, and UE5 DataTable export.
"""

import pytest
import tempfile
import json
import csv
from pathlib import Path

from uaf.narrative import (
    QuestType,
    QuestState,
    MoralAlignment,
    DialogueNodeType,
    SkillCheckAttribute,
    ConditionOperator,
    ConsequenceType,
    PrerequisiteCondition,
    ConsequenceAction,
    DialogueChoice,
    DialogueNode,
    DialogueTreeSpec,
    QuestStep,
    QuestDefinition,
    WorldFlagSnapshot,
    SkillCheckResult,
    BranchingNarrativeDAG,
    DialogueTreeCompiler,
    WorldStateFlagRegistry,
    UE5NarrativeExporter,
)


def _build_test_quest_dag() -> BranchingNarrativeDAG:
    dag = BranchingNarrativeDAG()

    q1 = QuestDefinition(
        quest_id="Q_Prologue",
        title="Awakening in Sector 0",
        quest_type=QuestType.MAIN_STORY,
        description="Escape the malfunctioning cryogenic pod.",
        recommended_level=1,
    )
    q2 = QuestDefinition(
        quest_id="Q_Crossroads",
        title="Faction Crossroads",
        quest_type=QuestType.MAIN_STORY,
        description="Meet the intermediaries of the Syndicate and the Rebel front.",
        recommended_level=3,
        prerequisite_quest_ids=["Q_Prologue"],
    )
    q3_syn = QuestDefinition(
        quest_id="Q_Syndicate_Pact",
        title="Corporate Contract",
        quest_type=QuestType.FACTION_CONTRACT,
        description="Secure the mainframe for Syndicate directors.",
        recommended_level=5,
        faction_id="SYNDICATE",
        prerequisite_quest_ids=["Q_Crossroads"],
        mutually_exclusive_quest_ids=["Q_Rebel_Sabotage"],
    )
    q3_reb = QuestDefinition(
        quest_id="Q_Rebel_Sabotage",
        title="Free the Grid",
        quest_type=QuestType.FACTION_CONTRACT,
        description="Overload the mainframe generators for the rebellion.",
        recommended_level=5,
        faction_id="REBELS",
        prerequisite_quest_ids=["Q_Crossroads"],
        mutually_exclusive_quest_ids=["Q_Syndicate_Pact"],
    )
    q4 = QuestDefinition(
        quest_id="Q_Climax",
        title="The Final Breach",
        quest_type=QuestType.MAIN_STORY,
        description="Breach the central citadel vault.",
        recommended_level=8,
        prerequisite_quest_ids=["Q_Crossroads"],
    )

    dag.add_quest(q1)
    dag.add_quest(q2)
    dag.add_quest(q3_syn)
    dag.add_quest(q3_reb)
    dag.add_quest(q4)

    return dag


def _build_test_dialogue_tree() -> DialogueTreeSpec:
    node_greeting = DialogueNode(
        node_id="node_npc_intro",
        speaker_name="Agent Vance",
        speaker_faction="SYNDICATE",
        dialogue_text="State your business, outsider. Sector 4 is corporate territory.",
        node_type=DialogueNodeType.NPC_STATEMENT,
        is_start_node=True,
        choices=[
            DialogueChoice(
                choice_id="choice_friendly",
                prompt_text="I'm here to fulfill the cargo contract.",
                target_node_id="node_contract_accept",
            ),
            DialogueChoice(
                choice_id="choice_intimidate",
                prompt_text="[Intimidate] Step aside before I scrap your cyberware.",
                target_node_id="node_intimidated",
                fallback_node_id="node_combat_trigger",
                skill_check_attr=SkillCheckAttribute.INTIMIDATION,
                skill_check_difficulty=5,
            ),
            DialogueChoice(
                choice_id="choice_rebel_secret",
                prompt_text="The sparrow flies at midnight. (Rebel pass code)",
                target_node_id="node_rebel_pass",
                prerequisites=[
                    PrerequisiteCondition(
                        condition_key="knows_rebel_passcode",
                        operator=ConditionOperator.EQUALS,
                        target_value=True,
                        failure_message="You don't know the code.",
                    ),
                    PrerequisiteCondition(
                        condition_key="REBELS",
                        operator=ConditionOperator.FACTION_REPUTATION_GE,
                        target_value=25.0,
                    ),
                ],
                consequences=[
                    ConsequenceAction(
                        consequence_type=ConsequenceType.MUTATE_REPUTATION,
                        target_key="REBELS",
                        value=10.0,
                    ),
                    ConsequenceAction(
                        consequence_type=ConsequenceType.GIVE_ITEM,
                        target_key="Keycard_Citadel",
                    ),
                ],
            ),
        ],
    )

    node_contract = DialogueNode(
        node_id="node_contract_accept",
        speaker_name="Agent Vance",
        dialogue_text="Very well. Here is your clearance.",
        is_terminal_node=True,
    )

    node_intimidated = DialogueNode(
        node_id="node_intimidated",
        speaker_name="Agent Vance",
        dialogue_text="Easy now... I don't want any trouble. Take the gate key.",
        is_terminal_node=True,
    )

    node_combat = DialogueNode(
        node_id="node_combat_trigger",
        speaker_name="Agent Vance",
        dialogue_text="Security drones, eliminate the intruder!",
        is_terminal_node=True,
    )

    node_rebel = DialogueNode(
        node_id="node_rebel_pass",
        speaker_name="Agent Vance",
        dialogue_text="...Understood, comrade. The western vent is unmonitored.",
        is_terminal_node=True,
    )

    return DialogueTreeSpec(
        tree_id="DT_Vance_Checkpoint",
        tree_name="Checkpoint Vance Dialogue",
        start_node_id="node_npc_intro",
        nodes={
            "node_npc_intro": node_greeting,
            "node_contract_accept": node_contract,
            "node_intimidated": node_intimidated,
            "node_combat_trigger": node_combat,
            "node_rebel_pass": node_rebel,
        },
    )


class TestAcceptanceUAF81_98:

    def test_uaf81_98_contracts_and_models(self):
        """Validates all Pydantic models in contracts with keyword arguments."""
        prereq = PrerequisiteCondition(
            condition_key="has_key",
            operator=ConditionOperator.EQUALS,
            target_value=True,
        )
        assert prereq.condition_key == "has_key"

        action = ConsequenceAction(
            consequence_type=ConsequenceType.MUTATE_REPUTATION,
            target_key="SYNDICATE",
            value=15.0,
        )
        assert action.consequence_type == ConsequenceType.MUTATE_REPUTATION

        step = QuestStep(step_id="s1", title="Hack Terminal", description="Find terminal")
        assert step.step_id == "s1"

        quest = QuestDefinition(quest_id="q1", title="First Quest", steps={"s1": step})
        assert quest.title == "First Quest"

    def test_uaf81_98_narrative_dag_valid_topological_sort(self):
        """Tests that a clean branching DAG is acyclic and yields a valid topological order."""
        dag = _build_test_quest_dag()
        is_acyclic, cycle = dag.validate_acyclicity()
        assert is_acyclic is True
        assert len(cycle) == 0

        order = dag.get_topological_order()
        assert len(order) == 5
        # Prologue must precede Crossroads
        assert order.index("Q_Prologue") < order.index("Q_Crossroads")
        # Crossroads must precede Syndicate, Rebel, and Climax
        assert order.index("Q_Crossroads") < order.index("Q_Syndicate_Pact")
        assert order.index("Q_Crossroads") < order.index("Q_Rebel_Sabotage")
        assert order.index("Q_Crossroads") < order.index("Q_Climax")

    def test_uaf81_98_narrative_dag_cycle_detection(self):
        """Tests that circular quest dependencies are flagged as cycles."""
        dag = BranchingNarrativeDAG()
        q_a = QuestDefinition(quest_id="QA", title="A", prerequisite_quest_ids=["QC"])
        q_b = QuestDefinition(quest_id="QB", title="B", prerequisite_quest_ids=["QA"])
        q_c = QuestDefinition(quest_id="QC", title="C", prerequisite_quest_ids=["QB"])

        dag.add_quest(q_a)
        dag.add_quest(q_b)
        dag.add_quest(q_c)

        is_acyclic, cycle_nodes = dag.validate_acyclicity()
        assert is_acyclic is False
        assert set(cycle_nodes) == {"QA", "QB", "QC"}

        with pytest.raises(ValueError, match="ERR_NARRATIVE_CYCLE_DETECTED"):
            dag.get_topological_order()

    def test_uaf81_98_narrative_dag_critical_path(self):
        """Verifies longest dependency chain computation."""
        dag = _build_test_quest_dag()
        crit_path = dag.compute_critical_path()
        assert len(crit_path) >= 3
        assert crit_path[0] == "Q_Prologue"
        assert crit_path[1] == "Q_Crossroads"

    def test_uaf81_98_mutually_exclusive_faction_branches(self):
        """Siding with Syndicate abandons Rebel faction contract."""
        dag = _build_test_quest_dag()
        initial_states = {q_id: QuestState.NOT_STARTED for q_id in dag.quests}

        new_states = dag.resolve_faction_branch_commitment("Q_Syndicate_Pact", initial_states)
        assert new_states["Q_Syndicate_Pact"] == QuestState.ACTIVE
        assert new_states["Q_Rebel_Sabotage"] == QuestState.ABANDONED

    def test_uaf81_98_get_available_quests(self):
        """Tests that quests only unlock when all prerequisite quests are completed."""
        dag = _build_test_quest_dag()
        states = {q_id: QuestState.NOT_STARTED for q_id in dag.quests}
        completed = set()

        # Initially, only Prologue is available (in-degree 0)
        avail = dag.get_available_quests(completed, states)
        assert len(avail) == 1
        assert avail[0].quest_id == "Q_Prologue"

        # Complete Prologue
        completed.add("Q_Prologue")
        states["Q_Prologue"] = QuestState.COMPLETED

        # Now Crossroads is available
        avail2 = dag.get_available_quests(completed, states)
        assert len(avail2) == 1
        assert avail2[0].quest_id == "Q_Crossroads"

    def test_uaf81_98_dialogue_tree_integrity_validation(self):
        """Tests dialogue tree integrity validation and broken link detection."""
        tree = _build_test_dialogue_tree()
        is_valid, errors = DialogueTreeCompiler.validate_tree_integrity(tree)
        assert is_valid is True
        assert len(errors) == 0

        # Create broken link
        tree.nodes["node_npc_intro"].choices[0].target_node_id = "node_does_not_exist"
        is_valid2, errors2 = DialogueTreeCompiler.validate_tree_integrity(tree)
        assert is_valid2 is False
        assert any("node_does_not_exist" in e for e in errors2)

    def test_uaf81_98_dialogue_prerequisite_evaluation_flags(self):
        """Tests condition checking against world flags."""
        choice = DialogueChoice(
            choice_id="c1",
            prompt_text="Secret",
            target_node_id="target",
            prerequisites=[
                PrerequisiteCondition(
                    condition_key="story_chapter",
                    operator=ConditionOperator.GREATER_THAN,
                    target_value=2,
                ),
                PrerequisiteCondition(
                    condition_key="boss_defeated",
                    operator=ConditionOperator.EQUALS,
                    target_value=True,
                ),
            ],
        )

        flags_fail = {"story_chapter": 1, "boss_defeated": False}
        ok, fails = DialogueTreeCompiler.evaluate_choice_prerequisites(choice, flags_fail, {}, [])
        assert ok is False
        assert len(fails) == 2

        flags_pass = {"story_chapter": 3, "boss_defeated": True}
        ok2, fails2 = DialogueTreeCompiler.evaluate_choice_prerequisites(choice, flags_pass, {}, [])
        assert ok2 is True
        assert len(fails2) == 0

    def test_uaf81_98_dialogue_prerequisite_evaluation_reputation_and_items(self):
        """Tests condition checking against faction standing and inventory."""
        tree = _build_test_dialogue_tree()
        rebel_choice = tree.nodes["node_npc_intro"].choices[2]

        # Case 1: Lacks passcode and lacks reputation
        ok1, fails1 = DialogueTreeCompiler.evaluate_choice_prerequisites(
            rebel_choice,
            flags={"knows_rebel_passcode": False},
            reputation={"REBELS": 10.0},
            inventory=[],
        )
        assert ok1 is False
        assert len(fails1) == 2

        # Case 2: Satisfies all conditions
        ok2, fails2 = DialogueTreeCompiler.evaluate_choice_prerequisites(
            rebel_choice,
            flags={"knows_rebel_passcode": True},
            reputation={"REBELS": 30.0},
            inventory=[],
        )
        assert ok2 is True
        assert len(fails2) == 0

    def test_uaf81_98_dialogue_skill_check_resolution_deterministic(self):
        """Tests deterministic skill check pass and fail."""
        choice = DialogueChoice(
            choice_id="c_persuade",
            prompt_text="Persuade guard",
            target_node_id="target",
            skill_check_attr=SkillCheckAttribute.PERSUASION,
            skill_check_difficulty=6,
        )

        res_fail = DialogueTreeCompiler.resolve_skill_check(
            choice=choice,
            player_skills={SkillCheckAttribute.PERSUASION: 4},
            deterministic=True,
        )
        assert res_fail.success is False
        assert res_fail.player_skill_level == 4

        res_pass = DialogueTreeCompiler.resolve_skill_check(
            choice=choice,
            player_skills={SkillCheckAttribute.PERSUASION: 7},
            deterministic=True,
        )
        assert res_pass.success is True

    def test_uaf81_98_dialogue_skill_check_resolution_stochastic(self):
        """Tests stochastic skill check with reproducible probability calculation."""
        choice = DialogueChoice(
            choice_id="c_hack",
            prompt_text="Hack Terminal",
            target_node_id="target",
            skill_check_attr=SkillCheckAttribute.TECHNICAL_HACK,
            skill_check_difficulty=10,
        )

        # 10 / (10 + 10) = 0.50 probability
        res = DialogueTreeCompiler.resolve_skill_check(
            choice=choice,
            player_skills={SkillCheckAttribute.TECHNICAL_HACK: 10},
            deterministic=False,
            seed=42,
        )
        assert res.probability == 0.50
        assert isinstance(res.success, bool)

    def test_uaf81_98_world_state_flag_registry_mutations(self):
        """Tests setting flags, reputation clamping, and inventory."""
        reg = WorldStateFlagRegistry()
        reg.set_flag("door_open", True)
        assert reg.get_flag("door_open") is True

        # Reputation clamp test
        rep1 = reg.mutate_reputation("SYNDICATE", 150.0)
        assert rep1 == 100.0  # Clamped to 100
        rep2 = reg.mutate_reputation("SYNDICATE", -250.0)
        assert rep2 == -100.0  # Clamped to -100

        # Inventory
        reg.add_item("Keycard_Alpha")
        assert reg.has_item("Keycard_Alpha") is True
        assert reg.remove_item("Keycard_Alpha") is True
        assert reg.has_item("Keycard_Alpha") is False

    def test_uaf81_98_world_state_snapshot_and_rollback(self):
        """Tests creating a snapshot, mutating state, and restoring."""
        reg = WorldStateFlagRegistry()
        reg.set_flag("checkpoint", "Alpha")
        reg.mutate_reputation("REBELS", 20.0)
        reg.add_item("Medkit")

        snapshot = reg.create_snapshot()

        # Mutate further
        reg.set_flag("checkpoint", "Omega")
        reg.mutate_reputation("REBELS", -80.0)
        reg.remove_item("Medkit")

        assert reg.get_flag("checkpoint") == "Omega"
        assert reg.get_reputation("REBELS") == -60.0
        assert reg.has_item("Medkit") is False

        # Restore
        reg.restore_snapshot(snapshot)
        assert reg.get_flag("checkpoint") == "Alpha"
        assert reg.get_reputation("REBELS") == 20.0
        assert reg.has_item("Medkit") is True

    def test_uaf81_98_world_state_apply_consequences(self):
        """Tests atomic batch application of consequence actions."""
        reg = WorldStateFlagRegistry()
        actions = [
            ConsequenceAction(consequence_type=ConsequenceType.SET_FLAG, target_key="portal_open", value=True),
            ConsequenceAction(consequence_type=ConsequenceType.MUTATE_REPUTATION, target_key="REBELS", value=15.0),
            ConsequenceAction(consequence_type=ConsequenceType.GIVE_ITEM, target_key="Plasma_Rifle"),
            ConsequenceAction(consequence_type=ConsequenceType.START_QUEST, target_key="Q_Final_Assault"),
        ]

        changelog = reg.apply_consequences(actions)
        assert len(changelog) == 4
        assert reg.get_flag("portal_open") is True
        assert reg.get_reputation("REBELS") == 15.0
        assert reg.has_item("Plasma_Rifle") is True
        assert reg.get_quest_state("Q_Final_Assault") == QuestState.ACTIVE

    def test_uaf81_98_ue5_narrative_exporter_csv_and_json(self):
        """Tests export to UDataTable CSV and narrative JSON bundle."""
        dag = _build_test_quest_dag()
        tree = _build_test_dialogue_tree()

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Quests CSV
            q_csv = tmp_path / "Quests_DataTable.csv"
            csv_content = UE5NarrativeExporter.export_quests_datatable_csv(list(dag.quests.values()), q_csv)
            assert q_csv.exists()
            assert "---,QuestId,Title,QuestType" in csv_content
            assert "Q_Prologue" in csv_content

            # Dialogue CSV
            d_csv = tmp_path / "Dialogue_DataTable.csv"
            d_content = UE5NarrativeExporter.export_dialogue_datatable_csv(tree, d_csv)
            assert d_csv.exists()
            assert "---,NodeId,SpeakerName" in d_content
            assert "<Speaker>Agent Vance:</>" in d_content

            # JSON Bundle
            bundle_file = tmp_path / "Narrative_Bundle.json"
            json_content = UE5NarrativeExporter.export_narrative_bundle_json(dag, [tree], bundle_file)
            assert bundle_file.exists()
            data = json.loads(json_content)
            assert len(data["quests"]) == 5
            assert len(data["dialogue_trees"]) == 1
            assert "topological_order" in data
            assert "critical_path" in data
