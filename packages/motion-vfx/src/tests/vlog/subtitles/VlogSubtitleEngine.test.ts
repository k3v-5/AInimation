import assert from "node:assert/strict";
import { describe, it } from "node:test";
import fc from "fast-check";
import {
  SubtitleTrackSchema,
  SUPPORTED_LOCALES,
  SupportedLocale,
  VlogSubtitleEngine,
  VoiceoverTrack,
} from "../../../vlog/index.js";

describe("Milestone 6-B — Vlog Subtitle Engine Suite", () => {
  const createMockVoiceoverTrack = (locale: SupportedLocale = "es-MX"): VoiceoverTrack => ({
    id: `vo_${locale}_test`,
    locale,
    voiceId: "mock_voice",
    audioWavPath: "audio.wav",
    durationSeconds: 3.5,
    checksumSha256: "b".repeat(64),
    format: {
      sampleRateHz: 44100,
      bitDepth: 16,
      channels: 1,
    },
    segments: [
      {
        narrativeSegmentId: "seg_01",
        speechText: "Bienvenidos a México.",
        displayText: "Bienvenidos a México.",
        startSeconds: 0.0,
        endSeconds: 3.5,
        durationSeconds: 3.5,
        words: [
          { word: "Bienvenidos", startSeconds: 0.0, endSeconds: 1.0, confidence: 0.99 },
          { word: "a", startSeconds: 1.0, endSeconds: 1.3, confidence: 0.99 },
          { word: "México", startSeconds: 1.3, endSeconds: 2.2, confidence: 0.99 },
        ],
      },
    ],
  });

  it("generates valid SubtitleTrack adhering to schema for all 7 locales", () => {
    for (const loc of SUPPORTED_LOCALES) {
      const vo = createMockVoiceoverTrack(loc);
      const subTrack = VlogSubtitleEngine.generateTrack(`sub_${loc}`, vo);

      assert.equal(subTrack.locale, loc);
      assert.ok(subTrack.cues.length >= 1);
      assert.equal(subTrack.style.highlightFillColor, "#FF1424");
      assert.equal(subTrack.checksumSha256.length, 64);
      assert.doesNotThrow(() => SubtitleTrackSchema.parse(subTrack));
    }
  });

  it("guarantees idempotency: same VoiceoverTrack generates identical checksum", () => {
    const vo = createMockVoiceoverTrack("en-US");
    const sub1 = VlogSubtitleEngine.generateTrack("sub_track_id", vo);
    const sub2 = VlogSubtitleEngine.generateTrack("sub_track_id", vo);

    assert.equal(sub1.checksumSha256, sub2.checksumSha256);
    assert.deepEqual(sub1, sub2);
  });

  it("PBT: cue startSeconds is strictly <= endSeconds and cues are temporally ordered", () => {
    fc.assert(
      fc.property(
        fc.array(fc.stringMatching(/^[a-zA-Z]{3,8}$/), { minLength: 3, maxLength: 12 }),
        (words) => {
          let time = 0.0;
          const timings = words.map((w) => {
            const start = time;
            const end = time + 0.3;
            time = end + 0.05;
            return { word: w, startSeconds: start, endSeconds: end, confidence: 0.99 };
          });

          const vo: VoiceoverTrack = {
            id: "vo_pbt",
            locale: "es-MX",
            voiceId: "mock",
            audioWavPath: "a.wav",
            durationSeconds: time,
            checksumSha256: "c".repeat(64),
            format: { sampleRateHz: 44100, bitDepth: 16, channels: 1 },
            segments: [
              {
                narrativeSegmentId: "s1",
                speechText: words.join(" "),
                displayText: words.join(" "),
                startSeconds: 0,
                endSeconds: time,
                durationSeconds: time,
                words: timings,
              },
            ],
          };

          const sub = VlogSubtitleEngine.generateTrack("sub_pbt", vo);
          for (let i = 0; i < sub.cues.length; i++) {
            const cue = sub.cues[i];
            assert.ok(cue.startSeconds <= cue.endSeconds);
            if (i > 0) {
              assert.ok(cue.startSeconds >= sub.cues[i - 1].startSeconds);
            }
          }
        }
      )
    );
  });
});
