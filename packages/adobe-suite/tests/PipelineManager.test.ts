import { describe, it, expect, afterAll } from 'vitest';
import { PipelineManager } from '../src/core/PipelineManager.js';
import fs from 'fs';
import path from 'path';
import os from 'os';

describe('PipelineManager (Phase 7 - Multimodal Vision & One-Click Pipelines)', () => {
  const tempDir = path.join(os.tmpdir(), `test_pipeline_p7_${Date.now()}`);

  afterAll(() => {
    try { if (fs.existsSync(tempDir)) fs.rmSync(tempDir, { recursive: true, force: true }); } catch {}
  });

  it('extracts Base64 image payload and metadata for multimodal visual inspection', async () => {
    fs.mkdirSync(tempDir, { recursive: true });
    const testPng = path.join(tempDir, 'sample_frame.png');

    // Create a valid 2x2 PNG file
    const samplePngBase64 = 'iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAYAAABytg0kAAAAFElEQVQIW2P8z/D/PwMjgxhDAwMDAB1nBAX+I8WdAAAAAElFTkSuQmCC';
    fs.writeFileSync(testPng, Buffer.from(samplePngBase64, 'base64'));

    const result = await PipelineManager.getFrameBase64(testPng);

    expect(result.mimeType).toBe('image/png');
    expect(result.fileSizeBytes).toBeGreaterThan(10);
    expect(result.base64Data.length).toBeGreaterThan(20);
    expect(result.resolvedPath).toBe(path.resolve(testPng));
    expect(result.resolution).toBeDefined();
    expect(result.resolution?.width).toBe(2);
    expect(result.resolution?.height).toBe(2);
  });

  it('runs pipeline_create_talking_character end-to-end', async () => {
    const outDir = path.join(tempDir, 'talking_char');
    const result = await PipelineManager.createTalkingCharacter({
      characterName: 'Luna',
      dialogueText: 'Hola, este es un personaje animado completo creado en un solo clic.',
      outputDir: outDir,
      voice: 'mexico_female',
      emotionPreset: 'cheerful',
      launchCharacterAnimator: false,
      puppetDimensions: { width: 800, height: 800 }
    });

    expect(result.status).toBe('SUCCESS');
    expect(result.characterName).toBe('Luna');
    expect(fs.existsSync(result.puppetPsd)).toBe(true);
    expect(fs.existsSync(result.dialogueWav)).toBe(true);
    expect(fs.existsSync(result.lipSyncMarkers.json)).toBe(true);
    expect(fs.existsSync(result.lipSyncMarkers.afterEffectsJsx)).toBe(true);
    expect(fs.existsSync(result.lipSyncMarkers.csv)).toBe(true);

    // Verify PSD file
    const psdBuf = fs.readFileSync(result.puppetPsd);
    expect(psdBuf.toString('utf8', 0, 4)).toBe('8BPS');

    // Verify WAV audio
    const wavBuf = fs.readFileSync(result.dialogueWav);
    expect(wavBuf.toString('utf8', 0, 4)).toBe('RIFF');
    expect(wavBuf.readUInt32LE(24)).toBe(48000); // 48kHz

    // Verify JSON Lip-Sync Markers
    const jsonCues = JSON.parse(fs.readFileSync(result.lipSyncMarkers.json, 'utf8'));
    expect(jsonCues.cues.length).toBeGreaterThan(5);
    expect(jsonCues.metadata.generator).toContain('AdobeEngineSuit');
  }, 35000);

  it('runs pipeline_render_social_clip generating vertical 9:16 Scene Manifest and JSX', async () => {
    const outDir = path.join(tempDir, 'social_clip');
    const dummyChar = path.join(outDir, 'hero.psd');
    fs.mkdirSync(outDir, { recursive: true });
    fs.writeFileSync(dummyChar, 'dummy psd');

    const result = await PipelineManager.createSocialClip({
      projectName: 'TikTok_Dance_Clip',
      outputDir: outDir,
      aspectRatio: '9:16',
      characterFile: dummyChar,
      durationSeconds: 15,
      enableSecondaryBounce: true
    });

    expect(result.status).toBe('SUCCESS');
    expect(result.aspectRatio).toBe('9:16');
    expect(result.resolution.width).toBe(1080);
    expect(result.resolution.height).toBe(1920); // Vertical 9:16
    expect(fs.existsSync(result.sceneManifestPath)).toBe(true);
    expect(fs.existsSync(result.afterEffectsJsxPath)).toBe(true);

    const manifestData = JSON.parse(fs.readFileSync(result.sceneManifestPath, 'utf8'));
    expect(manifestData.width).toBe(1080);
    expect(manifestData.height).toBe(1920);
    expect(manifestData.layers[0].name).toBe('Character_Puppet');
    expect(manifestData.layers[0].expressions[0].type).toBe('squash_and_stretch');

    const jsxContent = fs.readFileSync(result.afterEffectsJsxPath, 'utf8');
    expect(jsxContent).toContain('1080, 1920');
    expect(jsxContent).toContain('Squash & Stretch');
  });
});
