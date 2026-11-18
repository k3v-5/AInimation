import { Composition } from "../../../core/composition.js";
import { TextElement } from "../../../elements/TextElement.js";
import { AEJSXParser, ParsedJSXComposition } from "./AEJSXParser.js";
import { ProjectSerializer } from "../../../persistence/ProjectSerializer.js";

export interface ImportedTemplateResult {
  composition: Composition;
  parsedMetadata: ParsedJSXComposition;
  canonicalHash: string;
}

export class AETemplateImporter {
  /**
   * Importa un script JSX de After Effects y reconstruye la instancia de Composition canónica.
   */
  public static importTemplate(jsxContent: string, compIdOverride?: string): ImportedTemplateResult {
    const parsed = AEJSXParser.parse(jsxContent);
    const compId = compIdOverride ?? `imported_${parsed.name.replace(/[^a-zA-Z0-9_]/g, "_")}`;

    const comp = new Composition({
      id: compId,
      name: parsed.name,
      width: parsed.width,
      height: parsed.height,
      fps: parsed.fps,
      duration: parsed.duration,
    });

    // Agregar capas de texto
    for (let i = 0; i < parsed.textLayers.length; i++) {
      const t = parsed.textLayers[i];
      const textElem = new TextElement({
        id: `text_layer_${i + 1}`,
        name: t.name || `Text ${i + 1}`,
        text: t.text,
        style: {
          fontSize: t.fontSize ?? 48,
          fontFamily: "Inter-Bold",
        },
      });
      comp.addElement(textElem);
    }

    const canonicalHash = ProjectSerializer.hashCanonical({
      id: comp.id,
      name: comp.name,
      width: comp.width,
      height: comp.height,
      fps: comp.fps,
      duration: comp.duration,
      elementsCount: comp.getElements().length,
    });

    return {
      composition: comp,
      parsedMetadata: parsed,
      canonicalHash,
    };
  }
}
