import test from "node:test";
import assert from "node:assert/strict";
import fc from "fast-check";
import {
  EditorialIRBuilder,
  EditorialIRSchema,
} from "../../editorial/index.js";

test("Fase 4C — Editorial IR Builder Suite", async (t) => {
  const baseMetadata = {
    title: "The Arctic Anomaly",
    profile: "DOCUMENTARY",
    frameRate: 30,
    width: 1920,
    height: 1080,
    sampleRate: 44100,
    targetDialogueLufs: -20,
  };

  await t.test("builds valid multi-track Editorial IR conforming to schema", () => {
    const builder = new EditorialIRBuilder("proj_arctic_01", baseMetadata);

    builder
      .createTrack({ id: "t_v1", name: "A-Roll Primary", type: "VIDEO_PRIMARY", index: 0 })
      .createTrack({ id: "t_v2", name: "B-Roll Cutaways", type: "VIDEO_BROLL", index: 1 })
      .createTrack({ id: "t_a1", name: "Dialogue Track", type: "AUDIO_DIALOGUE", index: 2 })
      .createTrack({ id: "t_a2", name: "Ambient Bed", type: "AUDIO_AMBIENCE", index: 3 });

    builder.addClip("t_v1", {
      id: "clip_interview_01",
      assetId: "assets/interview_scientist.mp4",
      label: "Interview Scientist A",
      sourceRange: { startSeconds: 10.0, durationSeconds: 5.0 },
      timelineRange: { startSeconds: 0.0, durationSeconds: 5.0 },
    });

    builder.addClip("t_v2", {
      id: "clip_broll_glacier",
      assetId: "assets/glacier_aerial.mp4",
      label: "Glacier Aerial",
      sourceRange: { startSeconds: 0.0, durationSeconds: 4.0 },
      timelineRange: { startSeconds: 5.0, durationSeconds: 4.0 },
    });

    builder.addMarker({
      id: "m_chapter_1",
      timestampSeconds: 0.0,
      name: "Chapter 1: The Melt",
      color: "#FF0000",
    });

    const ir = builder.build();

    assert.equal(ir.projectId, "proj_arctic_01");
    assert.equal(ir.tracks.length, 4);
    assert.equal(ir.markers.length, 1);
    assert.equal(ir.checksum.length, 64);
    assert.doesNotThrow(() => EditorialIRSchema.parse(ir));
  });

  await t.test("guarantees 100% byte-a-byte deterministic checksum across independent builds", () => {
    const buildProject = () => {
      const b = new EditorialIRBuilder("proj_det", baseMetadata);
      b.createTrack({ id: "v1", name: "Video", type: "VIDEO_PRIMARY", index: 0 });
      b.addClip("v1", {
        id: "c1",
        assetId: "media/test.mp4",
        sourceRange: { startSeconds: 0, durationSeconds: 3 },
        timelineRange: { startSeconds: 0, durationSeconds: 3 },
      });
      return b.build("2026-09-02T12:00:00.000Z");
    };

    const ir1 = buildProject();
    const ir2 = buildProject();

    assert.equal(ir1.checksum, ir2.checksum);
  });

  await t.test("PBT: tracks are always sorted by index ascending", () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.record({
            id: fc.string({ minLength: 1, maxLength: 6 }),
            index: fc.integer({ min: 0, max: 100 }),
          }),
          { minLength: 1, maxLength: 8 }
        ),
        (trackConfigs) => {
          const b = new EditorialIRBuilder("pbt_proj", baseMetadata);
          const seen = new Set<string>();

          for (const tc of trackConfigs) {
            if (!seen.has(tc.id)) {
              seen.add(tc.id);
              b.createTrack({
                id: tc.id,
                name: `Track_${tc.id}`,
                type: "VIDEO_PRIMARY",
                index: tc.index,
              });
            }
          }

          const ir = b.build();
          for (let i = 0; i < ir.tracks.length - 1; i++) {
            if (ir.tracks[i].index > ir.tracks[i + 1].index) {
              return false;
            }
          }
          return true;
        }
      ),
      { numRuns: 40 }
    );
  });
});
