#!/usr/bin/env node
/**
 * Build the MCP bundle.
 *
 * An MCPB file is a zip archive holding the server, its runtime dependencies
 * and a manifest that tells a client how to run it. It is the way to install
 * this server with one click, and the package type the official MCP registry
 * accepts without a package registry.
 *
 * Usage: node scripts/build-mcpb.mjs [output directory]
 */
import { createHash } from 'node:crypto';
import { cp, mkdir, readFile, readdir, rm, writeFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const packageRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const outputRoot = path.resolve(process.argv[2] ?? path.join(packageRoot, 'build'));
const staging = path.join(outputRoot, 'mcpb-staging');
const bundleName = 'stykanimate-mcp';

const manifest = JSON.parse(await readFile(path.join(packageRoot, 'package.json'), 'utf8'));
const version = manifest.version;

/** The files the bundle carries. The layout has to match the source tree, because
 * the server resolves its vendored core relative to itself. The readme and its
 * images travel with it, so the readme still renders inside the bundle. */
const CONTENT = [
  'src',
  'vendor',
  'py',
  'assets',
  'package.json',
  'package-lock.json',
  'README.md',
  'LICENSE',
  'NOTICE.md',
  'llms.txt',
];

/** The tool names and descriptions the bundle advertises. */
async function toolList() {
  const { createServer, createSession } = await import(path.join(packageRoot, 'src/server.js'));
  const { Client, InMemoryTransport } = await import('@modelcontextprotocol/client');
  const server = createServer(createSession({ pivot: false }));
  const client = new Client({ name: 'build-mcpb', version: '1.0.0' });
  const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair();
  await Promise.all([client.connect(clientTransport), server.connect(serverTransport)]);
  const { tools } = await client.listTools();
  await client.close();
  return tools.map(tool => ({ name: tool.name, description: tool.description }));
}

async function main() {
  await rm(staging, { recursive: true, force: true });
  await mkdir(staging, { recursive: true });

  for (const entry of CONTENT) {
    const source = path.join(packageRoot, entry);
    if (!existsSync(source)) continue;
    await cp(source, path.join(staging, entry), { recursive: true });
  }

  // The bundle carries the runtime dependencies only.
  execFileSync('npm', ['ci', '--omit=dev', '--ignore-scripts'], { cwd: staging, stdio: 'inherit' });

  const tools = await toolList();
  const bundleManifest = {
    manifest_version: '0.3',
    name: bundleName,
    display_name: 'StykAnimate',
    version,
    description: 'Read, inspect and edit StykAnimate and Pivot stick figure animations.',
    long_description:
      'Opens StykAnimate and Pivot projects, reports their timeline and rig, and changes the animation.\n\n' +
      'The server reuses the app\'s own document model, rig evaluator and file codec, so a project it opens is ' +
      'the project the desktop app opens. It can read the solved rig at any tick — where every joint sits, where ' +
      'each segment starts and ends, what the inverse kinematics controllers are doing — and change the animation: ' +
      'pose joints, move IK targets, transform figures, edit keyframes, layers and appearance, and undo any of it.\n\n' +
      'StykAnimate native files are read and written in JavaScript. Pivot files need Python 3.10 or newer on the ' +
      'machine; the server starts the bundled codec on demand.',
    author: {
      name: 'StykAnimate',
      url: 'https://stykanimate.com',
    },
    repository: {
      type: 'git',
      url: 'https://github.com/ghassenTn/stykanimate-mcp.git',
    },
    homepage: 'https://stykanimate.com',
    documentation: 'https://github.com/ghassenTn/stykanimate-mcp#readme',
    support: 'https://github.com/ghassenTn/stykanimate-mcp/issues',
    icon: 'icon.png',
    keywords: ['animation', 'stick figure', 'pivot', 'stykanimate', 'rig', 'keyframe'],
    license: 'GPL-3.0-or-later',
    server: {
      type: 'node',
      entry_point: 'src/index.js',
      mcp_config: {
        command: 'node',
        args: ['${__dirname}/src/index.js'],
        env: {},
      },
    },
    tools,
    tools_generated: false,
    compatibility: {
      platforms: ['darwin', 'win32', 'linux'],
      runtimes: {
        node: '>=20.0.0',
      },
    },
  };
  await writeFile(path.join(staging, 'manifest.json'), `${JSON.stringify(bundleManifest, null, 2)}\n`);

  // The app's own icon, when a checkout of the app is beside this repository.
  const icon = path.join(packageRoot, '..', 'StykAnimate-App', 'desktop', 'assets', 'stykanimate.png');
  if (existsSync(icon)) await cp(icon, path.join(staging, 'icon.png'));

  const bundle = path.join(outputRoot, `${bundleName}-${version}.mcpb`);
  await rm(bundle, { force: true });
  execFileSync('mcpb', ['pack', staging, bundle], { stdio: 'inherit', cwd: outputRoot });

  const bytes = await readFile(bundle);
  const sha256 = createHash('sha256').update(bytes).digest('hex');
  console.log(`bundle: ${bundle} (${(bytes.byteLength / 1024 / 1024).toFixed(1)} MiB)`);
  console.log(`sha256: ${sha256}`);
  await writeFile(path.join(outputRoot, `${bundleName}-${version}.mcpb.sha256`), `${sha256}  ${bundleName}-${version}.mcpb\n`);
}

main().catch(error => {
  console.error(`build-mcpb failed: ${error.message}`);
  process.exitCode = 1;
});
