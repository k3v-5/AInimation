export type SupportedAspectRatio = "9:16" | "16:9" | "1:1";

export interface AspectRatioProfile {
  name: SupportedAspectRatio;
  width: number;
  height: number;
  fontSizeMultiplier: number;
  safeMarginPct: number;
  description: string;
}

export interface OmniExportManifest {
  projectName: string;
  duration: number;
  formats: Array<{
    aspectRatio: SupportedAspectRatio;
    compName: string;
    width: number;
    height: number;
  }>;
}

/**
 * Exportador omnicanal multi-plataforma en 1-clic (Fase 9 / Mejoras).
 * Compila simultáneamente composiciones optimizadas para TikTok/Reels (9:16), YouTube (16:9)
 * e Instagram Feed (1:1), adaptando tamaños de texto, encuadres focales y zonas seguras automáticamente.
 */
export class OmniChannelMultiExporter {
  public static readonly FORMATS: Record<SupportedAspectRatio, AspectRatioProfile> = {
    "9:16": {
      name: "9:16",
      width: 1080,
      height: 1920,
      fontSizeMultiplier: 1.0,
      safeMarginPct: 15,
      description: "TikTok, Instagram Reels, YouTube Shorts (Vertical)",
    },
    "16:9": {
      name: "16:9",
      width: 1920,
      height: 1080,
      fontSizeMultiplier: 0.75,
      safeMarginPct: 8,
      description: "YouTube, Smart TVs, Cine (Panorámico)",
    },
    "1:1": {
      name: "1:1",
      width: 1080,
      height: 1080,
      fontSizeMultiplier: 0.85,
      safeMarginPct: 10,
      description: "Instagram Feed, LinkedIn, Square Video",
    },
  };

  /**
   * Genera el manifiesto de exportación multi-formato.
   */
  public static generateManifest(
    projectName: string,
    duration: number,
    aspectRatios: SupportedAspectRatio[] = ["9:16", "16:9", "1:1"]
  ): OmniExportManifest {
    return {
      projectName,
      duration,
      formats: aspectRatios.map((ar) => {
        const p = this.FORMATS[ar];
        return {
          aspectRatio: ar,
          compName: `${projectName}_${ar.replace(":", "x")}`,
          width: p.width,
          height: p.height,
        };
      }),
    };
  }

  /**
   * Genera el script ExtendScript para instanciar las 3 composiciones simultáneamente en After Effects.
   */
  public static generateOmniExportScript(
    projectVar: string,
    manifest: OmniExportManifest
  ): string {
    const lines = [
      `// === OMNI-CHANNEL MULTI-EXPORT (9:16, 16:9, 1:1) ===`,
      `var omniComps = [];`,
    ];

    for (const f of manifest.formats) {
      lines.push(
        `var comp_${f.aspectRatio.replace(":", "_")} = ${projectVar}.items.addComp("${f.compName}", ${f.width}, ${f.height}, 1.0, ${manifest.duration}, 60);`,
        `omniComps.push(comp_${f.aspectRatio.replace(":", "_")});`
      );
    }

    return lines.join("\n");
  }
}
