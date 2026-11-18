export interface ParallaxPhotoConfig {
  id: string;
  subjectImageLayer: string;
  backgroundImageLayer: string;
  targetScalePct?: number; // default: 108%
  blurRadiusPx?: number; // default: 28px
  durationSec?: number; // default: 5.0s
}

export interface StatCounterConfig {
  prefix?: string;
  targetValue: number;
  suffix?: string;
  durationSec: number;
}

/**
 * Motor Especializado del Preset #2: Dark Noir Business Empire (Estilo MagnatesMedia / Neo).
 * Genera composiciones cinematográficas oscuras de negocios, efecto 3D Parallax en fotos de magnates,
 * destellos anamórficos sobre títulos dorados y contadores numéricos de riqueza.
 */
export class DarkNoirBusinessPreset {
  public static readonly PALETTE = {
    carbonBlack: [0.051, 0.051, 0.051] as [number, number, number], // #0D0D0D
    metallicGold: [0.831, 0.686, 0.216] as [number, number, number], // #D4AF37
    crimsonBlood: [0.62, 0.106, 0.106] as [number, number, number], // #9E1B1B
    smokeSilver: [0.753, 0.753, 0.753] as [number, number, number], // #C0C0C0
    pureWhite: [0.98, 0.98, 0.98] as [number, number, number], // #FAFAFA
  };

  /**
   * Formatea un valor numérico a moneda o formato de negocios (ej. $142,500,000,000).
   */
  public static formatCurrency(value: number, prefix = "$", suffix = ""): string {
    const formatted = Math.round(value).toLocaleString("en-US");
    return `${prefix}${formatted}${suffix}`;
  }

  /**
   * Evalúa el valor de un contador de riqueza en el tiempo t con curva de desaceleración Bézier (Ease-Out).
   */
  public static evaluateCounterProgress(t: number, totalDuration: number, targetValue: number): number {
    if (t <= 0) return 0;
    if (t >= totalDuration) return targetValue;
    const progress = t / totalDuration;
    // Curva Ease-Out cúbica: 1 - (1 - p)^3
    const eased = 1 - Math.pow(1 - progress, 3);
    return Math.round(eased * targetValue);
  }

  /**
   * Genera el fragmento ExtendScript para el efecto 3D Photo Parallax Cutout (Sujeto al frente y fondo desenfocado).
   */
  public static generateParallaxPhotoSnippet(
    compVar: string,
    config: ParallaxPhotoConfig
  ): string {
    const dur = config.durationSec ?? 5.0;
    const maxScale = config.targetScalePct ?? 108;
    const blur = config.blurRadiusPx ?? 28;

    return [
      `// === 3D PHOTO PARALLAX CUTOUT (${config.id}) ===`,
      `// 1. Fondo Desenfocado y Oscurecido`,
      `var bgLayer = ${compVar}.layer("${config.backgroundImageLayer}");`,
      `if (bgLayer) {`,
      `  bgLayer.threeDLayer = true;`,
      `  var fastBlur = bgLayer.property("Effects").addProperty("ADBE Fast Blur");`,
      `  fastBlur.property("Blurriness").setValue(${blur});`,
      `  var tint = bgLayer.property("Effects").addProperty("ADBE Tint");`,
      `  tint.property("Amount to Tint").setValue(45);`,
      `  bgLayer.transform.scale.setValueAtTime(0, [100, 100, 100]);`,
      `  bgLayer.transform.scale.setValueAtTime(${dur}, [104, 104, 100]);`,
      `}`,
      `// 2. Sujeto en Primer Plano (Slow Push-In hacia la cámara)`,
      `var fgLayer = ${compVar}.layer("${config.subjectImageLayer}");`,
      `if (fgLayer) {`,
      `  fgLayer.threeDLayer = true;`,
      `  fgLayer.transform.position.setValueAtTime(0, [fgLayer.transform.position.value[0], fgLayer.transform.position.value[1], -150]);`,
      `  fgLayer.transform.position.setValueAtTime(${dur}, [fgLayer.transform.position.value[0], fgLayer.transform.position.value[1], -50]);`,
      `  fgLayer.transform.scale.setValueAtTime(0, [100, 100, 100]);`,
      `  fgLayer.transform.scale.setValueAtTime(${dur}, [${maxScale}, ${maxScale}, 100]);`,
      `  // Drop shadow sobre el fondo`,
      `  var ds = fgLayer.property("Effects").addProperty("ADBE Drop Shadow");`,
      `  ds.property("Opacity").setValue(50);`,
      `  ds.property("Distance").setValue(35);`,
      `  ds.property("Softness").setValue(45);`,
      `}`,
    ].join("\n");
  }

