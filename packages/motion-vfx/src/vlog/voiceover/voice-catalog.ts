import {
  UnsupportedLocaleError,
  VoiceNotAvailableError,
} from "../contracts/errors.js";
import { SupportedLocale, VoiceProfile } from "../contracts/language.types.js";
import { SUPPORTED_LOCALES } from "../contracts/vlog.constants.js";

/** Estado de disponibilidad de una voz en el sistema */
export type VoiceAvailabilityStatus = "SUPPORTED" | "AVAILABLE" | "UNAVAILABLE";

/** Entrada completa de catálogo de voz */
export interface VoiceCatalogEntry extends VoiceProfile {
  modelName: string;
  channels: number;
  status: VoiceAvailabilityStatus;
  isDefault: boolean;
}

/** Catálogo maestro estático de voces soportadas para los 7 locales oficiales */
export const MASTER_VOICE_CATALOG: VoiceCatalogEntry[] = [
  // es-MX
  {
    id: "es_MX-ald-medium",
    name: "Aldo (México)",
    locale: "es-MX",
    gender: "MALE",
    engine: "piper",
    modelName: "es_MX-ald-medium.onnx",
    sampleRateHz: 44100,
    channels: 1,
    quality: "neural",
    status: "SUPPORTED",
    isDefault: true,
  },
  {
    id: "es_MX-claude-medium",
    name: "Claudia (México)",
    locale: "es-MX",
    gender: "FEMALE",
    engine: "piper",
    modelName: "es_MX-claude-medium.onnx",
    sampleRateHz: 44100,
    channels: 1,
    quality: "neural",
    status: "SUPPORTED",
    isDefault: false,
  },

  // es-ES
  {
    id: "es_ES-davefx-medium",
    name: "David (España)",
    locale: "es-ES",
    gender: "MALE",
    engine: "piper",
    modelName: "es_ES-davefx-medium.onnx",
    sampleRateHz: 44100,
    channels: 1,
    quality: "neural",
    status: "SUPPORTED",
    isDefault: true,
  },
  {
    id: "es_ES-sharvard-medium",
    name: "Sara (España)",
    locale: "es-ES",
    gender: "FEMALE",
    engine: "piper",
    modelName: "es_ES-sharvard-medium.onnx",
    sampleRateHz: 44100,
    channels: 1,
    quality: "neural",
    status: "SUPPORTED",
    isDefault: false,
  },

  // en-US
  {
    id: "en_US-lessac-medium",
    name: "Leslie (US)",
    locale: "en-US",
    gender: "FEMALE",
    engine: "piper",
    modelName: "en_US-lessac-medium.onnx",
    sampleRateHz: 44100,
    channels: 1,
    quality: "neural",
    status: "SUPPORTED",
    isDefault: true,
  },
  {
    id: "en_US-ryan-medium",
    name: "Ryan (US)",
    locale: "en-US",
    gender: "MALE",
    engine: "piper",
    modelName: "en_US-ryan-medium.onnx",
    sampleRateHz: 44100,
    channels: 1,
    quality: "neural",
    status: "SUPPORTED",
    isDefault: false,
  },

  // en-GB
  {
    id: "en_GB-alan-medium",
    name: "Alan (UK)",
    locale: "en-GB",
    gender: "MALE",
    engine: "piper",
    modelName: "en_GB-alan-medium.onnx",
    sampleRateHz: 44100,
    channels: 1,
    quality: "neural",
    status: "SUPPORTED",
    isDefault: true,
  },
  {
    id: "en_GB-southern_english_female-medium",
    name: "Emma (UK)",
    locale: "en-GB",
    gender: "FEMALE",
    engine: "piper",
    modelName: "en_GB-southern_english_female-medium.onnx",
    sampleRateHz: 44100,
    channels: 1,
    quality: "neural",
    status: "SUPPORTED",
    isDefault: false,
  },

  // pt-BR
  {
    id: "pt_BR-edresson-medium",
    name: "Edresson (Brasil)",
    locale: "pt-BR",
    gender: "MALE",
    engine: "piper",
    modelName: "pt_BR-edresson-medium.onnx",
    sampleRateHz: 44100,
    channels: 1,
    quality: "neural",
    status: "SUPPORTED",
    isDefault: true,
  },
  {
    id: "pt_BR-faber-medium",
    name: "Fabiana (Brasil)",
    locale: "pt-BR",
    gender: "FEMALE",
    engine: "piper",
    modelName: "pt_BR-faber-medium.onnx",
    sampleRateHz: 44100,
    channels: 1,
    quality: "neural",
    status: "SUPPORTED",
    isDefault: false,
  },

  // fr-FR
  {
    id: "fr_FR-siwis-medium",
    name: "Siwis (France)",
    locale: "fr-FR",
    gender: "FEMALE",
    engine: "piper",
    modelName: "fr_FR-siwis-medium.onnx",
    sampleRateHz: 44100,
    channels: 1,
    quality: "neural",
    status: "SUPPORTED",
    isDefault: true,
  },
  {
    id: "fr_FR-gilles-medium",
    name: "Gilles (France)",
    locale: "fr-FR",
    gender: "MALE",
    engine: "piper",
    modelName: "fr_FR-gilles-medium.onnx",
    sampleRateHz: 44100,
    channels: 1,
    quality: "neural",
    status: "SUPPORTED",
    isDefault: false,
  },

  // de-DE
  {
    id: "de_DE-thorsten-medium",
    name: "Thorsten (Deutschland)",
    locale: "de-DE",
    gender: "MALE",
    engine: "piper",
    modelName: "de_DE-thorsten-medium.onnx",
    sampleRateHz: 44100,
    channels: 1,
    quality: "neural",
    status: "SUPPORTED",
    isDefault: true,
  },
  {
    id: "de_DE-eva_k-medium",
    name: "Eva (Deutschland)",
    locale: "de-DE",
    gender: "FEMALE",
    engine: "piper",
    modelName: "de_DE-eva_k-medium.onnx",
    sampleRateHz: 44100,
    channels: 1,
    quality: "neural",
    status: "SUPPORTED",
    isDefault: false,
  },
];

/**
 * Catálogo Tipado de Voces Multilingües (Milestone 4-05).
 */
export class VoiceCatalog {
  private static catalog: VoiceCatalogEntry[] = [...MASTER_VOICE_CATALOG];

  public static getVoicesForLocale(locale: SupportedLocale): VoiceCatalogEntry[] {
    if (!SUPPORTED_LOCALES.includes(locale)) {
      throw new UnsupportedLocaleError(locale, SUPPORTED_LOCALES);
    }
    return this.catalog.filter((v) => v.locale === locale);
  }

  public static getDefaultVoice(locale: SupportedLocale): VoiceCatalogEntry {
    const voices = this.getVoicesForLocale(locale);
    const defaultVoice = voices.find((v) => v.isDefault) ?? voices[0];
    if (!defaultVoice) {
      throw new VoiceNotAvailableError(`default`, locale);
    }
    return defaultVoice;
  }

  public static getVoiceById(voiceId: string, locale?: SupportedLocale): VoiceCatalogEntry {
    const entry = this.catalog.find((v) => v.id === voiceId && (!locale || v.locale === locale));
    if (!entry) {
      throw new VoiceNotAvailableError(voiceId, locale ?? "any");
    }
    return entry;
  }

  public static setVoiceStatus(voiceId: string, status: VoiceAvailabilityStatus): void {
    const entry = this.catalog.find((v) => v.id === voiceId);
    if (entry) {
      entry.status = status;
    }
  }

  public static getAllVoices(): VoiceCatalogEntry[] {
    return [...this.catalog];
  }
}
