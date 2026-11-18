/**
 * Tests for the editing tools: figures, layers, appearance and timing.
 */
import assert from 'node:assert/strict';
import { mkdtemp, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { Client, InMemoryTransport } from '@modelcontextprotocol/client';
import { buildContainerV2, Editor, createStartupDocument } from '../src/core.js';
import { createServer, createSession } from '../src/server.js';

async function connect() {
  const session = createSession({ pivot: false });
  const server = createServer(session);
  const client = new Client({ name: 'test', version: '1.0.0' });
  const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair();
  await Promise.all([client.connect(clientTransport), server.connect(serverTransport)]);
  return { client, session };
}

const call = (client, name, args = {}) => client.callTool({ name, arguments: args });

async function openProject(client) {
  const folder = await mkdtemp(path.join(tmpdir(), 'stykanimate-mcp-edit-'));
  const editor = new Editor({ demo: false });
  editor.load(createStartupDocument());
  const file = path.join(folder, 'blue.styk');
  await writeFile(file, await buildContainerV2(editor.serialize(), 'styk'));
  const opened = await call(client, 'project_open', { path: file });
  assert.equal(opened.isError, undefined, opened.content?.[0]?.text);
  return { folder, file };
}

test('a figure can be added, moved and removed', async t => {
  const { client } = await connect();
  t.after(async () => client.close());
  const { folder } = await openProject(client);
  t.after(async () => rm(folder, { recursive: true, force: true }));

  const before = await call(client, 'figure_list');
  assert.equal(before.structuredContent.figures.total, 1);

  const added = await call(client, 'figure_add', { frame: 0, x: 200, y: 300 });
  assert.equal(added.isError, undefined, added.content?.[0]?.text);
  const newUid = added.structuredContent.uid;

  const listed = await call(client, 'figure_list');
  assert.equal(listed.structuredContent.figures.total, 2);
  const row = listed.structuredContent.figures.items.find(entry => entry.uid === newUid);
  assert.equal(Math.round(row.root.x), 200);
  assert.equal(Math.round(row.root.y), 300);

  const moved = await call(client, 'figure_transform', { uid: newUid, frame: 0, action: 'move', dx: 50, dy: -25 });
  assert.equal(moved.isError, undefined, moved.content?.[0]?.text);
  const afterMove = await call(client, 'figure_list');
  const movedRow = afterMove.structuredContent.figures.items.find(entry => entry.uid === newUid);
  assert.equal(Math.round(movedRow.root.x), 250);
  assert.equal(Math.round(movedRow.root.y), 275);

  const removed = await call(client, 'figure_delete', { uid: newUid, frame: 0 });
  assert.equal(removed.isError, undefined, removed.content?.[0]?.text);
  const afterDelete = await call(client, 'figure_list');
  assert.equal(afterDelete.structuredContent.figures.total, 1);
});

test('a figure can be duplicated', async t => {
  const { client } = await connect();
  t.after(async () => client.close());
  const { folder } = await openProject(client);
  t.after(async () => rm(folder, { recursive: true, force: true }));

  const listed = await call(client, 'figure_list');
  const uid = listed.structuredContent.figures.items[0].uid;
  const copy = await call(client, 'figure_duplicate', { uid, frame: 0, offset: 10 });
  assert.equal(copy.isError, undefined, copy.content?.[0]?.text);
  const after = await call(client, 'figure_list');
  assert.equal(after.structuredContent.figures.total, 2);
  assert.notEqual(after.structuredContent.figures.items[1].uid, uid);
});

test('a layer can be created and a figure moved into it', async t => {
  const { client } = await connect();
  t.after(async () => client.close());
  const { folder } = await openProject(client);
  t.after(async () => rm(folder, { recursive: true, force: true }));

  const created = await call(client, 'layer_edit', { action: 'create', name: 'Characters' });
  assert.equal(created.isError, undefined, created.content?.[0]?.text);
  const layerId = created.structuredContent.layer.id;

  const listed = await call(client, 'figure_list');
  const uid = listed.structuredContent.figures.items[0].uid;
  const assigned = await call(client, 'layer_edit', { action: 'assign', layerId, uids: [uid] });
  assert.equal(assigned.isError, undefined, assigned.content?.[0]?.text);

  const layers = await call(client, 'layer_list');
  const layer = layers.structuredContent.layers.find(entry => entry.id === layerId);
  assert.equal(layer.name, 'Characters');
  assert.ok(layer.figureUids.includes(uid));

  const renamed = await call(client, 'layer_edit', { action: 'rename', layerId, name: 'Cast' });
  assert.equal(renamed.isError, undefined);
  const hidden = await call(client, 'layer_edit', { action: 'visible', layerId, visible: false });
  assert.equal(hidden.isError, undefined);
});

test('a figure colour and a part colour can be changed', async t => {
  const { client } = await connect();
  t.after(async () => client.close());
  const { folder } = await openProject(client);
  t.after(async () => rm(folder, { recursive: true, force: true }));

  const listed = await call(client, 'figure_list');
  const uid = listed.structuredContent.figures.items[0].uid;

  const recoloured = await call(client, 'style_set', {
    target: 'figure',
    uid,
    color: '#ff0000',
  });
  assert.equal(recoloured.isError, undefined, recoloured.content?.[0]?.text);

  const described = await call(client, 'figure_describe', { uid });
  const handleId = described.structuredContent.definition.segments[0].handleId;
  const part = await call(client, 'style_set', {
    target: 'part',
    uid,
    handleId,
    color: [0, 128, 255],
    thickness: 12,
  });
  assert.equal(part.isError, undefined, part.content?.[0]?.text);

  const after = await call(client, 'figure_describe', { uid });
  const segment = after.structuredContent.definition.segments[0];
  assert.deepEqual(segment.colorRgb, [0, 128, 255]);
  assert.equal(segment.thickness, 12);
});

test('a figure can be restyled after the project gained a keyframe', async t => {
  const { client } = await connect();
  t.after(async () => client.close());
  const { folder } = await openProject(client);
  t.after(async () => rm(folder, { recursive: true, force: true }));

  // The startup project uses the advanced timeline, where the playback exposes
  // fewer ticks than the project has keyframes.
  const added = await call(client, 'keyframe_edit', { action: 'add', frame: 0 });
  assert.equal(added.isError, undefined, added.content?.[0]?.text);
  assert.equal(added.structuredContent.keyframes, 2);

  const listed = await call(client, 'figure_list');
  const uid = listed.structuredContent.figures.items[0].uid;
  const recoloured = await call(client, 'style_set', { target: 'figure', uid, color: '#00ff00' });
  assert.equal(recoloured.isError, undefined, recoloured.content?.[0]?.text);
  // The change names the ticks the playback reaches, not the stored poses.
  assert.ok(recoloured.structuredContent.ticks.length >= 1);
});

test('the evaluated rig names the keyframe it was read at', async t => {
  const { client } = await connect();
  t.after(async () => client.close());
  const { folder } = await openProject(client);
  t.after(async () => rm(folder, { recursive: true, force: true }));

  const pose = await call(client, 'pose_evaluate', { frame: 0 });
  assert.equal(pose.isError, undefined);
  assert.equal(pose.structuredContent.keyframe, 0);
  assert.match(pose.content[0].text, /Keyframe 0 \(tick 0/);
  assert.equal(pose.structuredContent.figures[0].joints[0].name, 'Root');
});

test('the frame rate and the canvas can be changed', async t => {
  const { client } = await connect();
  t.after(async () => client.close());
  const { folder } = await openProject(client);
  t.after(async () => rm(folder, { recursive: true, force: true }));

  const fps = await call(client, 'keyframe_timing', { action: 'fps', fps: 30 });
  assert.equal(fps.isError, undefined, fps.content?.[0]?.text);
  const canvas = await call(client, 'keyframe_timing', { action: 'canvas', width: 1280, height: 720 });
  assert.equal(canvas.isError, undefined, canvas.content?.[0]?.text);

  const described = await call(client, 'project_describe');
  assert.equal(described.structuredContent.project.fps, 30);
  assert.equal(described.structuredContent.project.canvas.width, 1280);
  assert.equal(described.structuredContent.project.canvas.height, 720);
});

test('a bad figure id is reported rather than thrown', async t => {
  const { client } = await connect();
  t.after(async () => client.close());
  const { folder } = await openProject(client);
  t.after(async () => rm(folder, { recursive: true, force: true }));

  const missing = await call(client, 'pose_set', { uid: 9999, frame: 0, root: { x: 1, y: 2 } });
  assert.equal(missing.isError, true);
  assert.match(missing.content[0].text, /No figure with the id 9999/);
});
