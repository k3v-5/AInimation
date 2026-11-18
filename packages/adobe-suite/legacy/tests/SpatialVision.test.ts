import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { AnimationEngine } from '../src/core/AnimationEngine.js';
import { Intent, Capability, Provider } from '../src/core/abstractions.js';
import { FileSystemObserver } from '../src/core/FileSystemObserver.js';
import { db } from '../src/core/Database.js';

describe('Spatial Vision Correction (VLM + Swarm)', () => {
  let engine: AnimationEngine;

  beforeEach(() => {
    engine = new AnimationEngine();
    db.exec('DELETE FROM asset_dependencies');
    db.exec('DELETE FROM operations');
    db.exec('DELETE FROM executions');
    db.exec('DELETE FROM assets');
    db.exec('DELETE FROM projects');
    vi.spyOn(FileSystemObserver.prototype, 'waitForFileStabilization').mockResolvedValue(true);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should generate JSX to correct spatial misalignment dynamically', async () => {
    let mockPsCalls = 0;
    let aeJsxScripts: string[] = [];

    class MockPsProvider implements Provider {
      id = 'mock-ps'; name = 'Mock Photoshop';
      supportedCapabilities = ['ps.document.create' as Capability];
      async executeCapability(capability: Capability, parameters: Record<string, any>) {
        mockPsCalls++;
        return { success: true, observed_state: { executed: true, created_file: parameters.target_file || '/path/mock.psd' } };
      }
    }

    class MockAeProvider implements Provider {
      id = 'after_effects'; name = 'Mock After Effects';
      supportedCapabilities = ['ae.execute_jsx' as Capability];
      async executeCapability(capability: Capability, parameters: Record<string, any>) {
        if (parameters.script_content) {
            aeJsxScripts.push(parameters.script_content);
        }
        return { success: true, observed_state: { executed: true } };
      }
    }

    engine.registerProvider(new MockPsProvider());
    engine.registerProvider(new MockAeProvider());

    // Create a manual node structure directly to feed to resolveExecutionOrder
    const mockNodes = [
      [ {
          id: 'op1', capability: 'ps.document.create' as Capability, inputs: [], outputs: [],
          constraints: [{ provider: 'mock-ps', parameters: { target_file: '/path/mock.psd', spatial_validation: 'misaligned_eye' } }]
      } ]
    ];
    vi.spyOn(engine['workflowEngine'], 'resolveExecutionOrder').mockReturnValue(mockNodes);

    // Mock VLM spatial validation
    // The first time it should fail with an offset, the second time it should pass
    const vlmSpy = vi.spyOn(engine['perception']['vlmProvider'], 'inspectImageSpatial');
    vlmSpy.mockResolvedValueOnce({ found: true, x: 100, y: -50, feedback: 'Eye is misaligned' })
          .mockResolvedValueOnce({ found: true, x: 0, y: 0, feedback: 'Eye is aligned' });

    // Mock attemptRecovery because visual and spatial validation inside attemptRecovery need to pass.
    vi.spyOn(engine['perception'], 'attemptRecovery').mockImplementation(async (opId, cb) => {
        await cb(opId); // Trigger the retry block
        return true; // Simulate successful recovery
    });

    const intent: Intent = { id: "intent_vis_2", type: "create", parameters: {} };
    const result = await engine.processIntent(intent, 'mock-ps');

    console.log("RESULT:", result);
    expect(result.status).toBe('SUCCESS');
    expect(mockPsCalls).toBe(2);
    expect(vlmSpy).toHaveBeenCalledTimes(2);

    expect(aeJsxScripts.length).toBe(1);
    expect(aeJsxScripts[0]).toContain('layer.property("Position").setValue([currentPos[0] + (100), currentPos[1] + (-50)]);');
  });
});
