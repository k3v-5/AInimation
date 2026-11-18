import fs from 'fs';
import path from 'path';
import os from 'os';
import { execFileSync } from 'child_process';
import { IAnimationProvider, CapabilityDefinition, CapabilityId } from '../../core/abstractions.js';

export class BlenderProvider implements IAnimationProvider {
  id = 'blender_3d';

  capabilities(): CapabilityDefinition[] {
    return [
      {
        id: 'blender.execute_python',
        inputSchema: { type: 'object', properties: { script_content: { type: 'string' } } },
        outputSchema: { type: 'object' },
        supports: 'async',
        reversibility: 'irreversible',
        observability: 'full'
      }
    ];
  }

  async connect(): Promise<void> {
    return Promise.resolve();
  }

  async executeCapability(capabilityId: CapabilityId, input: Record<string, any> = {}, abortSignal?: AbortSignal): Promise<any> {
    if (abortSignal && abortSignal.aborted) {
       throw new Error('Operation aborted');
    }

    if (capabilityId === 'blender.execute_python') {
        const scriptContent = input.script_content;
        if (!scriptContent) {
             return { success: false, error: 'No script_content provided for Blender' };
        }

        try {
            const tempScriptPath = path.join(os.tmpdir(), `blender_script_${Date.now()}.py`);
            fs.writeFileSync(tempScriptPath, scriptContent);

            if (process.env.NODE_ENV === 'test') {
                return { success: true, observed_state: { executed: true, script: tempScriptPath } };
            }

            // Execute headless Blender
            console.log(`[BlenderProvider] Dispatching python script to Blender...`);
            // Assuming 'blender' is in the system PATH
            execFileSync('blender', ['-b', '-P', tempScriptPath], { encoding: 'utf8', stdio: 'pipe' });

            return { success: true, observed_state: { executed: true, script: tempScriptPath } };
        } catch (e: any) {
            console.error("[BlenderProvider] Execution failed:", e.message);
            return { success: false, error: e.message };
        }
    }

    return { success: false, error: 'Unknown capability mapped for BlenderProvider' };
  }

  async disconnect(): Promise<void> {
    return Promise.resolve();
  }
}
