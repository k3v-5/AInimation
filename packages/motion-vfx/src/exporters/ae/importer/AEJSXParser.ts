export interface ParsedJSXComposition {
  name: string;
  width: number;
  height: number;
  fps: number;
  duration: number;
  textLayers: Array<{
    name: string;
    text: string;
    fontSize?: number;
    position?: { x: number; y: number };
  }>;
  solidLayers: Array<{
    name: string;
    width: number;
    height: number;
    color?: [number, number, number];
  }>;
}

export class AEJSXParser {
  /**
   * Parsea un script JSX de After Effects y extrae las especificaciones de composición y capas.
   */
  public static parse(jsxContent: string): ParsedJSXComposition {
    const compMatch = jsxContent.match(/app\.project\.items\.addComp\(\s*"([^"]+)",\s*(\d+),\s*(\d+),\s*([0-9.]+),\s*([0-9.]+),\s*([0-9.]+)\s*\)/);

    const compName = compMatch ? compMatch[1] : "Imported_Comp";
    const width = compMatch ? parseInt(compMatch[2], 10) : 1920;
    const height = compMatch ? parseInt(compMatch[3], 10) : 1080;
    const duration = compMatch ? parseFloat(compMatch[5]) : 10.0;
    const fps = compMatch ? parseFloat(compMatch[6]) : 30.0;

    const textLayers: ParsedJSXComposition["textLayers"] = [];
    const solidLayers: ParsedJSXComposition["solidLayers"] = [];

    // Parsear capas de texto
    const textMatches = jsxContent.matchAll(/addText\(\s*"([^"]*)"\s*\)[\s\S]*?\.name\s*=\s*"([^"]*)"/g);
    for (const match of textMatches) {
      textLayers.push({
        text: match[1],
        name: match[2],
      });
    }

    // Parsear capas de sólidos
    const solidMatches = jsxContent.matchAll(/addSolid\(\s*\[([0-9.,\s]+)\],\s*"([^"]+)",\s*(\d+),\s*(\d+)/g);
    for (const match of solidMatches) {
      const colorParts = match[1].split(",").map((s) => parseFloat(s.trim()));
      solidLayers.push({
        name: match[2],
        width: parseInt(match[3], 10),
        height: parseInt(match[4], 10),
        color: colorParts.length >= 3 ? [colorParts[0], colorParts[1], colorParts[2]] : [0, 0, 0],
      });
    }

    return {
      name: compName,
      width,
      height,
      fps,
      duration,
      textLayers,
      solidLayers,
    };
  }
}
