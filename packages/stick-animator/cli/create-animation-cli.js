#!/usr/bin/env node
import { spawn } from 'node:child_process';
import { writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const mcpRoot = path.join(__dirname, 'stykanimate-mcp');
const { Editor, createStartupDocument, buildContainerV2 } = await import(
  pathToFileURL(path.join(mcpRoot, 'src', 'core.js')).href
);
const { exportToHtml } = await import(pathToFileURL(path.join(__dirname, 'export-html.js')).href);

async function main() {
  console.log('🎬 Iniciando sesión con StykAnimate MCP...');

  // 1. Crear documento base
  const editor = new Editor({ demo: false });
  editor.load(createStartupDocument());
  const initialStyk = path.join(__dirname, 'temp_base.styk');
  await writeFile(initialStyk, await buildContainerV2(editor.serialize(), 'styk'));

  // 2. Levantar servidor MCP en subproceso stdio
  const child = spawn(process.execPath, [path.join(mcpRoot, 'src', 'index.js')], {
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
    const res = message.result;
    console.log(`▸ ${name}: ${res.content?.[0]?.text || 'OK'}`);
    return res;
  }

  await send('initialize', {
    protocolVersion: '2025-06-18',
    capabilities: {},
    clientInfo: { name: 'animator-agent', version: '1.0' },
  });

  // 3. Inspeccionar proyecto
  await call('project_open', { path: initialStyk });
  await call('project_describe', { include: ['figures'] });
  const figures = await call('figure_list', {});
  const stickmanUid = figures.structuredContent.figures.items[0].uid;

  console.log(`\n🤸 Posando y configurando animación para Stickman (UID: ${stickmanUid})...`);
  // Frame 0: De pie
  await call('pose_set', { uid: stickmanUid, frame: 0, root: { x: 300, y: 350 } });

  // Cambiar estilo: color llamativo (#00d26a - verde neón)
  await call('style_set', { target: 'figure', uid: stickmanUid, color: '#00d26a' });

  // Guardar proyecto
  const finalStyk = path.join(__dirname, 'stickman_pose');
  const saved = await call('project_save', { path: finalStyk, format: 'styk' });
  child.stdin.end();

  const savedPath = saved.structuredContent?.path || finalStyk + '.styk';
  const finalHtml = path.join(__dirname, 'stickman_pose.html');
  await exportToHtml(savedPath, finalHtml);

  console.log(`\n✨ ¡Animación creada con éxito!`);
  console.log(`- Archivo de proyecto: ${savedPath}`);
  console.log(`- Reproductor web: ${finalHtml}`);
}

main().catch(console.error);
