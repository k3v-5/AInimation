import assert from "node:assert/strict";
import { describe, it } from "node:test";
import fc from "fast-check";
import { PolaroidGenerator } from "../../../vlog/overlays/polaroid-generator.js";

describe("Milestone 6-C — Polaroid Generator & SoundBank Shutter Suite", () => {
  it("guarantees deterministic rotation within [-15°, 15°]", () => {
    const res1 = PolaroidGenerator.createPolaroid({
      id: "pol_01",
      freezeTimestampSeconds: 5.25,
      captionText: "Atardecer en Chapala",
    });

    const res2 = PolaroidGenerator.createPolaroid({
      id: "pol_01",
      freezeTimestampSeconds: 5.25,
      captionText: "Atardecer en Chapala",
    });

    // Mismos inputs -> exactamente misma rotación sin aleatoriedad
    assert.equal(res1.polaroid.rotationDegrees, res2.polaroid.rotationDegrees);
    assert.ok(res1.polaroid.rotationDegrees >= -15.0);
    assert.ok(res1.polaroid.rotationDegrees <= 15.0);

    // Audio de obturador generado y verificado
    assert.ok(res1.shutterAudioBuffer.length > 44);
    assert.equal(res1.shutterAudioBuffer.toString("ascii", 0, 4), "RIFF");
  });

  it("synchronizes shutter SFX timestamp within 1 frame (<= 33.3ms) of freeze", () => {
    const freezeTime = 8.432;
    const res = PolaroidGenerator.createPolaroid({
      id: "pol_sync",
      freezeTimestampSeconds: freezeTime,
      fps: 30,
    });

    const diff = Math.abs(res.polaroid.shutterSfxSyncSeconds - freezeTime);
    assert.ok(diff <= 1 / 30, `Expected sync <= 1 frame (0.0333s), got ${diff}s`);
  });

  it("PBT: rotationDegrees is strictly bounded in [-15.0, 15.0] for any input", () => {
    fc.assert(
      fc.property(
        fc.string({ minLength: 1, maxLength: 20 }),
        fc.double({ min: 0.0, max: 1000.0, noNaN: true }),
        (id, time) => {
          const res = PolaroidGenerator.createPolaroid({
            id,
            freezeTimestampSeconds: time,
          });

          assert.ok(res.polaroid.rotationDegrees >= -15.0);
          assert.ok(res.polaroid.rotationDegrees <= 15.0);
          assert.ok(!isNaN(res.polaroid.rotationDegrees));
        }
      )
    );
  });
});
