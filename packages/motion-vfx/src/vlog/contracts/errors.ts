import { MotionEngineError, ValidationError } from "../../errors/index.js";

/**
 * Error emitido cuando la estructura del proyecto Vlog no cumple el contrato o invariantes.
 */
export class InvalidVlogProjectError extends ValidationError {
  constructor(message: string, public readonly context?: Record<string, unknown>) {
    super(`Invalid Vlog Project: ${message}`);
  }
}

/**
 * Error emitido cuando los parámetros de configuración de producción son inválidos o están fuera de rango.
 */
export class InvalidVlogConfigurationError extends ValidationError {
  constructor(message: string, public readonly context?: Record<string, unknown>) {
    super(`Invalid Vlog Configuration: ${message}`);
  }
}

/**
 * Error emitido cuando se solicita un locale que no forma parte del catálogo soportado.
 */
export class UnsupportedLocaleError extends ValidationError {
  constructor(locale: string, supportedLocales: readonly string[]) {
    super(`Unsupported Locale '${locale}'. Officially supported locales are: ${supportedLocales.join(", ")}`);
  }
}

/**
 * Error emitido cuando una timeline o sus eventos temporales violan monotonía o integridad.
 */
export class InvalidTimelineError extends ValidationError {
  constructor(message: string, public readonly context?: Record<string, unknown>) {
    super(`Invalid Timeline: ${message}`);
  }
}

/**
 * Error emitido cuando el cálculo de adaptación elástica o anclas narrativas no puede resolverse.
 */
export class InvalidPacingError extends ValidationError {
  constructor(message: string, public readonly context?: Record<string, unknown>) {
    super(`Invalid Pacing: ${message}`);
  }
}

/**
 * Error emitido cuando un archivo multimedia no puede ser escaneado, probado o no cumple requisitos.
 */
export class InvalidMediaError extends ValidationError {
  constructor(message: string, public readonly context?: Record<string, unknown>) {
    super(`Invalid Media: ${message}`);
  }
}

/**
 * Error emitido cuando un artefacto producido por una fase del pipeline es corrupto o no concuerda con su hash.
 */
export class VlogArtifactError extends MotionEngineError {
  constructor(message: string, public readonly context?: Record<string, unknown>) {
    super(`Vlog Artifact Error: ${message}`);
  }
}

/**
 * Error emitido por esquemas Zod o validaciones sintácticas de contratos Vlog.
 */
export class VlogContractValidationError extends ValidationError {
  constructor(message: string, public readonly issues?: unknown[]) {
    super(`Vlog Contract Validation Failed: ${message}`);
  }
}

/** Error emitido cuando una voz solicitada no está disponible en el catálogo o sistema */
export class VoiceNotAvailableError extends ValidationError {
  constructor(voiceId: string, locale: string) {
    super(`Voice '${voiceId}' is not available for locale '${locale}'`);
  }
}

/** Error general de proveedor TTS */
export class TTSProviderError extends MotionEngineError {
  constructor(providerId: string, message: string) {
    super(`TTS Provider Error [${providerId}]: ${message}`);
  }
}

/** Error emitido cuando el modelo neuronal local del proveedor no está instalado en disco */
export class TTSModelMissingError extends MotionEngineError {
  constructor(providerId: string, modelName: string, expectedPath?: string) {
    super(`TTS Model Missing [${providerId}]: Model '${modelName}' not found on disk${expectedPath ? ` at '${expectedPath}'` : ""}`);
  }
}

/** Error emitido cuando un proveedor o proceso intenta violar la política offline estricta */
export class TTSOfflineViolationError extends MotionEngineError {
  constructor(providerId: string, attemptDescription: string) {
    super(`TTS Offline Violation [${providerId}]: Attempted network or non-offline operation: ${attemptDescription}`);
  }
}

/** Error emitido cuando una solicitud de síntesis TTS no cumple los requisitos sintácticos o de contenido */
export class TTSInvalidRequestError extends ValidationError {
  constructor(message: string) {
    super(`TTS Invalid Request: ${message}`);
  }
}

/** Error emitido cuando falla el proceso de síntesis de voz en el motor */
export class VoiceoverSynthesisError extends MotionEngineError {
  constructor(message: string, public readonly causeError?: unknown) {
    super(`Voiceover Synthesis Error: ${message}`);
  }
}

/** Error emitido cuando un archivo o buffer WAV viola la especificación PCM canónica o está corrupto */
export class InvalidWavError extends ValidationError {
  constructor(message: string) {
    super(`Invalid WAV Audio: ${message}`);
  }
}

/** Error emitido cuando falla la lectura, escritura o validación de caché de voz */
export class VoiceoverCacheError extends MotionEngineError {
  constructor(message: string) {
    super(`Voiceover Cache Error: ${message}`);
  }
}

/** Error emitido cuando los timings o alineaciones de palabras no cumplen la monotonía o tolerancias */
export class VoiceoverAlignmentError extends ValidationError {
  constructor(message: string) {
    super(`Voiceover Alignment Error: ${message}`);
  }
}

