import test from "node:test";
import assert from "node:assert/strict";
import fc from "fast-check";
import {
  BrutalistTypeEngine,
  LiquidChromeEngine,
  PerspectiveAnchorEngine,
  WordSlamEngine,
  KineticTypographyOrchestrator,
  BrutalistTypeSpecSchema,
  LiquidChromeSpecSchema,
  PerspectiveAnchorSpecSchema,
  WordSlamSpecSchema,
} from "../../kinetic-typography/index.js";

test("Fase 24: Avant-Garde Brutalist Kinetic Typography, Liquid Chrome & 3D Perspective Suite", async (t) => {
  // 1. UNIT TESTS: Hex Color Parsing
  await t.test("BrutalistTypeEngine.hexToRgbTuple converts hex colors to normalized [0, 1] RGB", () => {
    const crimson = BrutalistTypeEngine.hexToRgbTuple("#FF1424");
    assert.equal(crimson[0], 1.0);
    assert.ok(Math.abs(crimson[1] - 0.0784) < 0.001);
    assert.ok(Math.abs(crimson[2] - 0.1412) < 0.001);

    const white = BrutalistTypeEngine.hexToRgbTuple("#FFFFFF");
    assert.deepEqual(white, [1.0, 1.0, 1.0]);

    const black = BrutalistTypeEngine.hexToRgbTuple("#000000");
    assert.deepEqual(black, [0.0, 0.0, 0.0]);
  });

  // 2. UNIT TESTS: Brutalist Type ExtendScript Emission
  await t.test("BrutalistTypeEngine: produces TIME editorial style text with centered anchor point", () => {
    const lines = BrutalistTypeEngine.exportToExtendScript({
      id: "tyler_title",
      text: "máquina culona",
      fontFamily: "Impact",
      fontSizePx: 240,
      verticalStretchPercent: 140,
      tracking: -75,
      colorHex: "#FF1424",
      allCaps: true,
    }).join("\n");

    // Texto en mayúsculas forzadas
    assert.match(lines, /MÁQUINA CULONA/);
    // Centrado de párrafo
    assert.match(lines, /ParagraphJustification\.CENTER_JUSTIFY/);
    // Recálculo de punto de anclaje geométrico centrado
    assert.match(lines, /sourceRectAtTime\(0, false\)/);
    assert.match(lines, /Anchor Point/);
    // Estiramiento anamórfico vertical al 140%
    assert.match(lines, /Scale"\)\.setValue\(\[100\.0, 140\.0\]\)/);
    // Invariante de motion blur
    assert.match(lines, /motionBlur = true/);
  });

  // 3. UNIT TESTS: Liquid Chrome Shader
  await t.test("LiquidChromeEngine: generates metallic shader stack with Bevel, Turbulent Displace and Tint", () => {
    const lines = LiquidChromeEngine.exportToExtendScript({
      id: "chrome_effect",
      bevelDepthPx: 5.0,
      turbulentAmount: 16.0,
      turbulentSize: 22.0,
      evolutionSpeed: 2.0,
      chromePalette: "PLATINUM",
    }).join("\n");

    assert.match(lines, /ADBE Bevel Alpha/);
    assert.match(lines, /Edge Thickness"\)\.setValue\(5\.0\)/);
    assert.match(lines, /ADBE Turbulent Displace/);
    assert.match(lines, /time \*/);
    assert.match(lines, /ADBE Tint/);
    assert.match(lines, /Map White To/);
  });

  // 4. UNIT TESTS: 3D Perspective Geometry
  await t.test("PerspectiveAnchorEngine: resolves floor receding and wall vanishing angles", () => {
    const floor = PerspectiveAnchorEngine.resolveTransform3D({
      position3D: [540, 960, 0],
      rotation3D: [0, 0, 0],
      vanishingPointAlign: "FLOOR_RECEDING",
    });

    // Inclinado 72 grados en X para acostarse en el asfalto
    assert.equal(floor.rotation[0], 72.0);
    assert.ok(floor.position[1] > 960); // Desplazado hacia abajo en Y
    assert.ok(floor.position[2] > 0);   // Desplazado en profundidad Z

    const wall = PerspectiveAnchorEngine.resolveTransform3D({
      position3D: [540, 960, 0],
      rotation3D: [0, 0, 0],
      vanishingPointAlign: "WALL_LEFT",
    });

    assert.equal(wall.rotation[1], 55.0); // Giro en Y
    assert.ok(wall.position[0] < 540);    // Hacia la izquierda

    const script = PerspectiveAnchorEngine.exportToExtendScript({
      vanishingPointAlign: "FLOOR_RECEDING",
    }).join("\n");
    assert.match(script, /threeDLayer = true/);
    assert.match(script, /X Rotation/);
    assert.match(script, /Y Rotation/);
  });

  // 5. UNIT TESTS: Word Slam Underdamped Elastic Bounce
  await t.test("WordSlamEngine: starts at initial scale and converges to 100% target", () => {
    const initial = 280.0;
    // En t = 0 -> initialScale
    assert.equal(WordSlamEngine.evaluateSlamScale(0.0, initial, 100.0, 0.55, 24.0), initial);

    // En t = 0.5s -> prácticamente converged en 100%
    const late = WordSlamEngine.evaluateSlamScale(0.5, initial, 100.0, 0.55, 24.0);
    assert.ok(Math.abs(late - 100.0) < 5.0, `late scale (${late}) should be near 100.0`);

    const kfs = WordSlamEngine.generateScaleKeyframes(
      {
        triggerTimeSeconds: 1.0,
        durationSeconds: 0.3,
        initialScalePercent: 250,
      },
      30.0,
      1.35 // 135% vertical stretch
    );

    assert.ok(kfs.length >= 9);
    assert.equal(kfs[0].timeSeconds, 1.0);
    assert.equal(kfs[0].scaleX, 250);
    assert.equal(kfs[0].scaleY, Number((250 * 1.35).toFixed(2)));
  });

  // 6. ORCHESTRATION & INVARIANT TESTS
  await t.test("KineticTypographyOrchestrator: produces deterministic plan with SHA-256 and motion blur", () => {
    const plan1 = KineticTypographyOrchestrator.compilePlan({
      id: "ktype_showcase",
      brutalist: {
        text: "guadalajara",
        fontSizePx: 250,
        verticalStretchPercent: 135,
        tracking: -60,
        colorHex: "#FF1424",
      },
      chrome: {
        chromePalette: "PLATINUM",
      },
      perspective: {
        vanishingPointAlign: "FLOOR_RECEDING",
      },
      slam: {
        triggerTimeSeconds: 2.0,
        initialScalePercent: 260,
      },
    });

    const plan2 = KineticTypographyOrchestrator.compilePlan({
      id: "ktype_showcase",
      brutalist: {
        text: "guadalajara",
        fontSizePx: 250,
        verticalStretchPercent: 135,
        tracking: -60,
        colorHex: "#FF1424",
      },
      chrome: {
        chromePalette: "PLATINUM",
      },
      perspective: {
        vanishingPointAlign: "FLOOR_RECEDING",
      },
      slam: {
        triggerTimeSeconds: 2.0,
        initialScalePercent: 260,
      },
    });

    assert.equal(plan1.id, "ktype_showcase");
    assert.equal(plan1.checksumSha256, plan2.checksumSha256);
    assert.equal(plan1.checksumSha256.length, 64);

    const jsx = plan1.extendScriptLines.join("\n");
    assert.match(jsx, /comp\.motionBlur = true/);
    assert.match(jsx, /threeDLayer = true/);
    assert.match(jsx, /ADBE Bevel Alpha/);
    assert.match(jsx, /setValueAtTime/);
    assert.match(jsx, /app\.endUndoGroup\(\)/);
  });

  // 7. PROPERTY-BASED TESTING: Slam Damping Convergence
  await t.test("PBT: Word Slam scale converges smoothly toward targetScale as time advances", () => {
    fc.assert(
      fc.property(
        fc.double({ min: 180.0, max: 350.0, noNaN: true }), // initialScale
        fc.double({ min: 0.35, max: 0.85, noNaN: true }),  // dampingRatio
        fc.double({ min: 15.0, max: 40.0, noNaN: true }),  // naturalFrequency
        (initial, zeta, wn) => {
          const s0 = WordSlamEngine.evaluateSlamScale(0.0, initial, 100.0, zeta, wn);
          const sMid = WordSlamEngine.evaluateSlamScale(0.15, initial, 100.0, zeta, wn);
          const sEnd = WordSlamEngine.evaluateSlamScale(0.60, initial, 100.0, zeta, wn);

          // Al inicio es exactamente initial
          const startsExact = Math.abs(s0 - initial) < 1e-4;
          // Al final (0.6s) debe estar amortiguado muy cerca de 100
          const converges = Math.abs(sEnd - 100.0) < 15.0;

          return startsExact && converges;
        }
      ),
      { numRuns: 150 }
    );
  });

  await t.test("PBT: hexToRgbTuple produces values strictly bounded in [0.0, 1.0]", () => {
    fc.assert(
      fc.property(
        fc.stringMatching(/^[0-9a-fA-F]{6}$/),
        (hex) => {
          const [r, g, b] = BrutalistTypeEngine.hexToRgbTuple("#" + hex);
          return r >= 0.0 && r <= 1.0 && g >= 0.0 && g <= 1.0 && b >= 0.0 && b <= 1.0;
        }
      ),
      { numRuns: 100 }
    );
  });
});
