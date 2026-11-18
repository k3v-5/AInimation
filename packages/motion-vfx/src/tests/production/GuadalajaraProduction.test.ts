import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { ProductionDSLCompiler } from "../../dsl/ProductionDSL.js";
import { StyleProfileManager } from "../../styles/StyleProfileManager.js";
import { MinimalistCipherPreset } from "../../styles/presets/MinimalistCipherPreset.js";
import { TimeEditorialPosterPreset } from "../../styles/presets/TimeEditorialPosterPreset.js";
import { CinematicFlowVlogPreset } from "../../styles/presets/CinematicFlowVlogPreset.js";

describe("Production Suite — Guadalajara 2023 Master Project", () => {
  it("compiles the Guadalajara 2023 narrative project through ProductionDSL successfully", () => {
    const compiled = ProductionDSLCompiler.compile({
      video: {
        format: "9:16", // Formato vertical óptimo para Reels/TikTok
        durationSec: 35.0,
        projectName: "Guadalajara_2023_Master_Editorial",
      },
      style: {
        preset: "time_editorial_poster",
        title: "GUADALAJARA // EL ARTE DE DISFRUTAR",
      },
      editing: {
        pacing: "aggressive",
        beatSync: true,
        speedRamping: true,
        depthSandwich: true,
      },
      captions: {
        enabled: true,
        text: "GUADALAJARA JUNIO 2023 UNA EXPERIENCIA INOLVIDABLE",
      },
      soundDesign: {
        enabled: true,
        autoDucking: true,
      },
    });

    assert.equal(compiled.composition.width, 1080);
    assert.equal(compiled.composition.height, 1920);
    assert.equal(compiled.composition.duration, 35.0);
    assert.ok(compiled.appliedProfile.includes("TIME Editorial"));

    const profile = StyleProfileManager.getProfile("time_editorial_poster");
    assert.equal(profile.typography.fontFamily, "Impact");
    assert.equal(profile.typography.verticalStretchPct, 140);
  });

  it("validates GPS coordinates for Guadalajara Jalisco", () => {
    // Coordenadas geográficas exactas de Guadalajara, Jalisco, México
    const coords = MinimalistCipherPreset.formatCoordinates(20.6597, -103.3496);
    assert.equal(coords, "20.6597° N, 103.3496° W");

    const hud = MinimalistCipherPreset.generateGPSHUDOverlaySnippet("comp", {
      latitude: 20.6597,
      longitude: -103.3496,
      timestampUTC: "JUNIO 2023 // JALISCO",
      codename: "GDL_EXPEDITION",
    });
    assert.ok(hud.includes("20.6597° N"));
    assert.ok(hud.includes("GDL_EXPEDITION"));
  });

  it("generates TIME Editorial headline and rotating dials for Guadalajara project", () => {
    const headlineSnippet = TimeEditorialPosterPreset.generateTIMEHeadlineSnippet(
      "comp",
      "EL ARTE DE DISFRUTAR",
      [540, 960],
      140
    );
    assert.ok(headlineSnippet.includes("Impact"));
    assert.ok(headlineSnippet.includes("ParagraphJustification.CENTER_JUSTIFY"));
    assert.ok(headlineSnippet.includes("comp.motionBlur = true"));

    const frameSnippet = TimeEditorialPosterPreset.generateTIMEFrameSnippet("comp", 1080, 1920);
    assert.ok(frameSnippet.includes("TIME_Crimson_Border"));

    const dialSnippet = TimeEditorialPosterPreset.generateEditorialDialSnippet(
      "comp",
      { center: [540, 960], radiusPx: 220 },
      2.0
    );
    assert.ok(dialSnippet.includes("Editorial_Dial"));
    assert.ok(dialSnippet.includes("time * 45"));
  });
});
