import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { AfterEffectsProvider } from '../src/providers/after-effects/AfterEffectsProvider.js';
import fs from 'fs';

describe('AfterEffectsProvider - ExtendScript Bridge', () => {
    let provider: AfterEffectsProvider;

    beforeEach(() => {
        provider = new AfterEffectsProvider();
        // Skip actual MCP connection
        provider['isConnected'] = true;
    });

    afterEach(() => {
        vi.restoreAllMocks();
    });

    it('should read JSX file, substitute templates, and mock execution', async () => {
        // Mock fs.existsSync to pretend the script exists
        vi.spyOn(fs, 'existsSync').mockReturnValue(true);

        // Mock fs.readFileSync to return a dummy script
        const scriptContent = 'var fileToImport = "PATH_TO_REPLACE";';
        vi.spyOn(fs, 'readFileSync').mockReturnValue(scriptContent);

        // Mock fs.writeFileSync to capture the interpolated script
        let writtenScript = '';
        vi.spyOn(fs, 'writeFileSync').mockImplementation((path: any, data: any) => {
            writtenScript = data;
        });

        const result = await provider.executeCapability('ae.execute_jsx', {
            script_path: '/dummy/path/script.jsx',
            template_vars: {
                'PATH_TO_REPLACE': '/mock/asset.psd'
            }
        });

        expect(result.success).toBe(true);
        expect(result.observed_state.executed).toBe(true);
        expect(writtenScript).toBe('var fileToImport = "/mock/asset.psd";');
    });

    it('should return error if script is missing', async () => {
        vi.spyOn(fs, 'existsSync').mockReturnValue(false);

        const result = await provider.executeCapability('ae.execute_jsx', {
            script_path: '/dummy/missing.jsx'
        });

        expect(result.success).toBe(false);
        expect(result.error).toContain('No script_path or script_content provided');
    });
});
