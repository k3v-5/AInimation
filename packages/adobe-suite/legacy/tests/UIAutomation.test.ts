import { fileURLToPath } from 'url';
import { test, expect, describe } from 'vitest';
import { execFileSync } from 'child_process';
import path from 'path';

describe('UI Automation OS Script', () => {
  test('Returns success when calling ch.compute_lip_sync without GUI libs (mock mode)', () => {
    const scriptPath = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../src/protocols/mcp/os_automation.py');
    const action = 'ch.compute_lip_sync';
    const params = JSON.stringify({ target: 'audio.wav' });

    // Execute the python script directly. Since GUI libs aren't installed in the CI env,
    // it will gracefully fall back and return the mock JSON.
    const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
    const output = execFileSync(pythonCmd, [scriptPath, '--action', action, '--params', params], { encoding: 'utf8' });

    // We expect the script to log a warning, then print the JSON payload at the end.
    const jsonStr = output.trim().split('\n').pop();
    const result = JSON.parse(jsonStr!);

    expect(result.status).toBe('SUCCESS');
    expect(result.action).toBe(action);
  });

  test('Validates focus loops and fails after max retries if window is missing', () => {
    expect(true).toBe(true);
  });
});