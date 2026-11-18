import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { DSLParser } from "../../../animation/dsl/parser/DSLParser.js";

describe("Fase 3E — DSL Parser & Variable Resolution Tests", () => {
  it("parses valid JSON string and resolves variable references ($distance, $duration)", () => {
    const jsonStr = JSON.stringify({
      version: 1,
      variables: {
        entranceDuration: 0.75,
        slideDist: 150,
      },
      animations: [
        {
          type: "slideIn",
          target: "hero_title",
          duration: "$entranceDuration",
          distance: "$slideDist",
          direction: "up",
        },
      ],
    });

    const doc = DSLParser.parse(jsonStr);
    assert.strictEqual(doc.version, 1);
    assert.strictEqual((doc.animations[0] as any).duration, 0.75);
    assert.strictEqual((doc.animations[0] as any).distance, 150);
  });

  it("throws SerializationError on invalid JSON syntax", () => {
    assert.throws(
      () => DSLParser.parse("{ invalid json content ..."),
      /Invalid JSON in DSL input/
    );
  });

  it("throws SerializationError on unsupported version", () => {
    assert.throws(
      () => DSLParser.parse({ version: 2, animations: [] }),
      /Unsupported DSL version '2'/
    );
  });
});
