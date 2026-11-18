import { describe, it, expect, afterAll } from 'vitest';
import { PuppetBuilder, CH_VISEMES } from '../src/core/PuppetBuilder.js';
import fs from 'fs';
import path from 'path';
import os from 'os';

describe('PuppetBuilder (Phase 2 Deep Rigging)', () => {
  const testPsdPath = path.join(os.tmpdir(), `test_hero_${Date.now()}.psd`);

  afterAll(() => {
    try {
      if (fs.existsSync(testPsdPath)) fs.unlinkSync(testPsdPath);
    } catch {}
  });

  it('scaffolds a valid binary PSD puppet with Character Animator hierarchy, physics tags, hand triggers, and parallax', () => {
    const generatedPath = PuppetBuilder.scaffoldPuppet({
      characterName: 'TestHero',
      outPath: testPsdPath,
      width: 1000,
      height: 1000,
      includeLimbs: true,
      includePhysicsTags: true,
      includeHandTriggers: true,
      includeFaceParallax: true
    });

    expect(fs.existsSync(generatedPath)).toBe(true);
    expect(fs.statSync(generatedPath).size).toBeGreaterThan(1000);
  });

  it('deeply validates the scaffolded puppet against Character Animator rules and Phase 2 features', () => {
    const report = PuppetBuilder.validatePuppet(testPsdPath);

    expect(report.isValid).toBe(true);
    expect(report.characterRoot).toBe('TestHero');
    expect(report.hasHead).toBe(true);
    expect(report.headIsIndependent).toBe(true); // +Head
    expect(report.hasMouth).toBe(true);

    // All 14 custom visual visemes present
    expect(report.foundVisemes.length).toBe(CH_VISEMES.length);
    expect(report.missingVisemes.length).toBe(0);

    // Eyes and pupils
    expect(report.hasEyes.leftEye).toBe(true);
    expect(report.hasEyes.rightEye).toBe(true);
    expect(report.hasEyes.leftPupil).toBe(true);
    expect(report.hasEyes.rightPupil).toBe(true);

    // Limbs
    expect(report.hasLimbs.torso).toBe(true);
    expect(report.hasLimbs.leftArm).toBe(true);
    expect(report.hasLimbs.rightArm).toBe(true);

    // Phase 2: Physics Tags Audit
    expect(report.physicsFeatures.hasDangle).toBe(true);
    expect(report.physicsFeatures.hasDraggable).toBe(true);
    expect(report.physicsFeatures.hasFixed).toBe(true);
    expect(report.physicsFeatures.dangleLayers.length).toBeGreaterThan(0);
    expect(report.physicsFeatures.draggableLayers.length).toBeGreaterThan(0);
    expect(report.physicsFeatures.fixedLayers.length).toBeGreaterThan(0);

    // Phase 2: Hand Swap Sets Audit
    expect(report.handTriggers.hasSwapSets).toBe(true);
    expect(report.handTriggers.triggerKeysFound.length).toBeGreaterThanOrEqual(4);

    // Phase 2: Parallax Layers Audit
    expect(report.hasParallaxLayers).toBe(true);
  });
});
