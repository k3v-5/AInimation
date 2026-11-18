import { describe, it, expect } from 'vitest';
import { SwarmDirector } from '../src/ai/swarm/SwarmDirector.js';
import { IntentParser } from '../src/core/IntentParser.js';
import { AnimationEngine } from '../src/core/AnimationEngine.js';
import { BlenderProvider } from '../src/providers/blender/BlenderProvider.js';

describe('Blender Complete Flow Validation', () => {
    it('should route, parse, and execute a Blender intent successfully', async () => {
        // 1. SwarmDirector routing
        const director = new SwarmDirector();
        const intent = await director.routeTask('Create a 3d model of a cube in blender');

        expect(intent.type).toBe('blender.execute_python');
        expect(intent.parameters.script_content).toContain('import bpy');

        // 2. Intent Parsing (Single node fallback graph)
        const parser = new IntentParser();
        const graph = parser.parse(intent, 'blender_3d');

        expect(graph.nodes.length).toBe(1);
        expect(graph.nodes[0].capability).toBe('blender.execute_python');
        expect(graph.nodes[0].constraints[0].provider).toBe('blender_3d');

        // 3. Engine Execution
        const engine = new AnimationEngine();
        engine.registerProvider(new BlenderProvider());
        await engine.connectAll();

        const results = await engine.processIntent(intent, 'blender_3d');

        expect(results).toBeDefined();
        expect(results.status).toBe('SUCCESS');

        await engine.disconnectAll();
    });
});