  /**
   * Genera el fragmento ExtendScript para un título dorado con destello anamórfico (Light Sweep).
   */
  public static generateGoldTitleSnippet(
    compVar: string,
    titleText: string,
    position: [number, number],
    startTimeSec: number,
    durationSec = 3.0
  ): string {
    const pal = this.PALETTE;
    return [
      `// === DARK NOIR GOLD METALLIC TITLE ===`,
      `var txt = ${compVar}.layers.addText("${titleText}");`,
      `txt.name = "Gold_Title_${titleText.slice(0, 10)}";`,
      `txt.transform.position.setValue([${position[0]}, ${position[1]}]);`,
      `var tProp = txt.property("Source Text");`,
      `var tDoc = tProp.value;`,
      `tDoc.fontSize = 72;`,
      `tDoc.font = "Cinzel-Bold";`,
      `tDoc.fillColor = [${pal.metallicGold[0]}, ${pal.metallicGold[1]}, ${pal.metallicGold[2]}];`,
      `tDoc.tracking = 15;`,
      `tProp.setValue(tDoc);`,
      `// Destello de Luz Anamórfica`,
      `var sweep = txt.property("Effects").addProperty("CC Light Sweep");`,
      `if (sweep) {`,
      `  sweep.property("Center").setValueAtTime(${startTimeSec}, [${position[0]} - 400, ${position[1]}]);`,
      `  sweep.property("Center").setValueAtTime(${startTimeSec + durationSec}, [${position[0]} + 400, ${position[1]}]);`,
      `  sweep.property("Edge Intensity").setValue(40);`,
      `  sweep.property("Light Color").setValue([1.0, 0.95, 0.8]);`,
      `}`,
    ].join("\n");
  }

  /**
   * Genera la expresión ExtendScript para animar un contador de riqueza dinámico.
   */
  public static generateStatTickerSnippet(
    compVar: string,
    layerName: string,
    config: StatCounterConfig,
    position: [number, number],
    startTimeSec: number
  ): string {
    const pal = this.PALETTE;
    const pfx = config.prefix ?? "$";
    const sfx = config.suffix ?? "";
    return [
      `// === WEALTH STAT TICKER (${layerName}) ===`,
      `var ticker = ${compVar}.layers.addText("${pfx}0${sfx}");`,
      `ticker.name = "${layerName}";`,
      `ticker.transform.position.setValue([${position[0]}, ${position[1]}]);`,
      `var tProp = ticker.property("Source Text");`,
      `var tDoc = tProp.value;`,
      `tDoc.fontSize = 64;`,
      `tDoc.font = "Cinzel-Bold";`,
      `tDoc.fillColor = [${pal.pureWhite[0]}, ${pal.pureWhite[1]}, ${pal.pureWhite[2]}];`,
      `tDoc.tracking = 10;`,
      `tProp.setValue(tDoc);`,
      `// Expresión de conteo Ease-Out`,
      `var expr = [`,
      `  "var t = time - ${startTimeSec};",`,
      `  "var dur = ${config.durationSec};",`,
      `  "var target = ${config.targetValue};",`,
      `  "if (t <= 0) { '${pfx}0${sfx}'; }",`,
      `  "else if (t >= dur) { '${pfx}' + target.toLocaleString('en-US') + '${sfx}'; }",`,
      `  "else {",`,
      `  "  var prog = t / dur;",`,
      `  "  var eased = 1 - Math.pow(1 - prog, 3);",`,
      `  "  var cur = Math.round(eased * target);",`,
      `  "  '${pfx}' + cur.toLocaleString('en-US') + '${sfx}';",`,
      `  "}"`,
      `].join('\\n');`,
      `tProp.expression = expr;`,
    ].join("\n");
  }
}
