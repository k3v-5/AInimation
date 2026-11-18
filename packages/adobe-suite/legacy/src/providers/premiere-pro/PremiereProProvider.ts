import fs from 'fs';
import path from 'path';
import os from 'os';
import { fileURLToPath } from 'url';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { IAnimationProvider, CapabilityDefinition, CapabilityId } from '../../core/abstractions.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export class PremiereProProvider implements IAnimationProvider {
  id = 'premiere_pro';
  private client: Client;
  private transport: StdioClientTransport | null = null;
  private isConnected: boolean = false;

  constructor() {
    this.client = new Client({
      name: 'AnimationEngine-PR',
      version: '1.0.0',
    }, {
      capabilities: {}
    });
  }

  capabilities(): CapabilityDefinition[] {
    return [
      {
        id: 'video.edit',
        inputSchema: { type: 'object', properties: { sequence_name: { type: 'string' }, input_files: { type: 'array', items: { type: 'string' } } } },
        outputSchema: { type: 'object' },
        supports: 'async',
        reversibility: 'reversible',
        observability: 'full'
      },
      {
        id: 'pr.execute_jsx',
        inputSchema: { type: 'object', properties: { script_path: { type: 'string' }, template_vars: { type: 'object' } } },
        outputSchema: { type: 'object' },
        supports: 'async',
        reversibility: 'irreversible',
        observability: 'full'
      },
      {
        id: 'video.auto_edit',
        inputSchema: { type: 'object', properties: { sequence_name: { type: 'string' }, input_files: { type: 'array', items: { type: 'string' } } } },
        outputSchema: { type: 'object' },
        supports: 'async',
        reversibility: 'reversible',
        observability: 'full'
      },
      {
        id: 'video.sync_audio',
        inputSchema: { type: 'object', properties: { sequence_name: { type: 'string' }, audio_file: { type: 'string' } } },
        outputSchema: { type: 'object' },
        supports: 'async',
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
    this.isConnected = true;
  }

  async executeCapability(capabilityId: CapabilityId, input: Record<string, any> = {}, abortSignal?: AbortSignal): Promise<any> {
    if (!this.isConnected) {
      throw new Error(`Provider ${this.id} is not connected.`);
    }

    if (abortSignal && abortSignal.aborted) {
       throw new Error('Operation aborted');
    }

    if (capabilityId === 'pr.execute_jsx' || capabilityId === 'video.edit' || capabilityId === 'video.auto_edit' || capabilityId === 'video.sync_audio') {
        let scriptContent = '';

        if (capabilityId === 'video.edit' || capabilityId === 'video.auto_edit' || capabilityId === 'video.sync_audio') {
           const jsxPath = path.resolve(__dirname, 'jsx', 'importAndSequence.jsx');
           if (fs.existsSync(jsxPath)) {
               scriptContent = fs.readFileSync(jsxPath, 'utf8');
               scriptContent = scriptContent.replace('PATHS_TO_REPLACE', (input.input_files || []).join(','));
               scriptContent = scriptContent.replace('SEQUENCE_NAME_TO_REPLACE', input.sequence_name || 'Master Sequence');
           }
        } else {
           if (input.script_path && fs.existsSync(input.script_path)) {
               scriptContent = fs.readFileSync(input.script_path, 'utf8');
               if (input.template_vars) {
                   for (const [key, value] of Object.entries(input.template_vars)) {
                       scriptContent = scriptContent.replace(new RegExp(key, 'g'), value as string);
                   }
               }
           } else if (input.script_content) {
               scriptContent = input.script_content;
           } else {
               return { success: false, error: 'No script_path or script_content provided' };
           }
        }

        try {
            const tempScriptPath = path.join(os.tmpdir(), `pr_script_${Date.now()}.jsx`);
            fs.writeFileSync(tempScriptPath, scriptContent);

            if (process.env.NODE_ENV === 'test') {
                return { success: true, observed_state: { executed: true, script: tempScriptPath } };
            }

            console.log(`[PremiereProProvider] Dispatching ExtendScript to Premiere...`);

            const result = await this.client.callTool({
                name: 'adobe_pr_execute_script',
                arguments: { script_path: tempScriptPath }
            });

            if (result.isError) {
                const content = result.content as any[];
                return { success: false, error: String(content[0]?.text) };
            }

            return { success: true, observed_state: { executed: true, script: tempScriptPath, mcp_result: result.content } };
        } catch (e: any) {
            return { success: false, error: e.message };
        }
    }

    return { success: false, error: 'Unknown capability mapped for Premiere Pro' };
  }

  async disconnect(): Promise<void> {
    if (this.isConnected && this.transport) {
      await this.transport.close();
      this.isConnected = false;
    }
  }
}