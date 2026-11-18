import * as fs from "fs";
import * as path from "path";
import { AfterEffectsJSXCompiler } from "../../exporters/ae/AfterEffectsJSXCompiler.js";
import { PathSanitizer } from "../../exporters/common/PathSanitizer.js";
import { McpProjectNotFoundError, McpValidationError } from "../errors/mcp-errors.js";
import { ExportAfterEffectsJSXSchema } from "../schemas/mcp-tools.schema.js";
import { MCPProjectStore } from "../types.js";

/**
 * Handler de la herramienta MCP `export_to_after_effects_jsx` (Fase 17).
 */
export async function handleExportAfterEffectsJSX(rawArgs: unknown) {
  const parseResult = ExportAfterEffectsJSXSchema.safeParse(rawArgs);
  if (!parseResult.success) {
    throw new McpValidationError("Invalid arguments for export_to_after_effects_jsx", {
      issues: parseResult.error.issues,
    });
  }

  const { projectId, revisionId, outputPath, strict, dryRun } = parseResult.data;

  // 1. Obtener snapshot inmutable del almacén
  const snapshot = MCPProjectStore.getRevision(projectId, revisionId);
  if (!snapshot) {
    throw new McpProjectNotFoundError(projectId, revisionId);
  }

  const comp = snapshot.ir.composition ?? snapshot.ir;

  // 2. Compilar a ExtendScript JSX
  const compileResult = AfterEffectsJSXCompiler.compile(comp, {
    strict,
    dryRun,
    projectId: snapshot.projectId,
    revisionId: snapshot.revisionId,
  });

  let savedFilePath: string | undefined;

  // 3. Escribir archivo en disco si se solicitó ruta y no es dryRun
  if (outputPath && !dryRun) {
    const sanitized = PathSanitizer.sanitizeOutputPath(outputPath);
    const parentDir = path.dirname(sanitized);
    if (!fs.existsSync(parentDir)) {
      fs.mkdirSync(parentDir, { recursive: true });
    }
    fs.writeFileSync(sanitized, compileResult.jsxContent, "utf8");
    savedFilePath = sanitized;
  }

  return {
    projectId: snapshot.projectId,
    revisionId: snapshot.revisionId,
    manifest: compileResult.manifest,
    codeLength: compileResult.jsxContent.length,
    savedFilePath,
    jsxContent: compileResult.jsxContent,
    jsxSnippet: compileResult.jsxContent.slice(0, 500) + "\n// ... [TRUNCATED]",
  };
}
