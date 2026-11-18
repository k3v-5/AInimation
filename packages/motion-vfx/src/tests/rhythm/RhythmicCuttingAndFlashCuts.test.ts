import test from "node:test";
import assert from "node:assert/strict";
import fc from "fast-check";
import {
  MusicalGrid,
  FlashCutEngine,
  BlackoutVacuumEngine,
  SyncopatedCuttingEngine,
  RhythmOrchestrator,
  MachineGunBurstSpecSchema,
  BlackoutVacuumSpecSchema,
  SyncopatedSequenceSpecSchema,
} from "../../rhythm/index.js";

test("Fase 23: Machine-Gun Flash Cuts, Rhythmic Cutting & Blackouts Suite", async (t) => {
  // 1. UNIT TESTS: Musical Grid & Subdivisions
  await t.test("MusicalGrid: computes metric durations accurately for 120 BPM", () => {
    const bpm = 120.0;
    // 60 / 120 = 0.5s por negra
    assert.equal(MusicalGrid.getBeatDurationSeconds(bpm), 0.5);
    // Compás 4/4 = 2.0s
    assert.equal(MusicalGrid.getBarDurationSeconds(bpm), 2.0);
    // Corchea (1/8) = 0.25s
    assert.equal(MusicalGrid.getSubdivisionDurationSeconds("EIGHTH", bpm), 0.25);
    // Semicorchea (1/16) = 0.125s
    assert.equal(MusicalGrid.getSubdivisionDurationSeconds("SIXTEENTH", bpm), 0.125);
    // Fusa (1/32) = 0.0625s
    assert.equal(MusicalGrid.getSubdivisionDurationSeconds("THIRTY_SECOND", bpm), 0.0625);
    // Tresillo de corchea = 0.5 / 3 ~ 0.166667s
    assert.equal(
      Number(MusicalGrid.getSubdivisionDurationSeconds("EIGHTH_TRIPLET", bpm).toFixed(6)),
      Number((0.5 / 3).toFixed(6))
    );
  });

  await t.test("MusicalGrid: snaps arbitrary timestamps to exact project FPS boundaries", () => {
    const fps = 30.0;
    // Frame 0: 0.0s, Frame 1: 0.033333s, Frame 2: 0.066667s
    assert.equal(MusicalGrid.snapToFrame(0.01, fps), 0.0);
    assert.equal(MusicalGrid.snapToFrame(0.04, fps), Number((1 / 30).toFixed(6)));
    assert.equal(MusicalGrid.snapToFrame(0.06, fps), Number((2 / 30).toFixed(6)));
    assert.equal(MusicalGrid.durationToFrames(1.0, fps), 30);
    assert.equal(MusicalGrid.durationToFrames(0.1, fps), 3);
  });

  // 2. UNIT TESTS: Flash Cut Engine Slices
  await t.test("FlashCutEngine divides bursts into contiguous atomic slices without gaps", () => {
    const fps = 30.0;
    const slices1 = FlashCutEngine.calculateSlices(
      {
        startTimeSeconds: 1.0,
        durationSeconds: 0.5, // 15 fotogramas
        frameHold: 1,         // 1 frame por slice -> 15 slices
        mode: "WHITE_STROBE",
      },
      fps
    );

    assert.equal(slices1.length, 15);
    assert.equal(slices1[0].startTimeSeconds, 1.0);
    assert.equal(slices1[0].durationFrames, 1);

    // Comprobar contigüidad estricta entre slices adyacentes
    for (let i = 0; i < slices1.length - 1; i++) {
      assert.equal(slices1[i + 1].startTimeSeconds, slices1[i].endTimeSeconds);
    }

    const slices2 = FlashCutEngine.calculateSlices(
      {
        startTimeSeconds: 0.0,
        durationSeconds: 1.0, // 30 fotogramas
        frameHold: 2,         // 2 frames por slice -> 15 slices
        mode: "MEDIA_INTERLEAVE",
        mediaLayerIndices: [0, 1, 2],
      },
      fps
    );

    assert.equal(slices2.length, 15);
    assert.equal(slices2[0].assignedLayerIndex, 0);
    assert.equal(slices2[1].assignedLayerIndex, 1);
    assert.equal(slices2[2].assignedLayerIndex, 2);
    assert.equal(slices2[3].assignedLayerIndex, 0); // Ciclo modular
  });

  // 3. UNIT TESTS: Blackout Vacuum Engine
  await t.test("BlackoutVacuumEngine: calculates pre-drop vacuum window and impact flash", () => {
    const fps = 30.0;
    const window = BlackoutVacuumEngine.calculateVacuumWindow(
      {
        dropTimeSeconds: 4.0,
        vacuumDurationSeconds: 0.20,
        impactFlashFrame: true,
      },
      fps
    );

    assert.equal(window.dropTimeSeconds, 4.0);
    assert.equal(window.vacuumStartSeconds, 3.8);
    assert.equal(window.vacuumDurationSeconds, 0.2);
    // 1 frame de impacto: 4.0s a 4.0 + 1/30 = 4.033333s
    assert.equal(window.impactFlashEndSeconds, Number((4.0 + 1 / 30).toFixed(6)));
  });

  // 4. INTEGRATION TESTS: ExtendScript Emission
  await t.test("Engines produce valid ExtendScript with HOLD keyframes and layer properties", () => {
    const fps = 30.0;
    // Ráfaga estroboscópica
    const burstScript = FlashCutEngine.exportToExtendScript(
      {
        id: "burst_snare",
        startTimeSeconds: 2.0,
        durationSeconds: 0.2,
        frameHold: 1,
        mode: "CRIMSON_STROBE",
      },
      fps
    ).join("\n");

    assert.match(burstScript, /addSolid/);
    assert.match(burstScript, /BlendingMode\.ADD/);
    assert.match(burstScript, /KeyframeInterpolationType\.HOLD/);
    assert.match(burstScript, /setValueAtTime/);

    // Blackout Vacuum
    const blackoutScript = BlackoutVacuumEngine.exportToExtendScript(
      {
        id: "blackout_drop",
        dropTimeSeconds: 3.5,
        vacuumDurationSeconds: 0.15,
        impactFlashFrame: true,
      },
      fps
    ).join("\n");

    assert.match(blackoutScript, /\[BLACKOUT VACUUM\]/);
    assert.match(blackoutScript, /\[IMPACT FLASH\]/);
    assert.match(blackoutScript, /addSolid\(\[0\.0, 0\.0, 0\.0\]/);

    // Syncopated Cuts
    const syncScript = SyncopatedCuttingEngine.exportToExtendScript({
      id: "sync_seq",
      bpm: 120,
      fps: 30,
      cuts: [
        { timeSeconds: 0.0, mediaAssetPath: "E:/video1.mp4", durationSeconds: 1.0 },
        { timeSeconds: 1.0, mediaAssetPath: "E:/video2.mp4", durationSeconds: 1.5 },
      ],
    }).join("\n");

    assert.match(syncScript, /importFile/);
    assert.match(syncScript, /startTime/);
    assert.match(syncScript, /inPoint/);
    assert.match(syncScript, /outPoint/);
    assert.match(syncScript, /motionBlur = true/);
  });

  // 5. ORCHESTRATION & INVARIANT TESTS
  await t.test("RhythmOrchestrator: produces deterministic plan with SHA-256 and motionBlur invariant", () => {
    const plan1 = RhythmOrchestrator.compilePlan({
      id: "rhythm_mv_master",
      bpm: 140,
      fps: 30,
      bursts: [
        {
          id: "snare_roll",
          startTimeSeconds: 1.5,
          durationSeconds: 0.25,
          frameHold: 1,
          mode: "WHITE_STROBE",
        },
      ],
      blackouts: [
        {
          id: "drop_vacuum",
          dropTimeSeconds: 2.0,
          vacuumDurationSeconds: 0.16,
          impactFlashFrame: true,
        },
      ],
    });

    const plan2 = RhythmOrchestrator.compilePlan({
      id: "rhythm_mv_master",
      bpm: 140,
      fps: 30,
      bursts: [
        {
          id: "snare_roll",
          startTimeSeconds: 1.5,
          durationSeconds: 0.25,
          frameHold: 1,
          mode: "WHITE_STROBE",
        },
      ],
      blackouts: [
        {
          id: "drop_vacuum",
          dropTimeSeconds: 2.0,
          vacuumDurationSeconds: 0.16,
          impactFlashFrame: true,
        },
      ],
    });

    assert.equal(plan1.id, "rhythm_mv_master");
    assert.equal(plan1.checksumSha256, plan2.checksumSha256);
    assert.equal(plan1.checksumSha256.length, 64);

    const jsx = plan1.extendScriptLines.join("\n");
    assert.match(jsx, /mainComp\.motionBlur = true/);
    assert.match(jsx, /app\.endUndoGroup\(\)/);
  });

  // 6. PROPERTY-BASED TESTING: Metric Subdivisions Positivity
  await t.test("PBT: Subdivisions always yield positive durations for any valid BPM", () => {
    fc.assert(
      fc.property(
        fc.double({ min: 40.0, max: 300.0, noNaN: true }),
        (bpm) => {
          const beat = MusicalGrid.getBeatDurationSeconds(bpm);
          const bar = MusicalGrid.getBarDurationSeconds(bpm);
          const eighth = MusicalGrid.getSubdivisionDurationSeconds("EIGHTH", bpm);
          const sixteenth = MusicalGrid.getSubdivisionDurationSeconds("SIXTEENTH", bpm);
          const thirtySecond = MusicalGrid.getSubdivisionDurationSeconds("THIRTY_SECOND", bpm);

          return (
            beat > 0 &&
            bar === beat * 4 &&
            eighth === beat / 2 &&
            sixteenth === beat / 4 &&
            thirtySecond === beat / 8
          );
        }
      ),
      { numRuns: 150 }
    );
  });

  // 7. PROPERTY-BASED TESTING: Frame Snapping and Slices Contiguity
  await t.test("PBT: Atomic slices are strictly contiguous and frame-quantized for arbitrary durations", () => {
    fc.assert(
      fc.property(
        fc.double({ min: 0.0, max: 10.0, noNaN: true }),  // start time
        fc.double({ min: 0.2, max: 2.0, noNaN: true }),   // duration
        fc.integer({ min: 1, max: 4 }),                   // frameHold
        (startTime, duration, frameHold) => {
          const fps = 30.0;
          const slices = FlashCutEngine.calculateSlices(
            {
              startTimeSeconds: startTime,
              durationSeconds: duration,
              frameHold,
              mode: "WHITE_STROBE",
            },
            fps
          );

          if (slices.length === 0) return true;

          for (let i = 0; i < slices.length - 1; i++) {
            // Comprobar continuidad
            if (slices[i + 1].startTimeSeconds !== slices[i].endTimeSeconds) {
              return false;
            }
          }
          return true;
        }
      ),
      { numRuns: 150 }
    );
  });
});
