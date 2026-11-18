import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { ScientificBlueprintPreset } from "../../styles/presets/ScientificBlueprintPreset.js";
import { MinimalistCipherPreset } from "../../styles/presets/MinimalistCipherPreset.js";
import { ProductivityPapercraftPreset } from "../../styles/presets/ProductivityPapercraftPreset.js";
import { StyleProfileManager } from "../../styles/StyleProfileManager.js";
import { ProductionDSLCompiler } from "../../dsl/ProductionDSL.js";

describe("Presets Batch #3, #4, #5 — Science, Cipher & Productivity Suites", () => {
  // Preset #3: Scientific Blueprint
  it("calculates euclidean distance, angle and midpoints for dimension callouts", () => {
    const geom = ScientificBlueprintPreset.calculateDistanceAndAngle([0, 0], [300, 400]);
    assert.equal(geom.distance, 500.0);
    assert.ok(Math.abs(geom.angleDegrees - 53.13) < 0.1);
    assert.deepEqual(geom.midpoint, [150, 200]);

    const gridSnippet = ScientificBlueprintPreset.generateBlueprintGridSnippet("comp");
    assert.ok(gridSnippet.includes("ADBE Grid"));

    const calloutSnippet = ScientificBlueprintPreset.generateDimensionCalloutSnippet(
      "comp",
      { id: "DistanceA", startPoint: [100, 200], endPoint: [400, 600], label: "500 nm" },
      1.0,
      1.2
    );
    assert.ok(calloutSnippet.includes("DistanceA_Ruler"));
    assert.ok(calloutSnippet.includes("Inter-Bold"));
  });

  // Preset #4: Minimalist Cipher
  it("formats military GPS coordinates and generates HUD overlay snippets", () => {
    const coords = MinimalistCipherPreset.formatCoordinates(51.5074, -0.1278);
    assert.equal(coords, "51.5074° N, 0.1278° W");

    const hudSnippet = MinimalistCipherPreset.generateGPSHUDOverlaySnippet("comp", {
      latitude: 37.2431,
      longitude: -115.793,
      timestampUTC: "04:15:22 UTC",
      codename: "Area51_Recon",
    });
    assert.ok(hudSnippet.includes("DIN-Light"));
    assert.ok(hudSnippet.includes("HUD_Coordinates"));

    const laserSnippet = MinimalistCipherPreset.generateScanningLaserSnippet("comp", 0.5, 2.5);
    assert.ok(laserSnippet.includes("Laser_Scanner"));
    assert.ok(laserSnippet.includes("ADBE Glo2"));
  });

  // Preset #5: Productivity Papercraft
  it("evaluates spring physics overshoot curve and generates floating card snippets", () => {
    assert.equal(ProductivityPapercraftPreset.evaluateSpringScale(-0.1), 0);
    // En t=0, scale = 0
    assert.equal(ProductivityPapercraftPreset.evaluateSpringScale(0), 0);

    // En t=0.15s, la escala rebota por encima de 100%
    const scalePeak = ProductivityPapercraftPreset.evaluateSpringScale(0.15);
    assert.ok(scalePeak > 100);

    const cardSnippet = ProductivityPapercraftPreset.generateFloatingCardSnippet(
      "comp",
      { id: "HabitsCard", title: "ATOMIC HABITS RULE 1", body: "Make it obvious" },
      [960, 540],
      1.0
    );
    assert.ok(cardSnippet.includes("Card_HabitsCard"));
    assert.ok(cardSnippet.includes("PlusJakartaSans-Bold"));
    assert.ok(cardSnippet.includes("ADBE Drop Shadow"));
  });

  // Integración en ProductionDSL
  it("compiles all 3 presets through ProductionDSL successfully", () => {
    const scienceComp = ProductionDSLCompiler.compile({
      video: { format: "16:9", durationSec: 30.0 },
      style: { preset: "veritasium_scientific_blueprint", title: "QUANTUM MECHANICS" },
      editing: { pacing: "balanced", beatSync: false, speedRamping: false, depthSandwich: false },
    });
    assert.ok(scienceComp.appliedProfile.includes("Scientific Blueprint"));

    const cipherComp = ProductionDSLCompiler.compile({
      video: { format: "16:9", durationSec: 30.0 },
      style: { preset: "lemmino_minimalist_cipher", title: "UNIDENTIFIED PHENOMENA" },
      editing: { pacing: "cinematic_slow", beatSync: false, speedRamping: false, depthSandwich: false },
    });
    assert.ok(cipherComp.appliedProfile.includes("Minimalist Cipher"));

    const prodComp = ProductionDSLCompiler.compile({
      video: { format: "9:16", durationSec: 30.0 },
      style: { preset: "ali_abdaal_productivity", title: "HOW I MANAGE MY TIME" },
      editing: { pacing: "balanced", beatSync: true, speedRamping: false, depthSandwich: true },
    });
    assert.ok(prodComp.appliedProfile.includes("Productivity Papercraft"));
  });
});
