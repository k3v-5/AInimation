import { ParsedCLIArgs } from "../CLIArgs.js";
import { CLIOutput } from "../CLIOutput.js";
import { Composition } from "../../core/composition.js";
import { SocialDeliveryPackager } from "../../delivery/packaging/SocialDeliveryPackager.js";
import { AspectRatio } from "../../delivery/core/AspectRatio.js";

export class ExportSocialCommand {
  public static async execute(args: ParsedCLIArgs): Promise<number> {
    if (!args.inputFile) {
      CLIOutput.error("Missing input project file for 'export-social' command.");
      return 1;
    }

    const outDir = args.output || "./dist/social_delivery";
    const ratios = (args.ratios as AspectRatio[]) || ["9:16", "16:9", "1:1"];

    CLIOutput.info(`Packaging multi-aspect social delivery to '${outDir}'...`);

    const comp = new Composition({
      id: "cli_social_comp",
      name: "Social Delivery",
      width: 1080,
      height: 1920,
      fps: 30,
      duration: 10.0,
    });

    const { pkg, manifest } = SocialDeliveryPackager.package(comp, "proj_cli", "rev_cli", {
      targetAspectRatios: ratios,
    });

    CLIOutput.success(`Created package '${pkg.packageId}' with ${Object.keys(pkg.variants).length} variants.`);
    CLIOutput.success(`Platform manifest hash: ${manifest.manifestHash}`);
    return 0;
  }
}
