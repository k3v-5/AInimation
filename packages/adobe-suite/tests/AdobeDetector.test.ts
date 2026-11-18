import { describe, it, expect } from 'vitest';
import { AdobeDetector } from '../src/core/AdobeDetector.js';

describe('AdobeDetector', () => {
  it('detects installed creative apps on the workstation', () => {
    const status = AdobeDetector.getStatus();

    expect(status).toBeDefined();
    expect(status.characterAnimator).toBeDefined();
    expect(status.illustrator).toBeDefined();
    expect(status.afterEffects).toBeDefined();
    expect(status.blender).toBeDefined();

    // Verify detection of installed 2026 suite on this machine
    expect(status.characterAnimator.installed).toBe(true);
    expect(status.characterAnimator.path).toContain('Character Animator');

    expect(status.illustrator.installed).toBe(true);
    expect(status.illustrator.path).toContain('Illustrator');

    expect(status.afterEffects.installed).toBe(true);
    expect(status.afterEffects.path).toContain('AfterFX');

    expect(status.blender.installed).toBe(true);
    expect(status.blender.path).toContain('blender');
  });
});
