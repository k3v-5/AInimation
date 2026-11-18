import { z } from 'zod';
import { Intent, CapabilityId, WorkflowGraph, WorkflowNode } from './abstractions.js';

// Strict DSL Schemas
export const CharacterSchema = z.object({
  id: z.string(),
  asset_path: z.string().optional(),
});

export const AudioTrackSchema = z.object({
  id: z.string(),
  file_path: z.string(),
  character_id: z.string(),
});

export const ActionSchema = z.object({
  type: z.enum(['lip_sync', 'pose', 'render', 'ae_comp', 'ae_render', 'ps_create', 'ps_layer', 'ps_export', 'ai_create', 'puppet_import', 'audio_import', 'audio_generate', 'blender_execute', 'ame_batch', 'ame_compress', 'pr_auto_edit', 'pr_sync_audio', 'ai_generate_rig', 'ai_style_transfer']),
  provider: z.string().optional(),
  character_id: z.string().optional(),
  target_file: z.string().optional(),
  input_file: z.string().optional(),
  input_files: z.array(z.string()).optional(),
  audio_file: z.string().optional(),
  target_format: z.string().optional(),
  style_reference: z.string().optional(),
  composition_name: z.string().optional(),
  sequence_name: z.string().optional(),
  width: z.number().optional(),
  height: z.number().optional(),
  layer_name: z.string().optional(),
  parent_group: z.string().optional(),
  expected_layers: z.array(z.string()).optional() // Added for dynamic layer validation
});

export const AnimationIntentSchema = z.object({
  id: z.string(),
  type: z.literal('animation.sequence'),
  parameters: z.object({
    scene: z.object({
      name: z.string()
    }),
    characters: z.array(CharacterSchema),
    audio_tracks: z.array(AudioTrackSchema).optional(),
    actions: z.array(ActionSchema)
  })
});

export class IntentParser {
  public parse(intent: Intent, defaultProvider: string = 'character_animator'): WorkflowGraph {
    const graph: WorkflowGraph = {
      nodes: [],
      edges: []
    };

    if (intent.type === 'animation.sequence') {
      const parsedIntent = AnimationIntentSchema.parse(intent);
      const params = parsedIntent.parameters;

      const sceneNodeId = `scene_${Date.now()}`;
      const sceneNode: WorkflowNode = {
        id: sceneNodeId,
        capability: 'scene.create',
        inputs: [],
        outputs: [],
        constraints: [{ provider: defaultProvider, parameters: { name: params.scene.name } }]
      };
      graph.nodes.push(sceneNode);

      const characterNodes: Record<string, string> = {};
      const audioNodes: Record<string, string> = {};

      for (const char of params.characters) {
        const charNodeId = `char_${char.id}_${Date.now()}`;
        const charNode: WorkflowNode = {
          id: charNodeId,
          capability: 'puppet.import',
          inputs: [],
          outputs: [],
          constraints: [{ provider: defaultProvider, parameters: { id: char.id, path: char.asset_path } }]
        };
        graph.nodes.push(charNode);
        graph.edges.push({ sourceId: sceneNodeId, targetId: charNodeId });
        characterNodes[char.id] = charNodeId;
      }

      if (params.audio_tracks) {
        for (const audio of params.audio_tracks) {
          const audioNodeId = `audio_${audio.id}_${Date.now()}`;
          const audioNode: WorkflowNode = {
            id: audioNodeId,
            capability: 'audio.import',
            inputs: [],
            outputs: [],
            constraints: [{ provider: defaultProvider, parameters: { file_path: audio.file_path } }]
          };
          graph.nodes.push(audioNode);
          graph.edges.push({ sourceId: sceneNodeId, targetId: audioNodeId });
          audioNodes[audio.id] = audioNodeId;
        }
      }

      for (let i = 0; i < params.actions.length; i++) {
        const action = params.actions[i];
        const actionNodeId = `action_${action.type}_${i}`;

        let capability: CapabilityId = 'unknown';
        if (action.type === 'lip_sync') capability = 'puppet.lip_sync';
        if (action.type === 'pose') capability = 'puppet.pose';
        if (action.type === 'render') capability = 'render.export';
        if (action.type === 'ae_comp') capability = 'ae.comp.create';
        if (action.type === 'ae_render') capability = 'ae.render.export';
        if (action.type === 'ps_create') capability = 'ps.document.create';
        if (action.type === 'ps_layer') capability = 'ps.layer.setup';
        if (action.type === 'ps_export') capability = 'ps.document.export';
        if (action.type === 'ai_create') capability = 'ai.document.create';
        if (action.type === 'puppet_import') capability = 'puppet.import';
        if (action.type === 'audio_import') capability = 'audio.import';
        if (action.type === 'audio_generate') capability = 'audio.generate_tts';
        if (action.type === 'blender_execute') capability = 'blender.execute_python';
        if (action.type === 'ame_batch') capability = 'render.batch_encode';
        if (action.type === 'ame_compress') capability = 'render.compress';
        if (action.type === 'pr_auto_edit') capability = 'video.auto_edit';
        if (action.type === 'pr_sync_audio') capability = 'video.sync_audio';
        if (action.type === 'ai_generate_rig') capability = 'vector.generate_rig_layers';
        if (action.type === 'ai_style_transfer') capability = 'vector.style_transfer';

        const actionNode: WorkflowNode = {
          id: actionNodeId,
          capability: capability,
          inputs: [],
          outputs: [],
          constraints: [{ provider: action.provider || defaultProvider, parameters: { ...action } }]
        };
        graph.nodes.push(actionNode);

        if (action.type === 'lip_sync' && action.character_id) {
           const cNode = characterNodes[action.character_id];
           if (cNode) graph.edges.push({ sourceId: cNode, targetId: actionNodeId });

           const aTrack = params.audio_tracks?.find(a => a.character_id === action.character_id);
           if (aTrack && audioNodes[aTrack.id]) {
              graph.edges.push({ sourceId: audioNodes[aTrack.id], targetId: actionNodeId });
           }
        } else if (action.type !== 'lip_sync') {
           // For all other sequential actions, link to the previous node
           const previousAction = graph.nodes[graph.nodes.length - 2];
           if (previousAction) {
             graph.edges.push({ sourceId: previousAction.id, targetId: actionNodeId });
           }
        }
      }

    } else {
      const capabilityMap: Record<string, CapabilityId> = {
        'character.pose': 'puppet.pose',
        'animation.lipSync': 'audio.lip_sync',
        'scene.create': 'scene.create'
      };

      const capabilityId = capabilityMap[intent.type] || intent.type;

      const node: WorkflowNode = {
        id: `step_${Date.now()}_1`,
        capability: capabilityId,
        inputs: [],
        outputs: [],
        constraints: [{ provider: defaultProvider, parameters: intent.parameters }]
      };
      graph.nodes.push(node);
    }

    return graph;
  }
}