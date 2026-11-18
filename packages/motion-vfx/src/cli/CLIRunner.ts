import { CLIArgs, ParsedCLIArgs } from "./CLIArgs.js";
import { CLIOutput } from "./CLIOutput.js";
import { RenderCommand } from "./commands/RenderCommand.js";
import { ExportAECommand } from "./commands/ExportAECommand.js";
import { ExportSocialCommand } from "./commands/ExportSocialCommand.js";
import { QACommand } from "./commands/QACommand.js";
import { ValidateCommand } from "./commands/ValidateCommand.js";

export class CLIRunner {
  public static readonly VERSION = "3.0.0-gold-master";

  public static async run(argv: string[]): Promise<number> {
    const args = CLIArgs.parse(argv);

    if (args.version || args.command === "version") {
      console.log(`motion-engine CLI v${this.VERSION} (Milestone 30 Gold Master)`);
      return 0;
    }

    if (args.help || args.command === "help") {
      this.printHelp();
      return 0;
    }

    CLIOutput.header(`Motion Graphics Engine & After Effects MCP CLI v${this.VERSION}`);

    switch (args.command) {
      case "render":
        return RenderCommand.execute(args);
      case "export-ae":
        return ExportAECommand.execute(args);
      case "export-social":
        return ExportSocialCommand.execute(args);
      case "qa":
        return QACommand.execute(args);
      case "validate":
        return ValidateCommand.execute(args);
      default:
        CLIOutput.error(`Unknown command: '${args.command}'. Run 'motion-engine --help' for usage.`);
        return 1;
    }
  }

  private static printHelp(): void {
    console.log(`
Motion Graphics Engine & After Effects MCP CLI v${this.VERSION}

Usage:
  motion-engine <command> [input-file] [options]

Commands:
  render <file>          Render project to video or frame sequence (-o <path>, --fps <fps>)
  export-ae <file>       Export project to After Effects ExtendScript JSX (-o <path>, --strict)
  export-social <file>   Export multi-aspect social delivery package (-o <dir>, --ratios <ratios>)
  qa <file>              Run 7-family deterministic QA battery (--threshold <score>)
  validate <file>        Validate project schema and integrity
  version                Print version info
  help                   Print this help message

Options:
  -o, --output <path>    Output file or directory path
  --fps <number>         Frame rate (default: 30)
  --strict               Enforce strict export capabilities
  --ratios <list>        Comma-separated aspect ratios (e.g. 9:16,16:9,1:1)
  --threshold <number>   QA passing score threshold [0..1] (default: 0.85)
  --workers <number>     Number of distributed worker nodes
  -v, --version          Show version
  -h, --help             Show help
`);
  }
}
