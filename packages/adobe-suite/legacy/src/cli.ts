import readlineSync from 'readline-sync';
import Spinnies from 'spinnies';
import { AnimationEngine } from './core/AnimationEngine.js';
import { AgentPlanner, ILLMProvider, LLMResponse } from './ai/AgentPlanner.js';
import { CharacterAnimatorProvider } from './providers/character-animator/CharacterAnimatorProvider.js';
import { PhotoshopProvider } from './providers/photoshop/PhotoshopProvider.js';
import { IllustratorProvider } from './providers/illustrator/IllustratorProvider.js';
import { PremiereProProvider } from './providers/premiere-pro/PremiereProProvider.js';
import { AfterEffectsProvider } from './providers/after-effects/AfterEffectsProvider.js';
import { BlenderProvider } from './providers/blender/BlenderProvider.js';
import { AudioProvider } from './providers/audio/AudioProvider.js';
import { MediaEncoderProvider } from './providers/media-encoder/MediaEncoderProvider.js';
import { cliLogger } from './core/Logger.js';

import { SwarmDirector } from './ai/swarm/SwarmDirector.js';

// Setup Mock LLM for the CLI (In a real app, this would connect to Claude/OpenAI)
// We will simulate the Agent returning a proper JSON structure based on the prompt for testing the CLI.
class CLI_LLM implements ILLMProvider {
  async prompt(messages: { role: string; content: string }[]): Promise<LLMResponse> {
    const userMsg = messages[messages.length - 1].content.toLowerCase();

    // Simulating reflection loop or clarification if prompt is empty
    if (userMsg.trim() === '') {
       return { type: 'message', content: 'Please provide an animation request.' };
    }

    // LLM Classification for SwarmDirector hook
    if (userMsg.includes("classify the following user request")) {
        if (userMsg.includes('draw') || userMsg.includes('psd')) return { type: 'message', content: 'design' };
        if (userMsg.includes('rig') || userMsg.includes('animate')) return { type: 'message', content: 'rigging' };
        if (userMsg.includes('voice') || userMsg.includes('tts')) return { type: 'message', content: 'audio' };
        if (userMsg.includes('3d') || userMsg.includes('blender')) return { type: 'message', content: '3d' };
        return { type: 'message', content: 'generic' };
    }

    // Return a mocked E2E JSON payload
    return {
      type: 'tool_call',
      tool_name: 'execute_intent',
      tool_payload: {
        intent_id: `cli_intent_${Date.now()}`,
        action: 'animation.sequence',
        parameters: {
          scene: { name: 'CLI Generated Scene' },
          characters: [],
          actions: [
            { type: 'ps_create', provider: 'photoshop', width: 1080, height: 1080 },
            { type: 'ps_export', provider: 'photoshop', expected_layers: ['+Head', 'Body'] },
            { type: 'puppet_import', provider: 'character_animator', input_file: '${action_ps_export_1.output}' },
            { type: 'pose', provider: 'character_animator' },
            { type: 'render', provider: 'character_animator' },
            { type: 'ae_render', provider: 'after_effects', input_file: '${action_render_4.output}' }
          ]
        },
        target_provider: 'character_animator'
      }
    };
  }
}

async function startCLI() {
  console.clear();
  console.log("=========================================");
  console.log("🎬 Animation Director OS - Agentic CLI ");
  console.log("=========================================\n");

const spinnies = new Spinnies();
  spinnies.add('init', { text: 'Initializing Animation Engine...' });
  const engine = new AnimationEngine();

  // DAG Visualization & Telemetry Setup
  engine.on('operation_status', (data) => {
    const key = data.id;
    try {
      if (data.status === 'PLANNED') {
         spinnies.add(key, { text: `[${data.provider}] ${data.capability} - Queued` });
      } else if (data.status === 'EXECUTING') {
         try {
           spinnies.update(key, { text: `[${data.provider}] ${data.capability} - Executing (Attempt ${data.attempt || 1})`, color: 'yellow' });
         } catch(e) {
           spinnies.add(key, { text: `[${data.provider}] ${data.capability} - Executing (Attempt ${data.attempt || 1})`, color: 'yellow' });
         }
      } else if (data.status === 'SUCCESS') {
         spinnies.succeed(key, { text: `[${data.provider}] ${data.capability} - Success` });
      } else if (data.status === 'FAILED') {
         spinnies.fail(key, { text: `[${data.provider}] ${data.capability} - Failed: ${data.error}` });
      } else if (data.status === 'DIVERGED') {
         spinnies.update(key, { text: `[${data.provider}] ${data.capability} - State Diverged: ${data.error}`, color: 'red' });
      }
    } catch(e) {}
  });

  engine.on('operation_recovery', (data) => {
    const key = data.id;
    try {
       spinnies.update(key, { text: `[${data.capability}] Self-healing active, attempting recovery...`, color: 'magenta' });
    } catch(e) {}
  });

  engine.on('operation_recovery', (data) => {
    const key = data.id;
    try {
       spinnies.update(key, { text: `[${data.capability}] Self-healing active, attempting recovery...`, color: 'magenta' });
    } catch(e) {}
  });


  engine.registerProvider(new CharacterAnimatorProvider());
  engine.registerProvider(new PhotoshopProvider());
  engine.registerProvider(new IllustratorProvider());
  engine.registerProvider(new PremiereProProvider());
  engine.registerProvider(new AfterEffectsProvider());
  engine.registerProvider(new BlenderProvider());
  engine.registerProvider(new AudioProvider());
  engine.registerProvider(new MediaEncoderProvider());

  await engine.connectAll();

  spinnies.succeed('init', { text: 'Engine Initialized and Providers Connected.\n' });

  const llm = new CLI_LLM();
  const swarmDirector = new SwarmDirector(llm);
  const planner = new AgentPlanner(llm, async (payload: any) => {
    // We bind the engine's processIntent to the planner
    return engine.processIntent(payload, payload.target_provider);
  });

  let running = true;

  while (running) {
    const input = readlineSync.question('\nDirector> ');

    if (input.toLowerCase() === '/exit') {
      running = false;
      break;
    }

    if (input.trim() === '') continue;

    cliLogger.info(`User requested: ${input}`);
    spinnies.add('agent', { text: 'Agent is thinking...' });

    try {
      // In a real scenario, this await blocks. The TUI DAG updates will be handled
      // by event emitters in the engine. For now, we simulate the wait.
      const result = await planner.handleUserRequest(input);
      spinnies.succeed('agent', { text: result });
      cliLogger.info(`Agent responded successfully`);
    } catch (e: any) {
      spinnies.fail('agent', { text: `Agent encountered a critical error: ${e.message}` });
      cliLogger.error(`Agent failure`, { error: e.message });
    }
  }

  console.log('\nShutting down gracefully...');
  await engine.disconnectAll();
  process.exit(0);
}

// Handle SIGINT for graceful shutdown during the REPL loop
process.on('SIGINT', () => {
  console.log('\nCaught interrupt signal. Use /exit to leave cleanly or press Ctrl+C again.');
  process.exit(0);
});

startCLI().catch(e => {
  console.error(e);
  process.exit(1);
});
