import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { IAnimationProvider, CapabilityDefinition, CapabilityId } from '../../core/abstractions.js';

export class IllustratorProvider implements IAnimationProvider {
  id = 'illustrator';
  private client: Client;
  private transport: StdioClientTransport | null = null;
  private isConnected: boolean = false;

  constructor() {
    this.client = new Client({
      name: 'AnimationEngine-AI',
      version: '1.0.0',
    }, {
      capabilities: {}
    });
  }

  capabilities(): CapabilityDefinition[] {
    return [
      {
        id: 'ai.document.create',
        inputSchema: { type: 'object' },
        outputSchema: { type: 'object' },
        supports: 'async',
        reversibility: 'reversible',
        observability: 'full'
      },
      {
        id: 'vector.generate_rig_layers',
        inputSchema: { type: 'object', properties: { input_file: { type: 'string' } } },
        outputSchema: { type: 'object' },
        supports: 'async',
        reversibility: 'reversible',
        observability: 'full'
      },
      {
        id: 'vector.style_transfer',
        inputSchema: { type: 'object', properties: { input_file: { type: 'string' }, style_reference: { type: 'string' } } },
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
    if (!this.isConnected) throw new Error(`Provider ${this.id} is not connected.`);
    if (abortSignal && abortSignal.aborted) throw new Error('Operation aborted');

    if (capabilityId === 'ai.document.create') {
        const result = await this.client.callTool({
            name: 'adobe_ai_new_document',
            arguments: {
               width: input.width || 1920,
               height: input.height || 1080
            }
        });
        if (result.isError) return { success: false, observed_state: null, error: "AI Native Error: " + JSON.stringify(result.content) };
        return { success: true, observed_state: { executed: true } };
    }

    if (capabilityId === 'vector.generate_rig_layers') {
        console.log(`[IllustratorProvider] Generating rig layers for ${input.input_file}`);
        // Mocking the complex ExtendScript call that would perform logical separation
        return { success: true, observed_state: { executed: true, layers_generated: ['+Head', '+Right Arm', '+Left Eye', 'Body'] } };
    }

    if (capabilityId === 'vector.style_transfer') {
        console.log(`[IllustratorProvider] Applying style transfer on ${input.input_file} using reference ${input.style_reference}`);
        // Mocking style transfer
        return { success: true, observed_state: { executed: true, styled: true } };
    }

    return { success: false, error: 'Unknown capability mapped for AI' };
  }

  async disconnect(): Promise<void> {
    if (this.isConnected && this.transport) {
      await this.transport.close();
      this.isConnected = false;
    }
  }
}
