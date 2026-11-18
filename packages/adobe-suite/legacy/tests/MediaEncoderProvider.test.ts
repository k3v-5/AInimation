import { describe, it, expect } from 'vitest';
import { MediaEncoderProvider } from '../src/providers/media-encoder/MediaEncoderProvider.js';

describe('MediaEncoderProvider', () => {
  it('should expose batch encode and compress capabilities', () => {
    const provider = new MediaEncoderProvider();
    const caps = provider.capabilities();
    expect(caps.some(c => c.id === 'render.batch_encode')).toBe(true);
    expect(caps.some(c => c.id === 'render.compress')).toBe(true);
  });

  it('should execute batch encode in test mode', async () => {
    const provider = new MediaEncoderProvider();
    await provider.connect();

    const result = await provider.executeCapability('render.batch_encode', {
      input_files: ['/path/to/test1.mp4', '/path/to/test2.mp4'],
      target_format: 'h264'
    });

    expect(result.success).toBe(true);
    expect(result.observed_state.executed).toBe(true);
    expect(result.observed_state.generated_files.length).toBe(2);
    expect(result.observed_state.generated_files[0]).toContain('ame_batch_');
  });

  it('should execute compress in test mode', async () => {
    const provider = new MediaEncoderProvider();
    await provider.connect();

    const result = await provider.executeCapability('render.compress', {
      input_file: '/path/to/large.mov'
    });

    expect(result.success).toBe(true);
    expect(result.observed_state.executed).toBe(true);
    expect(result.observed_state.generated_file).toContain('ame_compressed_');
  });

  it('should fail if provider is not connected', async () => {
    const provider = new MediaEncoderProvider();
    await expect(provider.executeCapability('render.compress', {})).rejects.toThrow(/not connected/);
  });
});
