import { test, expect, describe, vi } from 'vitest';
import { AnimationEngine } from '../src/core/AnimationEngine.js';
import { IAnimationProvider, CapabilityDefinition, CapabilityId } from '../src/core/abstractions.js';
import { cliLogger } from '../src/core/Logger.js';

class MockEventProvider implements IAnimationProvider {
  id = 'mock_events';
  capabilities(): CapabilityDefinition[] { return [{ id: 'mock.event_test', inputSchema: {}, outputSchema: {}, supports: 'sync', reversibility: 'reversible', observability: 'full' }]; }
  async connect() {}
  async disconnect() {}
  async executeCapability(capabilityId: CapabilityId, input: Record<string, any>): Promise<any> {
    return { success: true };
  }
}

describe('Engine Telemetry and Logging', () => {
  test('Emits operation_status events correctly during execution', async () => {
    const engine = new AnimationEngine();
    engine.registerProvider(new MockEventProvider());

    const intent = {
      id: 'intent_events',
      type: 'mock.event_test',
      parameters: {}
    };

    const emittedStatuses: string[] = [];

    engine.on('operation_status', (data) => {
       emittedStatuses.push(data.status);
    });

    await engine.processIntent(intent, 'mock_events');

    // We expect PLANNED -> EXECUTING -> SUCCESS
    expect(emittedStatuses).toContain('PLANNED');
    expect(emittedStatuses).toContain('EXECUTING');
    expect(emittedStatuses).toContain('SUCCESS');
  });

  test('CLI Logger does not throw when logging', () => {
    // We just ensure calling the logger methods works and doesn't crash the test runner.
    // The actual file write is handled by pino internally.
    expect(() => {
       cliLogger.info('Test Info Log');
       cliLogger.warn('Test Warn Log', { data: 123 });
       cliLogger.error('Test Error Log', new Error('Test'));
    }).not.toThrow();
  });
});
