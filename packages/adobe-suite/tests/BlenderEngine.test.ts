import { describe, it, expect, afterAll } from 'vitest';
import { BlenderEngine } from '../src/core/BlenderEngine.js';
import { AdobeDetector } from '../src/core/AdobeDetector.js';
import fs from 'fs';
import path from 'path';
import os from 'os';

describe('BlenderEngine (Phase 6 - 3D Hybrid & Grease Pencil)', () => {
  const tempDir = path.join(os.tmpdir(), `test_blender_p6_${Date.now()}`);
  const roomBlend = path.join(tempDir, 'test_cyberpunk.blend');
  const gpBlend = path.join(tempDir, 'test_grease_pencil.blend');
  const passesDir = path.join(tempDir, 'passes');

  afterAll(() => {
    try { if (fs.existsSync(tempDir)) fs.rmSync(tempDir, { recursive: true, force: true }); } catch {}
  });

  const hasBlender = !!AdobeDetector.getBlenderPath();

  it('scaffolds procedural 3D room with lighting, props, and camera', async () => {
    if (!hasBlender) return;

    const result = await BlenderEngine.scaffold3dRoom({
      roomType: 'cyberpunk_street',
      outputPath: roomBlend,
      renderPreview: true,
      width: 640,
      height: 360
    });

    expect(result.status).toBe('SUCCESS');
    expect(result.roomType).toBe('cyberpunk_street');
    expect(result.objectsCount).toBeGreaterThan(3);
    expect(result.lightsCount).toBeGreaterThanOrEqual(3);
    expect(fs.existsSync(roomBlend)).toBe(true);
    expect(fs.statSync(roomBlend).size).toBeGreaterThan(1000);

    // Verify preview PNG
    expect(result.previewImage).toBeDefined();
    expect(fs.existsSync(result.previewImage!)).toBe(true);

    const buf = fs.readFileSync(result.previewImage!);
    expect(buf.toString('hex', 0, 4)).toBe('89504e47'); // PNG magic bytes
  }, 45000);

  it('renders 3-pass parallax compositing stack (Beauty, Shadow Catcher Alpha, Z-Depth)', async () => {
    if (!hasBlender || !fs.existsSync(roomBlend)) return;

    const result = await BlenderEngine.renderParallaxPasses({
      blendFile: roomBlend,
      outputDir: passesDir,
      baseName: 'street_01',
      frameNumber: 1,
      width: 640,
      height: 360
    });

    expect(result.status).toBe('SUCCESS');
    expect(fs.existsSync(result.beautyPass)).toBe(true);
    expect(fs.existsSync(result.shadowPass)).toBe(true);
    expect(fs.existsSync(result.zDepthPass)).toBe(true);

    // Verify PNG magic numbers
    const beautyBuf = fs.readFileSync(result.beautyPass);
    expect(beautyBuf.toString('hex', 0, 4)).toBe('89504e47');

    const depthBuf = fs.readFileSync(result.zDepthPass);
    expect(depthBuf.toString('hex', 0, 4)).toBe('89504e47');
  }, 45000);

  it('generates procedural 2D Grease Pencil drawings in 3D space', async () => {
    if (!hasBlender) return;

    const result = await BlenderEngine.createGreasePencilSketch({
      sketchType: 'character_silhouette',
      outputPath: gpBlend,
      renderPreview: true,
      strokeColor: [0.1, 0.9, 1.0, 1.0],
      width: 640,
      height: 360
    });

    expect(result.status).toBe('SUCCESS');
    expect(result.sketchType).toBe('character_silhouette');
    expect(result.strokesCount).toBeGreaterThan(0);
    expect(fs.existsSync(gpBlend)).toBe(true);

    if (result.previewImage) {
      expect(fs.existsSync(result.previewImage)).toBe(true);
      const buf = fs.readFileSync(result.previewImage);
      expect(buf.toString('hex', 0, 4)).toBe('89504e47');
    }
  }, 45000);
});
