/**
 * Tests for the Python codec path: exporting a Pivot file and reading it back.
 *
 * These tests need a Python interpreter. They skip themselves when there is
 * none, so the suite still runs on a machine without Python.
 */
import assert from 'node:assert/strict';
import { mkdtemp, rm, writeFile, readFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { Client, InMemoryTransport } from '@modelcontextprotocol/client';
import { buildContainerV2, Editor, createStartupDocument } from '../src/core.js';
import { createServer, createSession } from '../src/server.js';
import { resolvePython } from '../src/codec.js';

const python = resolvePython();

async function connect() {
  const session = createSession({ pivot: true });
  const server = createServer(session);
  const client = new Client({ name: 'test', version: '1.0.0' });
  const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair();
  await Promise.all([client.connect(clientTransport), server.connect(serverTransport)]);
  return { client, session, server };
}

const call = (client, name, args = {}) => client.callTool({ name, arguments: args });

test('a project can be exported as a Pivot file and read back', { skip: python ? false : 'no Python interpreter' }, async t => {
  const folder = await mkdtemp(path.join(tmpdir(), 'stykanimate-mcp-piv-'));
  t.after(async () => rm(folder, { recursive: true, force: true }));

  const { client, session } = await connect();
  t.after(async () => {
    await client.close();
    await session.codec?.stop();
  });

  // A native project to start from.
  const editor = new Editor({ demo: false });
  editor.load(createStartupDocument());
  const native = path.join(folder, 'blue.styk');
  await writeFile(native, await buildContainerV2(editor.serialize(), 'styk'));

  const opened = await call(client, 'project_open', { path: native });
  assert.equal(opened.isError, undefined, opened.content?.[0]?.text);

  // Export it as a Pivot animation through the codec.
  const piv = path.join(folder, 'blue.piv');
  const exported = await call(client, 'project_save', { path: piv, format: 'piv' });
  assert.equal(exported.isError, undefined, exported.content?.[0]?.text);
  const bytes = await readFile(piv);
  assert.ok(bytes.byteLength > 0);

  // Read the Pivot file back through the codec.
  const reopened = await call(client, 'project_open', { path: piv });
  assert.equal(reopened.isError, undefined, reopened.content?.[0]?.text);
  const project = reopened.structuredContent.project;
  assert.equal(project.format, 'piv');
  // A decoded Pivot file keeps the implicit default figure type alongside the
  // figure that was exported.
  assert.ok(project.figures.definitions >= 1);
  assert.equal(project.figures.instances, 1);
  assert.equal(project.canvas.width, 960);
  assert.ok(project.frames.keyframes >= 1);
});
