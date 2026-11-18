import test from "node:test";
import assert from "node:assert/strict";
import fc from "fast-check";
import {
  BeatSyncEngine,
  BeatGridSpec,
  CandidateClip,
} from "../../editorial/audio/index.js";

test("BeatSyncEngine — Rhythmic Audio Transient & Beat Synchronization Suite", async (t) => {
  // 1. UNIT TESTS: BPM Grid Generation
  await t.test("generateBeatGrid computes exact mathematical intervals and downbeats for 120 BPM in 4/4", () => {
    const spec: BeatGridSpec = {
      bpm: 120,
      timeSignature: "4/4",
      offsetSeconds: 0.0,
      totalDurationSeconds: 4.0,
      subdivision: 1,
    };

    const { beats, markers } = BeatSyncEngine.generateBeatGrid(spec);

    // 120 BPM = 2 beats per second (every 0.5s)
    // At t = 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0 -> 9 beats
    assert.equal(beats.length, 9);
    assert.equal(beats[0].timestampSeconds, 0.0);
    assert.equal(beats[0].isDownbeat, true); // Bar 1, beat 1
    assert.equal(beats[1].timestampSeconds, 0.5);
    assert.equal(beats[1].isDownbeat, false); // Bar 1, beat 2
    assert.equal(beats[4].timestampSeconds, 2.0);
    assert.equal(beats[4].isDownbeat, true); // Bar 2, beat 1

    assert.equal(markers.length, 9);
    assert.equal(markers[0].name, "BAR 1 (DOWNBEAT)");
    assert.equal(markers[1].name, "Beat 1.2");
  });

  await t.test("generateBeatGrid handles 3/4 time signature with downbeats every 3 beats", () => {
    const spec: BeatGridSpec = {
      bpm: 60, // 1 beat per second
      timeSignature: "3/4",
      offsetSeconds: 0.0,
      totalDurationSeconds: 6.0,
      subdivision: 1,
    };

    const { beats } = BeatSyncEngine.generateBeatGrid(spec);
    assert.equal(beats.length, 7); // 0, 1, 2, 3, 4, 5, 6
    assert.equal(beats[0].isDownbeat, true); // Measure 1
    assert.equal(beats[1].isDownbeat, false);
    assert.equal(beats[2].isDownbeat, false);
    assert.equal(beats[3].isDownbeat, true); // Measure 2
    assert.equal(beats[6].isDownbeat, true); // Measure 3
  });

  // 2. UNIT TESTS: Adaptive Energy Transient Detection
  await t.test("detectTransientsFromEnergy identifies transient onsets and enforces refractory period", () => {
    const samples: { time: number; energy: number }[] = [];
    // Crear señal sintética de 2 segundos con 3 picos claros a 0.5s, 0.6s (demasiado cerca, <0.12s) y 1.2s
    for (let i = 0; i <= 200; i++) {
      const time = Number((i * 0.01).toFixed(3));
      let energy = 0.05 + Math.random() * 0.02; // Ruido de fondo

      if (Math.abs(time - 0.5) < 0.005) energy = 0.9;
      if (Math.abs(time - 0.55) < 0.005) energy = 0.85; // Ignorado por periodo refractario
      if (Math.abs(time - 1.2) < 0.005) energy = 0.95;

      samples.push({ time, energy });
    }

    const transients = BeatSyncEngine.detectTransientsFromEnergy(samples, {
      sensitivityK: 1.2,
      refractorySeconds: 0.12,
    });

    assert.ok(transients.length >= 2);
    // El primer pico debe estar cerca de 0.5s
    assert.ok(Math.abs(transients[0].timestampSeconds - 0.5) < 0.02);
    // El segundo pico debe estar cerca de 1.2s (0.55 fue refractado)
    assert.ok(Math.abs(transients[1].timestampSeconds - 1.2) < 0.02);
  });

  // 3. INTEGRATION TESTS: Continuous Beat-Synced Cuts Alignment
  await t.test("alignCutsToBeat guarantees zero gap continuity and aligns exactly to beats", () => {
    const spec: BeatGridSpec = {
      bpm: 120,
      timeSignature: "4/4",
      offsetSeconds: 0.0,
      totalDurationSeconds: 10.0,
      subdivision: 1,
    };
    const { beats } = BeatSyncEngine.generateBeatGrid(spec);

    const clips: CandidateClip[] = [
      { id: "c1", assetId: "media1.mp4", availableDurationSeconds: 8.0 },
      { id: "c2", assetId: "media2.mp4", availableDurationSeconds: 8.0 },
      { id: "c3", assetId: "media3.mp4", availableDurationSeconds: 8.0 },
    ];

    const plan = BeatSyncEngine.alignCutsToBeat({
      clips,
      beatGrid: beats,
      mode: "EVERY_BEAT",
      minCutDurationSeconds: 0.5,
    });

    assert.ok(plan.cuts.length > 0);
    assert.equal(plan.cuts[0].timelineStart, 0.0);

    // Invariante de continuidad: cada clip empieza exactamente donde termina el anterior
    for (let i = 0; i < plan.cuts.length - 1; i++) {
      const current = plan.cuts[i];
      const next = plan.cuts[i + 1];
      assert.equal(current.timelineEnd, next.timelineStart, `Gap detectado en corte ${i}`);
      assert.equal(current.driftSeconds, 0.0, `Drift no nulo en corte ${i}`);
      assert.ok(current.durationSeconds >= 0.5, `Duración sub-perceptual en corte ${i}`);
    }

    assert.ok(plan.checksumSha256.length === 64);
  });

  await t.test("alignCutsToBeat in DOWNBEAT_ONLY mode cuts exclusively on measure starts", () => {
    const spec: BeatGridSpec = {
      bpm: 120,
      timeSignature: "4/4",
      offsetSeconds: 0.0,
      totalDurationSeconds: 12.0,
      subdivision: 1,
    };
    const { beats } = BeatSyncEngine.generateBeatGrid(spec);

    const clips: CandidateClip[] = [
      { id: "c1", assetId: "media1.mp4", availableDurationSeconds: 10.0 },
      { id: "c2", assetId: "media2.mp4", availableDurationSeconds: 10.0 },
    ];

    const plan = BeatSyncEngine.alignCutsToBeat({
      clips,
      beatGrid: beats,
      mode: "DOWNBEAT_ONLY",
      minCutDurationSeconds: 1.0,
    });

    for (const cut of plan.cuts) {
      assert.equal(cut.isDownbeat, true);
      // En 120 BPM 4/4, cada compás dura 2.0s
      assert.equal(cut.durationSeconds, 2.0);
    }
  });

  // 4. EXTENDSCRIPT EXPORT TEST
  await t.test("exportToExtendScript generates valid marker placement commands", () => {
    const spec: BeatGridSpec = {
      bpm: 120,
      timeSignature: "4/4",
      offsetSeconds: 0.0,
      totalDurationSeconds: 2.0,
      subdivision: 1,
    };
    const { beats } = BeatSyncEngine.generateBeatGrid(spec);
    const clips: CandidateClip[] = [{ id: "c1", assetId: "media.mp4", availableDurationSeconds: 5.0 }];

    const plan = BeatSyncEngine.alignCutsToBeat({ clips, beatGrid: beats });
    const jsxLines = BeatSyncEngine.exportToExtendScript(plan, { compVarName: "myComp" });

    assert.ok(jsxLines.length > 0);
    assert.match(jsxLines[0], /RHYTHMIC BEAT SYNC/);
    assert.match(jsxLines[1], /myComp\.markerProperty\.setValueAtTime/);
  });

  // 5. PROPERTY-BASED TESTING (PBT con fast-check)
  await t.test("PBT: For any valid BPM and duration, beats are strictly monotonic and cuts contiguous", () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 60, max: 200 }), // bpm
        fc.float({ min: 4.0, max: 20.0, noNaN: true }), // duration
        fc.constantFrom("4/4" as const, "3/4" as const),
        (bpm, duration, timeSig) => {
          const { beats } = BeatSyncEngine.generateBeatGrid({
            bpm,
            timeSignature: timeSig,
            offsetSeconds: 0.0,
            totalDurationSeconds: duration,
            subdivision: 1,
          });

          // Monotonía estricta de beats
          for (let i = 0; i < beats.length - 1; i++) {
            if (beats[i + 1].timestampSeconds <= beats[i].timestampSeconds) return false;
          }

          const clips: CandidateClip[] = [
            { id: "c1", assetId: "test1.mp4", availableDurationSeconds: 30 },
            { id: "c2", assetId: "test2.mp4", availableDurationSeconds: 30 },
          ];

          const plan = BeatSyncEngine.alignCutsToBeat({
            clips,
            beatGrid: beats,
            mode: "EVERY_BEAT",
            minCutDurationSeconds: 0.2,
          });

          // Monotonía y continuidad de cortes
          for (let i = 0; i < plan.cuts.length - 1; i++) {
            if (plan.cuts[i].timelineEnd !== plan.cuts[i + 1].timelineStart) return false;
            if (plan.cuts[i].durationSeconds <= 0) return false;
          }

          return true;
        }
      ),
      { numRuns: 100 }
    );
  });
});
