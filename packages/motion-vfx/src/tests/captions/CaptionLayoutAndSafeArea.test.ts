import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { CaptionLayoutEngine } from "../../captions/layout/CaptionLayoutEngine.js";
import { CaptionPositionResolver, DEFAULT_TIKTOK_PROFILE } from "../../captions/layout/CaptionPositionResolver.js";
import { Caption } from "../../captions/types/index.js";

describe("Fase 5E — Caption Layout & Safe Area Positioning Tests", () => {
  it("wraps words onto multiple lines when exceeding maxWidth", () => {
    const caption: Caption = {
      id: "cap_1",
      timelineRange: { start: 0, end: 5 },
      words: [
        { id: "w1", text: "ESTO", start: 0, end: 1 },
        { id: "w2", text: "ES", start: 1, end: 2 },
        { id: "w3", text: "UNA", start: 2, end: 3 },
        { id: "w4", text: "ANIMACION", start: 3, end: 4 },
        { id: "w5", text: "INCREIBLE", start: 4, end: 5 },
      ],
      style: {
        fontFamily: "Montserrat",
        fontSize: 72,
        fontWeight: 900,
        color: { r: 1, g: 1, b: 1 },
        alignment: "center",
      },
      layoutMode: "highlight",
      position: "bottom-center",
    };

    // Con maxWidth = 400px debe generar múltiples líneas
    const layout = CaptionLayoutEngine.calculateLayout(caption, 400);
    assert.ok(layout.lines.length >= 2);
    assert.strictEqual(layout.words.length, 5);
  });

  it("positions captions strictly inside TikTok 9:16 safe area", () => {
    const profile = DEFAULT_TIKTOK_PROFILE;
    const blockWidth = 600;
    const blockHeight = 150;

    const bottomPos = CaptionPositionResolver.resolve("bottom-center", blockWidth, blockHeight, profile);

    // En bottom-center, la coordenada Y debe estar por encima de safeArea.bottom (350px de margen inferior)
    // 1920 - 350 - 150 = 1420
    assert.strictEqual(bottomPos.y, 1420);
    // X centrado: 60 + (1080 - 60 - 120 - 600) / 2 = 60 + 150 = 210
    assert.strictEqual(bottomPos.x, 210);

    // Verificar que no rebasa los límites de la pantalla ni la zona segura
    assert.ok(bottomPos.x >= profile.safeArea.left);
    assert.ok(bottomPos.x + blockWidth <= profile.width - profile.safeArea.right);
    assert.ok(bottomPos.y + blockHeight <= profile.height - profile.safeArea.bottom);
  });
});
