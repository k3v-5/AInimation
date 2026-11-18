/**
 * Regression tests for the faults a review found.
 *
 * Each one covers a bug that reached a user as a wrong result or a raw
 * JavaScript error.
 */
import assert from 'node:assert/strict';
import { mkdtemp, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { spawn } from 'node:child_process';
import { Client, InMemoryTransport } from '@modelcontextprotocol/client';
import { buildContainerV2, Editor, createStartupDocument } from '../src/core.js';
import { createServer, createSession } from '../src/server.js';
import { emptyDocument } from '../vendor/stykanimate/src/demo.mjs';

async function connect() {
  const session = createSession({ pivot: false });
  const server = createServer(session);
  const client = new Client({ name: 'test', version: '1.0.0' });
  const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair();
  await Promise.all([client.connect(clientTransport), server.connect(serverTransport)]);
  return { client, session };
}

const call = (client, name, args = {}) => client.callTool({ name, arguments: args });

async function openProject(client, { simple = false } = {}) {
  const folder = await mkdtemp(path.join(tmpdir(), 'stykanimate-mcp-regress-'));
  const editor = new Editor({ demo: false });
  editor.load(simple ? emptyDocument() : createStartupDocument());
  const file = path.join(folder, 'blue.styk');
  await writeFile(file, await buildContainerV2(editor.serialize(), 'styk'));
  const opened = await call(client, 'project_open', { path: file });
  assert.equal(opened.isError, undefined, opened.content?.[0]?.text);
  return { folder, projectId: opened.structuredContent.project.id };
}

test('removing a figure removes the one that was named', async t => {
  const { client } = await connect();
  t.after(async () => client.close());
  const { folder } = await openProject(client);
  t.after(async () => rm(folder, { recursive: true, force: true }));

  // Adding a figure leaves it selected.
  const added = await call(client, 'figure_add', { frame: 0, x: 200, y: 300 });
  const addedUid = added.structuredContent.uid;
  const before = await call(client, 'figure_list');
  assert.equal(before.structuredContent.figures.total, 2);

  // Removing the other figure must not touch the selected one.
  const removed = await call(client, 'figure_delete', { uid: 1, frame: 0 });
  assert.equal(removed.isError, undefined, removed.content?.[0]?.text);
  const after = await call(client, 'figure_list');
  const uids = after.structuredContent.figures.items.map(item => item.uid);
  assert.ok(!uids.includes(1), 'the named figure is still there');
  assert.ok(uids.includes(addedUid), 'the selected figure was removed instead');
});

test('removing a figure that is not there is an error, not a silent no-op', async t => {
  const { client } = await connect();
  t.after(async () => client.close());
  const { folder } = await openProject(client);
  t.after(async () => rm(folder, { recursive: true, force: true }));

  const removed = await call(client, 'figure_delete', { uid: 4242, frame: 0 });
  assert.equal(removed.isError, true);
  assert.match(removed.content[0].text, /not in that keyframe/);
  assert.doesNotMatch(removed.content[0].text, /undefined|Cannot read/);
});

test('a tool without a keyframe still works after a keyframe was added', async t => {
  const { client } = await connect();
  t.after(async () => client.close());
  const { folder } = await openProject(client);
  t.after(async () => rm(folder, { recursive: true, force: true }));

  const added = await call(client, 'keyframe_edit', { action: 'add', frame: 0 });
  assert.equal(added.isError, undefined, added.content?.[0]?.text);

  // No frame given: the tool has to work out where it is.
  const transformed = await call(client, 'figure_transform', { uid: 1, action: 'rotate', degrees: 10 });
  assert.equal(transformed.isError, undefined, transformed.content?.[0]?.text);
  assert.doesNotMatch(transformed.content[0].text, /Cannot read/);
});

test('a tick lands on the keyframe it falls in', async t => {
  const { client } = await connect();
  t.after(async () => client.close());
  const { folder } = await openProject(client, { simple: true });
  t.after(async () => rm(folder, { recursive: true, force: true }));

  // Three keyframes of one tick each.
  await call(client, 'keyframe_edit', { action: 'add', frame: 0 });
  await call(client, 'keyframe_edit', { action: 'add', frame: 1 });

  const sought = await call(client, 'project_seek', { tick: 1 });
  assert.equal(sought.isError, undefined, sought.content?.[0]?.text);
  assert.equal(sought.structuredContent.tick, 1, 'the playhead did not go to the tick');
  assert.equal(sought.structuredContent.keyframe, 1, 'the tick landed in the wrong keyframe');
});

test('the resources can be read', async t => {
  const { client } = await connect();
  t.after(async () => client.close());
  const { folder, projectId } = await openProject(client);
  t.after(async () => rm(folder, { recursive: true, force: true }));

  const templates = await client.listResourceTemplates();
  const uris = templates.resourceTemplates.map(template => template.uriTemplate);
  assert.ok(uris.includes('stykanimate://projects/{project}/document'));
  assert.ok(uris.includes('stykanimate://projects/{project}/pose'));

  const document = await client.readResource({ uri: `stykanimate://projects/${projectId}/document` });
  const parsed = JSON.parse(document.contents[0].text);
  assert.ok(Array.isArray(parsed.keyframes));

  const pose = await client.readResource({ uri: `stykanimate://projects/${projectId}/pose` });
  assert.equal(JSON.parse(pose.contents[0].text).keyframe, 0);
});

test('a transform says which axis the action needs', async t => {
  const { client } = await connect();
  t.after(async () => client.close());
  const { folder } = await openProject(client);
  t.after(async () => rm(folder, { recursive: true, force: true }));

  const mirrored = await call(client, 'figure_transform', { uid: 1, action: 'mirror', axis: 'x' });
  assert.equal(mirrored.isError, true);
  assert.match(mirrored.content[0].text, /"horizontal" or "vertical"/);

  const aligned = await call(client, 'figure_transform', { uid: 1, action: 'align', axis: 'horizontal', edge: 'start' });
  assert.equal(aligned.isError, true);
  assert.match(aligned.content[0].text, /"x" or "y"/);
});

test('a layer takes a colour the tool documents', async t => {
  const { client } = await connect();
  t.after(async () => client.close());
  const { folder } = await openProject(client);
  t.after(async () => rm(folder, { recursive: true, force: true }));

  const layers = await call(client, 'layer_list');
  const layer = layers.structuredContent.layers.find(entry => entry.kind === 'layer');
  const coloured = await call(client, 'style_set', { target: 'layer', layerId: layer.id, color: '#df6690' });
  assert.equal(coloured.isError, undefined, coloured.content[0].text);
  assert.equal(coloured.structuredContent.color, 'rose');
});

test('the server stops when the client closes the connection', async t => {
  const child = spawn(process.execPath, [new URL('../src/index.js', import.meta.url).pathname], {
    stdio: ['pipe', 'pipe', 'pipe'],
  });
  t.after(() => child.kill('SIGKILL'));
  child.stdout.resume();
  child.stderr.resume();
  child.stdin.write(
    `${JSON.stringify({
      jsonrpc: '2.0',
      id: 1,
      method: 'initialize',
      params: { protocolVersion: '2025-06-18', capabilities: {}, clientInfo: { name: 'test', version: '1' } },
    })}\n`,
  );
  await new Promise(resolve => setTimeout(resolve, 400));
  child.stdin.end();
  const exited = await Promise.race([
    new Promise(resolve => child.once('exit', () => resolve(true))),
    new Promise(resolve => setTimeout(() => resolve(false), 8000)),
  ]);
  assert.equal(exited, true, 'the server is still running after the client closed the connection');
});
