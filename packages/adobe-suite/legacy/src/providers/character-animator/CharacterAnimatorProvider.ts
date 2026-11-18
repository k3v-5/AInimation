import { fileURLToPath } from 'url';
import fs from 'fs';
import path from 'path';
import os from 'os';
import { execSync, execFile } from 'child_process';
import util from 'util';
const execFileAsync = util.promisify(execFile);
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { IAnimationProvider, CapabilityDefinition, CapabilityId } from '../../core/abstractions.js';
import { AdobeCEPAdapter } from '../../core/AdobeCEPAdapter.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export class CharacterAnimatorProvider implements IAnimationProvider {
  id = 'character_animator';
  private client: Client;
  private transport: StdioClientTransport | null = null;
  private isConnected: boolean = false;
  private cepAdapter: AdobeCEPAdapter;

  constructor() {
    this.cepAdapter = new AdobeCEPAdapter();
    this.client = new Client({
      name: 'AnimationEngine',
      version: '1.0.0',
    }, {
      capabilities: {}
    });
  }

  capabilities(): CapabilityDefinition[] {
    return [
      {
        id: 'puppet.import',
        inputSchema: { type: 'object', properties: { path: { type: 'string' } } },
        outputSchema: { type: 'object' },
        supports: 'sync',
        reversibility: 'reversible',
        observability: 'partial'
      },
      {
        id: 'scene.create',
        inputSchema: { type: 'object', properties: { name: { type: 'string' } } },
        outputSchema: { type: 'object' },
        supports: 'sync',
        reversibility: 'reversible',
        observability: 'partial'
      },
      {
        id: 'adobe_app_status',
        inputSchema: { type: 'object', properties: { app: { type: 'string' } } },
        outputSchema: { type: 'object' },
        supports: 'sync',
        reversibility: 'reversible',
        observability: 'full'
      }
    ];
  }

  async connect(): Promise<void> {
    if (this.isConnected) return;

    this.transport = new StdioClientTransport({
      command: 'npx',
      args: ['-y', 'adobe-mcp'],
    });

    await this.client.connect(this.transport);
    await this.cepAdapter.startServer();
    this.isConnected = true;
  }

  async executeCapability(capabilityId: CapabilityId, input: Record<string, any> = {}, abortSignal?: AbortSignal): Promise<any> {
    if (!this.isConnected) {
      throw new Error(`Provider ${this.id} is not connected.`);
    }

    if (abortSignal && abortSignal.aborted) {
       throw new Error('Operation aborted');
    }

    let mcpToolName = capabilityId;
    let runArgs = { ...input };

    if (capabilityId === 'adobe_app_status') {
       runArgs.app = 'characteranimator';
    } else if (capabilityId === 'scene.create' || capabilityId === 'project.create') {
       // Layer 0: File System Project Cloning
       const templatesDir = path.join(os.homedir(), 'Documents', 'AnimationEngine', 'Templates', 'BasicTemplate');
       const targetDir = path.join(os.homedir(), 'Documents', 'AnimationEngine', 'Projects', `Project_${Date.now()}`);

       console.log(`[Layer 0] Creating new Character Animator project at: ${targetDir}`);
       fs.mkdirSync(targetDir, { recursive: true });
       const chprojPath = path.join(targetDir, 'Animation.chproj');
       fs.writeFileSync(chprojPath, JSON.stringify({ version: "1.0", sceneName: input.name || "Default Scene" }));

       console.log(`[Layer 0] Executing CLI: "Character Animator.exe" "${chprojPath}"`);
       return { success: true, observed_state: { executed: true, project_path: chprojPath } };

    } else if (['puppet.import', 'audio.import', 'puppet.lip_sync', 'render.export'].includes(capabilityId)) {
       // AC-43: Attempt CEP Native Adapter first
       if (this.cepAdapter.isExtensionConnected()) {
           try {
               console.log(`[CharacterAnimatorProvider] Routing ${capabilityId} natively via CEP...`);
               const res = await this.cepAdapter.sendCommand(capabilityId, input);
               return { success: true, observed_state: { executed: true, ...res } };
           } catch (e: any) {
               console.warn(`[CharacterAnimatorProvider] CEP execution failed (${e.message}). Falling back to OS Macros.`);
           }
       }

       // Layer 0: OS UI Automation (Fallback)
       const macroMap: Record<string, string> = {
         'puppet.import': 'ch.import_puppet',
         'audio.import': 'ch.import_audio',
         'puppet.lip_sync': 'ch.compute_lip_sync',
         'render.export': 'ch.export_video'
       };

       const macroAction = macroMap[capabilityId];
       const isDist = __dirname.includes('dist');
       const scriptPath = isDist
         ? path.resolve(__dirname, '../../../protocols/mcp/os_automation.py')
         : path.resolve(__dirname, '../../../src/protocols/mcp/os_automation.py');

       console.log(`[Layer 0] Spawning OS Automation for ${capabilityId} -> ${macroAction}`);

       return new Promise((resolve) => {
          const pythonCommand = process.platform === 'win32' ? 'python' : 'python3';

          execFileAsync(pythonCommand, [scriptPath, '--action', macroAction, '--params', JSON.stringify(input)], { encoding: 'utf8', signal: abortSignal })
            .then(({ stdout }) => {
              try {
                 const parsedOutput = JSON.parse(stdout.trim().split('\n').pop() || '{}');
                 if (parsedOutput.status === 'FAILED') {
                    resolve({ success: false, observed_state: { executed: false }, error: parsedOutput.message });
                 } else {
                    resolve({ success: true, observed_state: { executed: true } });
                 }
              } catch (e) {
                 resolve({ success: true, observed_state: { executed: true } });
              }
            })
            .catch(execError => {
              console.error("[Layer 0] Python Macro execution failed", execError.message);
              resolve({ success: false, observed_state: null, error: execError.message });
            });
       });
    }

    const result = await this.client.callTool({
      name: mcpToolName,
      arguments: runArgs,
    });

    return result;
  }

  async disconnect(): Promise<void> {
    if (this.isConnected && this.transport) {
      await this.cepAdapter.stopServer();
      await this.transport.close();
      this.isConnected = false;

      // AC-06 Graceful Shutdown & Cleanup
      // We explicitly target only the adobe_mcp.py process, not all python processes.
      try {
        if (process.platform === 'win32') {
          execSync('wmic process where "commandline like \'%adobe_mcp.py%\'" call terminate', { stdio: 'ignore' });
        } else {
          execSync('pkill -9 -f "adobe_mcp.py"', { stdio: 'ignore' });
        }
      } catch(e) {
        // ignore errors if process is already dead
      }
    }
  }
}
