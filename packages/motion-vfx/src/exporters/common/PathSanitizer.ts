import * as path from "path";
import { MotionEngineError } from "../../errors/index.js";

export class SecurityPathError extends MotionEngineError {
  constructor(message: string, public readonly pathContext?: Record<string, any>) {
    super(`Security Path Error: ${message}`);
  }
}

export const DANGEROUS_EXTENSIONS = new Set([
  ".exe", ".bat", ".cmd", ".sh", ".ps1", ".vbs", ".dll", ".so", ".dylib", ".com", ".msi", ".jar", ".scr", ".pif"
]);

export const ALLOWED_EXPORT_EXTENSIONS = new Set([
  ".jsx", ".xml", ".fcpxml", ".edl", ".json", ".txt"
]);

/**
 * Sanitizador determinista y sandbox de seguridad para rutas de exportación y assets (Fase 17).
 */
export class PathSanitizer {
  /**
   * Sanitiza un nombre de archivo reemplazando caracteres no alfanuméricos seguros.
   */
  public static sanitizeFileName(fileName: string): string {
    return fileName.replace(/[^a-zA-Z0-9_.-]/g, "_");
  }

  /**
   * Sanitiza y valida una ruta de archivo de salida dentro de un directorio base permitido.
   */
  public static sanitizeOutputPath(
    requestedPath: string,
    allowedRootDirectory?: string,
    allowedExtensions: Set<string> = ALLOWED_EXPORT_EXTENSIONS
  ): string {
    if (!requestedPath || typeof requestedPath !== "string") {
      throw new SecurityPathError("Output path must be a non-empty string.");
    }

    // 1. Detección de caracteres nulos y secuencias de escape URL maliciosas
    if (requestedPath.includes("\0") || /%2e%2e|%252e%252e/i.test(requestedPath)) {
      throw new SecurityPathError("Path traversal pattern or null byte detected.", { requestedPath });
    }

    // 2. Normalización de ruta absoluta
    const normalized = path.normalize(requestedPath);
    const resolvedPath = path.resolve(normalized);

    // 3. Verificación de extensión de archivo
    const ext = path.extname(resolvedPath).toLowerCase();
    if (DANGEROUS_EXTENSIONS.has(ext)) {
      throw new SecurityPathError(`Dangerous executable file extension '${ext}' is strictly forbidden.`, {
        requestedPath,
        ext,
      });
    }

    if (allowedExtensions.size > 0 && !allowedExtensions.has(ext)) {
      throw new SecurityPathError(
        `Extension '${ext}' is not in allowed export extensions: [${Array.from(allowedExtensions).join(", ")}]`,
        { requestedPath, ext }
      );
    }

    // 4. Verificación de sandbox si existe raíz permitida
    if (allowedRootDirectory) {
      const resolvedRoot = path.resolve(allowedRootDirectory);
      const rootWithSep = resolvedRoot.endsWith(path.sep) ? resolvedRoot : resolvedRoot + path.sep;

      if (!resolvedPath.startsWith(rootWithSep) && resolvedPath !== resolvedRoot) {
        throw new SecurityPathError(
          `Sandbox violation: output path '${resolvedPath}' is outside allowed directory '${resolvedRoot}'.`,
          { requestedPath, allowedRootDirectory, resolvedPath }
        );
      }
    }

    return resolvedPath;
  }
}
