import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import * as fs from "fs";
import * as os from "os";
import * as path from "path";
import { z } from "zod";

function getAETempDir(): string {
  const homeDir = os.homedir();
  const bridgeDir = path.join(homeDir, "Documents", "ae-mcp-bridge");
  if (!fs.existsSync(bridgeDir)) {
    fs.mkdirSync(bridgeDir, { recursive: true });
  }
  return bridgeDir;
}

function readResultsFromTempFile(): string {
  try {
    const tempFilePath = path.join(getAETempDir(), "ae_mcp_result.json");
    if (fs.existsSync(tempFilePath)) {
      const stats = fs.statSync(tempFilePath);
      const content = fs.readFileSync(tempFilePath, "utf8");
      const thirtySecondsAgo = new Date(Date.now() - 30 * 1000);
      if (stats.mtime < thirtySecondsAgo) {
        return JSON.stringify({
          warning: "Result file appears to be stale (not recently updated).",
          lastModified: stats.mtime.toISOString(),
          originalContent: content,
        });
      }
      return content;
    }
    return JSON.stringify({ error: "No results file found. Please run a script in After Effects first." });
  } catch (error) {
    return JSON.stringify({ error: `Failed to read results: ${String(error)}` });
  }
}

async function waitForBridgeResult(
  expectedCommand?: string,
  timeoutMs: number = 5000,
  pollMs: number = 250
): Promise<string> {
  const start = Date.now();
  const resultPath = path.join(getAETempDir(), "ae_mcp_result.json");
  let lastSize = -1;

  while (Date.now() - start < timeoutMs) {
    if (fs.existsSync(resultPath)) {
      try {
        const content = fs.readFileSync(resultPath, "utf8");
        if (content && content.length > 0 && content.length !== lastSize) {
          lastSize = content.length;
          try {
            const parsed = JSON.parse(content);
            if (!expectedCommand || parsed._commandExecuted === expectedCommand) {
              return content;
            }
          } catch {}
        }
      } catch {}
    }
    await new Promise((r) => setTimeout(r, pollMs));
  }
  return JSON.stringify({
    error: `Timed out waiting for bridge result${expectedCommand ? ` for command '${expectedCommand}'` : ""}.`,
  });
}

function writeCommandFile(command: string, args: Record<string, any> = {}): void {
  try {
    const commandFile = path.join(getAETempDir(), "ae_command.json");
    const commandData = {
      command,
      args,
      timestamp: new Date().toISOString(),
      status: "pending",
    };
    fs.writeFileSync(commandFile, JSON.stringify(commandData, null, 2));
  } catch (error) {
    console.error("Error writing command file:", error);
  }
}

function clearResultsFile(): void {
  try {
    const resultFile = path.join(getAETempDir(), "ae_mcp_result.json");
    const resetData = {
      status: "waiting",
      message: "Waiting for new result from After Effects...",
      timestamp: new Date().toISOString(),
    };
    fs.writeFileSync(resultFile, JSON.stringify(resetData, null, 2));
  } catch (error) {
    console.error("Error clearing results file:", error);
  }
}

function uniqueExistingDirs(pathsToCheck: string[]): string[] {
  const seen = new Set<string>();
  const result: string[] = [];

  for (const p of pathsToCheck) {
    if (!p) continue;
    const normalized = path.normalize(p);
    if (seen.has(normalized)) continue;
    if (fs.existsSync(normalized)) {
      try {
        if (fs.statSync(normalized).isDirectory()) {
          seen.add(normalized);
          result.push(normalized);
        }
      } catch {}
    }
  }

  return result;
}

function getDefaultPresetRoots(): string[] {
  const home = os.homedir();
  const appData = process.env.APPDATA || "";
  const programFiles = process.env.ProgramFiles || "C:\\Program Files";

  const roots = [
    path.join(home, "Documents", "Adobe"),
    path.join(home, "Documents", "Adobe", "After Effects"),
    path.join(home, "Documents", "Adobe", "After Effects User Presets"),
    path.join(appData, "Adobe", "After Effects"),
    path.join(programFiles, "Adobe", "Adobe After Effects 2026", "Support Files", "Presets"),
    path.join(programFiles, "Adobe", "Adobe After Effects 2025", "Support Files", "Presets"),
    path.join(programFiles, "Adobe", "Adobe After Effects 2024", "Support Files", "Presets"),
  ];

  return uniqueExistingDirs(roots);
}

