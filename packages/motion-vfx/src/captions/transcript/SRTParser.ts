import { CaptionParseError } from "../../errors/index.js";
import { CaptionDocument, CaptionSegment, CaptionWord } from "../types/index.js";

/**
 * Parser determinista y robusto para subtítulos en formato SRT (SubRip) (Fase 16 / 16.1).
 */
export class SRTParser {
  /**
   * Parsea una cadena de texto en formato SRT hacia un CaptionDocument canónico.
   * Nota arquitectónica: Los subtítulos SRT carecen de timestamps acústicos por palabra;
   * por contrato determinista, se declaran explícitamente con `timingPrecision: "segment"`.
   */
  public static parse(srtContent: string, documentId = "srt_document"): CaptionDocument {
    if (typeof srtContent !== "string") {
      throw new CaptionParseError("SRT input must be a string.");
    }

    // 1. Limpieza de BOM y normalización de saltos de línea (CRLF -> LF)
    let clean = srtContent.replace(/^\uFEFF/, "").replace(/\r\n/g, "\n").replace(/\r/g, "\n").trim();

    if (clean.length === 0) {
      return {
        id: documentId,
        duration: 0,
        segments: [],
        timingPrecision: "segment",
        schemaVersion: "1.6.0",
      };
    }

    // 2. Separar por bloques de cues (doble salto de línea o más)
    const blocks = clean.split(/\n\s*\n+/);
    const rawSegments: CaptionSegment[] = [];

    for (let blockIdx = 0; blockIdx < blocks.length; blockIdx++) {
      const block = blocks[blockIdx].trim();
      if (!block) continue;

      const lines = block.split("\n").map((l) => l.trim()).filter((l) => l.length > 0);
      if (lines.length === 0) continue;

      let timeLineIdx = 0;
      if (/^\d+$/.test(lines[0])) {
        timeLineIdx = 1;
      }

      if (timeLineIdx >= lines.length) {
        continue;
      }

      const timeLine = lines[timeLineIdx];
      const timeMatch = timeLine.match(
        /(\d{1,2}):(\d{2}):(\d{2})[,.](\d{1,3})\s*-->\s*(\d{1,2}):(\d{2}):(\d{2})[,.](\d{1,3})/
      );

      if (!timeMatch) {
        throw new CaptionParseError(
          `Invalid SRT timestamp format at block ${blockIdx + 1}: '${timeLine}'`,
          { blockIndex: blockIdx, line: timeLine }
        );
      }

      const start = this.parseTimestamp(timeMatch[1], timeMatch[2], timeMatch[3], timeMatch[4]);
      const end = this.parseTimestamp(timeMatch[5], timeMatch[6], timeMatch[7], timeMatch[8]);

      if (isNaN(start) || isNaN(end) || !isFinite(start) || !isFinite(end) || start < 0) {
        throw new CaptionParseError(`Invalid numeric timestamp values: start=${start}, end=${end}`);
      }

      if (end <= start) {
        throw new CaptionParseError(
          `SRT cue end time (${end}s) must be strictly greater than start time (${start}s) at block ${blockIdx + 1}`
        );
      }

      const textLines = lines.slice(timeLineIdx + 1);
      const fullText = textLines.join(" ").trim();
      if (!fullText) {
        continue;
      }

      // Segmentación de palabras con distribución temporal uniforme inferida
      const rawWords = fullText.split(/\s+/).filter((w) => w.length > 0);
      const wordCount = rawWords.length;
      const wordDuration = wordCount > 0 ? (end - start) / wordCount : 0;

      const words: CaptionWord[] = rawWords.map((word, wIdx) => ({
        id: `w_${blockIdx}_${wIdx}`,
        text: word,
        start: Number((start + wIdx * wordDuration).toFixed(4)),
        end: Number((start + (wIdx + 1) * wordDuration).toFixed(4)),
        index: wIdx,
      }));

      rawSegments.push({
        id: `seg_${blockIdx}`,
        start,
        end,
        text: fullText,
        words,
        timingPrecision: "segment",
      });
    }

    // 3. Ordenar cronológicamente si venían desordenados
    rawSegments.sort((a, b) => a.start - b.start);

    // 4. Re-asignar IDs deterministas secuenciales post-ordenamiento
    const normalizedSegments = rawSegments.map((seg, sIdx) => ({
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
      timingPrecision: "segment",
      schemaVersion: "1.6.0",
    };
  }

  private static parseTimestamp(h: string, m: string, s: string, ms: string): number {
    const hours = parseInt(h, 10);
    const minutes = parseInt(m, 10);
    const seconds = parseInt(s, 10);
    const millis = parseInt(ms.padEnd(3, "0").slice(0, 3), 10);
    return hours * 3600 + minutes * 60 + seconds + millis / 1000;
  }
}
