import { describe, it } from "node:test";
import assert from "node:assert/strict";
import fc from "fast-check";
import { EditorialIR } from "../../editorial/ir/editorial-ir.types.js";
import { OtioExporter } from "../../editorial/exporters/otio-exporter.js";
import { OtioImporter } from "../../editorial/exporters/otio-importer.js";
import { OtioTimeEngine, STANDARD_FRAMERATES } from "../../editorial/exporters/otio-time.js";

describe("P1 — OpenTimelineIO (OTIO v1) Backend Bridge & Round-Trip Suite (REQ-036)", () => {
  const sampleIR: EditorialIR = {
    schemaVersion: "4.0.0",
    projectId: "otio_test_project",
    createdAt: "2026-09-02T12:00:00.000Z",
    checksum: "a".repeat(64),
    metadata: {
      title: "Documentary Master",
      profile: "DOCUMENTARY",
      frameRate: 24,
      width: 1920,
      height: 1080,
      sampleRate: 48000,
      targetDialogueLufs: -16,
    },
    tracks: [
      {
        id: "v1",
        name: "Video 1",
        type: "VIDEO_PRIMARY",
        index: 0,
        isMuted: false,
        isLocked: false,
        clips: [
          {
            id: "clip_01",
            assetId: "media/interview_01.mov",
            label: "Interview 1",
            sourceRange: { startSeconds: 1.0, durationSeconds: 5.0 },
            timelineRange: { startSeconds: 0.0, durationSeconds: 5.0 },
            speed: 1.0,
            volumeDb: 0.0,
            pan: 0.0,
            scale: 1.0,
          },
          {
            id: "clip_02",
            assetId: "media/broll_city.mov",
            label: "City B-Roll",
            sourceRange: { startSeconds: 0.0, durationSeconds: 4.0 },
            timelineRange: { startSeconds: 6.0, durationSeconds: 4.0 }, // 1.0s gap
            speed: 1.0,
            volumeDb: 0.0,
            pan: 0.0,
            scale: 1.0,
          },
        ],
      },
      {
        id: "a1",
        name: "Audio 1",
        type: "AUDIO_DIALOGUE",
        index: 1,
        isMuted: false,
        isLocked: false,
        clips: [
          {
            id: "audio_01",
            assetId: "media/interview_audio.wav",
            label: "Voice Track",
            sourceRange: { startSeconds: 1.0, durationSeconds: 5.0 },
            timelineRange: { startSeconds: 0.0, durationSeconds: 5.0 },
            speed: 1.0,
            volumeDb: 0.0,
            pan: 0.0,
            scale: 1.0,
          },
        ],
      },
    ],
    transitions: [],
    markers: [],
  };

  it("exports valid OTIO JSON structure conforming to Timeline.1 schema", () => {
    const json = OtioExporter.exportToOtioJson(sampleIR);
    assert.ok(json.length > 0);

    const parsed = JSON.parse(json);
    assert.equal(parsed.OTIO_SCHEMA, "Timeline.1");
    assert.equal(parsed.name, "Documentary Master");
    assert.equal(parsed.tracks.OTIO_SCHEMA, "Stack.1");
    assert.equal(parsed.tracks.children.length, 2);
  });

  it("performs full round-trip (IR -> OTIO -> IR) preserving clip count and temporal ranges", () => {
    const json = OtioExporter.exportToOtioJson(sampleIR);
    const { ir: importedIR } = OtioImporter.importFromOtioJson(json);

    assert.equal(importedIR.metadata.title, sampleIR.metadata.title);
    assert.equal(importedIR.metadata.frameRate, sampleIR.metadata.frameRate);
    assert.equal(importedIR.tracks.length, sampleIR.tracks.length);

    // Track 1 (Video) has 2 clips
    const vTrack = importedIR.tracks[0];
    assert.equal(vTrack.clips.length, 2);
    assert.equal(vTrack.clips[0].assetId, "media/interview_01.mov");
    assert.equal(vTrack.clips[0].timelineRange.startSeconds, 0.0);
    assert.equal(vTrack.clips[0].timelineRange.durationSeconds, 5.0);

    // Clip 2 starts at 6.0 (preserving gap)
    assert.equal(vTrack.clips[1].assetId, "media/broll_city.mov");
    assert.equal(vTrack.clips[1].timelineRange.startSeconds, 6.0);
    assert.equal(vTrack.clips[1].timelineRange.durationSeconds, 4.0);
  });

  it("validates round-trip across all 8 standard framerates without precision drift", () => {
    const fpsList = [23.976, 24, 25, 29.97, 30, 50, 59.94, 60];

    for (const fps of fpsList) {
      const customIR: EditorialIR = {
        ...sampleIR,
        metadata: { ...sampleIR.metadata, frameRate: fps },
      };

      const json = OtioExporter.exportToOtioJson(customIR);
      const { ir: roundtripIR } = OtioImporter.importFromOtioJson(json);

      assert.equal(roundtripIR.metadata.frameRate, fps);
      assert.equal(roundtripIR.tracks[0].clips.length, 2);

      // Verify rational time roundtrip
      const frames = OtioTimeEngine.secondsToFrames(5.0, fps);
      const seconds = OtioTimeEngine.framesToSeconds(frames, fps);
      assert.ok(Math.abs(seconds - 5.0) < 0.05);
    }
  });

  it("throws explicit OTIO errors upon malformed JSON or invalid schema", () => {
    assert.throws(
      () => OtioImporter.importFromOtioJson("{ invalid json"),
      /OTIO_PARSE_ERROR/
    );

    assert.throws(
      () => OtioImporter.importFromOtioJson(JSON.stringify({ OTIO_SCHEMA: "Timeline.2" })),
      /OTIO_SCHEMA_ERROR/
    );
  });

  it("guarantees byte-level determinism on identical inputs", () => {
    const json1 = OtioExporter.exportToOtioJson(sampleIR);
    const json2 = OtioExporter.exportToOtioJson(sampleIR);
    assert.equal(json1, json2);
  });

  it("PBT: rational time frames-to-seconds round-trip is strictly reversible", () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 1, max: 10000 }),
        fc.constantFrom(23.976, 24, 25, 29.97, 30, 50, 59.94, 60),
        (frames, fps) => {
          const seconds = OtioTimeEngine.framesToSeconds(frames, fps);
          const computedFrames = OtioTimeEngine.secondsToFrames(seconds, fps);
          return computedFrames === frames;
        }
      ),
      { numRuns: 100 }
    );
  });
});
