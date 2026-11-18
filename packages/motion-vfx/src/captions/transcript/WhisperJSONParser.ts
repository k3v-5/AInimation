import { CaptionParseError } from "../../errors/index.js";
import { CaptionDocument, CaptionSegment, CaptionTimingPrecision, CaptionWord } from "../types/index.js";

/**
 * Parser determinista para transcripciones de Whisper JSON (Fase 16 / 16.1).
 */
export class WhisperJSONParser {
  /**
   * Parsea un objeto o string JSON generado por OpenAI Whisper o WhisperX.
   */
  public static parse(jsonInput: string | Record<string, any>, documentId = "whisper_document"): CaptionDocument {
    let data: any;

    if (typeof jsonInput === "string") {
      try {
        data = JSON.parse(jsonInput);
      } catch (err: any) {
        throw new CaptionParseError(`Invalid JSON format: ${err?.message ?? String(err)}`);
      }
    } else if (typeof jsonInput === "object" && jsonInput !== null) {
      data = jsonInput;
    } else {
      throw new CaptionParseError("Whisper JSON input must be a JSON string or object.");
    }

    if (!data || typeof data !== "object") {
      throw new CaptionParseError("Whisper data must be a non-null object.");
    }

    const rawSegmentsList = Array.isArray(data.segments) ? data.segments : [];
    const parsedSegments: CaptionSegment[] = [];
    let hasRealWordTimings = false;

    for (let sIdx = 0; sIdx < rawSegmentsList.length; sIdx++) {
      const seg = rawSegmentsList[sIdx];
      if (!seg || typeof seg !== "object") continue;

      const start = Number(seg.start);
      const end = Number(seg.end);
      const text = String(seg.text ?? "").trim();

      if (isNaN(start) || isNaN(end) || !isFinite(start) || !isFinite(end) || start < 0) {
        throw new CaptionParseError(
          `Segment ${sIdx} has invalid timestamp numbers: start=${seg.start}, end=${seg.end}`,
          { segmentIndex: sIdx, segment: seg }
        );
      }

      if (end <= start) {
        throw new CaptionParseError(
          `Segment ${sIdx} end time (${end}s) must be strictly greater than start time (${start}s)`
        );
      }

      let words: CaptionWord[] = [];
      let segmentPrecision: CaptionTimingPrecision = "segment";

      if (Array.isArray(seg.words) && seg.words.length > 0) {
        segmentPrecision = "word";
        hasRealWordTimings = true;

        for (let wIdx = 0; wIdx < seg.words.length; wIdx++) {
          const w = seg.words[wIdx];
          if (!w || typeof w !== "object") continue;

          const wStart = Number(w.start ?? start);
          const wEnd = Number(w.end ?? end);
          const wText = String(w.word ?? w.text ?? "").trim();
          const confidence =
            w.probability !== undefined
              ? Number(w.probability)
              : w.confidence !== undefined
              ? Number(w.confidence)
              : undefined;

          if (isNaN(wStart) || isNaN(wEnd) || !isFinite(wStart) || !isFinite(wEnd)) {
            throw new CaptionParseError(
              `Word ${wIdx} in segment ${sIdx} has invalid timestamps: start=${w.start}, end=${w.end}`
            );
          }

          if (wText.length > 0) {
            words.push({
              id: `w_${sIdx}_${wIdx}`,
              text: wText,
              start: Number(wStart.toFixed(4)),
              end: Number(wEnd.toFixed(4)),
              index: wIdx,
              confidence: confidence !== undefined && isFinite(confidence) ? Math.max(0, Math.min(1, confidence)) : undefined,
            });
          }
        }
      } else if (text.length > 0) {
        // Fallback para segmentos sin timestamps detallados por palabra
        const rawWords = text.split(/\s+/).filter((w: string) => w.length > 0);
        const wordCount = rawWords.length;
        const wordDuration = wordCount > 0 ? (end - start) / wordCount : 0;

        words = rawWords.map((word: string, wIdx: number) => ({
          id: `w_${sIdx}_${wIdx}`,
          text: word,
          start: Number((start + wIdx * wordDuration).toFixed(4)),
          end: Number((start + (wIdx + 1) * wordDuration).toFixed(4)),
          index: wIdx,
        }));
      }

      parsedSegments.push({
        id: `seg_${sIdx}`,
        start: Number(start.toFixed(4)),
        end: Number(end.toFixed(4)),
        text,
        words,
        timingPrecision: segmentPrecision,
      });
    }

    // Ordenar cronológicamente
    parsedSegments.sort((a, b) => a.start - b.start);

    // Re-indexar deterministamente
    const normalizedSegments = parsedSegments.map((seg, sIdx) => ({
      ...seg,
      id: `seg_${sIdx}`,
      words: seg.words.map((w, wIdx) => ({
        ...w,
        id: `w_${sIdx}_${wIdx}`,
        index: wIdx,
      })),
    }));

    const totalDuration =
      normalizedSegments.length > 0
        ? Math.max(...normalizedSegments.map((s) => s.end))
        : 0;

    return {
      id: documentId,
      duration: Number(totalDuration.toFixed(4)),
      segments: normalizedSegments,
      timingPrecision: hasRealWordTimings ? "word" : "segment",
      metadata: {
        language: data.language ?? "unknown",
        model: data.model,
      },
      schemaVersion: "1.6.0",
    };
  }
}
