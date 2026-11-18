import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { McpRegistry } from "./registry.js";

/**
 * Inicializador y fábrica del Servidor Model Context Protocol (MCP) (Fase 17).
 */
export class MotionEngineMcpServer {
  private server: McpServer;

  constructor(name = "MotionEngineServer", version = "1.7.0") {
    this.server = new McpServer({ name, version });
    McpRegistry.registerAll(this.server);
  }

  public getServer(): McpServer {
    return this.server;
  }

  public async start(): Promise<void> {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error("Motion Graphics Engine MCP Server running via stdio transport...");
  }
}
