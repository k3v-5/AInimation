import { FileSystemObserver } from '../src/core/FileSystemObserver.js';
import { vi } from 'vitest';
import { test, expect, describe } from 'vitest';
import { AnimationEngine } from '../src/core/AnimationEngine.js';
import { IAnimationProvider, CapabilityDefinition, CapabilityId } from '../src/core/abstractions.js';

class MockProvider implements IAnimationProvider {
  id = 'mock_provider';
  public failFirstAttempt = false;
  public executionLog: string[] = [];

  capabilities(): CapabilityDefinition[] {
    return [{
      id: 'mock.action',
      inputSchema: {},
      outputSchema: {},
      supports: 'async',
      reversibility: 'reversible',
      observability: 'full'
    }];
  }

  async connect() {}
  async disconnect() {}

  async executeCapability(capabilityId: CapabilityId, input: Record<string, any>, abortSignal?: AbortSignal): Promise<any> {
    if (abortSignal && abortSignal.aborted) {
       throw new Error("Aborted");
    }

    if (this.failFirstAttempt) {
      this.failFirstAttempt = false; // succeed on retry
      throw new Error("Mock failure");
    }

    // Simulate async work
    await new Promise(resolve => setTimeout(resolve, 50));

    if (abortSignal && abortSignal.aborted) {
       throw new Error("Aborted");
    }

    this.executionLog.push(capabilityId);
    return { success: true };
  }
}

describe('AnimationEngine State Machine & Self-healing', () => {
  test('Executes happy path and returns artifact', async () => {
    vi.spyOn(FileSystemObserver.prototype, 'waitForFileStabilization').mockResolvedValue(true);
    const engine = new AnimationEngine();
    engine.registerProvider(new MockProvider());

    const intent = {
      id: 'intent_happy',
      type: 'mock.action',
      parameters: {}
    };

    const result = await engine.processIntent(intent, 'mock_provider');
    expect(result.status).toBe('SUCCESS');
    expect(result.intent_id).toBe('intent_happy');
    expect(result.artifacts).toBeDefined();
    expect(result.artifacts[0].local_path).toBeDefined();
  });

  test('Triggers self-healing on FAILED operation and recovers', async () => {
    vi.spyOn(FileSystemObserver.prototype, 'waitForFileStabilization').mockResolvedValue(true);
    const engine = new AnimationEngine();
    const mockProvider = new MockProvider();
    mockProvider.failFirstAttempt = true; // Will fail the first time
    engine.registerProvider(mockProvider);

    const intent = {
      id: 'intent_recovery',
      type: 'mock.action',
      parameters: {}
    };

    const result = await engine.processIntent(intent, 'mock_provider');

    // Should be SUCCESS because the recovery attempt succeeded.
    expect(result.status).toBe('SUCCESS');
  });

  test('Executes concurrent DAG nodes (animation.sequence)', async () => {
    vi.spyOn(FileSystemObserver.prototype, 'waitForFileStabilization').mockResolvedValue(true);
    const engine = new AnimationEngine();
    const mockProvider = new MockProvider();
    engine.registerProvider(mockProvider);

    const intent = {
      id: 'intent_dag',
      type: 'animation.sequence',
      parameters: {
        scene: { name: 'Test Scene' },
        characters: [{ id: 'char_1', asset_path: 'path' }],
        audio_tracks: [{ id: 'audio_1', file_path: 'audio.wav', character_id: 'char_1' }],
        actions: [{ type: 'lip_sync', character_id: 'char_1' }]
      }
    };
const startTime = Date.now();
    const result = await engine.processIntent(intent, 'mock_provider');
    const elapsed = Date.now() - startTime;

    expect(result.status).toBe('SUCCESS');

    // Since 'audio.generate' and 'puppet.prepare' run concurrently,
    // and 'puppet.lip_sync' runs after them, the total time should be ~100ms
    // not ~150ms if it were purely sequential.
    expect(elapsed).toBeLessThan(200);

    // Verify execution order constraints (lip_sync is the last one in the DAG)
    expect(mockProvider.executionLog[mockProvider.executionLog.length - 1]).toBe('puppet.lip_sync');
  });


  test('Handles AbortSignal for graceful shutdown', async () => {
    vi.spyOn(FileSystemObserver.prototype, 'waitForFileStabilization').mockResolvedValue(true);
    const engine = new AnimationEngine();
    engine.registerProvider(new MockProvider());

    const intent = {
      id: 'intent_abort',
      type: 'animation.sequence',
      parameters: {
        scene: { name: 'Test Scene' },
        characters: [{ id: 'char_1', asset_path: 'path' }],
        actions: [{ type: 'lip_sync', character_id: 'char_1' }]
      }
    };

    const abortController = new AbortController();

    // Trigger abort shortly after starting (inside the delay)
    setTimeout(() => {
      abortController.abort();
    }, 20);

    const result = await engine.processIntent(intent, 'mock_provider', abortController.signal);

    // In our implementation, processIntent returns a FAILED object when Promise.all fails
    // due to the abortSignal
    expect(result.status).toBe('FAILED');
    // We check that the failure was explicitly because it failed recovery due to the abort.
    expect(result.message).toContain('Operation failed and recovery max retries reached');
  });

});