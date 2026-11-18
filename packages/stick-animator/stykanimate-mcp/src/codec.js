/**
 * Client for the StykAnimate Python codec service.
 *
 * The service owns the authoritative Pivot grammar: it decodes `.piv` and
 * `.stk` files and writes `.piv`, `.stk` and native containers. The server
 * starts it on demand, talks to it over loopback HTTP and stops it again
 * once it has been idle, so a session that only touches `.styk` files never
 * pays for a Python process.
 */
import { spawn, spawnSync } from 'node:child_process';
import { createServer } from 'node:net';
import { existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { ToolError } from './errors.js';

const packageRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const CODEC_ROOT = path.join(packageRoot, 'py');
const SERVER_SCRIPT = path.join(CODEC_ROOT, 'backend', 'server.py');
const NATIVE_FRAME_TYPE = 'application/vnd.stykanimate.piv-frames-v1';

/** Interpreters to try, in the order the desktop app uses. */
export function pythonCandidates(env = process.env, platform = process.platform) {
  const candidates = [];
  const add = (command, args = []) => {
    if (command && !candidates.some(item => item.command === command)) candidates.push({ command, args });
  };
  add(env.STYK_PYTHON);
  if (env.VIRTUAL_ENV) add(path.join(env.VIRTUAL_ENV, platform === 'win32' ? 'Scripts/python.exe' : 'bin/python'));
  if (env.CONDA_PREFIX) add(path.join(env.CONDA_PREFIX, platform === 'win32' ? 'python.exe' : 'bin/python'));
  if (platform === 'win32') {
    add('py', ['-3']);
    add('python');
    add('python3');
  } else {
    add('python3');
    add('python');
  }
  return candidates;
}

/** The first candidate that can run the bundled codec, or null. */
export function resolvePython({ env = process.env, platform = process.platform } = {}) {
  for (const candidate of pythonCandidates(env, platform)) {
    const probe = spawnSync(candidate.command, [...candidate.args, '-c', 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)'], {
      stdio: 'ignore',
      windowsHide: true,
    });
    if (probe.status === 0) return candidate;
  }
  return null;
}

function freePort() {
  return new Promise((resolve, reject) => {
    const server = createServer();
    server.on('error', reject);
    server.listen(0, '127.0.0.1', () => {
      const { port } = server.address();
      server.close(error => (error ? reject(error) : resolve(port)));
    });
  });
}

const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

export class CodecService {
  #child = null;
  #port = null;
  #starting = null;
  #idleTimer = null;
  #lastError = null;

  /**
   * @param {object} options
   * @param {number} options.idleMs How long the service may sit unused before it stops.
   * @param {(message: string) => void} options.log Diagnostics sink; never stdout.
   */
  constructor({ idleMs = 120_000, log = () => {} } = {}) {
    this.idleMs = idleMs;
    this.log = log;
  }

  get running() {
    return Boolean(this.#child);
  }

  get lastError() {
    return this.#lastError;
  }

  /** Start the service if it is not already running. */
  async start() {
    if (this.#child) return this;
    if (this.#starting) return this.#starting;
    this.#starting = this.#start().finally(() => {
      this.#starting = null;
    });
    return this.#starting;
  }

  async #start() {
    if (!existsSync(SERVER_SCRIPT)) {
      throw new ToolError('The bundled Python codec is missing from this installation.', { code: 'codec_missing' });
    }
    const python = resolvePython();
    if (!python) {
      throw new ToolError(
        'Python 3.10 or newer is required to read Pivot .piv and .stk files. Install it, or set STYK_PYTHON to its executable.',
        { code: 'python_missing' },
      );
    }
    const port = await freePort();
    const child = spawn(
      python.command,
      [
        ...python.args,
        SERVER_SCRIPT,
        '--host',
        '127.0.0.1',
        '--port',
        String(port),
        '--workspace',
        packageRoot,
        // The codec stops when this process closes its standard input, so a
        // session that ends cannot leave a Python process behind.
        '--exit-on-stdin-close',
      ],
      {
        cwd: CODEC_ROOT,
        stdio: ['pipe', 'pipe', 'pipe'],
        windowsHide: true,
        env: { ...process.env, STYK_DISABLE_FAST_JSON: process.env.STYK_DISABLE_FAST_JSON ?? '' },
      },
    );
    this.#child = child;
    this.#port = port;
    let stderr = '';
    child.stderr.on('data', chunk => {
      stderr += chunk;
      if (stderr.length > 8192) stderr = stderr.slice(-8192);
    });
    child.stdout.on('data', () => {});
    child.on('exit', () => {
      this.#child = null;
      this.#port = null;
    });
    child.on('error', error => {
      this.#lastError = error.message;
      this.#child = null;
      this.#port = null;
    });

    const deadline = Date.now() + 30_000;
    while (Date.now() < deadline) {
      if (!this.#child) {
        throw new ToolError(`The Python codec service stopped before it was ready. ${stderr.trim()}`.trim(), {
          code: 'codec_start_failed',
        });
      }
      try {
        const response = await this.#request('GET', '/api/health');
        if (response.status === 200) {
          this.log(`codec ready on 127.0.0.1:${port}`);
          return this;
        }
      } catch {
        // The service is still binding its socket.
      }
      await sleep(100);
    }
    child.kill();
    this.#child = null;
    throw new ToolError(`The Python codec service did not become ready in time. ${stderr.trim()}`.trim(), {
      code: 'codec_start_timeout',
    });
  }

