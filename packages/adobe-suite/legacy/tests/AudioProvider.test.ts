import { describe, it, expect } from 'vitest';
import { AudioProvider } from '../src/providers/audio/AudioProvider.js';

describe('AudioProvider', () => {
  it('should expose audio.generate_tts capability', () => {
    const provider = new AudioProvider();
    const caps = provider.capabilities();
    expect(caps.some(c => c.id === 'audio.generate_tts')).toBe(true);
  });

  it('should execute audio.generate_tts mock capability', async () => {
    const provider = new AudioProvider();
    const result = await provider.executeCapability('audio.generate_tts', {
      text: 'Hello world'
    });

    expect(result.success).toBe(true);
    expect(result.observed_state.executed).toBe(true);
    expect(result.observed_state.generated_file).toContain('tts_');
    expect(result.observed_state.generated_file).toContain('.wav');
  });
});
