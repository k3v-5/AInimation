import crypto from "node:crypto";
import { UnsupportedLocaleError } from "../contracts/errors.js";
import { SupportedLocale } from "../contracts/language.types.js";
import {
  DEFAULT_TIME_EDITORIAL_SUBTITLE_STYLE,
  SubtitleMode,
  SubtitleStyle,
  SubtitleTrack,
  SubtitleTrackSchema,
} from "../contracts/subtitles.types.js";
import { VoiceoverTrack } from "../contracts/voiceover.types.js";
import { SUPPORTED_LOCALES, VlogAspectRatio } from "../contracts/vlog.constants.js";
import { KaraokeGenerationOptions, KaraokeGenerator } from "./karaoke-generator.js";

export interface SubtitleEngineOptions extends KaraokeGenerationOptions {
  mode?: SubtitleMode;
  style?: SubtitleStyle;
  aspectRatio?: VlogAspectRatio;
}

/**
 * Motor Central de Subtítulos Multilingües Vlog (Milestone 6-B).
 * Produce pistas de subtítulos completas y deterministas para los 7 locales oficiales
 * sincronizadas palabra por palabra con el voiceover y con formato TIME Editorial.
 */
export class VlogSubtitleEngine {
  public static generateTrack(
    trackId: string,
    voiceoverTrack: VoiceoverTrack,
    options: SubtitleEngineOptions = {}
  ): SubtitleTrack {
    const locale = voiceoverTrack.locale;
    if (!SUPPORTED_LOCALES.includes(locale)) {
      throw new UnsupportedLocaleError(locale, SUPPORTED_LOCALES);
    }

    const mode: SubtitleMode = options.mode ?? "KARAOKE";
    const style: SubtitleStyle = options.style ?? DEFAULT_TIME_EDITORIAL_SUBTITLE_STYLE;

    // 1. Extraer todos los word timings concatenados de los segmentos de voiceover
    const allWords = voiceoverTrack.segments.flatMap((seg) => seg.words);

    // 2. Generar cues karaoke sincronizados
    const cues = KaraokeGenerator.generateCues(allWords, locale, {
      ...options,
      style,
    });

    // 3. Generar hash SHA-256 determinista del contenido de los subtítulos
    const contentPayload = JSON.stringify({
      trackId,
      locale,
      mode,
      cueCount: cues.length,
      cues: cues.map((c) => ({
        start: c.startSeconds,
        end: c.endSeconds,
        text: c.text,
      })),
      style,
    });

    const checksumSha256 = crypto.createHash("sha256").update(contentPayload).digest("hex");

    const track: SubtitleTrack = {
      id: trackId,
      locale,
      mode,
      cues,
      style,
      checksumSha256,
    };

    // Validar formalmente con Zod
    SubtitleTrackSchema.parse(track);

    return track;
  }
}
