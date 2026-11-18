/**
 * Constructor de Scripts ExtendScript JSX para Adobe After Effects (Milestone 7).
 * Provee utilidades seguras para estructurar llamadas ExtendScript,
 * envolver en Undo Groups y configurar propiedades de capas y composición.
 */
export class VlogJsxBuilder {
  private lines: string[] = [];
  private indentLevel = 0;

  public addLine(line = ""): this {
    if (line.trim().length === 0) {
      this.lines.push("");
    } else {
      const indent = "  ".repeat(this.indentLevel);
      this.lines.push(indent + line);
    }
    return this;
  }

  public indent(): this {
    this.indentLevel++;
    return this;
  }

  public dedent(): this {
    this.indentLevel = Math.max(0, this.indentLevel - 1);
    return this;
  }

  public addComment(comment: string): this {
    return this.addLine(`// ${comment}`);
  }

  public addHeader(title: string): this {
    this.addLine();
    this.addLine("// " + "=".repeat(68));
    this.addLine(`// ${title}`);
    this.addLine("// " + "=".repeat(68));
    return this;
  }

  /**
   * Sanitiza un string para ser incrustado seguramente dentro de comillas simples en JSX.
   */
  public static escapeString(str: string): string {
    if (!str) return "";
    return str
      .replace(/\\/g, "\\\\")
      .replace(/'/g, "\\'")
      .replace(/\r/g, "")
      .replace(/\n/g, "\\n");
  }

  /**
   * Convierte un color Hexadecimal "#RRGGBB" a un arreglo normalizado [r, g, b] en [0, 1].
   */
  public static hexToRgbNormalized(hex: string): [number, number, number] {
    const clean = hex.replace("#", "").trim();
    if (clean.length !== 6) {
      return [1.0, 1.0, 1.0]; // fallback blanco
    }
    const r = parseInt(clean.substring(0, 2), 16) / 255;
    const g = parseInt(clean.substring(2, 4), 16) / 255;
    const b = parseInt(clean.substring(4, 6), 16) / 255;
    return [Number(r.toFixed(3)), Number(g.toFixed(3)), Number(b.toFixed(3))];
  }

  public toString(): string {
    return this.lines.join("\n");
  }
}
