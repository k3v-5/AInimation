import { CaptionValidationError } from "../../errors/index.js";
import { CaptionDocument, CaptionSegment, CaptionWord } from "../types/index.js";

/**
 * Normalizador determinista e idempotente para CaptionDocument (Fase 16 / 16.1).
 */
export class CaptionNormalizer {
  /**
   * Normaliza un CaptionDocument garantizando validez estructural e idempotencia:
   * normalize(normalize(doc)) === normalize(doc)
   */
  public static normalize(doc: CaptionDocument): CaptionDocument {
    if (!doc || typeof doc !== "object") {
      throw new CaptionValidationError("CaptionDocument must be a valid object.");
    }

    const segmentsInput = Array.isArray(doc.segments) ? doc.segments : [];
    const normalizedSegments: CaptionSegment[] = [];

    for (let sIdx = 0; sIdx < segmentsInput.length; sIdx++) {
      const seg = segmentsInput[sIdx];
      if (!seg) continue;

      const rawStart = Number(seg.start);
      const rawEnd = Number(seg.end);

      if (isNaN(rawStart) || isNaN(rawEnd) || !isFinite(rawStart) || !isFinite(rawEnd) || rawStart < 0) {
        throw new CaptionValidationError(
          `Segment ${sIdx} contains invalid timestamp values: start=${seg.start}, end=${seg.end}`
        );
      }

      if (rawEnd <= rawStart) {
        throw new CaptionValidationError(
          `Segment ${sIdx} end time (${rawEnd}s) must be strictly greater than start time (${rawStart}s)`
        );
      }

      const start = Number(rawStart.toFixed(4));
      const end = Number(rawEnd.toFixed(4));
      const text = this.normalizeText(seg.text ?? "");

      const rawWords = Array.isArray(seg.words) ? seg.words : [];
      const normalizedWords: CaptionWord[] = [];

      for (let wIdx = 0; wIdx < rawWords.length; wIdx++) {
        const w = rawWords[wIdx];
        if (!w) continue;

        const wStartRaw = Number(w.start);
        const wEndRaw = Number(w.end);

        if (isNaN(wStartRaw) || isNaN(wEndRaw) || !isFinite(wStartRaw) || !isFinite(wEndRaw)) {
          throw new CaptionValidationError(
            `Word ${wIdx} in segment ${sIdx} contains invalid timestamps: start=${w.start}, end=${w.end}`
          );
        }

        // Clamp suave de timestamps de palabra dentro de los límites del segmento
        const wStart = Number(Math.max(start, Math.min(end, wStartRaw)).toFixed(4));
        const wEnd = Number(Math.max(wStart, Math.min(end, wEndRaw)).toFixed(4));
        const wText = this.normalizeText(w.text ?? "");

        if (wText.length > 0) {
          normalizedWords.push({
            id: `w_${sIdx}_${wIdx}`,
            text: wText,
            start: wStart,
            end: wEnd >= wStart ? wEnd : Number((wStart + 0.05).toFixed(4)),
            index: wIdx,
            confidence: w.confidence !== undefined ? Math.max(0, Math.min(1, Number(w.confidence))) : undefined,
            prosody: w.prosody ? { ...w.prosody } : undefined,
            emphasis: w.emphasis ? { ...w.emphasis } : undefined,
            animation: w.animation ? { ...w.animation } : undefined,
            styleOverride: w.styleOverride ? { ...w.styleOverride } : undefined,
          });
        }
      }

      // Si no había palabras pero sí texto en el segmento, desglosar deterministamente
      if (normalizedWords.length === 0 && text.length > 0) {
        const tokens = text.split(/\s+/).filter((t) => t.length > 0);
        const durationPerWord = tokens.length > 0 ? (end - start) / tokens.length : 0;

        for (let tIdx = 0; tIdx < tokens.length; tIdx++) {
          const tStart = Number((start + tIdx * durationPerWord).toFixed(4));
          const tEnd = Number((start + (tIdx + 1) * durationPerWord).toFixed(4));
          normalizedWords.push({
            id: `w_${sIdx}_${tIdx}`,
            text: tokens[tIdx],
            start: tStart,
            end: tEnd,
            index: tIdx,
          });
        }
      }

      normalizedSegments.push({
        id: `seg_${sIdx}`,
        start,
        end,
        text,
        words: normalizedWords,
        timingPrecision: seg.timingPrecision ?? (doc.timingPrecision ?? "segment"),
      });
    }

    // Ordenar cronológicamente
    normalizedSegments.sort((a, b) => a.start - b.start);

    // Re-indexar deterministamente los identificadores secuenciales estables
    const finalSegments = normalizedSegments.map((s, sIdx) => ({
      ...s,
      id: `seg_${sIdx}`,
      words: s.words.map((w, wIdx) => ({
        ...w,
        id: `w_${sIdx}_${wIdx}`,
        index: wIdx,
      })),
    }));

    const maxEnd = finalSegments.length > 0 ? Math.max(...finalSegments.map((s) => s.end)) : 0;
    const duration = doc.duration > 0 ? Number(doc.duration.toFixed(4)) : Number(maxEnd.toFixed(4));

    return {
      id: doc.id || "normalized_document",
      duration: Math.max(duration, Number(maxEnd.toFixed(4))),
      segments: finalSegments,
      timingPrecision: doc.timingPrecision ?? "segment",
      defaultStyle: doc.defaultStyle ? { ...doc.defaultStyle } : undefined,
      safeZoneProfile: doc.safeZoneProfile,
      metadata: doc.metadata ? { ...doc.metadata } : undefined,
      schemaVersion: "1.6.0",
    };
  }

  /**
   * Normaliza cadenas de texto Unicode sin corromper caracteres diacríticos ni secuencias complejas de emojis (ZWJ).
   */
  public static normalizeText(input: string): string {
    if (!input) return "";
    return input
      .normalize("NFC")
      .replace(/[\u200B\uFEFF]/g, "") // Limpiar zero-width spaces y BOM sin eliminar ZWJ (\u200D)
      .replace(/\s+/g, " ") // Colapsar múltiples espacios
      .trim();
  }
}
