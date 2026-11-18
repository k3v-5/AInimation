import test from "node:test";
import assert from "node:assert/strict";
import fc from "fast-check";
import {
  BoundingBox2D,
  ObjectDetectionEngine,
  TextBehindSubjectEngine,
  MultiTakeCloneEngine,
  Point2D,
} from "../../compositing/subject/index.js";

test("Fase 19: Subject Detection & Multi-Instance Compositing Suite", async (t) => {
  // 1. UNIT TESTS: Geometría e IoU
  await t.test("calculateCentroid calculates exact center point", () => {
    const box: BoundingBox2D = { x: 100, y: 200, width: 400, height: 600 };
    const centroid = ObjectDetectionEngine.calculateCentroid(box);
    assert.equal(centroid.x, 300);
    assert.equal(centroid.y, 500);
  });

  await t.test("calculateIoU computes exact overlaps and handles disjoint boxes", () => {
    const boxA: BoundingBox2D = { x: 0, y: 0, width: 100, height: 100 };
    const boxB: BoundingBox2D = { x: 0, y: 0, width: 100, height: 100 };
    const boxDisjoint: BoundingBox2D = { x: 200, y: 200, width: 100, height: 100 };
    const boxHalf: BoundingBox2D = { x: 50, y: 0, width: 100, height: 100 };

    assert.equal(ObjectDetectionEngine.calculateIoU(boxA, boxB), 1.0);
    assert.equal(ObjectDetectionEngine.calculateIoU(boxA, boxDisjoint), 0.0);

    // Half overlap: Inter = 50 * 100 = 5000; Union = 10000 + 10000 - 5000 = 15000 -> IoU = 5000/15000 = 1/3 ~ 0.333333
    const iouHalf = ObjectDetectionEngine.calculateIoU(boxA, boxHalf);
    assert.ok(Math.abs(iouHalf - 1 / 3) < 1e-4);
  });

  await t.test("isPointInPolygon accurately tests point containment via Ray-Casting", () => {
    const square: Point2D[] = [
      { x: 0, y: 0 },
      { x: 100, y: 0 },
      { x: 100, y: 100 },
      { x: 0, y: 100 },
    ];

    assert.equal(ObjectDetectionEngine.isPointInPolygon({ x: 50, y: 50 }, square), true);
    assert.equal(ObjectDetectionEngine.isPointInPolygon({ x: 150, y: 50 }, square), false);
    assert.equal(ObjectDetectionEngine.isPointInPolygon({ x: -10, y: 50 }, square), false);
  });

  await t.test("createProceduralPersonDetection generates valid detected subject", () => {
    const det = ObjectDetectionEngine.createProceduralPersonDetection({
      frameIndex: 0,
      timestampSeconds: 1.5,
      compWidth: 1920,
      compHeight: 1080,
      zone: "CENTER",
    });

    assert.equal(det.label, "PERSON");
    assert.equal(det.confidence, 0.98);
    assert.ok(det.contourPoints && det.contourPoints.length >= 3);
    assert.ok(det.boundingBox.width > 0);
  });

  // 2. MATHEMATICAL & FILTERING TESTS
  await t.test("smoothTrajectory applies exponential smoothing without overshoot", () => {
    const rawPoints: Point2D[] = [
      { x: 0, y: 0 },
      { x: 100, y: 100 },
      { x: 100, y: 100 },
      { x: 100, y: 100 },
    ];

    const smoothed = ObjectDetectionEngine.smoothTrajectory(rawPoints, 0.5);
    assert.equal(smoothed[0].x, 0);
    assert.equal(smoothed[1].x, 50); // 0.5 * 100 + 0.5 * 0 = 50
    assert.equal(smoothed[2].x, 75); // 0.5 * 100 + 0.5 * 50 = 75
    assert.equal(smoothed[3].x, 87.5); // 0.5 * 100 + 0.5 * 75 = 87.5
  });

  await t.test("calculateSplitBounds produces non-overlapping continuous columns", () => {
    const takes = [
      { takeId: "t1", assetPath: "a1.mp4", subjectZone: "LEFT" as const, inPointSeconds: 0, durationSeconds: 5, volumeDb: 0, isMasterBackground: true },
      { takeId: "t2", assetPath: "a2.mp4", subjectZone: "CENTER" as const, inPointSeconds: 0, durationSeconds: 5, volumeDb: 0, isMasterBackground: false },
      { takeId: "t3", assetPath: "a3.mp4", subjectZone: "RIGHT" as const, inPointSeconds: 0, durationSeconds: 5, volumeDb: 0, isMasterBackground: false },
    ];

    const bounds = MultiTakeCloneEngine.calculateSplitBounds(takes, 1920);
    assert.equal(bounds.length, 3);
    assert.equal(bounds[0].xMin, 0);
    assert.equal(bounds[0].xMax, 640);
    assert.equal(bounds[1].xMin, 640);
    assert.equal(bounds[1].xMax, 1280);
    assert.equal(bounds[2].xMin, 1280);
    assert.equal(bounds[2].xMax, 1920);
  });

  // 3. INVARIANT TESTS: Text Behind Subject & Clones Compilation
  await t.test("TextBehindSubjectEngine compiles valid 3-layer sandwich with motion blur and TIME style", () => {
    const plan = TextBehindSubjectEngine.compile({
      id: "text_demo",
      sourceAssetPath: "E:/video.mp4",
      text: "GUADALAJARA",
      typography: {
        fontFamily: "Impact",
        fontSize: 180,
        colorHex: "#FF1424",
        verticalStretchPercent: 130,
        tracking: -25,
      },
      position: { x: 540, y: 960 },
      featherPx: 12.0,
      backgroundBlurPx: 15.0,
      inTimeSeconds: 0.0,
      outTimeSeconds: 6.0,
    });

    assert.equal(plan.type, "TEXT_BEHIND_SUBJECT");
    assert.equal(plan.layersCount, 3);
    assert.equal(plan.checksumSha256.length, 64);

    const jsx = plan.extendScriptLines.join("\n");
    assert.match(jsx, /mainComp\.motionBlur = true/);
    assert.match(jsx, /ParagraphJustification\.CENTER_JUSTIFY/);
    assert.match(jsx, /\[BG\] Background Video/);
    assert.match(jsx, /\[TEXT\] Behind Subject/);
    assert.match(jsx, /\[FG CUTOUT\] Foreground Subject/);
    assert.match(jsx, /ADBE Fast Blur/);
    assert.match(jsx, /maskFeather/);
  });

  await t.test("MultiTakeCloneEngine compiles clones with audio deduplication and split masks", () => {
    const plan = MultiTakeCloneEngine.compile({
      id: "clones_demo",
      compWidth: 1920,
      compHeight: 1080,
      fps: 30,
      takes: [
        { takeId: "take_left", assetPath: "left.mp4", subjectZone: "LEFT", inPointSeconds: 0, durationSeconds: 8, volumeDb: 0, isMasterBackground: true },
        { takeId: "take_right", assetPath: "right.mp4", subjectZone: "RIGHT", inPointSeconds: 0, durationSeconds: 8, volumeDb: 0, isMasterBackground: false },
      ],
      edgeFeatherPx: 30.0,
      totalDurationSeconds: 8.0,
      audioMode: "ACTIVE_SPEAKER",
    });

    assert.equal(plan.type, "MULTI_TAKE_CLONES");
    assert.equal(plan.layersCount, 2);
    assert.equal(plan.checksumSha256.length, 64);

    const jsx = plan.extendScriptLines.join("\n");
    assert.match(jsx, /cloneComp\.motionBlur = true/);
    assert.match(jsx, /\[CLONE TAKE 1\] LEFT \(MASTER BG\)/);
    assert.match(jsx, /\[CLONE TAKE 2\] RIGHT/);
    assert.match(jsx, /audioEnabled = false/); // Desduplicación de audio en la segunda toma
    assert.match(jsx, /maskFeather/);
  });

  // 4. PROPERTY-BASED TESTING (fast-check)
  await t.test("PBT: IoU is strictly symmetric and bounded within [0.0, 1.0]", () => {
    fc.assert(
      fc.property(
        fc.record({
          x: fc.float({ min: 0, max: 1000, noNaN: true }),
          y: fc.float({ min: 0, max: 1000, noNaN: true }),
          width: fc.float({ min: 1, max: 500, noNaN: true }),
          height: fc.float({ min: 1, max: 500, noNaN: true }),
        }),
        fc.record({
          x: fc.float({ min: 0, max: 1000, noNaN: true }),
          y: fc.float({ min: 0, max: 1000, noNaN: true }),
          width: fc.float({ min: 1, max: 500, noNaN: true }),
          height: fc.float({ min: 1, max: 500, noNaN: true }),
        }),
        (b1, b2) => {
          const iou1 = ObjectDetectionEngine.calculateIoU(b1, b2);
          const iou2 = ObjectDetectionEngine.calculateIoU(b2, b1);

          if (iou1 < 0 || iou1 > 1.0) return false;
          if (Math.abs(iou1 - iou2) > 1e-6) return false;
          return true;
        }
      ),
      { numRuns: 100 }
    );
  });

  await t.test("PBT: Split bounds are always contiguous without gaps for any take count and width", () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 2, max: 6 }), // takes count
        fc.integer({ min: 720, max: 3840 }), // width
        (takeCount, width) => {
          const takes = Array.from({ length: takeCount }, (_, i) => ({
            takeId: `t_${i}`,
            assetPath: `video_${i}.mp4`,
            subjectZone: "CUSTOM" as const,
            inPointSeconds: 0,
            durationSeconds: 5,
            volumeDb: 0,
            isMasterBackground: i === 0,
          }));

          const bounds = MultiTakeCloneEngine.calculateSplitBounds(takes, width);

          if (bounds[0].xMin !== 0) return false;
          if (bounds[bounds.length - 1].xMax !== width) return false;

          for (let i = 0; i < bounds.length - 1; i++) {
            if (bounds[i].xMax !== bounds[i + 1].xMin) return false;
          }

          return true;
        }
      ),
      { numRuns: 100 }
    );
  });
});
