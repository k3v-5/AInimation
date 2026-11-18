/**
 * Jerarquía de errores tipados para el Motion Engine.
 */

export class MotionEngineError extends Error {
  constructor(message: string) {
    super(message);
    this.name = this.constructor.name;
    Object.setPrototypeOf(this, new.target.prototype);
  }
}

export class ValidationError extends MotionEngineError {
  constructor(message: string) {
    super(`Validation Error: ${message}`);
  }
}

export class InvalidTimeError extends ValidationError {
  constructor(time: unknown, reason = "Time must be a finite non-negative number") {
    super(`Invalid Time '${String(time)}': ${reason}`);
  }
}

export class InvalidKeyframeError extends ValidationError {
  constructor(message: string) {
    super(`Invalid Keyframe: ${message}`);
  }
}

export class DuplicateLayerError extends ValidationError {
  constructor(layerId: string) {
    super(`A layer with id '${layerId}' already exists in the composition.`);
  }
}

export class LayerNotFoundError extends ValidationError {
  constructor(layerId: string) {
    super(`Layer with id '${layerId}' was not found.`);
  }
}

export class AssetNotFoundError extends ValidationError {
  constructor(assetId: string) {
    super(`Asset with id '${assetId}' was not found in registry.`);
  }
}

export class HierarchyCycleError extends ValidationError {
  constructor(message: string) {
    super(`Hierarchy Cycle: ${message}`);
  }
}

export class SerializationError extends MotionEngineError {
  constructor(message: string) {
    super(`Serialization Error: ${message}`);
  }
}

export class CaptionParseError extends MotionEngineError {
  constructor(message: string, public readonly context?: Record<string, any>) {
    super(`Caption Parse Error: ${message}`);
  }
}

export class CaptionValidationError extends ValidationError {
  constructor(message: string, public readonly context?: Record<string, any>) {
    super(`Caption Validation Error: ${message}`);
  }
}

export class CaptionLayoutError extends MotionEngineError {
  constructor(message: string, public readonly context?: Record<string, any>) {
    super(`Caption Layout Error: ${message}`);
  }
}

export class SafeZoneResolutionError extends MotionEngineError {
  constructor(message: string, public readonly context?: Record<string, any>) {
    super(`SafeZone Resolution Error: ${message}`);
  }
}

export class CaptionPresetError extends ValidationError {
  constructor(message: string, public readonly context?: Record<string, any>) {
    super(`Caption Preset Error: ${message}`);
  }
}

export class CaptionSerializationError extends SerializationError {
  constructor(message: string, public readonly context?: Record<string, any>) {
    super(`Caption Serialization Error: ${message}`);
  }
}

export * from "./runtime-errors.js";
