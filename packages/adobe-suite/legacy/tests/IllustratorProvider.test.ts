import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { IllustratorProvider } from '../src/providers/illustrator/IllustratorProvider.js';

describe('IllustratorProvider', () => {
    let provider: IllustratorProvider;

    beforeEach(() => {
        provider = new IllustratorProvider();
        provider['isConnected'] = true; // Mock connection
    });

    afterEach(() => {
        vi.restoreAllMocks();
    });

    it('should expose vector.generate_rig_layers and vector.style_transfer capabilities', () => {
        const caps = provider.capabilities();
        expect(caps.some(c => c.id === 'vector.generate_rig_layers')).toBe(true);
        expect(caps.some(c => c.id === 'vector.style_transfer')).toBe(true);
    });

    it('should execute vector.generate_rig_layers and return layers', async () => {
        const result = await provider.executeCapability('vector.generate_rig_layers', {
            input_file: '/path/to/flat_vector.svg'
        });

        expect(result.success).toBe(true);
        expect(result.observed_state.executed).toBe(true);
        expect(result.observed_state.layers_generated).toContain('+Head');
        expect(result.observed_state.layers_generated).toContain('+Right Arm');
    });

    it('should execute vector.style_transfer', async () => {
        const result = await provider.executeCapability('vector.style_transfer', {
            input_file: '/path/to/input.ai',
            style_reference: '/path/to/style.ai'
        });

        expect(result.success).toBe(true);
        expect(result.observed_state.executed).toBe(true);
        expect(result.observed_state.styled).toBe(true);
    });
});
