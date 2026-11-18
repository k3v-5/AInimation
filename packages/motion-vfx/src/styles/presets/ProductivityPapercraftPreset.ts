export interface FloatingCardConfig {
  id: string;
  title: string;
  body: string;
  backgroundColor?: [number, number, number];
  widthPx?: number;
  heightPx?: number;
}

/**
 * Motor Especializado del Preset #5: Productivity Papercraft (Ali Abdaal / Thomas Frank Style).
 * Genera tarjetas flotantes estilo Notion, texturas de papel punteado, física de resorte y resaltadores pastel.
 */
export class ProductivityPapercraftPreset {
  public static readonly PALETTE = {
    offWhitePaper: [0.98, 0.98, 0.98] as [number, number, number], // #FAFAFA
    pencilGraphite: [0.15, 0.15, 0.15] as [number, number, number], // #262626
    notionYellow: [0.996, 0.902, 0.541] as [number, number, number], // #FEE68A
    pastelMint: [0.655, 0.902, 0.761] as [number, number, number], // #A7E6C2
    pastelLavender: [0.773, 0.741, 0.957] as [number, number, number], // #C5B table
  };

  /**
   * Evalúa la escala en el tiempo t utilizando física de resorte inercial (Spring Physics).
   * S(t) = 100 * (1 - exp(-8t) * cos(20t))
   */
  public static evaluateSpringScale(t: number): number {
    if (t < 0) return 0;
    const scale = 100 * (1 - Math.exp(-8 * t) * Math.cos(20 * t));
    return Number(scale.toFixed(2));
  }

  /**
   * Genera el fragmento ExtendScript para una tarjeta flotante estilo Notion con sombra suave y resorte.
   */
  public static generateFloatingCardSnippet(
    compVar: string,
    config: FloatingCardConfig,
    position: [number, number],
    startTimeSec: number
  ): string {
    const pal = this.PALETTE;
    const bgCol = config.backgroundColor ?? pal.notionYellow;
    const w = config.widthPx ?? 720;
    const h = config.heightPx ?? 400;

    return [
      `// === NOTION FLOATING CARD (${config.id}) ===`,
      `var card = ${compVar}.layers.addSolid([${bgCol[0]}, ${bgCol[1]}, ${bgCol[2]}], "Card_${config.id}", ${w}, ${h}, 1.0);`,
      `card.transform.position.setValue([${position[0]}, ${position[1]}]);`,
      `card.inPoint = ${startTimeSec};`,
      `// Sombra difusa suave (Notion Soft Shadow)`,
      `var ds = card.property("Effects").addProperty("ADBE Drop Shadow");`,
      `ds.property("Opacity").setValue(15);`,
      `ds.property("Distance").setValue(20);`,
      `ds.property("Softness").setValue(45);`,
      `// Animación Spring Pop-In`,
      `card.transform.scale.setValueAtTime(${startTimeSec}, [0, 0]);`,
      `card.transform.scale.setValueAtTime(${startTimeSec + 0.12}, [118, 118]);`,
      `card.transform.scale.setValueAtTime(${startTimeSec + 0.25}, [96, 96]);`,
      `card.transform.scale.setValueAtTime(${startTimeSec + 0.38}, [100, 100]);`,
      `// Título dentro de la tarjeta`,
      `var titleLayer = ${compVar}.layers.addText("${config.title}");`,
      `titleLayer.parent = card;`,
      `titleLayer.transform.position.setValue([0, -${h * 0.25}]);`,
      `var tDoc = titleLayer.property("Source Text").value;`,
      `tDoc.fontSize = 42;`,
      `tDoc.font = "PlusJakartaSans-Bold";`,
      `tDoc.fillColor = [${pal.pencilGraphite[0]}, ${pal.pencilGraphite[1]}, ${pal.pencilGraphite[2]}];`,
      `titleLayer.property("Source Text").setValue(tDoc);`,
    ].join("\n");
  }
}
