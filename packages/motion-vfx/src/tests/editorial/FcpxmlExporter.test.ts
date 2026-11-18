import test from "node:test";
import assert from "node:assert/strict";
import {
  EditorialIRBuilder,
  FcpxmlExporter,
} from "../../editorial/index.js";

test("Fase 4C — Final Cut Pro XML (FCPXML v1.9) Exporter Suite", async (t) => {
  const baseMetadata = {
    title: "Investigative Report: The Spill",
    profile: "JOURNALISM",
    frameRate: 25,
    width: 1920,
    height: 1080,
    sampleRate: 48000,
    targetDialogueLufs: -23,
  };

  const builder = new EditorialIRBuilder("proj_fcpxml_01", baseMetadata);
  builder.createTrack({ id: "v1", name: "Primary Story", type: "VIDEO_PRIMARY", index: 0 });

  builder.addClip("v1", {
    id: "clip_interview_expert",
    assetId: "media/expert_spill.mov",
    label: "Expert Spill Testimony & Quotes",
    sourceRange: { startSeconds: 15.0, durationSeconds: 6.0 },
    timelineRange: { startSeconds: 0.0, durationSeconds: 6.0 },
  });

  builder.addMarker({
    id: "m_claim_01",
    timestampSeconds: 2.0,
    name: "Claim: 50,000 Gallons Leak",
    color: "#0000FF",
  });

  const ir = builder.build();

  await t.test("exports valid FCPXML v1.9 document with proper XML escaping and structure", () => {
    const xml = FcpxmlExporter.exportToFcpxml(ir);

    assert.match(xml, /<\?xml version="1.0" encoding="UTF-8"\?>/);
    assert.match(xml, /<!DOCTYPE fcpxml>/);
    assert.match(xml, /<fcpxml version="1.9">/);
    assert.match(xml, /<format id="r_fmt" name="FFVideoFormat_1920x1080p25" frameDuration="1\/25s"/);
    assert.match(xml, /<asset id="r_asset_1"/);
    assert.match(xml, /<spine>/);
    assert.match(xml, /<asset-clip ref="r_asset_1"/);
    assert.match(xml, /<marker start="50\/25s" duration="0s" value="Claim: 50,000 Gallons Leak"\/>/);
    assert.match(xml, /Expert Spill Testimony &amp; Quotes/); // XML escaped ampersand
  });
});
