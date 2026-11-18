import { generateDeterministicLayerId } from "../../core/id.js";
import { Time } from "../../core/types.js";
import { validateId } from "../../validation/validators.js";
import { Caption, CaptionWord } from "../types/index.js";

export interface CaptionTrackOptions {
  id?: string;
  name?: string;
  captions?: Caption[];
}

/**
 * Pista de subtítulos en la línea de tiempo (Fase 5E).
 */
export class CaptionTrack {
  public readonly id: string;
  public name: string;
  private _captions: Caption[] = [];

  constructor(options: CaptionTrackOptions = {}) {
    this.id = options.id ? validateId(options.id, "captionTrack.id") : `ctrack_${generateDeterministicLayerId()}`;
    this.name = options.name ?? `Captions ${this.id}`;

    if (options.captions) {
      for (const c of options.captions) {
        this.addCaption(c);
      }
    }
  }

  public get captions(): Caption[] {
    return [...this._captions];
  }

  public get size(): number {
    return this._captions.length;
  }

  public addCaption(caption: Caption): this {
    this._captions.push(caption);
    this._captions.sort((a, b) => a.timelineRange.start - b.timelineRange.start);
    return this;
  }

  public getActiveCaption(globalTime: Time): Caption | undefined {
    return this._captions.find(
      (c) => globalTime >= c.timelineRange.start && globalTime < c.timelineRange.end
    );
  }

  public getActiveWord(caption: Caption, globalTime: Time): CaptionWord | undefined {
    return caption.words.find((w) => globalTime >= w.start && globalTime < w.end);
  }

  public getWordProgress(word: CaptionWord, globalTime: Time): number {
    if (globalTime < word.start) return 0;
    if (globalTime >= word.end) return 1;
    const dur = word.end - word.start;
    return dur > 0 ? (globalTime - word.start) / dur : 1;
  }

  public toJSON(): { id: string; name: string; captions: Caption[] } {
    return {
      id: this.id,
      name: this.name,
      captions: this._captions.map((c) => ({
        ...c,
        words: c.words.map((w) => ({ ...w })),
        style: { ...c.style },
      })),
    };
  }

  public static fromJSON(data: any): CaptionTrack {
    return new CaptionTrack({
      id: data.id,
      name: data.name,
      captions: data.captions,
    });
  }
}
