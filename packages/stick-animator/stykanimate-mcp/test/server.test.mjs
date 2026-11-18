/**
 * End-to-end tests over an in-memory MCP connection.
 *
 * The tests drive the server the way a client does: list the tools, call
 * them, and check what comes back. A project is written to a temporary file
 * first, so the file path tools are exercised too.
 */
import assert from 'node:assert/strict';
import { mkdtemp, rm, writeFile, readFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { Client, InMemoryTransport } from '@modelcontextprotocol/client';
import { buildContainerV2 } from '../src/core.js';
import { createStartupDocument } from '../src/core.js';
import { createServer, createSession } from '../src/server.js';

async function makeProjectFile(folder) {
  const { Editor } = await import('../src/core.js');
  const editor = new Editor({ demo: false });
  editor.load(createStartupDocument());
  const bytes = await buildContainerV2(editor.serialize(), 'styk');
  const file = path.join(folder, 'blue.styk');
  await writeFile(file, bytes);
  return file;
}

async function connect() {
  const session = createSession({ pivot: false });
  const server = createServer(session);
  const client = new Client({ name: 'test', version: '1.0.0' });
  const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair();
  await Promise.all([client.connect(clientTransport), server.connect(serverTransport)]);
  return { client, session, server };
}

const call = (client, name, args = {}) => client.callTool({ name, arguments: args });

test('the server lists its tools and describes itself', async t => {
  const { client } = await connect();
  t.after(async () => client.close());

  const tools = await client.listTools();
  const names = tools.tools.map(tool => tool.name);
  for (const expected of [
    'capabilities',
    'project_open',
    'project_close',
    'project_describe',
    'project_validate',
    'project_save',
    'project_timeline',
    'project_seek',
    'figure_list',
    'figure_describe',
    'figure_add',
    'figure_duplicate',
    'figure_delete',
    'figure_transform',
    'pose_evaluate',
    'pose_set',
    'pose_ik_set',
    'pose_set_ik',
    'pose_reset',
    'keyframe_edit',
    'keyframe_timing',
    'layer_list',
    'layer_edit',
    'style_set',
    'history_undo',
    'history_redo',
  ]) {
    assert.ok(names.includes(expected), `the tool ${expected} is missing`);
  }
  for (const tool of tools.tools) {
    assert.ok(tool.description, `${tool.name} has no description`);
    assert.ok(tool.annotations, `${tool.name} has no annotations`);
  }

  const capabilities = await call(client, 'capabilities');
  assert.equal(capabilities.isError, undefined);
  assert.ok(capabilities.structuredContent.reads.includes('styk'));
  assert.equal(capabilities.structuredContent.pivotCodec, false);
});

test('a project opens, describes and evaluates', async t => {
  const folder = await mkdtemp(path.join(tmpdir(), 'stykanimate-mcp-'));
  t.after(async () => rm(folder, { recursive: true, force: true }));
  const file = await makeProjectFile(folder);

  const { client } = await connect();
  t.after(async () => client.close());

  const opened = await call(client, 'project_open', { path: file });
  assert.equal(opened.isError, undefined, opened.content?.[0]?.text);
  const project = opened.structuredContent.project;
  assert.equal(project.format, 'styk');
  assert.equal(project.frames.keyframes, 1);
  assert.equal(project.figures.definitions, 1);
  assert.equal(project.figures.instances, 1);
  assert.equal(project.canvas.width, 960);

  const described = await call(client, 'project_describe', { include: ['figures', 'layers', 'keyframes'] });
  assert.equal(described.isError, undefined);
  assert.equal(described.structuredContent.figures.total, 1);
  assert.ok(described.structuredContent.layers.length >= 1);

  const timeline = await call(client, 'project_timeline');
  assert.equal(timeline.structuredContent.keyframes.total, 1);
  assert.equal(timeline.structuredContent.keyframes.items[0].outputTicks, 10);

  const uid = described.structuredContent.figures.items[0].uid;
  const pose = await call(client, 'pose_evaluate', { frame: 0 });
  assert.equal(pose.isError, undefined, pose.content?.[0]?.text);
  assert.equal(pose.structuredContent.figures.length, 1);
  assert.ok(pose.structuredContent.figures[0].joints.length > 0);
  const root = pose.structuredContent.figures[0].root;
  assert.equal(typeof root.x, 'number');

  const figure = await call(client, 'figure_describe', { uid });
  assert.equal(figure.isError, undefined);
  assert.ok(figure.structuredContent.definition.segments.length > 0);
  assert.ok(figure.structuredContent.definition.segments[0].handleId > 0);
  assert.ok(figure.structuredContent.instance.ikControllers.length > 0);
});

test('a pose can be set, read back and undone', async t => {
  const folder = await mkdtemp(path.join(tmpdir(), 'stykanimate-mcp-'));
  t.after(async () => rm(folder, { recursive: true, force: true }));
  const file = await makeProjectFile(folder);

  const { client } = await connect();
  t.after(async () => client.close());
  await call(client, 'project_open', { path: file });

  const figures = await call(client, 'figure_list');
  const uid = figures.structuredContent.figures.items[0].uid;
  const before = await call(client, 'pose_evaluate', { frame: 0 });
  const beforeRoot = before.structuredContent.figures[0].root;

  const set = await call(client, 'pose_set', {
    uid,
    frame: 0,
    root: { x: beforeRoot.x + 40, y: beforeRoot.y + 25 },
  });
  assert.equal(set.isError, undefined, set.content?.[0]?.text);

  const after = await call(client, 'pose_evaluate', { frame: 0 });
  const afterRoot = after.structuredContent.figures[0].root;
  assert.equal(Math.round(afterRoot.x - beforeRoot.x), 40);
  assert.equal(Math.round(afterRoot.y - beforeRoot.y), 25);

  const undone = await call(client, 'history_undo');
  assert.equal(undone.structuredContent.undone, true);

  const restored = await call(client, 'pose_evaluate', { frame: 0 });
  assert.equal(Math.round(restored.structuredContent.figures[0].root.x - beforeRoot.x), 0);

  const redone = await call(client, 'history_redo');
  assert.equal(redone.structuredContent.redone, true);
});

test('a joint angle can be set and the rig re-evaluated', async t => {
  const folder = await mkdtemp(path.join(tmpdir(), 'stykanimate-mcp-'));
  t.after(async () => rm(folder, { recursive: true, force: true }));
  const file = await makeProjectFile(folder);

  const { client } = await connect();
  t.after(async () => client.close());
  await call(client, 'project_open', { path: file });

  const figures = await call(client, 'figure_list');
  const uid = figures.structuredContent.figures.items[0].uid;
  const described = await call(client, 'figure_describe', { uid });
  const joint = described.structuredContent.definition.segments[0];

  const set = await call(client, 'pose_set', {
    uid,
    frame: 0,
    joints: [{ handleId: joint.handleId, angleDeg: 30 }],
  });
  assert.equal(set.isError, undefined, set.content?.[0]?.text);

  const pose = await call(client, 'pose_evaluate', { frame: 0 });
  const evaluated = pose.structuredContent.figures[0].segments.find(segment => segment.handleId === joint.handleId);
  assert.ok(evaluated, 'the segment is missing from the evaluated rig');
  assert.ok(Math.abs(evaluated.angleRad - (30 * Math.PI) / 180) < 1e-6, `angle was ${evaluated.angleRad}`);
});

test('a keyframe can be added, timed and removed', async t => {
  const folder = await mkdtemp(path.join(tmpdir(), 'stykanimate-mcp-'));
  t.after(async () => rm(folder, { recursive: true, force: true }));
  const file = await makeProjectFile(folder);

  const { client } = await connect();
  t.after(async () => client.close());
  await call(client, 'project_open', { path: file });

  const added = await call(client, 'keyframe_edit', { action: 'add', frame: 0 });
  assert.equal(added.isError, undefined, added.content?.[0]?.text);
  assert.equal(added.structuredContent.keyframes, 2);

  const timed = await call(client, 'keyframe_timing', { action: 'duration', frame: 1, ticks: 4 });
  assert.equal(timed.isError, undefined);
  const timeline = await call(client, 'project_timeline');
  assert.equal(timeline.structuredContent.keyframes.items[1].durationRaw, 4);

  const removed = await call(client, 'keyframe_edit', { action: 'delete', frame: 1 });
  assert.equal(removed.structuredContent.keyframes, 1);
});

test('a project can be saved and read back', async t => {
  const folder = await mkdtemp(path.join(tmpdir(), 'stykanimate-mcp-'));
  t.after(async () => rm(folder, { recursive: true, force: true }));
  const file = await makeProjectFile(folder);

  const { client } = await connect();
  t.after(async () => client.close());
  await call(client, 'project_open', { path: file });

  const target = path.join(folder, 'saved.styk');
  const saved = await call(client, 'project_save', { path: target, format: 'styk' });
  assert.equal(saved.isError, undefined, saved.content?.[0]?.text);
  const bytes = await readFile(target);
  assert.ok(bytes.byteLength > 0);
  assert.equal(bytes.subarray(0, 4).toString('ascii'), 'STYK');

  const reopened = await call(client, 'project_open', { path: target });
  assert.equal(reopened.isError, undefined);
  assert.equal(reopened.structuredContent.project.figures.instances, 1);
});

test('a bad request comes back as a readable error', async t => {
  const { client } = await connect();
  t.after(async () => client.close());

  const noProject = await call(client, 'project_describe');
  assert.equal(noProject.isError, true);
  assert.match(noProject.content[0].text, /project_open/);

  const missing = await call(client, 'project_open', { path: '/nowhere/at/all.styk' });
  assert.equal(missing.isError, true);
  assert.match(missing.content[0].text, /No file at/);
});

test('a project saved as a figure file holds one figure', async t => {
  const folder = await mkdtemp(path.join(tmpdir(), 'stykanimate-mcp-figure-'));
  t.after(async () => rm(folder, { recursive: true, force: true }));
  const file = await makeProjectFile(folder);

  const { client } = await connect();
  t.after(async () => client.close());
  await call(client, 'project_open', { path: file });

  const target = path.join(folder, 'blue');
  const saved = await call(client, 'project_save', { path: target, format: 'stkz' });
  assert.equal(saved.isError, undefined, saved.content?.[0]?.text);
  assert.equal(saved.structuredContent.path, path.join(folder, 'blue.stkz'));

  const bytes = await readFile(saved.structuredContent.path);
  assert.equal(bytes.subarray(0, 4).toString('ascii'), 'STKZ');

  const reopened = await call(client, 'project_open', { path: saved.structuredContent.path });
  assert.equal(reopened.isError, undefined, reopened.content?.[0]?.text);
  assert.equal(reopened.structuredContent.project.format, 'stkz');
  assert.equal(reopened.structuredContent.project.figures.instances, 1);
});

test('a project saved with the wrong extension gets the right one', async t => {
  const folder = await mkdtemp(path.join(tmpdir(), 'stykanimate-mcp-ext-'));
  t.after(async () => rm(folder, { recursive: true, force: true }));
  const file = await makeProjectFile(folder);

  const { client } = await connect();
  t.after(async () => client.close());
  await call(client, 'project_open', { path: file });

  const saved = await call(client, 'project_save', { path: path.join(folder, 'copy.piv'), format: 'styk' });
  assert.equal(saved.isError, undefined, saved.content?.[0]?.text);
  assert.equal(saved.structuredContent.path, path.join(folder, 'copy.styk'));
});

test('a project stored as plain JSON can be opened', async t => {
  const folder = await mkdtemp(path.join(tmpdir(), 'stykanimate-mcp-json-'));
  t.after(async () => rm(folder, { recursive: true, force: true }));

  const { Editor, createStartupDocument } = await import('../src/core.js');
  const editor = new Editor({ demo: false });
  editor.load(createStartupDocument());
  const file = path.join(folder, 'blue.json');
  await writeFile(file, JSON.stringify(editor.serialize()));

  const { client } = await connect();
  t.after(async () => client.close());
  const opened = await call(client, 'project_open', { path: file });
  assert.equal(opened.isError, undefined, opened.content?.[0]?.text);
  assert.equal(opened.structuredContent.project.figures.instances, 1);
});
