import { IAnimationProvider, CapabilityDefinition, CapabilityId } from '../../core/abstractions.js';
import path from 'path';
import os from 'os';
import fs from 'fs';

export class MediaEncoderProvider implements IAnimationProvider {
  id = 'media_encoder';
  isConnected = false;

  capabilities(): CapabilityDefinition[] {
    return [
      {
        id: 'render.batch_encode',
        inputSchema: { type: 'object', properties: { input_files: { type: 'array', items: { type: 'string' } }, target_format: { type: 'string' } } },
        outputSchema: { type: 'object' },
        supports: 'async',
        reversibility: 'reversible',
        observability: 'full'
      },
      {
        id: 'render.compress',
        inputSchema: { type: 'object', properties: { input_file: { type: 'string' }, target_file: { type: 'string' } } },
        outputSchema: { type: 'object' },
        supports: 'async',
        reversibility: 'reversible',
        observability: 'full'
      }
    ];
  }

  async connect(): Promise<void> {
    this.isConnected = true;
    return Promise.resolve();
  }

  async executeCapability(capabilityId: CapabilityId, input: Record<string, any> = {}, abortSignal?: AbortSignal): Promise<any> {
    if (abortSignal && abortSignal.aborted) {
       throw new Error('Operation aborted');
    }

    if (!this.isConnected) {
        throw new Error(`Provider ${this.id} is not connected.`);
    }

    const outputDir = path.join(os.homedir(), 'Documents', 'AnimationEngine', 'Artifacts');
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    if (capabilityId === 'render.batch_encode') {
        const inputFiles = input.input_files || [];
        console.log(`[MediaEncoder] Batch encoding ${inputFiles.length} files to format: ${input.target_format || 'mp4'}`);

        // Mocking background batch encoding via ExtendScript or CLI
        const outputPaths = inputFiles.map((file: string) => {
            const tempPath = path.join(outputDir, `ame_batch_${Date.now()}_${path.basename(file)}`);
            if (process.env.NODE_ENV !== 'test') fs.writeFileSync(tempPath, '// Mock encoded artifact');
            return tempPath;
        });

        return { success: true, observed_state: { executed: true, generated_files: outputPaths } };
    }

    if (capabilityId === 'render.compress') {
        console.log(`[MediaEncoder] Compressing ${input.input_file}`);

        const tempPath = input.target_file || path.join(outputDir, `ame_compressed_${Date.now()}.mp4`);
        if (process.env.NODE_ENV !== 'test') {
             fs.writeFileSync(tempPath, '// Mock compressed artifact');
        }

        return { success: true, observed_state: { executed: true, generated_file: tempPath } };
    }

    return { success: false, error: 'Unknown capability mapped for MediaEncoderProvider' };
  }

  async disconnect(): Promise<void> {
    this.isConnected = false;
    return Promise.resolve();
  }
}
