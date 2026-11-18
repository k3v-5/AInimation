import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { AdobeCEPAdapter } from '../src/core/AdobeCEPAdapter.js';
import express from 'express';
import request from 'supertest';

describe('AdobeCEPAdapter', () => {
    let adapter: AdobeCEPAdapter;

    beforeEach(() => {
        // Mock process.env so it pretends CEP is connected
        process.env.CEP_MOCK_CONNECTED = 'true';
        adapter = new AdobeCEPAdapter();
    });

    afterEach(async () => {
        await adapter.stopServer();
        delete process.env.CEP_MOCK_CONNECTED;
        vi.restoreAllMocks();
    });

    it('should queue commands and expose them via GET /api/commands', async () => {
        const app = adapter['app'];

        // Don't wait for sendCommand to resolve, just let it queue
        const promise = adapter.sendCommand('test.command', { foo: 'bar' });

        const response = await request(app).get('/api/commands');
        expect(response.status).toBe(200);
        expect(Array.isArray(response.body)).toBe(true);
        expect(response.body.length).toBe(1);

        const cmd = response.body[0];
        expect(cmd.command).toBe('test.command');
        expect(cmd.payload.foo).toBe('bar');
        expect(cmd.id).toBeDefined();

        // Resolve the hanging promise so the test cleans up cleanly
        adapter['responsePromises'].get(cmd.id)?.resolve(true);
        await promise;
    });

    it('should resolve sendCommand when CEP posts to /api/results', async () => {
        const app = adapter['app'];

        // Fire command
        const promise = adapter.sendCommand('test.resolve', { wait: true });

        // Fetch it
        const fetchRes = await request(app).get('/api/commands');
        const cmd = fetchRes.body[0];

        // Simulate CEP posting back success
        const postRes = await request(app)
            .post('/api/results')
            .send({
                id: cmd.id,
                success: true,
                data: { created_file: '/path/mock.psd' }
            });

        expect(postRes.status).toBe(200);

        const result = await promise;
        expect(result.created_file).toBe('/path/mock.psd');
    });

    it('should timeout if CEP does not respond in time', async () => {
        // Send a command with a tiny timeout
        await expect(adapter.sendCommand('test.timeout', {}, 10)).rejects.toThrowError(/timed out/);
    });
});