  /** Stop the service and release its caches. */
  async stop() {
    this.#clearIdleTimer();
    const child = this.#child;
    this.#child = null;
    this.#port = null;
    if (!child) return;
    child.stdin?.end();
    child.kill();
    await new Promise(resolve => child.once('exit', resolve));
  }

  #clearIdleTimer() {
    if (this.#idleTimer) {
      clearTimeout(this.#idleTimer);
      this.#idleTimer = null;
    }
  }

  #scheduleIdleStop() {
    this.#clearIdleTimer();
    this.#idleTimer = setTimeout(() => {
      this.stop().catch(() => {});
    }, this.idleMs);
    this.#idleTimer.unref?.();
  }

  async #request(method, route, { body, headers = {}, raw = false } = {}) {
    if (!this.#child || !this.#port) throw new ToolError('The Python codec service is not running.', { code: 'codec_stopped' });
    const response = await fetch(`http://127.0.0.1:${this.#port}${route}`, {
      method,
      headers: { ...headers },
      body,
    });
    if (raw) return { status: response.status, headers: response.headers, bytes: new Uint8Array(await response.arrayBuffer()) };
    const text = await response.text();
    let body_ = null;
    if (text) {
      try {
        body_ = JSON.parse(text);
      } catch {
        body_ = { ok: false, error: text.slice(0, 500), code: 'bad_response' };
      }
    }
    return { status: response.status, headers: response.headers, body: body_ };
  }

  /**
   * Decode a file through the service.
   *
   * @returns {Promise<{document: object, sourceId?: string, kind: string, timings?: object}>}
   */
  async importFile(bytes, filename) {
    await this.start();
    this.#scheduleIdleStop();
    const jobId = jobIdentity();
    const response = await this.#request('POST', `/api/import?filename=${encodeURIComponent(filename)}`, {
      body: bytes,
      headers: {
        'Content-Type': 'application/octet-stream',
        Accept: `${NATIVE_FRAME_TYPE}, application/json`,
        'X-Styk-Job-Id': jobId,
      },
      raw: true,
    });
    if (response.status !== 200) throw codecError(response);
    const contentType = response.headers.get('content-type') ?? '';
    if (contentType.includes(NATIVE_FRAME_TYPE)) {
      const { unpackNativeFrameResponse, materializeNativeFrames } = await import(
        '../vendor/stykanimate/src/import-wire.mjs'
      );
      const buffer = response.bytes.buffer.slice(
        response.bytes.byteOffset,
        response.bytes.byteOffset + response.bytes.byteLength,
      );
      const { result, offset } = unpackNativeFrameResponse(buffer);
      const materialized = await materializeNativeFrames(result, buffer, offset);
      return { document: materialized.document, sourceId: materialized.sourceId, kind: materialized.kind, timings: materialized.timings };
    }
    const parsed = JSON.parse(new TextDecoder().decode(response.bytes));
    if (!parsed.ok) throw new ToolError(parsed.error || 'The codec could not read that file.', { code: parsed.code || 'codec_error' });
    return { document: parsed.document, sourceId: parsed.sourceId, kind: parsed.kind, timings: parsed.timings };
  }

  /**
   * Write a document through the service.
   *
   * @returns {Promise<{bytes: Uint8Array, filename: string}>}
   */
  async exportDocument(document, format, { sourceId, filename, figureTypeId } = {}) {
    await this.start();
    this.#scheduleIdleStop();
    const payload = JSON.stringify({ document, sourceId, format, filename, figureTypeId });
    const response = await this.#request('POST', '/api/export', {
      body: payload,
      headers: { 'Content-Type': 'application/json', 'X-Styk-Job-Id': jobIdentity() },
      raw: true,
    });
    if (response.status !== 200) {
      const text = new TextDecoder().decode(response.bytes);
      let parsed = null;
      try {
        parsed = JSON.parse(text);
      } catch {
        parsed = { error: text.slice(0, 500), code: 'codec_error' };
      }
      throw new ToolError(parsed.error || 'The codec could not write that file.', { code: parsed.code || 'codec_error' });
    }
    const disposition = response.headers.get('content-disposition') ?? '';
    const match = /filename\*=UTF-8''([^;]+)/i.exec(disposition);
    return {
      bytes: response.bytes,
      filename: match ? decodeURIComponent(match[1]) : `${filename || 'Untitled'}.${format}`,
    };
  }
}

function codecError(response) {
  const text = new TextDecoder().decode(response.bytes);
  let parsed = null;
  try {
    parsed = JSON.parse(text);
  } catch {
    parsed = { error: text.slice(0, 500) };
  }
  return new ToolError(parsed.error || 'The codec rejected that file.', { code: parsed.code || 'codec_error' });
}

/** A 32 lowercase hex identity the codec accepts as a cancellable job. */
export function jobIdentity() {
  return globalThis.crypto.randomUUID().replaceAll('-', '');
}
