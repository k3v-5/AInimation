import { generateDeterministicLayerId } from "../../core/id.js";
import { Asset } from "../Asset.js";
import { AssetType } from "../types.js";
import { MediaMetadataProbe } from "../core/MediaMetadataProbe.js";

/**
 * Importador de recursos multimedia (Fase 5A).
 * Detecta tipos de archivo, extrae metadatos y crea registros de activos sin decodificar píxeles.
 */
export class AssetImporter {
  /**
   * Importa un archivo a partir de su ruta del sistema de archivos o URI.
   */
  public static importFromPath(filePath: string, options: Partial<Asset> = {}): Asset {
    const filename = filePath.split(/[/\\]/).pop() ?? filePath;
    const ext = filename.includes(".") ? filename.split(".").pop()!.toLowerCase() : "";

    const type = options.type ?? this.detectTypeFromExtension(ext);
    const id = options.id ?? `asset_${generateDeterministicLayerId()}`;
    const name = options.name ?? filename;

    // Extraer metadatos reales mediante inspección binaria si existe el archivo
    const probed = MediaMetadataProbe.probe(filePath);
    const defaultMeta = this.createDefaultMetadata(type, ext);

    return {
      id,
      type,
      name,
      source: {
        path: filePath,
        ...options.source,
      },
      metadata: {
        ...defaultMeta,
        ...probed,
        ...(options.metadata ?? {}),
      },
      status: options.status ?? "ready",
    };
  }

  /**
   * Detecta el tipo de asset según la extensión del archivo.
   */
  public static detectTypeFromExtension(extension: string): AssetType {
    const ext = extension.toLowerCase();

    if (["mp4", "mov", "webm", "avi", "mkv", "m4v"].includes(ext)) {
      return "video";
    }

    if (["png", "jpg", "jpeg", "webp", "gif", "bmp", "tiff"].includes(ext)) {
      return "image";
    }

    if (["wav", "mp3", "aac", "flac", "ogg", "m4a"].includes(ext)) {
      return "audio";
    }

    if (["ttf", "otf", "woff", "woff2"].includes(ext)) {
      return "font";
    }

    if (["svg"].includes(ext)) {
      return "svg";
    }

    return "unknown";
  }

  private static createDefaultMetadata(type: AssetType, ext: string): Record<string, unknown> {
    switch (type) {
      case "video":
        return {
          width: 1920,
          height: 1080,
          duration: 10.0,
          fps: 30,
          hasAudio: true,
          codec: "h264",
        };
      case "image":
        return {
          width: 1920,
          height: 1080,
          format: ext || "png",
        };
      case "audio":
        return {
          duration: 10.0,
          sampleRate: 44100,
          channels: 2,
        };
      case "font":
        return {
          family: "CustomFont",
          style: "regular",
          weight: 400,
          format: ext || "ttf",
        };
      case "svg":
        return {
          width: 100,
          height: 100,
          viewBox: "0 0 100 100",
        };
      default:
        return {};
    }
  }
}
