import test from "node:test";
import assert from "node:assert/strict";
import {
  EditorialIRBuilder,
  OtioExporter,
} from "../../editorial/index.js";

test("Fase 4C — OpenTimelineIO (OTIO v1) Exporter Suite", async (t) => {
  const baseMetadata = {
    title: "Documentary Sequence",
    profile: "DOCUMENTARY",
    frameRate: 24,
    width: 3840,
    height: 2160,
    sampleRate: 48000,
    targetDialogueLufs: -24,
  };

  const builder = new EditorialIRBuilder("proj_otio_01", baseMetadata);
  builder
    .createTrack({ id: "v1", name: "V1", type: "VIDEO_PRIMARY", index: 0 })
    .createTrack({ id: "a1", name: "A1", type: "AUDIO_DIALOGUE", index: 1 });

  builder.addClip("v1", {
    id: "clip_1",
    assetId: "assets/take1.mov",
    label: "Take 1",
    sourceRange: { startSeconds: 2.0, durationSeconds: 4.0 },
    timelineRange: { startSeconds: 0.0, durationSeconds: 4.0 },
  });

  // Second clip has a 2-second gap on timeline (starts at 6.0 instead of 4.0)
  builder.addClip("v1", {
    id: "clip_2",
    assetId: "assets/take2.mov",
    label: "Take 2",
    sourceRange: { startSeconds: 0.0, durationSeconds: 3.0 },
    timelineRange: { startSeconds: 6.0, durationSeconds: 3.0 },
  });

  const ir = builder.build();

  await t.test("exports valid OpenTimelineIO JSON structure conforming to OTIO schema", () => {
    const otioJson = OtioExporter.exportToOtioJson(ir);
    assert.ok(otioJson.length > 100);

    const parsed = JSON.parse(otioJson);
    assert.equal(parsed.OTIO_SCHEMA, "Timeline.1");
    assert.equal(parsed.name, "Documentary Sequence");
    assert.equal(parsed.tracks.OTIO_SCHEMA, "Stack.1");
    assert.equal(parsed.tracks.children.length, 2);

    const v1Track = parsed.tracks.children[0];
    assert.equal(v1Track.name, "V1");
    assert.equal(v1Track.kind, "Video");

    // Clip 1 + Gap + Clip 2 = 3 items in V1 track
    assert.equal(v1Track.children.length, 3);
    assert.equal(v1Track.children[0].OTIO_SCHEMA, "Clip.1");
    assert.equal(v1Track.children[1].OTIO_SCHEMA, "Gap.1");
    assert.equal(v1Track.children[2].OTIO_SCHEMA, "Clip.1");

    // Check RationalTime rate is 24
    assert.equal(v1Track.children[0].source_range.duration.rate, 24);
  });
});
