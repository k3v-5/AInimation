export class DeliveryError extends Error {
  public readonly code: string;
  public readonly context?: Record<string, unknown>;

  constructor(message: string, code = "DELIVERY_ERROR", context?: Record<string, unknown>) {
    super(message);
    this.name = this.constructor.name;
    this.code = code;
    this.context = context;
    Object.setPrototypeOf(this, new.target.prototype);
  }
}

export class UnsupportedAspectRatioError extends DeliveryError {
  constructor(ratio: string, context?: Record<string, unknown>) {
    super(`Unsupported aspect ratio: ${ratio}`, "UNSUPPORTED_ASPECT_RATIO", { ratio, ...context });
  }
}

export class SafeZoneViolationError extends DeliveryError {
  constructor(platform: string, layerId: string, bounds: unknown, context?: Record<string, unknown>) {
    super(`Layer ${layerId} violates safe zone for platform ${platform}`, "SAFE_ZONE_VIOLATION", { platform, layerId, bounds, ...context });
  }
}

export class LoudnessOutOfRangeError extends DeliveryError {
  constructor(lufs: number, target: number, context?: Record<string, unknown>) {
    super(`Measured loudness (${lufs} LUFS) cannot be normalized to target (${target} LUFS)`, "LOUDNESS_OUT_OF_RANGE", { lufs, target, ...context });
  }
}

export class ThumbnailExtractionError extends DeliveryError {
  constructor(message: string, context?: Record<string, unknown>) {
    super(message, "THUMBNAIL_EXTRACTION_ERROR", context);
  }
}

export class PackagingIntegrityError extends DeliveryError {
  constructor(message: string, context?: Record<string, unknown>) {
    super(message, "PACKAGING_INTEGRITY_ERROR", context);
  }
}

export class InvalidPlatformProfileError extends DeliveryError {
  constructor(platform: string, context?: Record<string, unknown>) {
    super(`Invalid platform profile: ${platform}`, "INVALID_PLATFORM_PROFILE", { platform, ...context });
  }
}

export class DeliveryManifestError extends DeliveryError {
  constructor(message: string, context?: Record<string, unknown>) {
    super(message, "DELIVERY_MANIFEST_ERROR", context);
  }
}
