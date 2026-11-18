import { describe, it } from "node:test";
import assert from "node:assert/strict";
import fc from "fast-check";
import { MathUtils } from "../../editorial/attention/math-utils.js";

describe("Fase 4H — Attention Math & Canonical Serialization Utilities", () => {
  it("exponentialDecay converges smoothly towards baseline and never drops below baseline", () => {
    const a0 = 0.85;
    const baseline = 0.40;
    const lambda = 0.035;

    const after1s = MathUtils.exponentialDecay(a0, baseline, lambda, 1.0);
    const after18s = MathUtils.exponentialDecay(a0, baseline, lambda, 18.0);
    const after100s = MathUtils.exponentialDecay(a0, baseline, lambda, 100.0);

    assert.ok(after1s < a0, "Attention must decay after 1s");
    assert.ok(after18s < after1s, "Attention must continue decaying after 18s");
    assert.ok(after18s >= 0.60, "Attention after 18s must not prematurely collapse");
    assert.ok(after100s >= baseline, "Attention must not drop below baseline");
    assert.equal(after100s, 0.4136);
  });

  it("composeStimuli is strictly commutative (order-independent)", () => {
    const initial = 0.50;
    const stimuli1 = [0.15, 0.10, 0.22, 0.12];
    const stimuli2 = [0.12, 0.22, 0.10, 0.15];
    const stimuli3 = [0.22, 0.15, 0.12, 0.10];

    const res1 = MathUtils.composeStimuli(initial, stimuli1);
    const res2 = MathUtils.composeStimuli(initial, stimuli2);
    const res3 = MathUtils.composeStimuli(initial, stimuli3);

    assert.equal(res1, res2);
    assert.equal(res2, res3);
  });

  it("clamp and canonicalize reject NaN and Infinity and normalize -0 to 0", () => {
    assert.throws(() => MathUtils.clamp(NaN, 0, 1), /Invalid non-finite number/);
    assert.throws(() => MathUtils.clamp(Infinity, 0, 1), /Invalid non-finite number/);
    assert.throws(() => MathUtils.canonicalize({ bad: NaN }), /Cannot canonicalize non-finite number/);

    assert.equal(MathUtils.clamp(-0, 0, 1), 0);
    assert.equal(MathUtils.canonicalize(-0), 0);
  });

  it("canonicalStringify is strictly idempotent", () => {
    const sample = {
      zeta: 42.12345,
      alpha: "hello",
      beta: [-0, 1.99999, 0],
      nested: { y: 2, x: 1, checksumSha256: "ignored_hash" },
    };

    const str1 = MathUtils.canonicalStringify(sample);
    const parsed = JSON.parse(str1);
    const str2 = MathUtils.canonicalStringify(parsed);

    assert.equal(str1, str2, "Canonical stringify must be strictly idempotent");
    assert.ok(!str1.includes("checksumSha256"), "checksumSha256 must be omitted from canonical payload");
  });

  it("computeCanonicalSha256 produces identical hash regardless of key insertion order", () => {
    const objA = { b: 2, a: 1, c: { y: 20, x: 10 } };
    const objB = { a: 1, c: { x: 10, y: 20 }, b: 2 };

    const hashA = MathUtils.computeCanonicalSha256(objA);
    const hashB = MathUtils.computeCanonicalSha256(objB);

    assert.equal(hashA, hashB);
    assert.equal(hashA.length, 64);
  });

  it("PBT: composeStimuli always produces a finite number in [0.0, 1.0]", () => {
    fc.assert(
      fc.property(
        fc.double({ min: 0.0, max: 1.0, noNaN: true }),
        fc.array(fc.double({ min: 0.0, max: 0.99, noNaN: true }), { maxLength: 10 }),
        (initial, stimuli) => {
          const res = MathUtils.composeStimuli(initial, stimuli);
          return Number.isFinite(res) && res >= 0.0 && res <= 1.0;
        }
      ),
      { numRuns: 50 }
    );
  });
});
