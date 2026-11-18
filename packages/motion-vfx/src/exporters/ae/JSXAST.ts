/**
 * Árbol de Sintaxis Abstracta (AST) tipado para generación segura de scripts ExtendScript / After Effects JSX (Fase 17).
 */

export type JSXNodeType =
  | "Script"
  | "Comment"
  | "VarDeclaration"
  | "Assignment"
  | "FunctionCall"
  | "MethodCall"
  | "Block"
  | "LiteralString"
  | "LiteralNumber"
  | "LiteralBoolean"
  | "LiteralArray"
  | "LiteralObject"
  | "Identifier"
  | "RawStatement";

export interface JSXBaseNode {
  type: JSXNodeType;
}

export interface JSXLiteralString extends JSXBaseNode {
  type: "LiteralString";
  value: string;
}

export interface JSXLiteralNumber extends JSXBaseNode {
  type: "LiteralNumber";
  value: number;
}

export interface JSXLiteralBoolean extends JSXBaseNode {
  type: "LiteralBoolean";
  value: boolean;
}

export interface JSXLiteralArray extends JSXBaseNode {
  type: "LiteralArray";
  elements: JSXExpression[];
}

export interface JSXLiteralObject extends JSXBaseNode {
  type: "LiteralObject";
  properties: Array<{ key: string; value: JSXExpression }>;
}

export interface JSXIdentifier extends JSXBaseNode {
  type: "Identifier";
  name: string;
}

export type JSXExpression =
  | JSXLiteralString
  | JSXLiteralNumber
  | JSXLiteralBoolean
  | JSXLiteralArray
  | JSXLiteralObject
  | JSXIdentifier
  | JSXFunctionCall
  | JSXMethodCall;

export interface JSXVarDeclaration extends JSXBaseNode {
  type: "VarDeclaration";
  varName: string;
  initializer?: JSXExpression;
}

export interface JSXAssignment extends JSXBaseNode {
  type: "Assignment";
  target: string; // ej. "layer.position.setValue"
  value: JSXExpression;
}

export interface JSXFunctionCall extends JSXBaseNode {
  type: "FunctionCall";
  functionName: string;
  arguments: JSXExpression[];
}

export interface JSXMethodCall extends JSXBaseNode {
  type: "MethodCall";
  target: string;
  methodName: string;
  arguments: JSXExpression[];
}

export interface JSXComment extends JSXBaseNode {
  type: "Comment";
  text: string;
}

export interface JSXRawStatement extends JSXBaseNode {
  type: "RawStatement";
  statement: string;
}

export interface JSXBlock extends JSXBaseNode {
  type: "Block";
  title?: string;
  statements: JSXStatement[];
}

export type JSXStatement =
  | JSXVarDeclaration
  | JSXAssignment
  | JSXFunctionCall
  | JSXMethodCall
  | JSXComment
  | JSXRawStatement
  | JSXBlock;

export interface JSXScript extends JSXBaseNode {
  type: "Script";
  headerComment: string;
  statements: JSXStatement[];
}

/**
 * Constructores auxiliares para crear nodos AST de ExtendScript.
 */
export class JSXASTBuilder {
  public static str(val: string): JSXLiteralString {
    return { type: "LiteralString", value: String(val) };
  }

  public static num(val: number): JSXLiteralNumber {
    return { type: "LiteralNumber", value: Number(val) };
  }

  public static bool(val: boolean): JSXLiteralBoolean {
    return { type: "LiteralBoolean", value: Boolean(val) };
  }

  public static id(name: string): JSXIdentifier {
    return { type: "Identifier", name };
  }

  public static arr(elements: JSXExpression[]): JSXLiteralArray {
    return { type: "LiteralArray", elements };
  }

  public static varDecl(varName: string, initializer?: JSXExpression): JSXVarDeclaration {
    return { type: "VarDeclaration", varName, initializer };
  }

  public static call(target: string, methodName: string, args: JSXExpression[]): JSXMethodCall {
    return { type: "MethodCall", target, methodName, arguments: args };
  }

  public static assign(target: string, value: JSXExpression): JSXAssignment {
    return { type: "Assignment", target, value };
  }

  public static comment(text: string): JSXComment {
    return { type: "Comment", text };
  }

  public static block(title: string, statements: JSXStatement[]): JSXBlock {
    return { type: "Block", title, statements };
  }
}
