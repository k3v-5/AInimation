export * from "./compiler/DSLCompiler.js";
export * from "./parser/DSLParser.js";
export * from "./types/index.js";
export * from "./validator/DSLValidator.js";

import { DSLCompiler } from "./compiler/DSLCompiler.js";
import { DSLParser } from "./parser/DSLParser.js";
import { AnimationIR, DiagnosticError, DSLDocument } from "./types/index.js";
import { DSLValidator } from "./validator/DSLValidator.js";

/**
 * Facade de conveniencia para la capa DSL de animación (Fase 3E).
 */
export function parseDSL(input: string | Record<string, unknown>): DSLDocument {
  return DSLParser.parse(input);
}

export function validateDSL(doc: DSLDocument): DiagnosticError[] {
  return DSLValidator.validate(doc);
}

export function compileDSL(input: string | Record<string, unknown> | DSLDocument): AnimationIR {
  return DSLCompiler.compile(input);
}
