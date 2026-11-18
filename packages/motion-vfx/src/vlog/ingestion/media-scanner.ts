import fs from "node:fs";
import path from "node:path";
import { InvalidMediaError } from "../contracts/errors.js";

/** Extensiones de archivos multimedia soportadas */
export const SUPPORTED_MEDIA_EXTENSIONS = {
  VIDEO: new Set([".mp4", ".mov", ".m4v", ".webm", ".mkv"]),
  AUDIO: new Set([".wav", ".mp3", ".m4a", ".flac", ".aac"]),
  IMAGE: new Set([".png", ".jpg", ".jpeg", ".webp"]),
};

export const ALL_SUPPORTED_EXTENSIONS = new Set([
  ...SUPPORTED_MEDIA_EXTENSIONS.VIDEO,
  ...SUPPORTED_MEDIA_EXTENSIONS.AUDIO,
  ...SUPPORTED_MEDIA_EXTENSIONS.IMAGE,
]);

/**
 * Escáner determinista y seguro de archivos multimedia en disco.
 * Protege contra directory traversal, symlink traversal y bucles recursivos.
 */
export class MediaScanner {
  /**
   * Determina el tipo MIME estándar a partir de la extensión del archivo.
   */
  public static getMimeType(extension: string): string {
    const ext = extension.toLowerCase();
    switch (ext) {
      case ".mp4":
      case ".m4v":
        return "video/mp4";
      case ".mov":
        return "video/quicktime";
      case ".webm":
        return "video/webm";
      case ".mkv":
        return "video/x-matroska";
      case ".wav":
        return "audio/wav";
      case ".mp3":
        return "audio/mpeg";
      case ".m4a":
      case ".aac":
        return "audio/mp4";
      case ".flac":
        return "audio/flac";
      case ".png":
        return "image/png";
      case ".jpg":
      case ".jpeg":
        return "image/jpeg";
      case ".webp":
        return "image/webp";
      default:
        return "application/octet-stream";
    }
  }

  /**
   * Clasifica una extensión en categoría macro de medio: VIDEO, AUDIO o IMAGE.
   */
  public static getMediaCategory(extension: string): "VIDEO" | "AUDIO" | "IMAGE" | "UNKNOWN" {
    const ext = extension.toLowerCase();
    if (SUPPORTED_MEDIA_EXTENSIONS.VIDEO.has(ext)) return "VIDEO";
    if (SUPPORTED_MEDIA_EXTENSIONS.AUDIO.has(ext)) return "AUDIO";
    if (SUPPORTED_MEDIA_EXTENSIONS.IMAGE.has(ext)) return "IMAGE";
    return "UNKNOWN";
  }

  /**
   * Escanea recursivamente uno o varios directorios autorizados garantizando orden determinista y seguridad.
   */
  public static scanDirectories(rootDirectories: string[]): string[] {
    if (!rootDirectories || rootDirectories.length === 0) {
      return [];
    }

    const discoveredFiles: string[] = [];
    const visitedRealPaths = new Set<string>();

    for (const rawDir of rootDirectories) {
      if (!rawDir || typeof rawDir !== "string") continue;

      const normalizedRoot = path.resolve(path.normalize(rawDir));
      if (!fs.existsSync(normalizedRoot)) {
        throw new InvalidMediaError(`Root directory does not exist: '${normalizedRoot}'`);
      }

      const rootStat = fs.statSync(normalizedRoot);
      if (!rootStat.isDirectory()) {
        throw new InvalidMediaError(`Provided path is not a directory: '${normalizedRoot}'`);
      }

      // Obtener path canónico real de la raíz
      const canonicalRoot = fs.realpathSync(normalizedRoot);

      this.walkDirectory(normalizedRoot, canonicalRoot, visitedRealPaths, discoveredFiles);
    }

    // Ordenamiento canónico determinista e independiente del filesystem/SO
    return discoveredFiles.sort((a, b) => a.localeCompare(b, "en", { sensitivity: "base" }));
  }

  private static walkDirectory(
    currentDir: string,
    canonicalRoot: string,
    visitedRealPaths: Set<string>,
    results: string[]
  ): void {
    let realCurrentDir: string;
    try {
      realCurrentDir = fs.realpathSync(currentDir);
    } catch {
      return; // Ruta inaccesible
    }

    // Prevención de escape de raíz mediante symlinks
    const relativeToRoot = path.relative(canonicalRoot, realCurrentDir);
    if (relativeToRoot.startsWith("..") && !path.isAbsolute(relativeToRoot)) {
      // Intento de escape fuera de la raíz autorizada
      return;
    }

    // Prevención de bucles recursivos de symlinks
    if (visitedRealPaths.has(realCurrentDir)) {
      return;
    }
    visitedRealPaths.add(realCurrentDir);

    let entries: fs.Dirent[];
    try {
      entries = fs.readdirSync(currentDir, { withFileTypes: true });
    } catch {
      return;
    }

    // Ordenar entradas para recorrido determinista
    entries.sort((a, b) => a.name.localeCompare(b.name, "en", { sensitivity: "base" }));

    for (const entry of entries) {
      const name = entry.name;

      // Ignorar archivos ocultos (.DS_Store, .git, .env) y temporales (~$*, *.tmp)
      if (name.startsWith(".") || name.startsWith("~$") || name.endsWith(".tmp")) {
        continue;
      }

      const fullPath = path.join(currentDir, name);

      if (entry.isDirectory()) {
        this.walkDirectory(fullPath, canonicalRoot, visitedRealPaths, results);
      } else if (entry.isFile()) {
        const ext = path.extname(name).toLowerCase();
        if (ALL_SUPPORTED_EXTENSIONS.has(ext)) {
          // Asegurar que el archivo no escape de la raíz real
          try {
            const realFile = fs.realpathSync(fullPath);
            const fileRel = path.relative(canonicalRoot, realFile);
            if (!fileRel.startsWith("..") || path.isAbsolute(fileRel)) {
              results.push(fullPath.replace(/\\/g, "/"));
            }
          } catch {
            // Ignorar archivos no resolubles
          }
        }
      }
    }
  }
}
