import { ValidationError } from "../../../errors/index.js";
import { DiagnosticError, DSLBasicAnimationNode, DSLCompositionNode, DSLDocument, DSLNode } from "../types/index.js";

const VALID_PRIMITIVES = new Set([
  "fadeIn",
  "fadeOut",
  "slideIn",
  "slideOut",
  "scaleIn",
  "scaleOut",
  "rotateIn",
  "rotateOut",
]);

const VALID_COMPOSITIONS = new Set([
  "parallel",
  "sequence",
  "delay",
  "hold",
  "repeat",
  "offset",
  "stagger",
]);

const VALID_DIRECTIONS = new Set(["left", "right", "up", "down"]);

/**
 * Validador estructural y semántico con diagnóstico de rutas para el Animation DSL (Fase 3E).
 */
export class DSLValidator {
  /**
   * Valida un DSLDocument retornando todos los errores de diagnóstico encontrados.
   */
  public static validate(doc: DSLDocument): DiagnosticError[] {
    const errors: DiagnosticError[] = [];

    if (!doc || typeof doc !== "object") {
      errors.push({
        path: "$",
        code: "INVALID_DOCUMENT",
        message: "DSL Document must be an object.",
        received: doc,
      });
      return errors;
    }

    if (doc.version !== 1) {
      errors.push({
        path: "version",
        code: "UNSUPPORTED_VERSION",
        message: `Expected version 1, received '${doc.version}'.`,
        received: doc.version,
      });
    }

    if (!Array.isArray(doc.animations)) {
      errors.push({
        path: "animations",
        code: "INVALID_ANIMATIONS_LIST",
        message: "Field 'animations' must be an array of animation nodes.",
        received: doc.animations,
      });
      return errors;
    }

    doc.animations.forEach((node, index) => {
      this.validateNode(node, `animations[${index}]`, errors, doc.variables ?? {});
    });

    return errors;
  }

  /**
   * Valida un DSLDocument y lanza ValidationError con resumen diagnóstico si se encuentran errores.
   */
  public static assertValid(doc: DSLDocument): void {
    const errors = this.validate(doc);
    if (errors.length > 0) {
      const summary = errors.map((e) => `[${e.code}] at ${e.path}: ${e.message}`).join("\n");
      throw new ValidationError(`DSL validation failed with ${errors.length} errors:\n${summary}`);
    }
  }

  private static validateNode(
    node: any,
    path: string,
    errors: DiagnosticError[],
    variables: Record<string, number | string>
  ): void {
    if (!node || typeof node !== "object") {
      errors.push({
        path,
        code: "INVALID_NODE",
        message: "Animation node must be an object.",
        received: node,
      });
      return;
    }

    const { type } = node;
    if (!type || typeof type !== "string") {
      errors.push({
        path: `${path}.type`,
        code: "MISSING_TYPE",
        message: "Field 'type' is required on all animation nodes.",
        received: type,
      });
      return;
    }

    // 1. Validar variables no resueltas en propiedades de este nodo
    for (const [k, v] of Object.entries(node)) {
      if (typeof v === "string" && v.startsWith("$")) {
        const varName = v.slice(1);
        if (!(varName in variables)) {
          errors.push({
            path: `${path}.${k}`,
            code: "UNDEFINED_VARIABLE",
            message: `Variable '${v}' is not defined in the document variables.`,
            received: v,
          });
        }
      }
    }

    // 2. Validar tipos primitivos
    if (VALID_PRIMITIVES.has(type)) {
      this.validatePrimitiveNode(node as DSLBasicAnimationNode, path, errors);
      return;
    }

    // 3. Validar combinadores y composiciones
    if (VALID_COMPOSITIONS.has(type)) {
      this.validateCompositionNode(node as DSLCompositionNode, path, errors, variables);
      return;
    }

    // 4. Validar presets (reconocido conceptualmente para 4A)
    if (type === "preset") {
      if (!node.name || typeof node.name !== "string") {
        errors.push({
          path: `${path}.name`,
          code: "MISSING_PRESET_NAME",
          message: "Preset node requires a non-empty 'name' string.",
          received: node.name,
        });
      }
      if (!node.target || typeof node.target !== "string") {
        errors.push({
          path: `${path}.target`,
          code: "MISSING_TARGET",
          message: "Preset node requires a 'target' selector string.",
          received: node.target,
        });
      }
      return;
    }

    // 5. Validar animación tipográfica (Fase 4B)
    if (type === "textAnimation") {
      if (!node.target || typeof node.target !== "string") {
        errors.push({
          path: `${path}.target`,
          code: "MISSING_TARGET",
          message: "textAnimation node requires a target selector string.",
          received: node.target,
        });
      }
      if (!node.animation || typeof node.animation !== "object") {
        errors.push({
          path: `${path}.animation`,
          code: "MISSING_ANIMATION",
          message: "textAnimation node requires an 'animation' primitive definition.",
          received: node.animation,
        });
      } else {
        this.validateNode(node.animation, `${path}.animation`, errors, variables);
      }
      if (node.scope && !["element", "line", "word", "character"].includes(node.scope)) {
        errors.push({
          path: `${path}.scope`,
          code: "INVALID_TEXT_SCOPE",
          message: `Expected scope to be 'element' | 'line' | 'word' | 'character', got '${node.scope}'.`,
          received: node.scope,
        });
      }
      if (node.order && !["forward", "reverse", "random", "center", "edges"].includes(node.order)) {
        errors.push({
          path: `${path}.order`,
          code: "INVALID_TEXT_ORDER",
          message: `Expected order to be 'forward' | 'reverse' | 'random' | 'center' | 'edges', got '${node.order}'.`,
          received: node.order,
        });
      }
      return;
    }

    errors.push({
      path: `${path}.type`,
      code: "UNKNOWN_NODE_TYPE",
      message: `Unknown animation node type '${type}'.`,
      received: type,
    });
  }

