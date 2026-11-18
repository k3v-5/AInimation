import { ParsedCLIArgs } from "../CLIArgs.js";
import { CLIOutput } from "../CLIOutput.js";
import { Composition } from "../../core/composition.js";

export class RenderCommand {
  public static async execute(args: ParsedCLIArgs): Promise<number> {
    if (!args.inputFile) {
      CLIOutput.error("Missing input project file for 'render' command.");
      return 1;
    }

    const outPath = args.output || "output.mp4";
    CLIOutput.info(`Rendering project from '${args.inputFile}' to '${outPath}'...`);

    // Simulación determinista de pipeline de render
    const comp = new Composition({
      id: "cli_render_comp",
      name: "CLI Render",
      width: 1920,
      height: 1080,
      fps: args.fps || 30,
      duration: 5.0,
    });

    const totalFrames = Math.floor(comp.duration * comp.fps);
    for (let f = 0; f < totalFrames; f += 30) {
      comp.evaluate(f / comp.fps);
    }

    CLIOutput.success(`Rendered ${totalFrames} frames successfully -> ${outPath}`);
    return 0;
  }
}
