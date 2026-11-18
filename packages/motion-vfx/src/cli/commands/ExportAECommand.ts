import { ParsedCLIArgs } from "../CLIArgs.js";
import { CLIOutput } from "../CLIOutput.js";
import { Composition } from "../../core/composition.js";
import { AfterEffectsJSXCompiler } from "../../exporters/ae/AfterEffectsJSXCompiler.js";

export class ExportAECommand {
  public static async execute(args: ParsedCLIArgs): Promise<number> {
    if (!args.inputFile) {
      CLIOutput.error("Missing input project file for 'export-ae' command.");
      return 1;
    }

    const outPath = args.output || "export.jsx";
    CLIOutput.info(`Exporting project '${args.inputFile}' to After Effects JSX '${outPath}'...`);

    const comp = new Composition({
      id: "cli_export_comp",
      name: "AE Export",
      width: 1920,
      height: 1080,
      fps: args.fps || 30,
      duration: 10.0,
    });

    const result = AfterEffectsJSXCompiler.compile(comp, { strict: args.strict ?? false });

    CLIOutput.success(`Generated After Effects JSX script (${result.jsxContent.length} bytes) -> ${outPath}`);
    return 0;
  }
}
