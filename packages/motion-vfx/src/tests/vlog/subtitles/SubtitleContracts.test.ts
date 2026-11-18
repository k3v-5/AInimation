import assert from "node:assert/strict";
import { describe, it } from "node:test";
import {
  DEFAULT_TIME_EDITORIAL_SUBTITLE_STYLE,
  SubtitleCueSchema,
  SubtitleStyleSchema,
  SubtitleTrackSchema,
  SubtitleWordSchema,
} from "../../../vlog/index.js";

describe("Milestone 6-A — Subtitle Contracts & Invariants Suite", () => {
  it("validates default TIME Editorial style adhering to USER_DESIGN_PREFERENCES", () => {
    assert.equal(DEFAULT_TIME_EDITORIAL_SUBTITLE_STYLE.fontFamily, "Impact");
    assert.equal(DEFAULT_TIME_EDITORIAL_SUBTITLE_STYLE.fillColor, "#FFFFFF");
    assert.equal(DEFAULT_TIME_EDITORIAL_SUBTITLE_STYLE.highlightFillColor, "#FF1424");
    assert.equal(DEFAULT_TIME_EDITORIAL_SUBTITLE_STYLE.textTransform, "uppercase");
    assert.equal(DEFAULT_TIME_EDITORIAL_SUBTITLE_STYLE.letterSpacing, -20);
    assert.equal(DEFAULT_TIME_EDITORIAL_SUBTITLE_STYLE.verticalStretchPercent, 135);

    assert.doesNotThrow(() => SubtitleStyleSchema.parse(DEFAULT_TIME_EDITORIAL_SUBTITLE_STYLE));
  });

  it("validates word and cue schemas with strict timing bounds", () => {
    const word = {
      word: "GUADALAJARA",
      startSeconds: 1.0,
      endSeconds: 1.5,
      isHighlighted: true,
      highlightColor: "#FF1424",
    };

    assert.doesNotThrow(() => SubtitleWordSchema.parse(word));

    const cue = {
      id: "cue_001",
      locale: "es-MX",
      startSeconds: 1.0,
      endSeconds: 2.5,
      text: "BIENVENIDOS A GUADALAJARA",
      words: [word],
      position: {
        normalizedX: 0.5,
        normalizedY: 0.85,
        alignment: "center" as const,
      },
    };

    assert.doesNotThrow(() => SubtitleCueSchema.parse(cue));
  });

  it("validates a full SubtitleTrack with SHA-256 checksum", () => {
    const track = {
      id: "sub_es-MX_proj1",
      locale: "es-MX",
      mode: "KARAOKE" as const,
      cues: [],
      style: DEFAULT_TIME_EDITORIAL_SUBTITLE_STYLE,
      checksumSha256: "e".repeat(64),
    };

    assert.doesNotThrow(() => SubtitleTrackSchema.parse(track));
  });
});
