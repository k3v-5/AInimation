#!/usr/bin/env node
/**
 * Drive the server over stdio the way a client does, and print each answer.
 *
 * Usage: node scripts/demo-session.mjs [project file]
 */
import { spawn } from 'node:child_process';
import { mkdtemp, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const packageRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const { Editor, createStartupDocument, buildContainerV2 } = await import(pathToFileURL(path.join(packageRoot, 'src/core.js')).href);

const folder = await mkdtemp(path.join(tmpdir(), 'stykanimate-demo-'));
const file = path.join(folder, 'blue.styk');
const editor = new Editor({ demo: false });
editor.load(createStartupDocument());
await writeFile(file, await buildContainerV2(editor.serialize(), 'styk'));

const child = spawn(process.execPath, [path.join(packageRoot, 'src/index.js')], {
  stdio: ['pipe', 'pipe', 'inherit'],
});

let buffer = '';
const pending = new Map();
child.stdout.on('data', chunk => {
  buffer += chunk;
  let index;
  while ((index = buffer.indexOf('\n')) >= 0) {
    const line = buffer.slice(0, index).trim();
    buffer = buffer.slice(index + 1);
    if (!line) continue;
    const message = JSON.parse(line);
    const resolve = pending.get(message.id);
    if (resolve) {
      pending.delete(message.id);
      resolve(message);
    }
  }
});

let nextId = 1;
function send(method, params) {
  const id = nextId++;
  return new Promise(resolve => {
    pending.set(id, resolve);
    child.stdin.write(`${JSON.stringify({ jsonrpc: '2.0', id, method, params })}\n`);
  });
}

async function call(name, args) {
  const message = await send('tools/call', { name, arguments: args });
  const result = message.result;
  console.log(`\n▸ ${name}(${JSON.stringify(args)})`);
  console.log(`  ${result.content[0].text}`);
  return result;
}

await send('initialize', {
  protocolVersion: '2025-06-18',
  capabilities: {},
  clientInfo: { name: 'demo', version: '1.0.0' },
});

await call('capabilities', {});
await call('project_open', { path: file });
await call('project_describe', { include: ['figures', 'layers'] });
const figures = await call('figure_list', {});
const uid = figures.structuredContent.figures.items[0].uid;
await call('figure_describe', { uid });
await call('pose_evaluate', { frame: 0 });
await call('pose_set', { uid, frame: 0, root: { x: 400, y: 320 } });
await call('pose_evaluate', { frame: 0 });
await call('keyframe_edit', { action: 'add', frame: 0 });
await call('keyframe_timing', { action: 'duration', frame: 1, ticks: 24 });
await call('style_set', { target: 'figure', uid, color: '#e0552a' });
await call('history_undo', {});
const saved = await call('project_save', { path: path.join(folder, 'out'), format: 'styk' });
await call('project_open', { path: saved.structuredContent.path });
await call('project_validate', {});

child.stdin.end();
await rm(folder, { recursive: true, force: true });
