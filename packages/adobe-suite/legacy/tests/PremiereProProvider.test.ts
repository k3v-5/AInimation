import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { PremiereProProvider } from '../src/providers/premiere-pro/PremiereProProvider.js';
import fs from 'fs';

describe('PremiereProProvider', () => {
    let provider: PremiereProProvider;

    beforeEach(() => {
        provider = new PremiereProProvider();
        provider['isConnected'] = true;
    });

    afterEach(() => {
        vi.restoreAllMocks();
    });

    it('should format parameters and mock execution for video.edit', async () => {
        vi.spyOn(fs, 'existsSync').mockReturnValue(true);
        const scriptContent = 'var filePathsStr = "PATHS_TO_REPLACE"; var sequenceName = "SEQUENCE_NAME_TO_REPLACE";';
        vi.spyOn(fs, 'readFileSync').mockReturnValue(scriptContent);

        let writtenScript = '';
        vi.spyOn(fs, 'writeFileSync').mockImplementation((path: any, data: any) => {
            writtenScript = data;
        });

        const result = await provider.executeCapability('video.edit', {
            sequence_name: 'Test Sequence',
            input_files: ['/path/clip1.mp4', '/path/clip2.mp4']
        });

        expect(result.success).toBe(true);
        expect(result.observed_state.executed).toBe(true);
        expect(writtenScript).toContain('var filePathsStr = "/path/clip1.mp4,/path/clip2.mp4";');
        expect(writtenScript).toContain('var sequenceName = "Test Sequence";');
    });

    it('should read generic JSX files and execute them', async () => {
        vi.spyOn(fs, 'existsSync').mockReturnValue(true);
        const scriptContent = 'var myVar = "VAR_TO_REPLACE";';
        vi.spyOn(fs, 'readFileSync').mockReturnValue(scriptContent);

        let writtenScript = '';
        vi.spyOn(fs, 'writeFileSync').mockImplementation((path: any, data: any) => {
            writtenScript = data;
        });

        const result = await provider.executeCapability('pr.execute_jsx', {
            script_path: '/path/test.jsx',
            template_vars: {
                'VAR_TO_REPLACE': 'foo'
            }
        });

        expect(result.success).toBe(true);
        expect(writtenScript).toBe('var myVar = "foo";');
    });

    it('should format parameters and mock execution for video.auto_edit', async () => {
        vi.spyOn(fs, 'existsSync').mockReturnValue(true);
        const scriptContent = 'var filePathsStr = "PATHS_TO_REPLACE"; var sequenceName = "SEQUENCE_NAME_TO_REPLACE";';
        vi.spyOn(fs, 'readFileSync').mockReturnValue(scriptContent);

        let writtenScript = '';
        vi.spyOn(fs, 'writeFileSync').mockImplementation((path: any, data: any) => {
            writtenScript = data;
        });

        const result = await provider.executeCapability('video.auto_edit', {
            sequence_name: 'Auto Edit Sequence',
            input_files: ['/path/clip1.mp4', '/path/clip2.mp4']
        });

        expect(result.success).toBe(true);
        expect(result.observed_state.executed).toBe(true);
        expect(writtenScript).toContain('var filePathsStr = "/path/clip1.mp4,/path/clip2.mp4";');
        expect(writtenScript).toContain('var sequenceName = "Auto Edit Sequence";');
    });
});
