import {
  JSXExpression,
  JSXScript,
  JSXStatement,
} from "./JSXAST.js";

/**
 * Serializador determinista de AST a código fuente ExtendScript / After Effects JSX (Fase 17).
 */
export class JSXSerializer {
  /**
   * Serializa un script AST completo a texto ejecutable JSX.
   */
  public static serialize(script: JSXScript): string {
    const lines: string[] = [];

    // 1. Header determinista
    lines.push(`/**`);
    lines.push(` * ${script.headerComment}`);
    lines.push(` * Generated deterministically by Motion Graphics Engine v1.7.0`);
    lines.push(` */`);
    lines.push(``);
    lines.push(`(function() {`);
    lines.push(`  app.beginUndoGroup("Import Motion Engine Project");`);
    lines.push(`  try {`);

    // 2. Serializar declaraciones con indentación controlada
    for (const stmt of script.statements) {
      lines.push(this.serializeStatement(stmt, 4));
    }

    // 3. Footer y Undo Group
    lines.push(`  } catch (err) {`);
    lines.push(`    alert("Error executing Motion Engine script: " + err.toString());`);
    lines.push(`  } finally {`);
    lines.push(`    app.endUndoGroup();`);
    lines.push(`  }`);
    lines.push(`})();`);
    lines.push(``);

    return lines.join("\n");
  }

  /**
   * Serializa una sentencia individual con nivel de sangría.
   */
  public static serializeStatement(stmt: JSXStatement, indentSpaces = 0): string {
    const pad = " ".repeat(indentSpaces);

    switch (stmt.type) {
      case "Comment":
        return `${pad}// ${stmt.text}`;

      case "VarDeclaration":
        if (stmt.initializer) {
          return `${pad}var ${stmt.varName} = ${this.serializeExpression(stmt.initializer)};`;
        }
        return `${pad}var ${stmt.varName};`;

      case "Assignment":
        return `${pad}${stmt.target} = ${this.serializeExpression(stmt.value)};`;

      case "MethodCall":
        const argsStr = stmt.arguments.map((a) => this.serializeExpression(a)).join(", ");
        return `${pad}${stmt.target}.${stmt.methodName}(${argsStr});`;

      case "FunctionCall":
        const fnArgsStr = stmt.arguments.map((a) => this.serializeExpression(a)).join(", ");
        return `${pad}${stmt.functionName}(${fnArgsStr});`;

      case "RawStatement":
        return `${pad}${stmt.statement};`;

      case "Block":
        const blockLines: string[] = [];
        if (stmt.title) {
          blockLines.push(`${pad}// === ${stmt.title} ===`);
        }
        for (const child of stmt.statements) {
          blockLines.push(this.serializeStatement(child, indentSpaces));
        }
        return blockLines.join("\n");

      default:
        return `${pad}// (unknown statement)`;
    }
  }

  /**
   * Serializa una expresión individual escapando caracteres literales y estructuras.
   */
  public static serializeExpression(expr: JSXExpression): string {
    switch (expr.type) {
      case "LiteralString":
        return this.escapeString(expr.value);

      case "LiteralNumber":
        if (!isFinite(expr.value)) {
          return "0";
        }
        return String(Number(expr.value.toFixed(4)));

      case "LiteralBoolean":
        return expr.value ? "true" : "false";

      case "LiteralArray":
        const elements = expr.elements.map((e) => this.serializeExpression(e)).join(", ");
        return `[${elements}]`;

      case "LiteralObject":
        const props = expr.properties
          .map((p) => `${JSON.stringify(p.key)}: ${this.serializeExpression(p.value)}`)
          .join(", ");
        return `{ ${props} }`;

      case "Identifier":
        return expr.name;

      case "MethodCall":
        const mArgs = expr.arguments.map((a) => this.serializeExpression(a)).join(", ");
        return `${expr.target}.${expr.methodName}(${mArgs})`;

      case "FunctionCall":
        const fArgs = expr.arguments.map((a) => this.serializeExpression(a)).join(", ");
        return `${expr.functionName}(${fArgs})`;

      default:
        return "null";
    }
  }

  /**
   * Escapa cadenas de texto estrictamente para prevenir inyección de código ExtendScript y preservar Unicode.
   */
  public static escapeString(str: string): string {
    if (typeof str !== "string") {
      return `""`;
    }

    let escaped = "";
    for (let i = 0; i < str.length; i++) {
      const char = str[i];
      const code = char.charCodeAt(0);

      switch (char) {
        case "\\":
          escaped += "\\\\";
          break;
        case '"':
          escaped += '\\"';
          break;
        case "\n":
          escaped += "\\n";
          break;
        case "\r":
          escaped += "\\r";
          break;
        case "\t":
          escaped += "\\t";
          break;
        default:
          if (code < 32 || code > 126) {
            // Convertir caracteres no imprimibles o Unicode a \uXXXX
            escaped += "\\u" + code.toString(16).padStart(4, "0");
          } else {
            escaped += char;
          }
      }
    }

    return `"${escaped}"`;
  }
}