  private static validatePrimitiveNode(node: DSLBasicAnimationNode, path: string, errors: DiagnosticError[]): void {
    if (!node.target || typeof node.target !== "string") {
      errors.push({
        path: `${path}.target`,
        code: "MISSING_TARGET",
        message: `Primitive animation '${node.type}' requires a target selector.`,
        received: node.target,
      });
    }

    if (node.duration !== undefined && typeof node.duration === "number" && node.duration <= 0) {
      errors.push({
        path: `${path}.duration`,
        code: "INVALID_DURATION",
        message: `Duration must be a positive number (> 0), received ${node.duration}.`,
        received: node.duration,
      });
    }

    if (node.delay !== undefined && typeof node.delay === "number" && node.delay < 0) {
      errors.push({
        path: `${path}.delay`,
        code: "INVALID_DELAY",
        message: `Delay must be a non-negative number (>= 0), received ${node.delay}.`,
        received: node.delay,
      });
    }

    if (node.type === "slideIn" || node.type === "slideOut") {
      if (node.direction !== undefined && !VALID_DIRECTIONS.has(node.direction)) {
        errors.push({
          path: `${path}.direction`,
          code: "INVALID_DIRECTION",
          message: `Expected one of: left | right | up | down, received '${node.direction}'.`,
          received: node.direction,
        });
      }
      if (node.distance !== undefined && typeof node.distance === "number" && node.distance < 0) {
        errors.push({
          path: `${path}.distance`,
          code: "INVALID_DISTANCE",
          message: `Distance must be non-negative, received ${node.distance}.`,
          received: node.distance,
        });
      }
    }
  }

  private static validateCompositionNode(
    node: DSLCompositionNode,
    path: string,
    errors: DiagnosticError[],
    vars: Record<string, number | string>
  ): void {
    if (node.type === "parallel" || node.type === "sequence") {
      if (!Array.isArray(node.children)) {
        errors.push({
          path: `${path}.children`,
          code: "MISSING_CHILDREN",
          message: `Composition '${node.type}' requires a 'children' array.`,
          received: node.children,
        });
      } else {
        node.children.forEach((child, index) => {
          this.validateNode(child, `${path}.children[${index}]`, errors, vars);
        });
      }
    }

    if (node.type === "delay" || node.type === "hold") {
      if (node.duration === undefined || (typeof node.duration === "number" && node.duration <= 0)) {
        errors.push({
          path: `${path}.duration`,
          code: "INVALID_DURATION",
          message: `'${node.type}' requires a positive 'duration' (> 0).`,
          received: node.duration,
        });
      }
    }

    if (node.type === "repeat") {
      if (node.count === undefined || (typeof node.count === "number" && node.count < 1)) {
        errors.push({
          path: `${path}.count`,
          code: "INVALID_REPEAT_COUNT",
          message: "Repeat node requires a 'count' >= 1.",
          received: node.count,
        });
      }
      if (!node.children || node.children.length === 0) {
        errors.push({
          path: `${path}.children`,
          code: "MISSING_REPEAT_CHILD",
          message: "Repeat node requires at least one child in 'children'.",
          received: node.children,
        });
      } else {
        this.validateNode(node.children[0], `${path}.children[0]`, errors, vars);
      }
    }

    if (node.type === "offset") {
      if (node.offsetTime === undefined) {
        errors.push({
          path: `${path}.offsetTime`,
          code: "MISSING_OFFSET_TIME",
          message: "Offset node requires an 'offsetTime' number.",
          received: node.offsetTime,
        });
      }
      if (!node.children || node.children.length === 0) {
        errors.push({
          path: `${path}.children`,
          code: "MISSING_OFFSET_CHILD",
          message: "Offset node requires at least one child in 'children'.",
          received: node.children,
        });
      } else {
        this.validateNode(node.children[0], `${path}.children[0]`, errors, vars);
      }
    }

    if (node.type === "stagger") {
      if (node.staggerDelay === undefined || (typeof node.staggerDelay === "number" && node.staggerDelay < 0)) {
        errors.push({
          path: `${path}.staggerDelay`,
          code: "INVALID_STAGGER_DELAY",
          message: "Stagger node requires a non-negative 'staggerDelay'.",
          received: node.staggerDelay,
        });
      }
      if (!Array.isArray(node.children) || node.children.length === 0) {
        errors.push({
          path: `${path}.children`,
          code: "MISSING_STAGGER_CHILDREN",
          message: "Stagger node requires an array of children to distribute.",
          received: node.children,
        });
      } else {
        node.children.forEach((child, index) => {
          this.validateNode(child, `${path}.children[${index}]`, errors, vars);
        });
      }
    }
  }
}
