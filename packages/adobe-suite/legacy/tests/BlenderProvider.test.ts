import { describe, it, expect } from 'vitest';
import { BlenderProvider } from '../src/providers/blender/BlenderProvider.js';

describe('BlenderProvider', () => {
  it('should expose execute_python capability', () => {
    const provider = new BlenderProvider();
    const caps = provider.capabilities();
    expect(caps.some(c => c.id === 'blender.execute_python')).toBe(true);
  });

  it('should execute a mock python script successfully in test mode', async () => {
    const provider = new BlenderProvider();
    const result = await provider.executeCapability('blender.execute_python', {
      script_content: 'print("Hello from Blender")'
    });

    expect(result.success).toBe(true);
    expect(result.observed_state.executed).toBe(true);
    expect(result.observed_state.script).toContain('blender_script_');
  });

  it('should fail if no script content is provided', async () => {
    const provider = new BlenderProvider();
    const result = await provider.executeCapability('blender.execute_python', {});

    expect(result.success).toBe(false);
    expect(result.error).toContain('No script_content');
  });
});
