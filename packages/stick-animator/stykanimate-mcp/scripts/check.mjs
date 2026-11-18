#!/usr/bin/env node
/**
 * The package's own checks: every JavaScript file parses, the vendored core
 * still matches its source, and the tools are registered without a name
 * clash.
 */
import { readdir, readFile } from 'node:fs/promises';
import { spawnSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const packageRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const sources = [];

async function discover(directory) {
  let entries;
  try {
    entries = await readdir(path.join(packageRoot, directory), { withFileTypes: true });
  } catch (error) {
    if (error.code === 'ENOENT') return;
    throw error;
  }
  for (const entry of entries) {
    const relative = path.join(directory, entry.name);
    if (entry.isDirectory()) await discover(relative);
    else if (/\.(mjs|cjs|js)$/.test(entry.name)) sources.push(relative);
  }
}

for (const directory of ['src', 'test', 'scripts']) await discover(directory);

let failures = 0;
for (const source of sources) {
  const result = spawnSync(process.execPath, ['--check', source], {
    cwd: packageRoot,
    encoding: 'utf8',
    windowsHide: true,
  });
  if (result.status !== 0) {
    failures += 1;
    console.error(result.stderr || result.error?.message || `${source}: check failed.`);
  }
}
console.log(`${sources.length} JavaScript files checked; ${failures} syntax errors.`);

// The tool names are the server's public interface, so a clash is a defect.
const { Client, InMemoryTransport } = await import('@modelcontextprotocol/client');
const { createServer, createSession } = await import(path.join(packageRoot, 'src/server.js'));
const server = createServer(createSession({ pivot: false }));
const client = new Client({ name: 'check', version: '1.0.0' });
const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair();
await Promise.all([client.connect(clientTransport), server.connect(serverTransport)]);
const listed = await client.listTools();
const names = listed.tools.map(tool => tool.name);
const duplicates = names.filter((name, index) => names.indexOf(name) !== index);
if (duplicates.length) {
  failures += 1;
  console.error(`Duplicate tool names: ${[...new Set(duplicates)].join(', ')}.`);
}
for (const tool of listed.tools) {
  if (!tool.description) {
    failures += 1;
    console.error(`${tool.name} has no description.`);
  }
  if (!tool.annotations) {
    failures += 1;
    console.error(`${tool.name} has no annotations.`);
  }
}
console.log(`${names.length} tools registered.`);
await client.close();

const vendor = spawnSync(process.execPath, ['scripts/vendor-sync.mjs', '--check'], {
  cwd: packageRoot,
  encoding: 'utf8',
  windowsHide: true,
});
process.stdout.write(vendor.stdout ?? '');
process.stderr.write(vendor.stderr ?? '');
if (vendor.status !== 0) failures += 1;

const manifest = spawnSync(process.execPath, ['scripts/check-server-json.mjs'], {
  cwd: packageRoot,
  encoding: 'utf8',
  windowsHide: true,
});
process.stdout.write(manifest.stdout ?? '');
process.stderr.write(manifest.stderr ?? '');
if (manifest.status !== 0) failures += 1;

process.exitCode = failures ? 1 : 0;
