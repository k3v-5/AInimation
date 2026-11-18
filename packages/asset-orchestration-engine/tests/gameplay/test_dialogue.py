"""
Tests for Universal Dialogue System (UAF-81.58 Sections 51-65, 187).
"""
import pytest
from src.uaf.universal_gameplay.models.definition import (
    DialogueChoice,
    DialogueNode,
    DialogueGraph,
    DialogueHistoryRecord,
    InteractionCondition,
    InteractionConditionType,
    InteractionAction,
    InteractionActionType,
    GameplayCommand,
    GameplayCommandType,
    CommandFailureCode,
    GameplayState,
)
from src.uaf.universal_gameplay.engine.universal_gameplay_fabricator import (
    UniversalGameplayFabricator,
)


def test_dialogue_node_creation():
    node = DialogueNode(
        node_id="node_greeting",
        speaker="Elder",
        text="Greetings, traveler.",
        is_terminal=False,
    )
    assert node.node_id == "node_greeting"
    assert node.speaker == "Elder"
    assert node.text == "Greetings, traveler."
    assert not node.is_terminal
    assert len(node.choices) == 0


def test_dialogue_choice_creation():
    choice = DialogueChoice(
        choice_id="ch_1",
        text="Who are you?",
        target_node_id="node_identity",
    )
    assert choice.choice_id == "ch_1"
    assert choice.text == "Who are you?"
    assert choice.target_node_id == "node_identity"
    assert len(choice.conditions) == 0
    assert len(choice.actions) == 0


def test_dialogue_choice_with_conditions():
    cond = InteractionCondition(
        condition_type=InteractionConditionType.HAS_ITEM,
        target_key="relic_of_dawn",
        expected_value=True,
    )
    choice = DialogueChoice(
        choice_id="ch_relic",
        text="I bring the sacred relic.",
        target_node_id="node_relic_reward",
        conditions=[cond],
    )
    assert len(choice.conditions) == 1
    assert choice.conditions[0].condition_type == InteractionConditionType.HAS_ITEM
    assert choice.conditions[0].target_key == "relic_of_dawn"


def test_dialogue_choice_with_actions():
    action = InteractionAction(
        action_type=InteractionActionType.START_QUEST,
        payload={"quest_id": "quest_cleanse_shrine"},
    )
    choice = DialogueChoice(
        choice_id="ch_accept",
        text="I accept your challenge.",
        target_node_id="node_farewell",
        actions=[action],
    )
    assert len(choice.actions) == 1
    assert choice.actions[0].action_type == InteractionActionType.START_QUEST
    assert choice.actions[0].payload["quest_id"] == "quest_cleanse_shrine"


def test_dialogue_graph_assembly():
    n1 = DialogueNode(node_id="root", speaker="Guard", text="Halt! State your business.")
    n2 = DialogueNode(node_id="node_peaceful", speaker="Guard", text="Pass through in peace.", is_terminal=True)
    c1 = DialogueChoice(choice_id="c1", text="I am a trader.", target_node_id="node_peaceful")
    n1.choices.append(c1)

    graph = DialogueGraph(
        dialogue_id="diag_guard_gate",
        root_node_id="root",
        nodes={"root": n1, "node_peaceful": n2},
    )
    assert graph.dialogue_id == "diag_guard_gate"
    assert graph.root_node_id == "root"
    assert len(graph.nodes) == 2
    assert graph.nodes["root"].choices[0].target_node_id == "node_peaceful"


def test_dialogue_graph_traversal():
    n1 = DialogueNode(node_id="start", speaker="Merchant", text="Looking for goods?")
    n2 = DialogueNode(node_id="wares", speaker="Merchant", text="Here is what I have.")
    n3 = DialogueNode(node_id="leave", speaker="Merchant", text="Safe travels.", is_terminal=True)

    n1.choices.append(DialogueChoice("c_wares", "Show me.", "wares"))
    n1.choices.append(DialogueChoice("c_leave", "No thanks.", "leave"))
    n2.choices.append(DialogueChoice("c_done", "Done shopping.", "leave"))

    graph = DialogueGraph(
        dialogue_id="diag_merchant",
        root_node_id="start",
        nodes={"start": n1, "wares": n2, "leave": n3},
    )

    curr = graph.nodes[graph.root_node_id]
    assert curr.node_id == "start"
    # Take first choice
    next_node_id = curr.choices[0].target_node_id
    curr = graph.nodes[next_node_id]
    assert curr.node_id == "wares"
    # Take choice to leave
    next_node_id = curr.choices[0].target_node_id
    curr = graph.nodes[next_node_id]
    assert curr.node_id == "leave"
    assert curr.is_terminal


def test_dialogue_terminal_nodes():
    node = DialogueNode(node_id="end", speaker="Oracle", text="The prophecy is sealed.", is_terminal=True)
    assert node.is_terminal
    assert len(node.choices) == 0


def test_dialogue_history_recording():
    hist = DialogueHistoryRecord(
        dialogue_id="diag_intro",
        node_id="root",
        speaker="Elder",
        choice_taken="c_greet",
        timestamp=12.34,
    )
    assert hist.dialogue_id == "diag_intro"
    assert hist.node_id == "root"
    assert hist.speaker == "Elder"
    assert hist.choice_taken == "c_greet"
    assert hist.timestamp == 12.34


def test_dialogue_command_talk_success():
    state = GameplayState("SIM_DIALOGUE")
    node = DialogueNode("n0", "Priest", "Blessings upon you.")
    diag = DialogueGraph("diag_priest", "n0", {"n0": node})
    state.dialogues[diag.dialogue_id] = diag

    cmd = GameplayCommand(
        command_id="cmd_talk_1",
        source="player_1",
        target="priest_npc",
        command_type=GameplayCommandType.TALK,
        payload={"dialogue_id": "diag_priest"},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert res.success
    assert "Priest" in res.message


def test_dialogue_command_missing_dialogue():
    state = GameplayState("SIM_DIALOGUE")
    cmd = GameplayCommand(
        command_id="cmd_talk_missing",
        source="player_1",
        target="nobody",
        command_type=GameplayCommandType.TALK,
        payload={"dialogue_id": "diag_unknown"},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.INVALID_TARGET


def test_dialogue_command_missing_root():
    state = GameplayState("SIM_DIALOGUE")
    diag = DialogueGraph("diag_corrupt", "non_existent_root", {})
    state.dialogues[diag.dialogue_id] = diag

    cmd = GameplayCommand(
        command_id="cmd_talk_corrupt",
        source="player_1",
        target="target",
        command_type=GameplayCommandType.TALK,
        payload={"dialogue_id": "diag_corrupt"},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.INVALID_STATE


def test_dialogue_branching_paths():
    n_root = DialogueNode("root", "King", "Why do you seek an audience?")
    n_quest = DialogueNode("quest", "King", "Take this sword and slay the beast.", is_terminal=True)
    n_banish = DialogueNode("banish", "King", "Guards, throw him out!", is_terminal=True)

    n_root.choices.append(DialogueChoice("c_serve", "I wish to serve.", "quest"))
    n_root.choices.append(DialogueChoice("c_insult", "Your throne is weak.", "banish"))

    graph = DialogueGraph("diag_king", "root", {"root": n_root, "quest": n_quest, "banish": n_banish})
    assert len(graph.nodes["root"].choices) == 2
    assert graph.nodes[graph.nodes["root"].choices[0].target_node_id].node_id == "quest"
    assert graph.nodes[graph.nodes["root"].choices[1].target_node_id].node_id == "banish"
