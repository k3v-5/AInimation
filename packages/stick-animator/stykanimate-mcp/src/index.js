#!/usr/bin/env node
/**
 * StykAnimate MCP server.
 *
 * Two transports, one implementation:
 *   --transport stdio   the default; a local client starts the process itself
 *   --transport http    a Streamable HTTP endpoint for a hosted or shared server
 *
 * The server writes nothing to stdout in stdio mode except the protocol
 * itself; diagnostics go to stderr.
 */
import { createMcpHandler } from '@modelcontextprotocol/server';
import { serveStdio } from '@modelcontextprotocol/server/stdio';
import { localhostHostValidation, localhostOriginValidation, toNodeHandler } from '@modelcontextprotocol/node';
import { createServer, createSession } from './server.js';

const USAGE = `StykAnimate MCP server

Usage: stykanimate-mcp [options]

Options:
  --transport <stdio|http>  How clients reach the server (default: stdio)
  --host <address>          The address to listen on in http mode (default: 127.0.0.1)
  --port <number>           The port to listen on in http mode (default: 7331)
  --no-pivot                Do not start the Python codec, so Pivot files cannot be read
  -h, --help                Show this help
`;

function parseArgs(argv) {
  const options = { transport: 'stdio', host: '127.0.0.1', port: 7331, pivot: true, help: false };
  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index];
    if (argument === '--transport') options.transport = argv[++index];
    else if (argument === '--host') options.host = argv[++index];
    else if (argument === '--port') options.port = Number(argv[++index]);
    else if (argument === '--no-pivot') options.pivot = false;
    else if (argument === '-h' || argument === '--help') options.help = true;
    else throw new Error(`Unknown option "${argument}".`);
  }
  if (!['stdio', 'http'].includes(options.transport)) {
    throw new Error(`Unknown transport "${options.transport}". Use stdio or http.`);
  }
  if (!Number.isInteger(options.port) || options.port < 1 || options.port > 65535) {
    throw new Error('The port must be a number between 1 and 65535.');
  }
  return options;
}

const log = message => process.stderr.write(`[stykanimate-mcp] ${message}\n`);

async function serveHttp(options, session) {
  const { createServer: createNodeServer } = await import('node:http');
  const handler = createMcpHandler(() => createServer({ ...session, log }));
  const node = toNodeHandler(handler);
  // The handler itself is validation-free, so the host and origin checks go
  // in front of it: a browser page on another site must not be able to drive
  // a server that reads the machine's files.
  const validateHost = localhostHostValidation();
  const validateOrigin = localhostOriginValidation();
  const server = createNodeServer((request, response) => {
    if (!validateHost(request, response)) return;
    if (!validateOrigin(request, response)) return;
    return node(request, response);
  });
  await new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(options.port, options.host, resolve);
  });
  log(`listening on http://${options.host}:${options.port}/`);
  return server;
}

async function main() {
  let options;
  try {
    options = parseArgs(process.argv.slice(2));
  } catch (error) {
    process.stderr.write(`${error.message}\n\n${USAGE}`);
    process.exitCode = 2;
    return;
  }
  if (options.help) {
    process.stdout.write(USAGE);
    return;
  }

  const session = createSession({ pivot: options.pivot, log });
  // The codec is a child process. It must not outlive the session, whether
  // the session ends by a signal or by the client closing the connection.
  let stopping = null;
  const shutdown = () => {
    if (!stopping) {
      stopping = session.codec
        ?.stop()
        .catch(() => {})
        .finally(() => process.exit(0));
    }
    return stopping ?? Promise.resolve();
  };

  if (options.transport === 'stdio') {
    await serveStdio(() => createServer({ ...session, log }));
    log('serving on stdio');
    // The transport owns the standard input; when the client closes it, the
    // session is over and the process must go with it.
    process.stdin.on('end', shutdown);
    process.stdin.on('close', shutdown);
    process.on('SIGINT', shutdown);
    process.on('SIGTERM', shutdown);
    return;
  }

  const server = await serveHttp(options, session);
  process.on('SIGINT', shutdown);
  process.on('SIGTERM', shutdown);
  server.on('close', shutdown);
}

main().catch(error => {
  process.stderr.write(`stykanimate-mcp failed: ${error?.stack ?? error}\n`);
  process.exitCode = 1;
});
