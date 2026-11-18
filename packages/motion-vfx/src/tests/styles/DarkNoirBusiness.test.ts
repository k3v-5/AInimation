import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { DarkNoirBusinessPreset } from "../../styles/presets/DarkNoirBusinessPreset.js";
import { StyleProfileManager } from "../../styles/StyleProfileManager.js";
import { ProductionDSLCompiler } from "../../dsl/ProductionDSL.js";

describe("Preset #2 — Dark Noir Business Empire (MagnatesMedia / Neo Style)", () => {
  it("formats currency accurately with commas and custom prefixes", () => {
    const money1 = DarkNoirBusinessPreset.formatCurrency(145000000000);
    assert.equal(money1, "$145,000,000,000");

    const money2 = DarkNoirBusinessPreset.formatCurrency(2450000, "€", " EUR");
    assert.equal(money2, "€2,450,000 EUR");
  });

  it("evaluates Ease-Out wealth counter curve accurately across time", () => {
    const target = 1000000;
    const dur = 4.0;

    assert.equal(DarkNoirBusinessPreset.evaluateCounterProgress(0, dur, target), 0);
    // En t = 2s (50% tiempo), el progreso cúbico 1 - (1-0.5)^3 = 1 - 0.125 = 87.5%
    const midpoint = DarkNoirBusinessPreset.evaluateCounterProgress(2.0, dur, target);
    assert.equal(midpoint, 875000);

    // En t = 4s (100%), alcanza el 100%
    assert.equal(DarkNoirBusinessPreset.evaluateCounterProgress(4.0, dur, target), target);
    assert.equal(DarkNoirBusinessPreset.evaluateCounterProgress(5.0, dur, target), target);
  });

  it("generates valid ExtendScript snippets for 3D Photo Parallax, Gold Title and Stat Ticker", () => {
    const parallaxSnippet = DarkNoirBusinessPreset.generateParallaxPhotoSnippet("comp", {
      id: "MuskBiography",
      subjectImageLayer: "Musk_Cutout_PNG",
      backgroundImageLayer: "Factory_Background_JPG",
      targetScalePct: 110,
      blurRadiusPx: 32,
      durationSec: 6.0,
    });
    assert.ok(parallaxSnippet.includes("ADBE Fast Blur"));
    assert.ok(parallaxSnippet.includes("ADBE Drop Shadow"));
    assert.ok(parallaxSnippet.includes("threeDLayer = true"));

    const goldTitleSnippet = DarkNoirBusinessPreset.generateGoldTitleSnippet(
      "comp",
      "THE RISE AND FALL OF ENRON",
      [960, 540],
      1.0,
      3.5
    );
    assert.ok(goldTitleSnippet.includes("Cinzel-Bold"));
    assert.ok(goldTitleSnippet.includes("CC Light Sweep"));

    const tickerSnippet = DarkNoirBusinessPreset.generateStatTickerSnippet(
      "comp",
      "NetWorthCounter",
      { targetValue: 250000000000, durationSec: 4.0 },
      [960, 750],
      2.0
    );
    assert.ok(tickerSnippet.includes("toLocaleString"));
    assert.ok(tickerSnippet.includes("Math.pow"));
  });

  it("compiles through ProductionDSL seamlessly with magnates_business_noir profile", () => {
    const compiled = ProductionDSLCompiler.compile({
      video: { format: "16:9", durationSec: 50.0, projectName: "ThePonziScheme" },
      style: { preset: "magnates_business_noir", title: "HOW BILLIONS VANISHED" },
      editing: { pacing: "balanced", beatSync: false, speedRamping: false, depthSandwich: false },
      captions: { enabled: true, text: "HE CREATED THE GREATEST ILLUSION ON WALL STREET" },
      soundDesign: { enabled: true, autoDucking: true },
    });

    assert.equal(compiled.composition.width, 1920);
    assert.equal(compiled.composition.height, 1080);
    assert.ok(compiled.appliedProfile.includes("Dark Noir Business"));

    const profile = StyleProfileManager.getProfile("magnates_business_noir");
    assert.equal(profile.typography.fontFamily, "Cinzel");
    assert.equal(profile.soundDesign.autoDuckingDb, -4.0);
  });
});
