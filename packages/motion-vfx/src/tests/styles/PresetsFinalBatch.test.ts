import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { WallStreetFinancePreset } from "../../styles/presets/WallStreetFinancePreset.js";
import { SportsEnergyPreset } from "../../styles/presets/SportsEnergyPreset.js";
import { RetroSynthwavePreset } from "../../styles/presets/RetroSynthwavePreset.js";
import { TimeEditorialPosterPreset } from "../../styles/presets/TimeEditorialPosterPreset.js";
import { StyleProfileManager } from "../../styles/StyleProfileManager.js";
import { ProductionDSLCompiler } from "../../dsl/ProductionDSL.js";

describe("Presets Batch #12, #13, #14, #15 — Finance, Sports, Synthwave & TIME Editorial", () => {
  // Preset #12: Wall Street Finance
  it("determines bullish/bearish candles and generates candlestick snippets", () => {
    const bull = WallStreetFinancePreset.isBullish({ open: 150, close: 155, high: 160, low: 148, timestamp: 1 });
    assert.equal(bull, true);

    const bear = WallStreetFinancePreset.isBullish({ open: 155, close: 145, high: 158, low: 140, timestamp: 2 });
    assert.equal(bear, false);

    const candleSnippet = WallStreetFinancePreset.generateCandlestickSnippet(
      "comp",
      { open: 100, close: 110, high: 115, low: 95, timestamp: 1001 },
      500,
      800
    );
    assert.ok(candleSnippet.includes("Candle_1001"));
    assert.ok(candleSnippet.includes("ADBE Vector Shape - Rect"));

    const tickerSnippet = WallStreetFinancePreset.generateStockTickerSnippet("comp", "NVDA", 128.5, 4.35, [960, 200]);
    assert.ok(tickerSnippet.includes("NVDA $128.50 (+4.35%)"));
    assert.ok(tickerSnippet.includes("Consolas-Bold"));
  });

  // Preset #13: Sports Energy
  it("formats stopwatch millisecond times and generates timer snippets", () => {
    const formatted = SportsEnergyPreset.formatStopwatchTime(84850);
    assert.equal(formatted, "01:24.85");

    const timerSnippet = SportsEnergyPreset.generateStopwatchSnippet(
      "comp",
      { startMs: 0, endMs: 60000, durationSec: 60 },
      [960, 540],
      1.0
    );
    assert.ok(timerSnippet.includes("Stopwatch_Timer"));
    assert.ok(timerSnippet.includes("Teko-Bold"));
    assert.ok(timerSnippet.includes("totalMs % 60000"));
  });

  // Preset #14: Retro Synthwave
  it("generates 3D perspective floor grid and retro sun snippets", () => {
    const gridSnippet = RetroSynthwavePreset.generatePerspectiveGridSnippet("comp");
    assert.ok(gridSnippet.includes("Synthwave_Floor"));
    assert.ok(gridSnippet.includes("rotationX.setValue(80)"));
    assert.ok(gridSnippet.includes("ADBE Glo2"));

    const sunSnippet = RetroSynthwavePreset.generateRetroSunSnippet("comp", [960, 480], 200);
    assert.ok(sunSnippet.includes("Retro_Synthwave_Sun"));
    assert.ok(sunSnippet.includes("ADBE Vector Shape - Ellipse"));
    assert.ok(sunSnippet.includes("Glow Intensity"));
  });

  // Preset #15: TIME Editorial Poster
  it("generates TIME headline with vertical stretch, crimson frame and rotating dial snippets", () => {
    const headline = TimeEditorialPosterPreset.generateTIMEHeadlineSnippet("comp", "THE RISE OF ARTIFICIAL INTELLIGENCE", [960, 540], 140);
    assert.ok(headline.includes("TIME_Headline"));
    assert.ok(headline.includes("Impact"));
    assert.ok(headline.includes("CENTER_JUSTIFY"));
    assert.ok(headline.includes("scale.setValue([100, 140])"));
    assert.ok(headline.includes("comp.motionBlur = true"));

    const frame = TimeEditorialPosterPreset.generateTIMEFrameSnippet("comp", 1920, 1080);
    assert.ok(frame.includes("TIME_Crimson_Border"));
    assert.ok(frame.includes("Stroke Width").valueOf());

    const dial = TimeEditorialPosterPreset.generateEditorialDialSnippet("comp", { center: [200, 200], radiusPx: 100 }, 0.5);
    assert.ok(dial.includes("Editorial_Dial"));
    assert.ok(dial.includes("time * 45"));
  });

  // Integración en ProductionDSL
  it("compiles all 4 final presets through ProductionDSL successfully", () => {
    const finComp = ProductionDSLCompiler.compile({
      video: { format: "16:9", durationSec: 30.0 },
      style: { preset: "wall_street_finance", title: "THE FED RATE CUT" },
      editing: { pacing: "aggressive", beatSync: false, speedRamping: false, depthSandwich: false },
    });
    assert.ok(finComp.appliedProfile.includes("Wall Street"));

    const sportComp = ProductionDSLCompiler.compile({
      video: { format: "9:16", durationSec: 15.0 },
      style: { preset: "sports_energy_fitness", title: "NEW WORLD RECORD" },
      editing: { pacing: "aggressive", beatSync: true, speedRamping: true, depthSandwich: true },
    });
    assert.ok(sportComp.appliedProfile.includes("Sports Energy"));

    const synthComp = ProductionDSLCompiler.compile({
      video: { format: "16:9", durationSec: 45.0 },
      style: { preset: "retro_synthwave_arcade", title: "NEON HIGHWAY" },
      editing: { pacing: "balanced", beatSync: true, speedRamping: false, depthSandwich: false },
    });
    assert.ok(synthComp.appliedProfile.includes("Retro Synthwave"));

    const timeComp = ProductionDSLCompiler.compile({
      video: { format: "16:9", durationSec: 60.0 },
      style: { preset: "time_editorial_poster", title: "PERSON OF THE YEAR" },
      editing: { pacing: "aggressive", beatSync: false, speedRamping: false, depthSandwich: true },
    });
    assert.ok(timeComp.appliedProfile.includes("TIME Editorial News Poster"));
  });
});
