import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AgencyLuxuryPreset } from "../../styles/presets/AgencyLuxuryPreset.js";
import { HyperRetentionBeastPreset } from "../../styles/presets/HyperRetentionBeastPreset.js";
import { HormoziCashflowPreset } from "../../styles/presets/HormoziCashflowPreset.js";
import { StyleProfileManager } from "../../styles/StyleProfileManager.js";
import { ProductionDSLCompiler } from "../../dsl/ProductionDSL.js";

describe("Presets Batch #6, #7, #8 — Agency Luxury, Beast Retention & Hormozi Cashflow", () => {
  // Preset #6: Agency Luxury
  it("generates 16mm film negative border and luxury headline snippets", () => {
    const borders = AgencyLuxuryPreset.generateFilmBordersSnippet("comp", { compWidth: 1080, compHeight: 1920 });
    assert.ok(borders.includes("Film_Borders_Overlay"));
    assert.ok(borders.includes("ADBE Noise"));

    const headline = AgencyLuxuryPreset.generateLuxuryHeadlineSnippet("comp", "THE MASTERCLASS", [540, 960]);
    assert.ok(headline.includes("BodoniMT-Bold"));
    assert.ok(headline.includes("Luxury_Title"));
  });

  // Preset #7: Beast Retention
  it("evaluates sinusoidal arrow bounce and generates 3D bold title snippets", () => {
    const baseY = 500;
    const bounce0 = HyperRetentionBeastPreset.evaluateSinusoidalBounce(0, baseY);
    assert.equal(bounce0, baseY);

    // En t = pi / (2 * freq) = 3.14159 / 24 = 0.1309s -> sen(1.57) = 1 -> baseY + 22
    const peak = HyperRetentionBeastPreset.evaluateSinusoidalBounce(0.1309, baseY);
    assert.equal(peak, 522.0);

    const beastTitle = HyperRetentionBeastPreset.generateBeastTitleSnippet("comp", "I SURVIVED 100 DAYS", [540, 960]);
    assert.ok(beastTitle.includes("Impact"));
    assert.ok(beastTitle.includes("strokeWidth = 14"));
    assert.ok(beastTitle.includes("ADBE Drop Shadow"));

    const arrow = HyperRetentionBeastPreset.generateBouncingArrowSnippet("comp", { targetPoint: [540, 960] }, 1.0);
    assert.ok(arrow.includes("Beast_Arrow_Pointer"));
    assert.ok(arrow.includes("Math.sin"));
  });

  // Preset #8: Hormozi Cashflow
  it("resolves Hormozi word highlight colors and generates punch zoom snippets", () => {
    const colYellow = HormoziCashflowPreset.resolveWordColor("yellow");
    assert.deepEqual(colYellow, [0.918, 0.702, 0.031]);

    const colGreen = HormoziCashflowPreset.resolveWordColor("green");
    assert.deepEqual(colGreen, [0.133, 0.773, 0.369]);

    const captionSnippet = HormoziCashflowPreset.generateHormoziCaptionSnippet(
      "comp",
      [
        { word: "how", isKeyWord: false },
        { word: "to", isKeyWord: false },
        { word: "get", isKeyWord: false },
        { word: "rich", isKeyWord: true, colorType: "green" },
      ],
      [540, 1400],
      2.0,
      1.5
    );
    assert.ok(captionSnippet.includes("HOW TO GET RICH"));
    assert.ok(captionSnippet.includes("TheBoldFont"));

    const punchSnippet = HormoziCashflowPreset.generatePunchZoomSnippet("comp", "SpeakerVideo", 3.5, 125);
    assert.ok(punchSnippet.includes("SpeakerVideo"));
    assert.ok(punchSnippet.includes("125"));
  });

  // Integración en ProductionDSL
  it("compiles all 3 viral presets through ProductionDSL successfully", () => {
    const agencyComp = ProductionDSLCompiler.compile({
      video: { format: "9:16", durationSec: 30.0 },
      style: { preset: "iman_gadzhi_agency_luxury", title: "THE SECRET PROTOCOL" },
      editing: { pacing: "aggressive", beatSync: true, speedRamping: false, depthSandwich: true },
    });
    assert.ok(agencyComp.appliedProfile.includes("Agency & Luxury"));

    const beastComp = ProductionDSLCompiler.compile({
      video: { format: "9:16", durationSec: 45.0 },
      style: { preset: "mrbeast_hyper_retention", title: "LAST TO LEAVE WINS" },
      editing: { pacing: "aggressive", beatSync: true, speedRamping: true, depthSandwich: false },
    });
    assert.ok(beastComp.appliedProfile.includes("Hyper-Retention Beast"));

    const hormoziComp = ProductionDSLCompiler.compile({
      video: { format: "9:16", durationSec: 60.0 },
      style: { preset: "hormozi_cashflow_captions", title: "THE 100M OFFER FORMULA" },
      editing: { pacing: "aggressive", beatSync: false, speedRamping: false, depthSandwich: true },
    });
    assert.ok(hormoziComp.appliedProfile.includes("Cashflow Direct-to-Camera"));
  });
});
