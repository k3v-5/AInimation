import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { SubjectMaskingEngine } from "../../tracking-rotoscopy/core/SubjectMaskingEngine.js";

describe("Tracking & Rotoscopy — SubjectMaskingEngine Tests", () => {
  it("builds canonical 3D Depth Layer Sandwich hierarchy", () => {
    const hierarchy = SubjectMaskingEngine.buildDepthSandwich({
      backgroundLayerId: "bg_footage_01",
      textLayerId: "text_editorial_01",
      foregroundSubjectLayerId: "fg_cutout_01",
      extractionMode: "luma_extract",
      thresholds: {
        blackPoint: 50,
        whitePoint: 180,
        feather: 6.0,
      },
      blurTransition: {
        enabled: true,
        transitionTimeSec: 2.0,
        maxBlurPx: 30,
        textShiftToFront: true,
      },
    });

    // Verify correct layer Z-order: [Background, Mid-ground/Text, Foreground/Subject]
    assert.deepEqual(hierarchy.layersInZOrder, [
      "bg_footage_01",
      "text_editorial_01",
      "fg_cutout_01",
    ]);

    // Verify effects configuration
    assert.equal(hierarchy.effectsConfig.length, 2);
    const extractEffect = hierarchy.effectsConfig.find((e) => e.effectName === "ADBE Extract");
    assert.ok(extractEffect);
    assert.equal(extractEffect?.parameters["Black Point"], 50);
    assert.equal(extractEffect?.parameters["White Point"], 180);

    const blurEffect = hierarchy.effectsConfig.find((e) => e.effectName === "ADBE Fast Blur");
    assert.ok(blurEffect);
    assert.equal(blurEffect?.parameters["Blurriness"], 30);
  });

  it("generates well-formed ExtendScript snippet for After Effects", () => {
    const script = SubjectMaskingEngine.generateExtendScriptSandwich(
      "comp",
      "footage",
      "textLayer",
      0.0,
      4.0,
      {
        thresholds: { blackPoint: 40, whitePoint: 200 },
      }
    );

    assert.ok(script.includes('fgLayer.name = "Foreground_Subject_Cutout"'));
    assert.ok(script.includes("extEffect.property(\"Black Point\").setValue(40)"));
    assert.ok(script.includes("extEffect.property(\"White Point\").setValue(200)"));
  });
});
