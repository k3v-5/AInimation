export interface ParsedCLIArgs {
  command: string;
  inputFile?: string;
  output?: string;
  fps?: number;
  strict?: boolean;
  ratios?: string[];
  threshold?: number;
  workers?: number;
  help?: boolean;
  version?: boolean;
  flags: Record<string, string | boolean | number>;
}

export class CLIArgs {
  /**
   * Parsea los argumentos de línea de comandos de forma determinista.
   */
  public static parse(argv: string[]): ParsedCLIArgs {
    const raw = argv.slice(2); // omitir node y script
    if (raw.length === 0) {
      return { command: "help", flags: {} };
    }

    const command = raw[0].startsWith("-") ? "help" : raw[0];
    const startIndex = raw[0].startsWith("-") ? 0 : 1;

    let inputFile: string | undefined;
    let output: string | undefined;
    let fps: number | undefined;
    let strict: boolean | undefined;
    let ratios: string[] | undefined;
    let threshold: number | undefined;
    let workers: number | undefined;
    let help = false;
    let version = false;

    const flags: Record<string, string | boolean | number> = {};

    for (let i = startIndex; i < raw.length; i++) {
      const arg = raw[i];

      if (arg === "-h" || arg === "--help") {
        help = true;
      } else if (arg === "-v" || arg === "--version") {
        version = true;
      } else if (arg === "-o" || arg === "--output" || arg === "--outdir") {
        output = raw[++i];
      } else if (arg === "--fps") {
        fps = parseFloat(raw[++i]);
      } else if (arg === "--strict") {
        strict = true;
      } else if (arg === "--ratios") {
        ratios = raw[++i].split(",").map((r) => r.trim());
      } else if (arg === "--threshold") {
        threshold = parseFloat(raw[++i]);
      } else if (arg === "--workers") {
        workers = parseInt(raw[++i], 10);
      } else if (arg.startsWith("--")) {
        const key = arg.slice(2);
        if (i + 1 < raw.length && !raw[i + 1].startsWith("-")) {
          flags[key] = raw[++i];
        } else {
          flags[key] = true;
        }
      } else if (!inputFile && !arg.startsWith("-")) {
        inputFile = arg;
      }
    }

    return {
      command,
      inputFile,
      output,
      fps,
      strict,
      ratios,
      threshold,
      workers,
      help,
      version,
      flags,
    };
  }
}
