import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { AnimationEngine } from '../src/core/AnimationEngine.js';
import { Intent, Capability, Provider } from '../src/core/abstractions.js';
import { db } from '../src/core/Database.js';
import { FileSystemObserver } from '../src/core/FileSystemObserver.js';

describe('Visual Perception (VLM) Integration', () => {
  let engine: AnimationEngine;

  beforeEach(() => {
    engine = new AnimationEngine();
    db.exec('DELETE FROM asset_dependencies');
    db.exec('DELETE FROM operations');
    db.exec('DELETE FROM executions');
    db.exec('DELETE FROM assets');
    db.exec('DELETE FROM projects');
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should trigger recovery if VLM visual validation fails', async () => {
    let psCalls = 0;

    class MockPsProvider implements Provider {
      id = 'mock-ps'; name = 'Mock Photoshop';
      supportedCapabilities = ['ps.document.create' as Capability];
      async executeCapability(capability: Capability, parameters: Record<string, any>) {
        psCalls++;
        return { success: true, observed_state: { executed: true, created_file: '/path/mock.psd' } };
      }
    }

    engine.registerProvider(new MockPsProvider());

    const intent: Intent = {
      id: "intent_vis_1",
      type: "create",
      parameters: {
        asset_type: "puppet",
        target_path: "/path/mock.psd"
      }
    };

    vi.spyOn(engine['intentParser'], 'parse').mockReturnValue({
      nodes: [
        {
          id: 'op1',
          capability: 'ps.document.create' as Capability,
          inputs: [], outputs: [],
          constraints: [{
            provider: 'mock-ps',
            parameters: {
              target_file: '/path/mock.psd',
              visual_validation: 'Check if dog has red collar'
            }
          }]
        }
      ],
      edges: []
    });

    vi.spyOn(engine['workflowEngine'], 'resolveExecutionOrder').mockReturnValue([
      [ {
          id: 'op1', capability: 'ps.document.create' as Capability, inputs: [], outputs: [],
          constraints: [{ provider: 'mock-ps', parameters: { target_file: '/path/mock.psd', visual_validation: 'Check if dog has red collar' } }]
      } ]
    ]);

    // Mock VLM to fail on first attempt, then succeed on second (simulating self-healing fixing it)
    vi.spyOn(FileSystemObserver.prototype, 'waitForFileStabilization').mockResolvedValue(true);
    const vlmSpy = vi.spyOn(engine['perception']['vlmProvider'], 'inspectImage');
    vlmSpy.mockResolvedValueOnce({ isValid: false, feedback: 'Collar is blue' })
          .mockResolvedValueOnce({ isValid: true, feedback: 'Collar is red' });

    // Ensure Perception layer correctly triggers attemptRecovery by returning true on the second try
    vi.spyOn(engine['perception'], 'attemptRecovery').mockImplementation(async (opId, cb) => {
        await cb(opId); // Trigger the retry block
        return true; // Simulate successful recovery
    });

    const result = await engine.processIntent(intent, 'mock-ps');

    console.log("RESULT", result, "CALLS", psCalls, vlmSpy.mock.calls.length);
    expect(result.status).toBe('SUCCESS');
    // Provider called twice: original attempt + 1 recovery attempt
    expect(psCalls).toBe(2);
    // VLM called once (it triggered the recovery, which succeeded physically)
    expect(vlmSpy).toHaveBeenCalledTimes(2);
  });
});
