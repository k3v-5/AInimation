import { FileSystemObserver } from '../src/core/FileSystemObserver.js';
import { vi } from 'vitest';
import { test, expect, describe } from 'vitest';
import { AnimationEngine } from '../src/core/AnimationEngine.js';
import { IAnimationProvider, CapabilityDefinition, CapabilityId } from '../src/core/abstractions.js';

class MockPhotoshopProvider implements IAnimationProvider {
  id = 'photoshop';
  public executionLog: string[] = [];
  capabilities(): CapabilityDefinition[] { return [{ id: 'ps.document.create', inputSchema: {}, outputSchema: {}, supports: 'sync', reversibility: 'reversible', observability: 'full' }, { id: 'ps.document.export', inputSchema: {}, outputSchema: {}, supports: 'sync', reversibility: 'reversible', observability: 'full' }]; }
  async connect() {}
  async disconnect() {}
  async executeCapability(capabilityId: CapabilityId, input: Record<string, any>): Promise<any> {
    this.executionLog.push(capabilityId);
    if (capabilityId === 'ps.document.export') {
      return { success: true, observed_state: { layers: ['+Head', 'Body'] } };
    }
    return { success: true };
  }
}

class MockCharacterProvider implements IAnimationProvider {
  id = 'character_animator';
  public executionLog: string[] = [];
  public lastInput: any = null;
  capabilities(): CapabilityDefinition[] { return [{ id: 'puppet.import', inputSchema: {}, outputSchema: {}, supports: 'sync', reversibility: 'reversible', observability: 'full' }, { id: 'render.export', inputSchema: {}, outputSchema: {}, supports: 'sync', reversibility: 'reversible', observability: 'full' }, { id: 'puppet.pose', inputSchema: {}, outputSchema: {}, supports: 'sync', reversibility: 'reversible', observability: 'full' }]; }
  async connect() {}
  async disconnect() {}
  async executeCapability(capabilityId: CapabilityId, input: Record<string, any>): Promise<any> {
    this.executionLog.push(capabilityId);
    if (capabilityId === 'puppet.import') this.lastInput = input;
    return { success: true };
  }
}

class MockAfterEffectsProvider implements IAnimationProvider {
  id = 'after_effects';
  public executionLog: string[] = [];
  public lastInput: any = null;
  capabilities(): CapabilityDefinition[] { return [{ id: 'ae.render.export', inputSchema: {}, outputSchema: {}, supports: 'sync', reversibility: 'reversible', observability: 'full' }]; }
  async connect() {}
  async disconnect() {}
  async executeCapability(capabilityId: CapabilityId, input: Record<string, any>): Promise<any> {
    this.executionLog.push(capabilityId);
    this.lastInput = input;
    return { success: true };
  }
}

describe('End-to-End Asset Factory Pipeline (PS -> CH -> AE)', () => {
  test('Orchestrates asset creation, animation, and post-production dynamically', async () => {
    vi.spyOn(FileSystemObserver.prototype, 'waitForFileStabilization').mockResolvedValue(true);
    const engine = new AnimationEngine();

    const psProvider = new MockPhotoshopProvider();
    const chProvider = new MockCharacterProvider();
    const aeProvider = new MockAfterEffectsProvider();

    engine.registerProvider(psProvider);
    engine.registerProvider(chProvider);
    engine.registerProvider(aeProvider);


    const intent = {
      id: 'e2e_intent',
      type: 'animation.sequence',
      parameters: {
        scene: { name: 'E2E Scene' },
        characters: [],
        actions: [
          { type: 'ps_create', provider: 'photoshop', width: 1080, height: 1080 },
          { type: 'ps_export', provider: 'photoshop', expected_layers: ['+Head', 'Body'] },
          { type: 'puppet_import', provider: 'character_animator', input_file: '${action_ps_export_1.output}' },
          { type: 'pose', provider: 'character_animator' },
          { type: 'render', provider: 'character_animator' },
          { type: 'ae_render', provider: 'after_effects', input_file: '${action_render_4.output}' }
        ]
      }
    };

    // Override the mock perception layer to prevent physical validation for our fake 'ps_export' and 'render' targets
    // Alternatively, we don't supply a target_file in our mock intent, so physical validation is skipped by the Engine's IF branch!

    const result = await engine.processIntent(intent as any, 'character_animator');

    if(result.status === 'FAILED') console.error('E2E FAILURE REASON:', result.message);
    expect(result.status).toBe('SUCCESS');

    // Verify PS executed
    expect(psProvider.executionLog).toContain('ps.document.create');
    expect(psProvider.executionLog).toContain('ps.document.export');

    // Verify CH executed
    expect(chProvider.executionLog).toContain('puppet.pose');
    expect(chProvider.executionLog).toContain('render.export');

    // Verify AE executed
    expect(aeProvider.executionLog).toContain('ae.render.export');

    // Verify DAG context injection (Context passing across 3 apps)
    expect(aeProvider.lastInput.input_file).toContain('Artifacts');
  });
});
