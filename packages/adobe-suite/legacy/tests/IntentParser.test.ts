import { test, expect, describe } from 'vitest';
import { IntentParser, AnimationIntentSchema } from '../src/core/IntentParser.js';

describe('Dynamic DSL Parser (Zod)', () => {
  test('Validates and parses a strict JSON schema intent into a DAG', () => {
    const parser = new IntentParser();

    const validIntent = {
      id: 'intent_123',
      type: 'animation.sequence',
      parameters: {
        scene: { name: 'My Test Scene' },
        characters: [
          { id: 'char_1', asset_path: '/assets/bob.puppet' }
        ],
        audio_tracks: [
          { id: 'audio_1', file_path: '/assets/voice.wav', character_id: 'char_1' }
        ],
        actions: [
          { type: 'lip_sync', character_id: 'char_1' },
          { type: 'render' }
        ]
      }
    };

    // The parser internally uses Zod for validation.
    // If the intent is invalid, Zod throws an error.
    const graph = parser.parse(validIntent as any);

    // Assert graph structure
    expect(graph.nodes.length).toBe(5);
    // Nodes: scene, char_1, audio_1, lip_sync, render

    const sceneNode = graph.nodes.find(n => n.capability === 'scene.create');
    expect(sceneNode).toBeDefined();

    const lipSyncNode = graph.nodes.find(n => n.capability === 'puppet.lip_sync');
    expect(lipSyncNode).toBeDefined();

    // Verify dependencies: Lip sync should depend on char and audio
    const incomingEdgesToLipSync = graph.edges.filter(e => e.targetId === lipSyncNode!.id);
    expect(incomingEdgesToLipSync.length).toBeGreaterThanOrEqual(2);
  });

  test('Throws an error for invalid JSON schema intents', () => {
    const parser = new IntentParser();

    const invalidIntent = {
      id: 'intent_123',
      type: 'animation.sequence',
      parameters: {
        // Missing scene
        characters: [{ id: 'char_1' }],
        actions: []
      }
    };

    expect(() => {
      parser.parse(invalidIntent as any);
    }).toThrow();
  });
});
