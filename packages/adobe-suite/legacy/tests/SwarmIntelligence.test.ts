import { describe, it, expect } from 'vitest';
import { SwarmDirector } from '../src/ai/swarm/SwarmDirector.js';

describe('Swarm Intelligence Routing', () => {
    it('should route design prompts to DesignAgent', async () => {
        const director = new SwarmDirector();
        const intent = await director.routeTask('Please draw a new dog in photoshop');
        expect(intent.type).toBe('ps.document.create');
        expect(intent.parameters.visual_validation).toBeDefined();
    });

    it('should route animation/rigging prompts to RiggingAgent', async () => {
        const director = new SwarmDirector();
        const intent = await director.routeTask('Rig the character and animate it in After Effects');
        expect(intent.type).toBe('ae.comp.create');
    });

    it('should route audio/TTS prompts to AudioAgent', async () => {
        const director = new SwarmDirector();
        const intent = await director.routeTask('Generate a voiceover saying hello using tts');

        expect(intent.type).toBe('audio.generate_tts');
        expect(intent.parameters.text).toBe('Generate a voiceover saying hello using tts');
    });

    it('should route 3D/Blender prompts to BlenderAgent', async () => {
        const director = new SwarmDirector();
        const intent = await director.routeTask('Create a 3d model in blender');

        expect(intent.type).toBe('blender.execute_python');
        expect(intent.parameters.script_content).toBeDefined();
    });
    it('should route using an LLM semantically if provided', async () => {
        const mockLLM = {
            prompt: async (messages: any[]) => {
                // Ignore the actual prompt and force a classification response to '3d'
                return { type: 'message', content: '3d' };
            }
        };

        const director = new SwarmDirector(mockLLM as any);
        // The user input doesn't contain the word 'blender' or '3d', but the LLM classified it as 3d.
        const intent = await director.routeTask('Make a polygon sphere for my game');

        expect(intent.type).toBe('blender.execute_python');
    });
});
