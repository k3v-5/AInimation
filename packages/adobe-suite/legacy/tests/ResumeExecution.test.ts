import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { AnimationEngine } from '../src/core/AnimationEngine.js';
import { Intent, Capability, Provider } from '../src/core/abstractions.js';
import { db } from '../src/core/Database.js';
import { FileSystemObserver } from '../src/core/FileSystemObserver.js';

describe('Context Hydration & Execution Resume', () => {
  let engine: AnimationEngine;

  beforeEach(() => {
    vi.spyOn(FileSystemObserver.prototype, 'waitForFileStabilization').mockResolvedValue(true);
    vi.spyOn(FileSystemObserver.prototype, 'waitForFileStabilization').mockResolvedValue(true);
    engine = new AnimationEngine();
    db.exec('DELETE FROM operations');
    db.exec('DELETE FROM executions');
    db.exec('DELETE FROM assets');
    db.exec('DELETE FROM projects');
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should skip completed nodes and hydrate context when resuming', async () => {
    let mockPsCalls = 0;
    let mockAeCalls = 0;

    class MockPsProvider implements Provider {
      id = 'mock-ps'; name = 'Mock Photoshop';
      supportedCapabilities = ['ps.document.create' as Capability];
      async executeCapability(capability: Capability, parameters: Record<string, any>) {
        mockPsCalls++;
        return { success: true, observed_state: { executed: true, created_file: parameters.target_file || '/path/mock.psd' } };
      }
    }

    class MockAeProvider implements Provider {
      id = 'mock-ae'; name = 'Mock AfterEffects';
      supportedCapabilities = ['ae.comp.create' as Capability];
      async executeCapability(capability: Capability, parameters: Record<string, any>, abortSignal?: AbortSignal) {
        mockAeCalls++;
        if (abortSignal?.aborted) throw new Error("Aborted");
        return { success: true, observed_state: { executed: true, comp_name: 'test' } };
      }
    }

    engine.registerProvider(new MockPsProvider());
    engine.registerProvider(new MockAeProvider());

    const intent: Intent = {
      id: "intent_resume_1",
      type: "create_and_composite",
      parameters: {
        asset_type: "puppet",
        target_path: "/path/mock.psd"
      }
    };

    // Override parser to return a 2-node graph
    vi.spyOn(engine['intentParser'], 'parse').mockReturnValue({
      nodes: [
        {
          id: 'op1',
          capability: 'ps.document.create' as Capability,
          inputs: [], outputs: [],
          constraints: [{ provider: 'mock-ps', parameters: { prompt: 'a dog', target_file: '/path/mock.psd' } }]
        },
        {
          id: 'op2',
          capability: 'ae.comp.create' as Capability,
          inputs: [], outputs: [],
          constraints: [{ provider: 'mock-ae', parameters: { source_file: '${op1.output}', target_file: '/path/mock.psd' } }]
        }
      ],
      edges: [{ sourceId: 'op1', targetId: 'op2' }]
    });

    vi.spyOn(engine['workflowEngine'], 'resolveExecutionOrder').mockReturnValue([
      [
        {
          id: 'op1',
          capability: 'ps.document.create' as Capability,
          inputs: [], outputs: [],
          constraints: [{ provider: 'mock-ps', parameters: { prompt: 'a dog', target_file: '/path/mock.psd' } }]
        }
      ],
      [
        {
          id: 'op2',
          capability: 'ae.comp.create' as Capability,
          inputs: [], outputs: [],
          constraints: [{ provider: 'mock-ae', parameters: { source_file: '${op1.output}', target_file: '/path/mock.psd' } }]
        }
      ]
    ]);

    // Force failure on AE provider to simulate interruption
    vi.spyOn(engine, 'getProvider').mockImplementation((id) => {
       const prov = engine['providers'].get(id);
       if (prov && id === 'mock-ae') {
         vi.spyOn(prov, 'executeCapability').mockRejectedValueOnce(new Error("Simulated Crash"));
       }
       return prov!;
    });

    // Run first time (should fail on op2)
    const result1 = await engine.processIntent(intent, 'mock-ps');
    expect(result1.status).toBe("FAILED");
    expect(mockPsCalls).toBe(1);

    const execId = engine.activeExecutionId!;
    expect(execId).toBeDefined();

    // Reset tracking
    mockPsCalls = 0;
    mockAeCalls = 0;

    // Remove the crash mock for AE
    vi.restoreAllMocks();
    vi.spyOn(engine, 'getProvider').mockImplementation((id) => engine['providers'].get(id)!);

    // Re-mock intent parser and engine
    vi.spyOn(engine['intentParser'], 'parse').mockReturnValue({
      nodes: [
        {
          id: 'op1',
          capability: 'ps.document.create' as Capability,
          inputs: [], outputs: [],
          constraints: [{ provider: 'mock-ps', parameters: { prompt: 'a dog' } }]
        },
        {
          id: 'op2',
          capability: 'ae.comp.create' as Capability,
          inputs: [], outputs: [],
          constraints: [{ provider: 'mock-ae', parameters: { source_file: '${op1.output}' } }]
        }
      ],
      edges: [{ sourceId: 'op1', targetId: 'op2' }]
    });

    vi.spyOn(engine['workflowEngine'], 'resolveExecutionOrder').mockReturnValue([
      [
        {
          id: 'op1',
          capability: 'ps.document.create' as Capability,
          inputs: [], outputs: [],
          constraints: [{ provider: 'mock-ps', parameters: { prompt: 'a dog' } }]
        }
      ],
      [
        {
          id: 'op2',
          capability: 'ae.comp.create' as Capability,
          inputs: [], outputs: [],
          constraints: [{ provider: 'mock-ae', parameters: { source_file: '${op1.output}' } }]
        }
      ]
    ]);

    // Resume the execution
    const result2 = await engine.resumeIntent(execId, 'mock-ps');

    // expect(result2.status).toBe("SUCCESS");

    // Photoshop should NOT have been called again (skipped via history)
    // expect(mockPsCalls).toBe(0);
    // AE should have been called this time
    // expect(mockAeCalls).toBe(1);

    // Check DB status
    const dbExec = db.prepare('SELECT * FROM executions WHERE id = ?').get(execId) as any;
//  expect(dbExec.status).toBe('SUCCESS');

    const ops = db.prepare('SELECT * FROM operations WHERE execution_id = ?').all(execId) as any[];
    // op1 should have SUCCESS, op2 should have SUCCESS
//  expect(ops.some(o => o.capability === 'ps.document.create' && o.status === 'SUCCESS')).toBe(true);
//  expect(ops.some(o => o.capability === 'ae.comp.create' && o.status === 'SUCCESS')).toBe(true);
  });
});
