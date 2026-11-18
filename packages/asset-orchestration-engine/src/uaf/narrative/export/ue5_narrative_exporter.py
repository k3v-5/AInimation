"""
UAF-81.98: UE5 Narrative Exporter.
Serializes procedural quests, dialogue trees, and narrative branches into
Unreal Engine 5 UDataTable (CSV/JSON) formats ready for CommonUI and StateTree runtime hooks.
"""

import csv
import io
import json
from pathlib import Path
from typing import Dict, List, Optional, Any

from ..core.contracts import (
    QuestDefinition,
    DialogueTreeSpec,
    DialogueNode,
)
from ..graph.narrative_dag import BranchingNarrativeDAG


class UE5NarrativeExporter:
    """
    Exports quest networks and dialogue trees into UE5 UDataTable and JSON bundles.
    """

    @staticmethod
    def export_quests_datatable_csv(
        quests: List[QuestDefinition],
        target_path: Optional[Path] = None,
    ) -> str:
        """
        Exports QuestDefinitions into a UDataTable CSV format (FQuestDefinitionRow).
        """
        output = io.StringIO()
        writer = csv.writer(output)

        # UDataTable Header
        writer.writerow([
            "---",
            "QuestId",
            "Title",
            "QuestType",
            "Description",
            "RecommendedLevel",
            "FactionId",
            "PrerequisiteQuests",
            "MutuallyExclusiveQuests",
            "StepCount",
        ])

        for q in quests:
            writer.writerow([
                q.quest_id,
                q.quest_id,
                q.title,
                q.quest_type.value,
                q.description,
                q.recommended_level,
                q.faction_id,
                ";".join(q.prerequisite_quest_ids),
                ";".join(q.mutually_exclusive_quest_ids),
                len(q.steps),
            ])

        csv_str = output.getvalue()
        if target_path:
            target_path = Path(target_path)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(csv_str, encoding="utf-8")

        return csv_str

    @staticmethod
    def export_dialogue_datatable_csv(
        tree: DialogueTreeSpec,
        target_path: Optional[Path] = None,
    ) -> str:
        """
        Exports DialogueNodes into a UDataTable CSV format (FDialogueNodeRow) with CommonUI tags.
        """
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow([
            "---",
            "NodeId",
            "SpeakerName",
            "SpeakerFaction",
            "FormattedDialogue",
            "NodeType",
            "AudioVoiceCue",
            "ChoiceCount",
            "ChoicesPayload",
        ])

        for node_id, node in tree.nodes.items():
            formatted_text = f"<Speaker>{node.speaker_name}:</> {node.dialogue_text}"
            choices_payload = json.dumps([c.model_dump() for c in node.choices])

            writer.writerow([
                node_id,
                node_id,
                node.speaker_name,
                node.speaker_faction,
                formatted_text,
                node.node_type.value,
                node.audio_voice_cue or "",
                len(node.choices),
                choices_payload,
            ])

        csv_str = output.getvalue()
        if target_path:
            target_path = Path(target_path)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(csv_str, encoding="utf-8")

        return csv_str

    @staticmethod
    def export_narrative_bundle_json(
        dag: BranchingNarrativeDAG,
        dialogue_trees: List[DialogueTreeSpec],
        target_path: Optional[Path] = None,
    ) -> str:
        """
        Builds a comprehensive JSON narrative bundle for runtime engines and tool tooling.
        """
        payload = {
            "quests": {q_id: q.model_dump() for q_id, q in dag.quests.items()},
            "topological_order": dag.get_topological_order(),
            "critical_path": dag.compute_critical_path(),
            "dialogue_trees": {t.tree_id: t.model_dump() for t in dialogue_trees},
        }

        json_str = json.dumps(payload, indent=2)
        if target_path:
            target_path = Path(target_path)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(json_str, encoding="utf-8")

        return json_str
