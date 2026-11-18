import test from "node:test";
import assert from "node:assert/strict";
import fc from "fast-check";
import {
  SnorricamEngine,
  InfiniteZoomPortalEngine,
  ParallaxOcclusionWipeEngine,
  SpatialCinematographyOrchestrator,
  SnorricamSpecSchema,
  InfiniteZoomPortalSpecSchema,
  ParallaxOcclusionWipeSpecSchema,
} from "../../spatial-cinematography/index.js";

test("Fase 25: Spatial Cinematography (Snorricam, Portals & Occlusion Wipes) Suite", async (t) => {
  // 1. UNIT TESTS: Snorricam Geometry & Motion Tile
  await t.test("SnorricamEngine: locks subject to comp center and provides mirror edge protection", () => {
    const subjectAnchor: [number, number] = [480, 720];
    const xform = SnorricamEngine.calculateAnchorAndPosition(subjectAnchor, 1080, 1920);

    assert.deepEqual(xform.anchorPoint, [480, 720]);
    assert.deepEqual(xform.position, [540, 960]);

    const script = SnorricamEngine.exportToExtendScript({
      id: "snorricam_take1",
      subjectAnchorPoint: subjectAnchor,
      scaleBufferPercent: 130,
      motionTileMirror: true,
    }).join("\n");

    assert.match(script, /ADBE Motion2/);
    assert.match(script, /Mirror Edges"\)\.setValue\(true\)/);
    assert.match(script, /Anchor Point"\)\.setValue\(\[480\.0, 720\.0\]\)/);
    assert.match(script, /Position"\)\.setValue\(\[comp\.width \/ 2\.0, comp\.height \/ 2\.0\]\)/);
    assert.match(script, /Scale"\)\.setValue\(\[130\.0, 130\.0\]\)/);
    assert.match(script, /motionBlur = true/);
  });

  // 2. UNIT TESTS: Infinite Zoom Super-Exponential Math
  await t.test("InfiniteZoomPortalEngine: starts at base scale and hits maxScale super-exponentially", () => {
    const maxScale = 6000.0;
    const gamma = 3.0;

    // En tau = 0 -> baseScale (100%)
    assert.equal(InfiniteZoomPortalEngine.evaluatePortalScale(0.0, maxScale, gamma), 100.0);
    // En tau = 1 -> maxScale (6000%)
    assert.equal(InfiniteZoomPortalEngine.evaluatePortalScale(1.0, maxScale, gamma), maxScale);

    // Crecimiento super-exponencial: en tau = 0.5 la escala es moderada, y explota en tau > 0.8
    const midScale = InfiniteZoomPortalEngine.evaluatePortalScale(0.5, maxScale, gamma);
    const lateScale = InfiniteZoomPortalEngine.evaluatePortalScale(0.85, maxScale, gamma);

    assert.ok(midScale > 100.0 && midScale < 300.0, `midScale (${midScale}) should be in early curve`);
    assert.ok(lateScale > 1000.0, `lateScale (${lateScale}) should be in explosive curve zone`);

    // Keyframes generados
    const kfs = InfiniteZoomPortalEngine.generatePortalKeyframes(
      {
        startTimeSeconds: 1.0,
        durationSeconds: 0.5,
        maxScalePercent: 6000,
        portalCenterPoint: [200, 300],
      },
      30.0,
      [540, 960]
    );

    assert.ok(kfs.length >= 15);
    assert.equal(kfs[0].scale, 100.0);
    assert.equal(kfs[kfs.length - 1].scale, 6000.0);
    assert.deepEqual(kfs[kfs.length - 1].anchorPoint, [200, 300]);
  });

  // 3. UNIT TESTS: Parallax Occlusion Wipe Bounds
  await t.test("ParallaxOcclusionWipeEngine: calculates mask progression and directional vertices", () => {
    const l2r = ParallaxOcclusionWipeEngine.calculateWipeBounds({
      direction: "LEFT_TO_RIGHT",
      durationSeconds: 1.0,
      startTimeSeconds: 0.0,
    });

    // Inicia fuera de la pantalla a la izquierda (-100)
    assert.equal(l2r.startVertices[0][0], -100);
    // Termina cubriendo toda la pantalla horizontalmente (1080 + 100 = 1180)
    assert.equal(l2r.endVertices[1][0], 1180);

    const script = ParallaxOcclusionWipeEngine.exportToExtendScript({
      direction: "LEFT_TO_RIGHT",
      featherPx: 40,
      startTimeSeconds: 2.0,
      durationSeconds: 0.6,
    }).join("\n");

    assert.match(script, /MaskMode\.ADD/);
    assert.match(script, /Mask Feather"\)\.setValue\(\[40\.0, 40\.0\]\)/);
    assert.match(script, /Mask Path/);
    assert.match(script, /setValueAtTime\(2\.0000/);
    assert.match(script, /setValueAtTime\(2\.6000/);
  });

  // 4. ORCHESTRATION & INVARIANT TESTS
  await t.test("SpatialCinematographyOrchestrator: produces deterministic plan with SHA-256 and motion blur", () => {
    const plan1 = SpatialCinematographyOrchestrator.compilePlan({
      id: "spatial_mv_take",
      fps: 30,
      snorricam: {
        subjectAnchorPoint: [500, 750],
        scaleBufferPercent: 125,
      },
      portal: {
        startTimeSeconds: 2.5,
        durationSeconds: 0.8,
        portalCenterPoint: [500, 750],
      },
      occlusionWipe: {
        direction: "RIGHT_TO_LEFT",
        featherPx: 30,
        startTimeSeconds: 3.3,
        durationSeconds: 0.5,
      },
    });

    const plan2 = SpatialCinematographyOrchestrator.compilePlan({
      id: "spatial_mv_take",
      fps: 30,
      snorricam: {
        subjectAnchorPoint: [500, 750],
        scaleBufferPercent: 125,
      },
      portal: {
        startTimeSeconds: 2.5,
        durationSeconds: 0.8,
        portalCenterPoint: [500, 750],
      },
      occlusionWipe: {
        direction: "RIGHT_TO_LEFT",
        featherPx: 30,
        startTimeSeconds: 3.3,
        durationSeconds: 0.5,
      },
    });

    assert.equal(plan1.id, "spatial_mv_take");
    assert.equal(plan1.checksumSha256, plan2.checksumSha256);
    assert.equal(plan1.checksumSha256.length, 64);

    const jsx = plan1.extendScriptLines.join("\n");
    assert.match(jsx, /comp\.motionBlur = true/);
    assert.match(jsx, /ADBE Motion2/);
    assert.match(jsx, /app\.endUndoGroup\(\)/);
  });

  // 5. PROPERTY-BASED TESTING: Portal Scale Strict Monotonicity
  await t.test("PBT: evaluatePortalScale is strictly monotonic non-decreasing for any tau in [0, 1]", () => {
    fc.assert(
      fc.property(
        fc.double({ min: 1000.0, max: 15000.0, noNaN: true }), // maxScale
        fc.double({ min: 2.0, max: 5.0, noNaN: true }),       // gamma
        fc.double({ min: 0.0, max: 1.0, noNaN: true }),       // tauA
        fc.double({ min: 0.0, max: 1.0, noNaN: true }),       // tauB
        (maxScale, gamma, tA, tB) => {
          const tauMin = Math.min(tA, tB);
          const tauMax = Math.max(tA, tB);
          const sMin = InfiniteZoomPortalEngine.evaluatePortalScale(tauMin, maxScale, gamma);
          const sMax = InfiniteZoomPortalEngine.evaluatePortalScale(tauMax, maxScale, gamma);

          return sMax >= sMin;
        }
      ),
      { numRuns: 150 }
    );
  });

  // 6. PROPERTY-BASED TESTING: Snorricam Center Alignment
  await t.test("PBT: calculateAnchorAndPosition always maps position to comp center", () => {
    fc.assert(
      fc.property(
        fc.double({ min: 0.0, max: 3840.0, noNaN: true }),
        fc.double({ min: 0.0, max: 2160.0, noNaN: true }),
        fc.double({ min: 720.0, max: 3840.0, noNaN: true }),
        fc.double({ min: 480.0, max: 2160.0, noNaN: true }),
        (anchorX, anchorY, compW, compH) => {
          const xform = SnorricamEngine.calculateAnchorAndPosition([anchorX, anchorY], compW, compH);
          return (
            xform.anchorPoint[0] === anchorX &&
            xform.anchorPoint[1] === anchorY &&
            xform.position[0] === compW / 2 &&
            xform.position[1] === compH / 2
          );
        }
      ),
      { numRuns: 100 }
    );
  });
});
