import { DesignAgent } from './DesignAgent.js';
import { RiggingAgent } from './RiggingAgent.js';
import { AudioAgent } from './AudioAgent.js';
import { BlenderAgent } from './BlenderAgent.js';
import { Intent } from '../../core/abstractions.js';
import { ILLMProvider } from '../AgentPlanner.js';

export class SwarmDirector {
    private designAgent: DesignAgent;
    private riggingAgent: RiggingAgent;
    private audioAgent: AudioAgent;
    private blenderAgent: BlenderAgent;
    private llm: ILLMProvider | null;

    constructor(llm?: ILLMProvider) {
        this.designAgent = new DesignAgent();
        this.riggingAgent = new RiggingAgent();
        this.audioAgent = new AudioAgent();
        this.blenderAgent = new BlenderAgent();
        this.llm = llm || null;
    }

    public async routeTask(userInput: string): Promise<Intent> {
        console.log(`[SwarmDirector] Routing task: "${userInput}"`);

        let route = 'generic';

        if (this.llm) {
             const prompt = `Classify the following user request into exactly one of these domains: 'design' (2D drawing/generation), 'rigging' (animation/compositing in AE), 'audio' (voice/TTS), '3d' (blender/3d modeling). Reply with ONLY the single domain word.\n\nRequest: "${userInput}"`;
             const response = await this.llm.prompt([{ role: 'user', content: prompt }]);
             if (response.type === 'message' && response.content) {
                 route = response.content.trim().toLowerCase();
                 console.log(`[SwarmDirector] LLM Router classified task as: ${route}`);
             }
        } else {
            // Heuristic Fallback
            if (userInput.toLowerCase().includes('draw') || userInput.toLowerCase().includes('photoshop') || userInput.toLowerCase().includes('create character')) {
                route = 'design';
            } else if (userInput.toLowerCase().includes('rig') || userInput.toLowerCase().includes('after effects') || userInput.toLowerCase().includes('animate')) {
                route = 'rigging';
            } else if (userInput.toLowerCase().includes('voice') || userInput.toLowerCase().includes('tts') || userInput.toLowerCase().includes('speak')) {
                route = 'audio';
            } else if (userInput.toLowerCase().includes('3d') || userInput.toLowerCase().includes('blender') || userInput.toLowerCase().includes('model')) {
                route = '3d';
            }
        }

        if (route.includes('design')) return this.designAgent.handleAssetGeneration(userInput);
        if (route.includes('rigging')) return this.riggingAgent.handleRiggingTask(userInput);
        if (route.includes('audio')) return this.audioAgent.handleAudioTask(userInput);
        if (route.includes('3d')) return this.blenderAgent.handle3DTask(userInput);

        return {
            id: `intent_swarm_${Date.now()}`,
            type: 'generic_task',
            parameters: {}
        };
    }
}
