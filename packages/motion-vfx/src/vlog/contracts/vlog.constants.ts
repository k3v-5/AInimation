/**
 * Constantes universales y canónicas para la expansión Vlog Multilingüe (v3.5.0).
 * Política de cero 'magic numbers': todos los umbrales numéricos y temporales
 * están explícitamente centralizados y documentados aquí.
 */

/** Locales oficialmente soportados por el motor multilingüe */
export const SUPPORTED_LOCALES = [
  "es-MX",
  "es-ES",
  "en-US",
  "en-GB",
  "pt-BR",
  "fr-FR",
  "de-DE",
] as const;

export type SupportedLocale = (typeof SUPPORTED_LOCALES)[number];

/** Categorías canónicas de clasificación editorial de metraje */
export const FOOTAGE_TYPES = [
  "A_ROLL",
  "B_ROLL",
  "ACTION",
  "TIMELAPSE",
  "SCREEN",
  "PHOTO",
  "OTHER",
  "UNKNOWN",
] as const;

export type FootageType = (typeof FOOTAGE_TYPES)[number];

/** Ratios de aspecto soportados */
export const SUPPORTED_ASPECT_RATIOS = [
  "16:9",
  "9:16",
  "1:1",
  "4:5",
  "21:9",
] as const;

export type VlogAspectRatio = (typeof SUPPORTED_ASPECT_RATIOS)[number];
export type VlogSupportedAspectRatio = VlogAspectRatio;

/**
 * Especificaciones de Formatos de Audio Diferenciados
 * (EXPLICIT_REQUIREMENT / DERIVED_REQUIREMENT)
 */
export const AUDIO_SPECS = {
  /** Formato para SFX procedurales y SoundBank (EXPLICIT_REQUIREMENT - Doc 04/11) */
  SFX: {
    sampleRate: 44100,
    bitDepth: 16,
    channels: 1, // Mono
    format: "wav",
  },
  /** Formato canónico para síntesis TTS neuronal local (EXPLICIT_REQUIREMENT - Doc 17 Sec 19) */
  VOICEOVER: {
    sampleRate: 44100,
    bitDepth: 16,
    channels: 1, // Mono
    format: "wav",
    targetLoudnessLufs: -16.0, // EBU R128 estándar para voz en internet
    truePeakLimitDb: -1.0,
  },
  /** Evaluación interna de buses de audio (IMPLEMENTATION_DETAIL) */
  INTERNAL_BUS: {
    sampleRate: 44100,
    bitDepth: 32, // Floating point interno
    channels: 2, // Stereo
  },
  /** Formato de entrega master por idioma (DERIVED_REQUIREMENT - Doc 11/20) */
  MASTER_DEFAULT: {
    sampleRate: 44100,
    bitDepth: 16,
    channels: 2, // Stereo
    ceilingDbFS: -1.0,
    truePeakCeilingDbTP: -1.0,
  },
} as const;

/**
 * Tolerancias de Sincronización Diferenciadas por Tipo
 * (EXPLICIT_REQUIREMENT)
 */
export const SYNC_TOLERANCES = {
  /** Tolerancia máxima para subtítulos palabra-a-palabra respecto a la voz (Doc 08 Sec 72) */
  SUBTITLE_WORD_DRIFT_SECONDS: 0.040, // ±40 ms
  /** Advertencia por deriva de alineación de segmento narrativo (Doc 18 Sec 65) */
  SEGMENT_ALIGNMENT_WARN_SECONDS: 0.100, // ±100 ms
  /** Fallo crítico por desalineación de segmento narrativo */
  SEGMENT_ALIGNMENT_FAIL_SECONDS: 0.250, // ±250 ms
  /** Margen de seguridad fonética en bordes de palabras para jump cuts (Doc 16 Sec 24) */
  WORD_BOUNDARY_SAFETY_SECONDS: 0.015, // ±15 ms
  /** Sincronía del efecto de obturador en Polaroid Freeze-Frame (Doc 19 Sec 60) */
  POLAROID_SFX_FRAME_TOLERANCE: 1, // ±1 frame
} as const;

