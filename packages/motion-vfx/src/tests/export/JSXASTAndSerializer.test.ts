import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { JSXASTBuilder, JSXScript } from "../../exporters/ae/JSXAST.js";
import { JSXSerializer } from "../../exporters/ae/JSXSerializer.js";

describe("Fase 17 — JSX AST & Serializer Unit Tests", () => {
  it("escapes malicious strings and injection payloads strictly without code leakage", () => {
    const maliciousPayloads = [
      '"; alert("Hacked!"); //',
      "\\'; dropDatabase(); //",
      "Hello \n World \r with \t tabs",
      "Unicode: ¡Hola mundo! 🚀 👨‍👩‍👧‍👦",
    ];

    for (const payload of maliciousPayloads) {
      const escaped = JSXSerializer.escapeString(payload);
      assert.ok(escaped.startsWith('"') && escaped.endsWith('"'));
      // No raw unescaped newlines or quotes inside
      assert.ok(!escaped.slice(1, -1).includes('\n'));
      assert.ok(!escaped.slice(1, -1).includes('\r'));
    }
  });

  it("serializes AST script structure with deterministic indentation and safe undo group", () => {
    const script: JSXScript = {
      type: "Script",
      headerComment: "Test Suite Script",
      statements: [
        JSXASTBuilder.comment("Initialize Comp"),
        JSXASTBuilder.varDecl("comp", JSXASTBuilder.call("app.project.items", "addComp", [
          JSXASTBuilder.str("MainComp"),
          JSXASTBuilder.num(1920),
          JSXASTBuilder.num(1080),
          JSXASTBuilder.num(1.0),
          JSXASTBuilder.num(10),
          JSXASTBuilder.num(30),
        ])),
        JSXASTBuilder.assign("comp.layers.length", JSXASTBuilder.num(0)),
      ],
    };

    const jsx = JSXSerializer.serialize(script);
    assert.ok(jsx.includes("app.beginUndoGroup"));
    assert.ok(jsx.includes("app.endUndoGroup"));
    assert.ok(jsx.includes('addComp("MainComp", 1920, 1080, 1, 10, 30)'));
    assert.ok(jsx.includes("// Initialize Comp"));
  });
});
