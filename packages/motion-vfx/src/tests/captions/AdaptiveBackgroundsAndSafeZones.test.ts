import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { AdaptiveBackgroundEngine } from "../../captions/backgrounds/AdaptiveBackgroundEngine.js";
import { DynamicCaptionLayoutEngine } from "../../captions/layout/DynamicCaptionLayoutEngine.js";
import { SafeZoneResolver, StandardSafeZoneProfiles } from "../../captions/safezones/SafeZoneResolver.js";
import { CaptionStyle, CaptionWord } from "../../captions/types/index.js";

describe("Fase 16 — Adaptive Backgrounds & Safe Zone Tests", () => {
  const style: CaptionStyle = {
    fontFamily: "Inter",
    fontSize: 60,
    fontWeight: 800,
    color: { r: 1, g: 1, b: 1, a: 1 },
    alignment: "center",
  };

  const words: CaptionWord[] = [
    { id: "w1", text: "Hola", start: 0, end: 0.5, index: 0 },
    { id: "w2", text: "Mundo", start: 0.5, end: 1.0, index: 1 },
  ];

  it("applies Pill Background creating bounding box per line", () => {
    const layout = DynamicCaptionLayoutEngine.layout(words, style);
    const withPill = AdaptiveBackgroundEngine.applyBackgrounds(layout, {
      type: "pill",
      color: { r: 0, g: 0, b: 0, a: 0.8 },
      padding: { top: 10, bottom: 10, left: 20, right: 20 },
      cornerRadius: 12,
    });

    assert.equal(withPill.backgrounds.length, 1);
    assert.ok(withPill.backgrounds[0].width > layout.lines[0].width);
    assert.ok(withPill.backgrounds[0].height > layout.lines[0].height);
    assert.ok(withPill.lines[0].backgroundBounds);
  });

  it("applies Split Boxes creating bounding boxes per word", () => {
    const layout = DynamicCaptionLayoutEngine.layout(words, style);
    const withSplit = AdaptiveBackgroundEngine.applyBackgrounds(layout, {
      type: "split-boxes",
      color: { r: 0, g: 0, b: 0, a: 0.9 },
      padding: { top: 6, bottom: 6, left: 12, right: 12 },
      cornerRadius: 6,
    });

    assert.equal(withSplit.backgrounds.length, 2);
    assert.ok(withSplit.words[0].backgroundBounds);
    assert.ok(withSplit.words[1].backgroundBounds);
  });

  it("resolves Safe Zones for TikTok and adjusts position when overflowing bottom inset", () => {
    const profile = StandardSafeZoneProfiles["tiktok-portrait"];
    assert.ok(profile);
    assert.equal(profile.canvasHeight, 1920);

    // Bloque centrado normal que cae dentro de la Safe Area
    const centered = SafeZoneResolver.resolve(400, 150, "center", profile);
    assert.equal(centered.status, "safe");
    assert.ok(centered.adjustedBounds.y + centered.adjustedBounds.height <= profile.canvasHeight - profile.bottomInset);

    // Bloque en bottom-center que desborda el inset inferior de TikTok (350px) y es ajustado hacia arriba
    const bottomAdjusted = SafeZoneResolver.resolve(600, 150, "bottom-center", profile);
    assert.equal(bottomAdjusted.status, "adjusted");
    assert.ok(bottomAdjusted.adjustedBounds.y + bottomAdjusted.adjustedBounds.height <= profile.canvasHeight - profile.bottomInset);
  });

  it("marks unresolved when block height exceeds entire canvas height", () => {
    const profile = StandardSafeZoneProfiles["tiktok-portrait"];
    const impossible = SafeZoneResolver.resolve(500, 2500, "center", profile);
    assert.equal(impossible.status, "unresolved");
    assert.ok(impossible.diagnostics.includes("block-larger-than-canvas"));
  });
});
