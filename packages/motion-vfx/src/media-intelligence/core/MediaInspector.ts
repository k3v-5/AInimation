import { ValidationError } from "../../errors/index.js";
import { AssetMetadata, AssetSource, AssetType } from "../types/index.js";

/**
 * Inspector y validador de formatos y metadatos multimedia (Fase 6).
 */
export class MediaInspector {
  public static inferTypeFromFilename(filename: string): AssetType {
    const ext = filename.split(".").pop()?.toLowerCase() ?? "";

    switch (ext) {
      case "mp4":
      case "mov":
      case "webm":
      case "mkv":
        return "video";
      case "mp3":
      case "wav":
      case "aac":
      case "ogg":
      case "flac":
        return "audio";
      case "png":
      case "jpg":
      case "jpeg":
      case "webp":
        return "image";
      case "ttf":
      case "otf":
      case "woff2":
        return "font";
      case "srt":
      case "vtt":
        return "subtitle";
      case "svg":
        return "graphic";
      default:
        return "sequence";
    }
  }

  public static validateMetadata(metadata: AssetMetadata): void {
    if (!metadata.filename) {
      throw new ValidationError("AssetMetadata requires a valid filename.");
    }
    if (metadata.width !== undefined && metadata.width <= 0) {
      throw new ValidationError("Asset width must be positive.");
    }
    if (metadata.height !== undefined && metadata.height <= 0) {
      throw new ValidationError("Asset height must be positive.");
    }
    if (metadata.duration !== undefined && metadata.duration < 0) {
      throw new ValidationError("Asset duration cannot be negative.");
    }
  }

  public static createDefaultMetadata(source: AssetSource): AssetMetadata {
    const filename = source.uri.split(/[/\\]/).pop() ?? "unnamed_file";
    const type = this.inferTypeFromFilename(filename);

    return {
      filename,
      mimeType: `${type}/${filename.split(".").pop() ?? "octet-stream"}`,
      duration: type === "video" || type === "audio" ? 10.0 : undefined,
      width: type === "video" || type === "image" ? 1920 : undefined,
      height: type === "video" || type === "image" ? 1080 : undefined,
      frameRate: type === "video" ? 30 : undefined,
      sampleRate: type === "audio" || type === "video" ? 48000 : undefined,
      channels: type === "audio" || type === "video" ? 2 : undefined,
    };
  }
}
