/**
 * Tests for the Streamable HTTP transport.
 *
 * The server is started the way the entry point starts it, and a real MCP
 * request is sent over it.
 */
import assert from 'node:assert/strict';
import test from 'node:test';
import { createServer as createNodeServer } from 'node:http';
import { createMcpHandler } from '@modelcontextprotocol/server';
import { localhostHostValidation, localhostOriginValidation, toNodeHandler } from '@modelcontextprotocol/node';
import { createServer, createSession } from '../src/server.js';

async function startHttp() {
  const session = createSession({ pivot: false });
  const handler = createMcpHandler(() => createServer(session));
  const node = toNodeHandler(handler);
  const validateHost = localhostHostValidation();
  const validateOrigin = localhostOriginValidation();
  const server = createNodeServer((request, response) => {
    if (!validateHost(request, response)) return;
    if (!validateOrigin(request, response)) return;
    return node(request, response);
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const { port } = server.address();
  return { server, port, session };
}

test('the HTTP transport answers an MCP request', async t => {
  const { server, port } = await startHttp();
  t.after(async () => new Promise(resolve => server.close(resolve)));

  const response = await fetch(`http://127.0.0.1:${port}/`, {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      accept: 'application/json, text/event-stream',
    },
    body: JSON.stringify({
      jsonrpc: '2.0',
      id: 1,
      method: 'initialize',
      params: {
        protocolVersion: '2025-06-18',
        capabilities: {},
        clientInfo: { name: 'test', version: '1.0.0' },
      },
    }),
  });
  assert.equal(response.status, 200);
  const text = await response.text();
  assert.match(text, /"result"/);
  assert.match(text, /stykanimate/);
});

test('the HTTP transport rejects a foreign host', async t => {
  const { server, port } = await startHttp();
  t.after(async () => new Promise(resolve => server.close(resolve)));

  const response = await fetch(`http://127.0.0.1:${port}/`, {
    method: 'POST',
    headers: { 'content-type': 'application/json', host: 'evil.example.com' },
    body: JSON.stringify({ jsonrpc: '2.0', id: 1, method: 'initialize', params: {} }),
  });
  assert.ok(response.status >= 400, `expected a rejection, got ${response.status}`);
});