function collectPresetFiles(
  roots: string[],
  recursive: boolean,
  query?: string,
  maxResults: number = 500,
  maxDepth: number = 10
): Array<{ path: string; name: string; directory: string; size: number; modifiedAt: string }> {
  const results: Array<{ path: string; name: string; directory: string; size: number; modifiedAt: string }> = [];
  const loweredQuery = query ? query.toLowerCase() : "";

  function walk(currentDir: string, depth: number) {
    if (results.length >= maxResults || depth > maxDepth) return;
    let entries: fs.Dirent[] = [];
    try {
      entries = fs.readdirSync(currentDir, { withFileTypes: true });
    } catch {
      return;
    }

    for (const entry of entries) {
      if (results.length >= maxResults) return;
      const entryPath = path.join(currentDir, entry.name);
      if (entry.isDirectory()) {
        if (recursive) walk(entryPath, depth + 1);
        continue;
      }
      if (!entry.isFile() || !entry.name.toLowerCase().endsWith(".ffx")) continue;
      if (loweredQuery && !entry.name.toLowerCase().includes(loweredQuery) && !entryPath.toLowerCase().includes(loweredQuery)) continue;

      try {
        const stat = fs.statSync(entryPath);
        results.push({
          path: entryPath,
          name: entry.name,
          directory: currentDir,
          size: stat.size,
          modifiedAt: stat.mtime.toISOString(),
        });
      } catch {}
    }
  }

  for (const root of roots) {
    if (results.length >= maxResults) break;
    walk(root, 0);
  }

  return results;
}

/**
 * Registra los 30 comandos y recursos legado del After Effects Bridge panel (Fase 17 modularizada).
 */
export function registerLegacyAEBridge(server: McpServer): void {
  server.resource("compositions", "aftereffects://compositions", async (uri) => {
    clearResultsFile();
    writeCommandFile("listCompositions", {});
    const result = await waitForBridgeResult("listCompositions", 6000, 250);
    return {
      contents: [{ uri: uri.href, mimeType: "application/json", text: result }],
    };
  });

  server.tool(
    "run-script",
    "Run a predefined bridge script in After Effects",
    {
      script: z.string().describe("Name of the predefined script to run"),
      parameters: z.record(z.any()).optional().describe("Optional parameters"),
    },
    async ({ script, parameters = {} }) => {
      clearResultsFile();
      writeCommandFile(script, parameters);
      return {
        content: [{ type: "text", text: `Command '${script}' queued for execution in After Effects.` }],
      };
    }
  );

  server.tool("get-results", "Get results from the last script executed in After Effects", {}, async () => {
    return { content: [{ type: "text", text: readResultsFromTempFile() }] };
  });

  server.tool(
    "create-composition",
    "Create a new composition in After Effects with specified parameters",
    {
      name: z.string(),
      width: z.number().int().positive(),
      height: z.number().int().positive(),
      duration: z.number().positive().optional(),
      frameRate: z.number().positive().optional(),
    },
    async (params) => {
      writeCommandFile("createComposition", params);
      return {
        content: [{ type: "text", text: `Command to create composition '${params.name}' queued.` }],
      };
    }
  );

  server.tool(
    "apply-effect",
    "Apply an effect to a layer in After Effects",
    {
      compIndex: z.number().int().positive(),
      layerIndex: z.number().int().positive(),
      effect: z.string().optional(),
      effectMatchName: z.string().optional(),
      effectSettings: z.record(z.any()).optional(),
    },
    async (params) => {
      writeCommandFile("applyEffect", params);
      return {
        content: [{ type: "text", text: `Command to apply effect to layer ${params.layerIndex} queued.` }],
      };
    }
  );

  server.tool(
    "list-presets",
    "List available After Effects .ffx presets",
    {
      presetRoots: z.array(z.string()).optional(),
      recursive: z.boolean().optional(),
      maxResults: z.number().int().positive().optional(),
    },
    async (parameters) => {
      const roots = uniqueExistingDirs(
        parameters.presetRoots && parameters.presetRoots.length > 0
          ? parameters.presetRoots
          : getDefaultPresetRoots()
      );
      const presets = collectPresetFiles(roots, parameters.recursive ?? true, undefined, parameters.maxResults ?? 500);
      return {
        content: [{ type: "text", text: JSON.stringify({ status: "success", count: presets.length, presets }, null, 2) }],
      };
    }
  );

  server.tool(
    "set-audio-levels",
    "Set the audio levels (in dB) for an audio or AV layer",
    {
      compIndex: z.number().int().positive(),
      layerIndex: z.number().int().positive(),
      level: z.number().optional(),
      timeInSeconds: z.number().optional(),
    },
    async (parameters) => {
      clearResultsFile();
      writeCommandFile("setLayerAudioLevels", parameters);
      const result = await waitForBridgeResult("setLayerAudioLevels", 7000, 250);
      return { content: [{ type: "text", text: result }] };
    }
  );
}
