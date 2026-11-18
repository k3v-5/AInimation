import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { DSLValidator } from "../../../animation/dsl/validator/DSLValidator.js";

describe("Fase 3E — DSL Validator & Path-Based Error Reporting Tests", () => {
  it("validates a healthy DSL document with zero errors", () => {
    const doc: any = {
      version: 1,
      variables: { dur: 0.5 },
      animations: [
        {
          type: "fadeIn",
          target: "title",
          duration: 0.5,
        },
      ],
    };

    const errors = DSLValidator.validate(doc);
    assert.strictEqual(errors.length, 0);
  });

  it("reports INVALID_DIRECTION with exact JSON path for invalid direction", () => {
    const doc: any = {
      version: 1,
      animations: [
        {
          type: "sequence",
          children: [
            { type: "fadeIn", target: "title" },
            { type: "slideIn", target: "title", direction: "banana" },
          ],
        },
      ],
    };

    const errors = DSLValidator.validate(doc);
    assert.strictEqual(errors.length, 1);
    assert.strictEqual(errors[0].code, "INVALID_DIRECTION");
    assert.strictEqual(errors[0].path, "animations[0].children[1].direction");
    assert.strictEqual(errors[0].received, "banana");
  });

  it("reports UNDEFINED_VARIABLE when referencing an undeclared variable", () => {
    const doc: any = {
      version: 1,
      variables: {},
      animations: [
        {
          type: "slideIn",
          target: "title",
          duration: "$unresolvedDuration",
        },
      ],
    };

    const errors = DSLValidator.validate(doc);
    assert.strictEqual(errors.length, 1);
    assert.strictEqual(errors[0].code, "UNDEFINED_VARIABLE");
    assert.strictEqual(errors[0].path, "animations[0].duration");
  });

  it("reports MISSING_TARGET when primitive animation has no target selector", () => {
    const doc: any = {
      version: 1,
      animations: [
        {
          type: "scaleIn",
        },
      ],
    };

    const errors = DSLValidator.validate(doc);
    assert.strictEqual(errors.length, 1);
    assert.strictEqual(errors[0].code, "MISSING_TARGET");
    assert.strictEqual(errors[0].path, "animations[0].target");
  });
});
