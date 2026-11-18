import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { InvestigativeCartographerPreset } from "../../styles/presets/InvestigativeCartographerPreset.js";
import { StyleProfileManager } from "../../styles/StyleProfileManager.js";
import { ProductionDSLCompiler } from "../../dsl/ProductionDSL.js";

describe("Preset #1 — The Investigative Cartographer (Johnny Harris / Vox Style)", () => {
  it("provides deterministic document rotations within [-3.0°, +3.0°]", () => {
    const rot1 = InvestigativeCartographerPreset.calculateDeterministicRotation("doc_cia_1953");
    const rot2 = InvestigativeCartographerPreset.calculateDeterministicRotation("doc_cia_1953");
    const rot3 = InvestigativeCartographerPreset.calculateDeterministicRotation("doc_treaty_1919");

    // Invariante de determinismo
    assert.equal(rot1, rot2);
    assert.ok(rot1 >= -3.0 && rot1 <= 3.0);
    assert.ok(rot3 >= -3.0 && rot3 <= 3.0);
  });

  it("calculates pin overshoot scale accurately with cosine damping", () => {
    assert.equal(InvestigativeCartographerPreset.calculatePinOvershootScale(-0.1), 0);
    // En t=0, scale = 100 + 45 = 145%
    const scale0 = InvestigativeCartographerPreset.calculatePinOvershootScale(0);
    assert.equal(scale0, 145.0);

    // En t grande (t=2.0), el rebote se amortigua cerca de 100%
    const scaleLate = InvestigativeCartographerPreset.calculatePinOvershootScale(2.0);
    assert.ok(Math.abs(scaleLate - 100) < 0.01);
  });

  it("generates valid ExtendScript snippets for 2.5D camera, highlighter, route and cutout", () => {
    const camSnippet = InvestigativeCartographerPreset.generateMapCameraSnippet("comp", [960, 540], 3.5);
    assert.ok(camSnippet.includes("Carto_Camera"));
    assert.ok(camSnippet.includes("X Rotation"));
    assert.ok(camSnippet.includes("Z Rotation"));

    const highlightSnippet = InvestigativeCartographerPreset.generateHighlighterSnippet(
      "comp",
      "SecretDoc",
      "DECLASSIFIED TOP SECRET",
      [960, 400],
      1.0,
      1.5
    );
    assert.ok(highlightSnippet.includes("PlayfairDisplay-Bold"));
    assert.ok(highlightSnippet.includes("BlendingMode.MULTIPLY"));
    assert.ok(highlightSnippet.includes("ADBE Vector Filter - Trim"));

    const routeSnippet = InvestigativeCartographerPreset.generateRouteTraceSnippet(
      "comp",
      "SilkRoadRoute",
      [[100, 200], [500, 400], [900, 800]],
      0.5,
      2.0
    );
    assert.ok(routeSnippet.includes("ADBE Vector Dash - 1"));
    assert.ok(routeSnippet.includes("ADBE Vector Filter - Trim"));

    const cutoutSnippet = InvestigativeCartographerPreset.generateDocumentCutoutSnippet(
      "comp",
      { id: "TreatyOfVersailles", headline: "WAR ENDS", sourceDate: "1919-06-28" },
      [960, 540],
      2.0
    );
    assert.ok(cutoutSnippet.includes("ADBE Drop Shadow"));
    assert.ok(cutoutSnippet.includes("TreatyOfVersailles_Pin"));
  });

  it("compiles through ProductionDSL seamlessly with johnny_harris_investigative profile", () => {
    const compiled = ProductionDSLCompiler.compile({
      video: { format: "16:9", durationSec: 45.0, projectName: "SuezCanalCrisis" },
      style: { preset: "johnny_harris_investigative", title: "THE BATTLE FOR THE SUEZ CANAL" },
      editing: { pacing: "balanced", beatSync: false, speedRamping: false, depthSandwich: false },
      captions: { enabled: true, text: "IN OCTOBER 1956 FORCES MOBILIZED" },
      soundDesign: { enabled: true, autoDucking: true },
    });

    assert.equal(compiled.composition.width, 1920);
    assert.equal(compiled.composition.height, 1080);
    assert.ok(compiled.appliedProfile.includes("Johnny Harris"));

    const profile = StyleProfileManager.getProfile("johnny_harris_investigative");
    assert.equal(profile.typography.fontFamily, "Playfair Display");
    assert.equal(profile.typography.fontWeight, 900);
    assert.equal(profile.soundDesign.autoDuckingDb, -3.5);
  });
});
