import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { Composition } from "../../core/composition.js";
import { ShapeElement } from "../../elements/ShapeElement.js";
import { ProjectResourceLimitError } from "../../errors/runtime-errors.js";
import { DeterminismValidator } from "../../runtime/validation/DeterminismValidator.js";
import { ReferentialIntegrityValidator } from "../../runtime/validation/ReferentialIntegrityValidator.js";
import { ResourceValidator } from "../../runtime/validation/ResourceValidator.js";
import { RuntimeValidator } from "../../runtime/validation/RuntimeValidator.js";

describe("Fase 18 — Multi-Layer Runtime Validation Tests", () => {
  it("detects missing parent and circular hierarchy cycles", () => {
    const cyclicProject = {
      elements: [
        { id: "elem_A", parentId: "elem_B" },
        { id: "elem_B", parentId: "elem_A" },
        { id: "elem_C", parentId: "non_existent_id" },
      ],
    };

    const diagnostics = ReferentialIntegrityValidator.validate(cyclicProject);
    const cycleDiag = diagnostics.find((d) => d.code === "HIERARCHY_CYCLE_DETECTED");
    const missingDiag = diagnostics.find((d) => d.code === "MISSING_PARENT_ID");

    assert.ok(cycleDiag);
    assert.ok(missingDiag);
  });

  it("throws ProjectResourceLimitError when layers or keyframes exceed limits", () => {
    const hugeProject = {
      elements: Array.from({ length: 5001 }, (_, i) => ({ id: `elem_${i}`, name: `Elem ${i}` })),
    };

    assert.throws(
      () => ResourceValidator.validate(hugeProject),
      (err: any) => err instanceof ProjectResourceLimitError
    );
  });

  it("verifies temporal determinism on evaluated frames", () => {
    const comp = new Composition({ name: "DetComp", width: 1920, height: 1080, fps: 30, duration: 10 });
    const shape = new ShapeElement({ id: "s1", name: "Box", shapeType: "rectangle", shapeData: { width: 100, height: 100 } });
    shape.transform.position.setValue({ x: 500, y: 500 });
    comp.addElement(shape);

    const result = DeterminismValidator.verifyDeterminism(comp);
    assert.ok(result.verified);
    assert.ok(result.hash.length === 64);
  });
});
