import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { TrueCrimeEvidencePreset } from "../../styles/presets/TrueCrimeEvidencePreset.js";
import { CinematicFlowVlogPreset } from "../../styles/presets/CinematicFlowVlogPreset.js";
import { SaaSTechShowcasePreset } from "../../styles/presets/SaaSTechShowcasePreset.js";
import { StyleProfileManager } from "../../styles/StyleProfileManager.js";
import { ProductionDSLCompiler } from "../../dsl/ProductionDSL.js";

describe("Presets Batch #9, #10, #11 — True Crime, Cinematic Vlog & SaaS Interface", () => {
  // Preset #9: True Crime
  it("generates red yarn connection and classified stamp snippets", () => {
    const yarnSnippet = TrueCrimeEvidencePreset.generateRedYarnSnippet(
      "comp",
      { id: "SuspectLink", pinA: [400, 300], pinB: [1100, 650], sagPx: 20 },
      1.5
    );
    assert.ok(yarnSnippet.includes("Yarn_SuspectLink"));
    assert.ok(yarnSnippet.includes("ADBE Vector Graphic - Stroke"));
    assert.ok(yarnSnippet.includes("ADBE Drop Shadow"));

    const stampSnippet = TrueCrimeEvidencePreset.generateClassifiedStampSnippet("comp", [960, 540], 2.0);
    assert.ok(stampSnippet.includes("TOP SECRET // CLASSIFIED"));
    assert.ok(stampSnippet.includes("Classified_Stamp"));
    assert.ok(stampSnippet.includes("Impact"));
  });

  // Preset #10: Cinematic Flow Vlog
  it("generates sky mask transition and horizon 3D title snippets", () => {
    const skySnippet = CinematicFlowVlogPreset.generateSkyMaskTransitionSnippet(
      "comp",
      { incomingVideoLayer: "DroneClip2", outgoingVideoLayer: "DroneClip1", featherPx: 140, durationSec: 1.5 },
      4.0
    );
    assert.ok(skySnippet.includes("SEAMLESS SKY MASK"));
    assert.ok(skySnippet.includes("ADBE Mask Atom"));

    const horizonSnippet = CinematicFlowVlogPreset.generateHorizonTitleSnippet("comp", "SWITZERLAND ALPS", [960, 400, 300]);
    assert.ok(horizonSnippet.includes("Horizon_Title"));
    assert.ok(horizonSnippet.includes("Futura-Bold"));
    assert.ok(horizonSnippet.includes("threeDLayer = true"));
  });

  // Preset #11: SaaS Interface
  it("generates cursor ripple clicks and glassmorphism window frames", () => {
    const rippleSnippet = SaaSTechShowcasePreset.generateCursorClickSnippet("comp", [500, 400], 1.2);
    assert.ok(rippleSnippet.includes("Cursor_Ripple_1.2"));
    assert.ok(rippleSnippet.includes("ADBE Vector Shape - Ellipse"));

    const glassSnippet = SaaSTechShowcasePreset.generateGlassWindowSnippet("comp", "Dashboard", [960, 540]);
    assert.ok(glassSnippet.includes("GlassWindow_Dashboard"));
    assert.ok(glassSnippet.includes("ADBE Drop Shadow"));
  });

  // Integración en ProductionDSL
  it("compiles all 3 specialized presets through ProductionDSL successfully", () => {
    const crimeComp = ProductionDSLCompiler.compile({
      video: { format: "16:9", durationSec: 40.0 },
      style: { preset: "true_crime_evidence_room", title: "THE ZODIAC MYSTERY" },
      editing: { pacing: "cinematic_slow", beatSync: false, speedRamping: false, depthSandwich: false },
    });
    assert.ok(crimeComp.appliedProfile.includes("True Crime"));

    const vlogComp = ProductionDSLCompiler.compile({
      video: { format: "16:9", durationSec: 60.0 },
      style: { preset: "cinematic_flow_vlog", title: "EXPLORING ICELAND" },
      editing: { pacing: "aggressive", beatSync: true, speedRamping: true, depthSandwich: true },
    });
    assert.ok(vlogComp.appliedProfile.includes("Cinematic Flow Vlogging"));

    const saasComp = ProductionDSLCompiler.compile({
      video: { format: "16:9", durationSec: 30.0 },
      style: { preset: "saas_tech_showcase", title: "MODERN WORKFLOW ENGINE" },
      editing: { pacing: "balanced", beatSync: false, speedRamping: false, depthSandwich: true },
    });
    assert.ok(saasComp.appliedProfile.includes("SaaS & Tech"));
  });
});
