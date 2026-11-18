import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { BuiltinOutputProfiles } from "../../rendering/profiles/OutputProfiles.js";
import { RenderValidator } from "../../rendering/validation/RenderValidator.js";

describe("Fase 9 — Render Validation & Quality Checks Tests", () => {
  it("validates rendered output conforming to target profile specifications", () => {
    const profile = BuiltinOutputProfiles["youtube-1080p"];

    const validOutput = {
      width: 1920,
      height: 1080,
      fps: 30,
      duration: 10.0,
      codec: "H.264",
      framesRendered: 300,
    };

    const resValid = RenderValidator.validateOutput(validOutput, profile, 10.0);
    assert.strictEqual(resValid.valid, true);
    assert.strictEqual(resValid.issues.length, 0);

    const invalidOutput = {
      width: 1280, // Mismatch
      height: 720,
      fps: 30,
      duration: 10.0,
      codec: "H.264",
      framesRendered: 300,
    };

    const resInvalid = RenderValidator.validateOutput(invalidOutput, profile, 10.0);
    assert.strictEqual(resInvalid.valid, false);
    assert.strictEqual(resInvalid.issues.length >= 2, true);
  });
});