/**
 * Constantes para VlogJumpCutEngine (EXPLICIT_REQUIREMENT - Doc 05 / 16)
 */
export const JUMP_CUT_DEFAULTS = {
  /** Umbral mínimo de silencio para corte (segundos) */
  SILENCE_THRESHOLD_SECONDS: 0.25, // 250 ms
  /** Duración mínima para considerar una pausa narrativa intencional y conservarla */
  NARRATIVE_PAUSE_MIN_SECONDS: 0.80, // 800 ms
  /** Micro-crossfade de audio obligatorio para evitar pops/clicks en cortes */
  MICRO_CROSSFADE_SECONDS: 0.010, // 10 ms
  /** Duración de respiración mínima detectable */
  BREATH_MIN_DURATION_SECONDS: 0.15,
  /** Duración de respiración máxima detectable */
  BREATH_MAX_DURATION_SECONDS: 0.60,
  /** Atenuación en decibelios para respiraciones conservadas */
  BREATH_ATTENUATION_DB: -6.0,
} as const;

/**
 * Constantes para DynamicPunchIn (EXPLICIT_REQUIREMENT - Doc 05 / 16)
 */
export const PUNCH_IN_DEFAULTS = {
  NORMAL_SCALE: 1.0,
  STANDARD_PUNCH_SCALE: 1.15, // 115%
  MICRO_PUNCH_SCALE: 1.12, // 112% para eventos breves
  MAX_SCALE_CEILING: 1.20, // 120% límite seguro
  HOLD_MIN_DURATION_SECONDS: 0.35,
  HOLD_MAX_DURATION_SECONDS: 2.50,
  COOLDOWN_SECONDS: 3.0,
  MAX_DENSITY_PER_MINUTE: 12,
  FOCAL_SMOOTHING_ALPHA: 0.20,
} as const;

/**
 * Constantes para VlogAdaptivePacingEngine (EXPLICIT_REQUIREMENT - Doc 08 / 18)
 */
export const PACING_DEFAULTS = {
  /** Rango elástico automático de time-stretch vocal */
  AUTOMATIC_STRETCH_MIN: 0.95,
  AUTOMATIC_STRETCH_MAX: 1.05,
  /** Límite duro absoluto permitido únicamente ante override explícito del usuario */
  HARD_STRETCH_LIMIT_MIN: 0.85,
  HARD_STRETCH_LIMIT_MAX: 1.15,
  /** B-Roll: extensión máxima permitida antes de advertencia */
  BROLL_MAX_EXTENSION_RATIO: 1.50,
  /** B-Roll: compresión máxima permitida antes de advertencia */
  BROLL_MAX_COMPRESSION_RATIO: 0.70,
} as const;

/**
 * Ponderaciones canónicas de Scoring para B-Roll Matcher (Doc 15)
 */
export const BROLL_SCORING_WEIGHTS = {
  SEMANTIC: 0.30,
  ENTITY: 0.20,
  VISUAL: 0.15,
  LOCATION: 0.10,
  ACTIVITY: 0.10,
  QUALITY: 0.05,
  DURATION: 0.05,
  CONTINUITY: 0.05,
} as const;

/**
 * Constantes Geodésicas para Mapas y Distancias (Doc 12 / 19)
 */
export const GEODESIC_CONSTANTS = {
  /** Radio medio de la Tierra (radio canónico para la fórmula Haversine) en kilómetros */
  EARTH_MEAN_RADIUS_KM: 6371.0088,
  EARTH_RADIUS_KM: 6371.0088, // Compatibilidad
} as const;

/**
 * Constantes para Mezclador de Audio y Ducking (Doc 11 / 16)
 */
export const AUDIO_MIX_DEFAULTS = {
  /** Atenuación de música cuando hay diálogo activo */
  MUSIC_DUCKING_DB: -10.0,
  /** Tiempo de ataque para entrar a ducking (segundos) */
  DUCKING_ATTACK_SECONDS: 0.12,
  /** Tiempo de relajación tras finalizar el diálogo (segundos) */
  DUCKING_RELEASE_SECONDS: 0.40,
} as const;

/**
 * Tolerancia matemática general para comparación de puntos flotantes
 */
export const EPSILON = 1e-10;
