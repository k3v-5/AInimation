import { ValidationError } from "../errors/index.js";
import { validateId } from "../validation/validators.js";
import { Asset } from "./Asset.js";
import { AssetMetadata, AssetType, AudioMetadata, ImageMetadata, VideoMetadata } from "./types.js";

/**
 * Validador estricto para modelos de recursos y metadatos audiovisuales.
 */
export class AssetValidator {
  /**
   * Valida exhaustivamente un objeto Asset. Lanza ValidationError si no cumple los contratos.
   */
  public static validate(asset: unknown): asserts asset is Asset {
    if (!asset || typeof asset !== "object") {
      throw new ValidationError("Asset must be an object.");
    }

    const raw = asset as Partial<Asset>;
    const id = validateId(raw.id, "asset.id");

    const validTypes: AssetType[] = ["image", "video", "audio", "font", "svg"];
    if (!raw.type || !validTypes.includes(raw.type)) {
      throw new ValidationError(`Invalid asset type '${String(raw.type)}'. Expected one of [${validTypes.join(", ")}].`);
    }

    if (!raw.source || typeof raw.source !== "object" || !raw.source.path || typeof raw.source.path !== "string" || !raw.source.path.trim()) {
      throw new ValidationError(`Asset '${id}' must have a valid source object with a non-empty 'path'.`);
    }

    this.validateMetadata(raw.type as AssetType, raw.metadata);
  }

  /**
   * Valida la coherencia de los metadatos específicos por tipo de activo.
   */
  public static validateMetadata(type: AssetType, metadata?: AssetMetadata): void {
    if (!metadata) return;

    if (type === "image") {
      const img = metadata as ImageMetadata;
      if (img.width !== undefined && (typeof img.width !== "number" || !Number.isFinite(img.width) || img.width <= 0)) {
        throw new ValidationError("Image asset width must be a positive finite number (> 0).");
      }
      if (img.height !== undefined && (typeof img.height !== "number" || !Number.isFinite(img.height) || img.height <= 0)) {
        throw new ValidationError("Image asset height must be a positive finite number (> 0).");
      }
    } else if (type === "video") {
      const vid = metadata as VideoMetadata;
      if (vid.width !== undefined && (typeof vid.width !== "number" || !Number.isFinite(vid.width) || vid.width <= 0)) {
        throw new ValidationError("Video asset width must be a positive finite number (> 0).");
      }
      if (vid.height !== undefined && (typeof vid.height !== "number" || !Number.isFinite(vid.height) || vid.height <= 0)) {
        throw new ValidationError("Video asset height must be a positive finite number (> 0).");
      }
      if (vid.duration !== undefined && (typeof vid.duration !== "number" || !Number.isFinite(vid.duration) || vid.duration <= 0)) {
        throw new ValidationError("Video asset duration must be a positive finite number (> 0).");
      }
      if (vid.fps !== undefined && (typeof vid.fps !== "number" || !Number.isFinite(vid.fps) || vid.fps <= 0)) {
        throw new ValidationError("Video asset fps must be a positive finite number (> 0).");
      }
    } else if (type === "audio") {
      const aud = metadata as AudioMetadata;
      if (aud.duration !== undefined && (typeof aud.duration !== "number" || !Number.isFinite(aud.duration) || aud.duration <= 0)) {
        throw new ValidationError("Audio asset duration must be a positive finite number (> 0).");
      }
      if (aud.sampleRate !== undefined && (typeof aud.sampleRate !== "number" || !Number.isFinite(aud.sampleRate) || aud.sampleRate <= 0)) {
        throw new ValidationError("Audio asset sampleRate must be a positive finite number (> 0).");
      }
      if (aud.channels !== undefined && (typeof aud.channels !== "number" || !Number.isInteger(aud.channels) || aud.channels <= 0)) {
        throw new ValidationError("Audio asset channels must be a positive integer (> 0).");
      }
    }
  }
}
