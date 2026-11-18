import { describe, it, expect, afterAll } from 'vitest';
import { SceneManifestBuilder, SceneManifest } from '../src/core/SceneManifestBuilder.js';
import fs from 'fs';
import path from 'path';
import os from 'os';

describe('SceneManifestBuilder (Phase 5)', () => {
  const tempDir = path.join(os.tmpdir(), `test_manifest_${Date.now()}`);

  afterAll(() => {
    try { if (fs.existsSync(tempDir)) fs.rmSync(tempDir, { recursive: true, force: true }); } catch {}
  });

  it('generates production-grade secondary animation expression snippets', () => {
    const squash = SceneManifestBuilder.getExpressionSnippet('squash_and_stretch', { maxAmplitude: 20, frequency: 4, decay: 6 });
    expect(squash).toContain('var maxAmp = 20;');
    expect(squash).toContain('var freq = 4;');
    expect(squash).toContain('var decay = 6;');
    expect(squash).toContain('Math.sin');

    const shake = SceneManifestBuilder.getExpressionSnippet('camera_shake', { frequency: 3, amplitude: 30 });
    expect(shake).toContain('wiggle(3, 30);');

    const bounce = SceneManifestBuilder.getExpressionSnippet('audio_reactive_bounce', { scaleMultiplier: 1.5, baseScale: 100 });
    expect(bounce).toContain('Audio Amplitude');
    expect(bounce).toContain('Both Channels');
    expect(bounce).toContain('1.5');

    const blink = SceneManifestBuilder.getExpressionSnippet('blink_cycle', { intervalSeconds: 4.0 });
    expect(blink).toContain('var interval = 4;');
    expect(blink).toContain('seedRandom');

    const float = SceneManifestBuilder.getExpressionSnippet('floating_idle', { speed: 2.0, amplitude: 15 });
    expect(float).toContain('Math.sin(time * 2');
  });

  it('generates comprehensive ExtendScript code for 2.5D multi-plane scene', () => {
    const manifest: SceneManifest = {
      schemaVersion: '1.0.0',
      sceneName: 'Test_25D_Stage',
      width: 1920,
      height: 1080,
      fps: 24,
      durationSeconds: 15,
      layers: [
        {
          name: 'City_Background',
          filePath: 'F:/Assets/bg.png',
          layerType: 'background',
          zDepth: 1800,
          scaleCompensation: true
        },
        {
          name: 'Main_Character',
          filePath: 'F:/Assets/hero.psd',
          layerType: 'character',
          zDepth: 0,
          expressions: [
            { property: 'Scale', type: 'squash_and_stretch', params: { maxAmplitude: 12 } }
          ]
        },
        {
          name: 'Street_Lamp_Prop',
          filePath: 'F:/Assets/lamp.png',
          layerType: 'prop',
          zDepth: 350
        },
        {
          name: 'Rain_Foreground',
          filePath: 'F:/Assets/rain.png',
          layerType: 'foreground',
          zDepth: -300
        }
      ],
      audioTracks: [
        { name: 'Voiceover', filePath: 'F:/Assets/voice.wav', inPoint: 0.5 }
      ],
      camera: {
        enabled: true,
        createController: true,
        depthOfField: true
      }
    };

    const jsx = SceneManifestBuilder.toExtendScript(manifest);

    expect(jsx).toContain('app.beginUndoGroup("Assemble 2.5D Scene: Test_25D_Stage");');
    expect(jsx).toContain('addComp("Test_25D_Stage", 1920, 1080');
    expect(jsx).toContain('addCamera("Test_25D_Stage_Camera"');
    expect(jsx).toContain('addNull()');
    expect(jsx).toContain('Camera_Controller');
    expect(jsx).toContain('threeDLayer = true');
    expect(jsx).toContain('Depth of Field');
    expect(jsx).toContain('City_Background');
    expect(jsx).toContain('Main_Character');
    expect(jsx).toContain('Voiceover');
    expect(jsx).toContain('comp.openInViewer()');
  });

  it('saves Scene Manifest JSON and matching ExtendScript constructor to disk', () => {
    const jsonPath = path.join(tempDir, 'scene_manifest.json');
    const manifest: SceneManifest = {
      schemaVersion: '1.0.0',
      sceneName: 'Episode_01_Scene_A',
      width: 1920,
      height: 1080,
      fps: 24,
      durationSeconds: 12,
      layers: [
        { name: 'Forest_BG', filePath: 'F:/bg.png', layerType: 'background', zDepth: 1500 },
        { name: 'Hero_Rig', filePath: 'F:/hero.psd', layerType: 'character', zDepth: 0 }
      ]
    };

    const result = SceneManifestBuilder.saveManifestAndScript(manifest, jsonPath);

    expect(fs.existsSync(result.jsonPath)).toBe(true);
    expect(fs.existsSync(result.jsxPath)).toBe(true);

    const savedJson = JSON.parse(fs.readFileSync(result.jsonPath, 'utf8'));
    expect(savedJson.sceneName).toBe('Episode_01_Scene_A');
    expect(savedJson.layers.length).toBe(2);

    const savedJsx = fs.readFileSync(result.jsxPath, 'utf8');
    expect(savedJsx).toContain('Episode_01_Scene_A');
    expect(savedJsx).toContain('Forest_BG');
  });
});
