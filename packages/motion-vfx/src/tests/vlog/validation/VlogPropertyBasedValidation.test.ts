import assert from "node:assert/strict";
import { describe, it } from "node:test";
import fc from "fast-check";
import {
  AudioDuckingEngine,
  HaversineGeodesic,
  SafeZoneLayoutEngine,
} from "../../../vlog/index.js";

describe("Milestone 9 — Property-Based Mathematical & Invariant Validation Suite", () => {
  it("PBT: Haversine geodesic satisfies the triangle inequality d(A,C) <= d(A,B) + d(B,C) + eps", () => {
    fc.assert(
      fc.property(
        fc.double({ min: -60.0, max: 60.0, noNaN: true }),
        fc.double({ min: -120.0, max: 120.0, noNaN: true }),
        fc.double({ min: -60.0, max: 60.0, noNaN: true }),
        fc.double({ min: -120.0, max: 120.0, noNaN: true }),
        fc.double({ min: -60.0, max: 60.0, noNaN: true }),
        fc.double({ min: -120.0, max: 120.0, noNaN: true }),
        (latA, lonA, latB, lonB, latC, lonC) => {
          const dAB = HaversineGeodesic.calculateDistanceKm(latA, lonA, latB, lonB);
          const dBC = HaversineGeodesic.calculateDistanceKm(latB, lonB, latC, lonC);
          const dAC = HaversineGeodesic.calculateDistanceKm(latA, lonA, latC, lonC);

          const epsilon = 0.01; // Tolerancia numérica de redondeo
          assert.ok(
            dAC <= dAB + dBC + epsilon,
            `Triangle inequality violated: ${dAC} > ${dAB} + ${dBC}`
          );
        }
      ),
      { numRuns: 100 }
    );
  });

  it("PBT: Audio Ducking envelope keyframes always strictly bounded within [duckDb, 0.0]", () => {
    fc.assert(
      fc.property(
        fc.double({ min: -24.0, max: -3.0, noNaN: true }),
        fc.double({ min: 1.0, max: 10.0, noNaN: true }),
        fc.double({ min: 0.5, max: 4.0, noNaN: true }),
        (duckDb, start, dur) => {
          const env = AudioDuckingEngine.generateDuckingEnvelope(
            "target",
            "trigger",
            [{ startSeconds: start, endSeconds: start + dur }],
            { duckAmountDb: duckDb }
          );

          for (const kf of env.keyframes) {
            assert.ok(kf.gainDb >= duckDb - 0.001);
            assert.ok(kf.gainDb <= 0.001);
          }
        }
      ),
      { numRuns: 100 }
    );
  });

  it("PBT: Safe Zone placement always yields valid positive width and height", () => {
    fc.assert(
      fc.property(
        fc.constantFrom("16:9", "9:16", "1:1", "4:5", "21:9"),
        fc.integer({ min: 50, max: 500 }),
        fc.integer({ min: 30, max: 300 }),
        (aspectRatio: any, w, h) => {
          const placement = SafeZoneLayoutEngine.resolveSafePlacement(
            "TOP_LEFT",
            w,
            h,
            [],
            aspectRatio
          );

          assert.ok(placement.box.width > 0);
          assert.ok(placement.box.height > 0);
          assert.ok(placement.box.x >= 0);
          assert.ok(placement.box.y >= 0);
        }
      ),
      { numRuns: 100 }
    );
  });
});
