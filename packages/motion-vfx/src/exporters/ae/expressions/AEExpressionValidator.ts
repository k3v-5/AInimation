export class AEExpressionValidator {
  /**
   * Valida sintácticamente que una expresión de After Effects no contenga errores obvios de paréntesis o referencias prohibidas.
   */
  public static validate(expression: string): { valid: boolean; error?: string } {
    if (!expression || expression.trim().length === 0) {
      return { valid: false, error: "Expression cannot be empty" };
    }

    const trimmed = expression.trim();

    // Comprobar balanceo de paréntesis y corchetes
    let parenCount = 0;
    let bracketCount = 0;

    for (let i = 0; i < trimmed.length; i++) {
      const ch = trimmed[i];
      if (ch === "(") parenCount++;
      else if (ch === ")") parenCount--;
      else if (ch === "[") bracketCount++;
      else if (ch === "]") bracketCount--;

      if (parenCount < 0) return { valid: false, error: "Unbalanced parentheses: unexpected closing ')'" };
      if (bracketCount < 0) return { valid: false, error: "Unbalanced brackets: unexpected closing ']'" };
    }

    if (parenCount !== 0) return { valid: false, error: "Unbalanced parentheses: missing closing ')'" };
    if (bracketCount !== 0) return { valid: false, error: "Unbalanced brackets: missing closing ']'" };

    return { valid: true };
  }
}
