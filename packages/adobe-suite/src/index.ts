import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';

import { characterTools } from './tools/characterTools.js';
import { illustratorTools } from './tools/illustratorTools.js';
import { audioTools } from './tools/audioTools.js';
import { afterEffectsTools } from './tools/afterEffectsTools.js';
import { blenderTools } from './tools/blenderTools.js';
import { pipelineTools } from './tools/pipelineTools.js';

const allTools = [
  ...characterTools,
  ...illustratorTools,
  ...audioTools,
  ...afterEffectsTools,
  ...blenderTools,
  ...pipelineTools
];

const toolMap = new Map<string, (args: any) => Promise<any>>();
for (const t of allTools) {
  toolMap.set(t.name, t.handler);
}

const server = new Server(
  {
    name: 'adobe-animation-mcp',
    version: '2.0.0',
  },
  {
    capabilities: {
      tools: {}
    }
  }
);

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: allTools.map(t => ({
      name: t.name,
      description: t.description,
      inputSchema: t.inputSchema
    }))
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  const handler = toolMap.get(name);

  if (!handler) {
    return {
      content: [{ type: 'text', text: `Tool '${name}' not found.` }],
      isError: true
    };
  }

  try {
    const result = await handler(args || {});
    return result;
  } catch (err: any) {
    console.error(`[MCP Error in ${name}]:`, err);
    return {
      content: [{
        type: 'text',
        text: JSON.stringify({
          status: 'ERROR',
          tool: name,
          error: err.message || String(err)
        }, null, 2)
      }],
      isError: true
    };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error(`[adobe-animation-mcp] Server running on stdio with ${allTools.length} animation tools active.`);
}

function handleShutdown(signal: string) {
  console.error(`[adobe-animation-mcp] Received ${signal}. Shutting down cleanly...`);
  process.exit(0);
}

process.on('SIGINT', () => handleShutdown('SIGINT'));
process.on('SIGTERM', () => handleShutdown('SIGTERM'));
process.stdin.on('end', () => handleShutdown('STDIN_END'));
process.stdin.on('close', () => handleShutdown('STDIN_CLOSE'));

main().catch(err => {
  console.error('[adobe-animation-mcp] Fatal error:', err);
  process.exit(1);
});