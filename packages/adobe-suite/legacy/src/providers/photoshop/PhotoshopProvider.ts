import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { IAnimationProvider, CapabilityDefinition, CapabilityId } from '../../core/abstractions.js';

export class PhotoshopProvider implements IAnimationProvider {
  id = 'photoshop';
  private client: Client;
  private transport: StdioClientTransport | null = null;
  private isConnected: boolean = false;

  constructor() {
    this.client = new Client({
      name: 'AnimationEngine-PS',
      version: '1.0.0',
    }, {
      capabilities: {}
    });
  }

  capabilities(): CapabilityDefinition[] {
    return [
      {
        id: 'ps.document.create',
        inputSchema: { type: 'object', properties: { width: { type: 'number' }, height: { type: 'number' } } },
        outputSchema: { type: 'object' },
        supports: 'async',
        reversibility: 'reversible',
        observability: 'full'
      },
      {
        id: 'ps.layer.setup',
        inputSchema: { type: 'object', properties: { layer_name: { type: 'string' } } },
        outputSchema: { type: 'object' },
        supports: 'async',
        reversibility: 'reversible',
        observability: 'full'
      },
      {
        id: 'ps.document.export',
        inputSchema: { type: 'object', properties: { target_file: { type: 'string' } } },
        outputSchema: { type: 'object' },
        supports: 'async',
        reversibility: 'irreversible',
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

    if (capabilityId === 'ps.document.create') {
        const result = await this.client.callTool({
            name: 'adobe_ps_new_document',
            arguments: {
               width: input.width || 1920,
               height: input.height || 1080
            }
        });
        if (result.isError) return { success: false, observed_state: null, error: "PS Native Error: " + JSON.stringify(result.content) };
        return { success: true, observed_state: { executed: true } };
    }

    if (capabilityId === 'ps.layer.setup') {
        const result = await this.client.callTool({
            name: 'adobe_ps_layers',
            arguments: {
               action: 'create',
               layer_name: input.layer_name || '+New Layer'
            }
        });
        if (result.isError) return { success: false, observed_state: null, error: "PS Native Error: " + JSON.stringify(result.content) };
        return { success: true, observed_state: { executed: true } };
    }

    if (capabilityId === 'ps.document.export') {
        // First get layer data to report back to perception layer
        let observedLayers: string[] = [];
        try {
           const layerResult: any = await this.client.callTool({
              name: 'adobe_run_jsx',
              arguments: {
                 app: 'photoshop',
                 code: 'var doc = app.activeDocument; var layers = []; for(var i=0; i<doc.layers.length; i++) { layers.push(doc.layers[i].name); }; JSON.stringify(layers);'
              }
           });
           if (!layerResult.isError && layerResult.content && layerResult.content[0]?.text) {
              observedLayers = JSON.parse(layerResult.content[0].text);
           }
        } catch (e) {
           // Silently ignore if jsx fails, perception will catch missing layers anyway if required
        }

        const result = await this.client.callTool({
            name: 'adobe_ps_export',
            arguments: {
               action: 'save_as',
               file_path: input.target_file || 'C:/temp/character.psd'
            }
        });
        if (result.isError) return { success: false, observed_state: null, error: "PS Native Error: " + JSON.stringify(result.content) };
        return { success: true, observed_state: { executed: true, layers: observedLayers } };
    }

    return { success: false, error: 'Unknown capability mapped for PS' };
  }

  async disconnect(): Promise<void> {
    if (this.isConnected && this.transport) {
      await this.transport.close();
      this.isConnected = false;
    }
  }
}
