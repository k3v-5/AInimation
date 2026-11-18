import assert from "node:assert/strict";
import { describe, it } from "node:test";
import fc from "fast-check";
import { TimeMapper } from "../../../vlog/index.js";

describe("Milestone 5 — Time Mapping Suite", () => {
  it("maps source to derived and derived to source deterministically", () => {
    const mapper = new TimeMapper([
      {
        sourceStart: 0.0,
        sourceEnd: 5.0,
        derivedStart: 0.0,
        derivedEnd: 5.5, // Estirado 1.1x
        strategy: "STRETCH",
        scaleFactor: 1.1,
      },
      {
        sourceStart: 5.0,
        sourceEnd: 10.0,
        derivedStart: 5.5,
        derivedEnd: 10.0, // Comprimido a 4.5s
        strategy: "TRIM",
        scaleFactor: 0.9,
      },
    ]);

    // Punto medio del primer segmento: t=2.5s -> 2.5 * 1.1 = 2.75s
    const derived1 = mapper.mapSourceToDerived(2.5);
    assert.equal(derived1, 2.75);

    // Mapeo inverso
    const source1 = mapper.mapDerivedToSource(derived1);
    assert.equal(source1, 2.5);

    // Límite de inicio y fin
    assert.equal(mapper.mapSourceToDerived(0.0), 0.0);
    assert.equal(mapper.mapSourceToDerived(5.0), 5.5);
    assert.equal(mapper.mapSourceToDerived(10.0), 10.0);
  });

  it("handles visual hold mapping: derived advances while source stays frozen", () => {
    const mapper = new TimeMapper([
      {
        sourceStart: 0.0,
        sourceEnd: 4.0,
        derivedStart: 0.0,
        derivedEnd: 4.0,
        strategy: "KEEP",
        scaleFactor: 1.0,
      },
      {
        sourceStart: 4.0,
        sourceEnd: 4.0, // Duración fuente 0 (hold)
        derivedStart: 4.0,
        derivedEnd: 6.0, // 2 segundos de freeze frame
        strategy: "HOLD",
        scaleFactor: Infinity,
      },
    ]);

    assert.equal(mapper.mapSourceToDerived(2.0), 2.0);
    // Durante el hold (entre 4.0 y 6.0 en derived), source debe permanecer congelado en 4.0
    assert.equal(mapper.mapDerivedToSource(5.0), 4.0);
    assert.equal(mapper.mapDerivedToSource(6.0), 4.0);
  });

  it("PBT: mapSourceToDerived is strictly monotonic non-decreasing", () => {
    const mapper = new TimeMapper([
      {
        sourceStart: 0.0,
        sourceEnd: 5.0,
        derivedStart: 0.0,
        derivedEnd: 6.0,
        strategy: "STRETCH",
        scaleFactor: 1.2,
      },
      {
        sourceStart: 5.0,
        sourceEnd: 10.0,
        derivedStart: 6.0,
        derivedEnd: 10.0,
        strategy: "TRIM",
        scaleFactor: 0.8,
      },
    ]);

    fc.assert(
      fc.property(
        fc.double({ min: 0.0, max: 5.0, noNaN: true }),
        fc.double({ min: 5.0, max: 10.0, noNaN: true }),
        (t1, t2) => {
          const d1 = mapper.mapSourceToDerived(t1);
          const d2 = mapper.mapSourceToDerived(t2);
          assert.ok(d1 <= d2, `Monotonicity violated: d1 (${d1}) > d2 (${d2}) for t1 (${t1}) <= t2 (${t2})`);
        }
      )
    );
  });
});
