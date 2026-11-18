import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { AnimationEngine } from '../src/core/AnimationEngine.js';
import { Intent, Capability, Provider } from '../src/core/abstractions.js';
import { db } from '../src/core/Database.js';
import * as hashUtils from '../src/core/utils/hash.js';
import fs from 'fs';

describe('Asset Versioning & Hash Invalidation', () => {
  let engine: AnimationEngine;

  beforeEach(() => {
    engine = new AnimationEngine();
    db.exec('DELETE FROM asset_dependencies');
    db.exec('DELETE FROM operations');
    db.exec('DELETE FROM executions');
    db.exec('DELETE FROM assets');
    db.exec('DELETE FROM projects');

    // Default mock: file exists and hash is 'hash_1'
    vi.spyOn(fs, 'existsSync').mockReturnValue(true);
    vi.spyOn(hashUtils, 'calculateFileHash').mockReturnValue('hash_1');
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should execute node if physical hash differs from DB (Dirty State)', async () => {
    let mockPsCalls = 0;

    class MockPsProvider implements Provider {
      id = 'mock-ps'; name = 'Mock Photoshop';
      supportedCapabilities = ['ps.document.create' as Capability];
      async executeCapability(capability: Capability, parameters: Record<string, any>) {
        mockPsCalls++;
        return { success: true, observed_state: { executed: true, created_file: '/path/mock.psd' } };
      }
    }

    engine.registerProvider(new MockPsProvider());

    const intent: Intent = {
      id: "intent_ver_1",
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
          constraints: [{ provider: 'mock-ps', parameters: { input_file: '/path/mock.psd', prompt: 'a dog' } }]
        }
      ],
      edges: []
    });

    vi.spyOn(engine['workflowEngine'], 'resolveExecutionOrder').mockReturnValue([
      [ { id: 'op1', capability: 'ps.document.create' as Capability, inputs: [], outputs: [], constraints: [{ provider: 'mock-ps', parameters: { input_file: '/path/mock.psd', prompt: 'a dog' } }] } ]
    ]);

    // Insert an old hash into DB to simulate modification
    const proj = engine['projectManager'].createProject('Test Project');
    engine['projectManager'].saveAsset({
       id: 'art_test',
       project_id: proj.id,
       type: 'puppet',
       local_path: '/path/mock.psd',
       hash: 'old_hash_0',
       created_at: new Date().toISOString()
    });

    const result = await engine.processIntent(intent, 'mock-ps');

    expect(result.status).toBe('SUCCESS');
    // Because current hash is 'hash_1' but DB was 'old_hash_0', it should NOT skip and execute Photoshop
    expect(mockPsCalls).toBe(1);

    const updatedAsset = engine['projectManager'].getAssetByPath('/path/mock.psd');
    expect(updatedAsset?.hash).toBe('hash_1');
  });

  it('should skip node if physical hash matches DB (Clean State)', async () => {
    let mockPsCalls = 0;

    class MockPsProvider implements Provider {
      id = 'mock-ps'; name = 'Mock Photoshop';
      supportedCapabilities = ['ps.document.create' as Capability];
      async executeCapability(capability: Capability, parameters: Record<string, any>) {
        mockPsCalls++;
        return { success: true, observed_state: { executed: true, created_file: '/path/mock.psd' } };
      }
    }

    engine.registerProvider(new MockPsProvider());

    const intent: Intent = {
      id: "intent_ver_2",
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
          constraints: [{ provider: 'mock-ps', parameters: { input_file: '/path/mock.psd', prompt: 'a dog' } }]
        }
      ],
      edges: []
    });

    vi.spyOn(engine['workflowEngine'], 'resolveExecutionOrder').mockReturnValue([
      [ { id: 'op1', capability: 'ps.document.create' as Capability, inputs: [], outputs: [], constraints: [{ provider: 'mock-ps', parameters: { input_file: '/path/mock.psd', prompt: 'a dog' } }] } ]
    ]);

    // Insert matching hash into DB to simulate clean state
    const proj2 = engine['projectManager'].createProject('Test Project 2');
    engine['projectManager'].saveAsset({
       id: 'art_test',
       project_id: proj2.id,
       type: 'puppet',
       local_path: '/path/mock.psd',
       hash: 'hash_1',
       created_at: new Date().toISOString()
    });

    const result = await engine.processIntent(intent, 'mock-ps');

    expect(result.status).toBe('SUCCESS');
    // Because current hash is 'hash_1' and DB is 'hash_1', it SHOULD skip
    expect(mockPsCalls).toBe(0);
  });
});
