import { MotionEngineMcpServer } from "./mcp/server.js";

export type { BoundingBox, Keyframe } from "./core/index.js";
export { ASPECT_RATIO_DIMENSIONS, AspectRatio, SafeZoneViolationError } from "./delivery/index.js";
export { EPSILON } from "./vlog/index.js";

export * from "./core/index.js";
export * from "./timeline/index.js";
export * from "./elements/index.js";
export * from "./captions/index.js";
export * from "./rendering/index.js";
export * from "./exporters/index.js";
export * from "./persistence/index.js";
export * from "./revisions/index.js";
export * from "./workflows/index.js";
export * from "./agent/index.js";
export * from "./project/index.js";
export * from "./distributed/index.js";
export * from "./delivery/index.js";
export * from "./cli/index.js";
export * from "./sdk/index.js";
export * from "./mcp/index.js";
export * from "./automation/index.js";
export * from "./vlog/index.js";
export * from "./editorial/index.js";
export { AudioMixPlan } from "./vlog/index.js";

async function main() {
  const mcpServer = new MotionEngineMcpServer();
  await mcpServer.start();
}

// Ejecutar servidor si este archivo es el entrypoint directo
if (process.argv[1] && process.argv[1].endsWith("index.js")) {
  main().catch((error) => {
    console.error("Fatal error starting Motion Engine MCP Server:", error);
    process.exit(1);
  });
}
