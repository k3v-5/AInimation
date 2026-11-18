import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { CinematicColorGradingEngine } from "../../effects/color/CinematicColorGradingEngine.js";

describe("Effects — CinematicColorGradingEngine Tests", () => {
  it("retrieves distinct film and commercial color grade profiles accurately", () => {
    const tealOrange = CinematicColorGradingEngine.getProfile("teal_orange");
    assert.equal(tealOrange.name, "teal_orange");
    assert.equal(tealOrange.saturation, 110);
    assert.ok(tealOrange.shadows[1] > 0.5, "Expected cyan/greenish shadows");

    const kodak = CinematicColorGradingEngine.getProfile("kodak_35mm");
    assert.equal(kodak.name, "kodak_35mm");
    assert.equal(kodak.liftPedestal, 0.05);

    const cyberpunk = CinematicColorGradingEngine.getProfile("cyberpunk_crimson");
    assert.equal(cyberpunk.name, "cyberpunk_crimson");
    assert.equal(cyberpunk.contrast, 28);
  });

  it("generates well-formed ExtendScript grade snippet with adjustment layer", () => {
    const snippet = CinematicColorGradingEngine.generateExtendScriptGrade(
      "comp",
      "MainScene",
      "teal_orange",
      0.0,
      15.0
    );

    assert.ok(snippet.includes('adjLayer.adjustmentLayer = true'));
    assert.ok(snippet.includes('ADBE Color Balance (HLS)'));
    assert.ok(snippet.includes('ADBE Tint'));
    assert.ok(snippet.includes('adjLayer.startTime = 0'));
    assert.ok(snippet.includes('adjLayer.outPoint = 15'));
  });
});
