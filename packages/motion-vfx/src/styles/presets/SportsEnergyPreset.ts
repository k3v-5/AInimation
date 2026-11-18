export interface MillisecondTimerConfig {
  startMs: number;
  endMs: number;
  durationSec: number;
}

/**
 * Motor Especializado del Preset #13: Sports Energy & Fitness Adrenaline.
 * Genera cronómetros de milisegundos ardiendo, destellos anamórficos, Depth Sandwich freeze-frames y tipografía Teko ultra-pesada.
 */
export class SportsEnergyPreset {
  public static readonly PALETTE = {
    blazeOrange: [1.0, 0.34, 0.13] as [number, number, number], // #FF5722
    voltYellow: [0.8, 1.0, 0.0] as [number, number, number], // #CCFF00
    deepCharcoal: [0.08, 0.08, 0.08] as [number, number, number], // #141414
    pureWhite: [1.0, 1.0, 1.0] as [number, number, number], // #FFFFFF
  };

  /**
   * Formatea milisegundos a formato deportivo MM:SS.ms (ej. 01:24.85).
   */
  public static formatStopwatchTime(ms: number): string {
    const totalSec = Math.floor(ms / 1000);
    const minutes = Math.floor(totalSec / 60);
    const seconds = totalSec % 60;
    const millis = Math.floor((ms % 1000) / 10);
    const pad = (n: number) => n.toString().padStart(2, "0");
    return `${pad(minutes)}:${pad(seconds)}.${pad(millis)}`;
  }

  /**
   * Genera el fragmento ExtendScript para un cronómetro de milisegundos deportivo.
   */
  public static generateStopwatchSnippet(
    compVar: string,
    config: MillisecondTimerConfig,
    position: [number, number],
    startTimeSec: number
  ): string {
    const pal = this.PALETTE;
    return [
      `// === SPORTS MILLISECOND STOPWATCH ===`,
      `var timer = ${compVar}.layers.addText("00:00.00");`,
      `timer.name = "Stopwatch_Timer";`,
      `timer.transform.position.setValue([${position[0]}, ${position[1]}]);`,
      `timer.inPoint = ${startTimeSec};`,
      `var tProp = timer.property("Source Text");`,
      `var tDoc = tProp.value;`,
      `tDoc.fontSize = 88;`,
      `tDoc.font = "Teko-Bold";`,
      `tDoc.fillColor = [${pal.voltYellow[0]}, ${pal.voltYellow[1]}, ${pal.voltYellow[2]}];`,
      `tProp.setValue(tDoc);`,
      `// Expresión de cronómetro deportivo continuo`,
      `var expr = [`,
      `  "var t = Math.max(0, time - ${startTimeSec});",`,
      `  "var totalMs = Math.round(t * 1000);",`,
      `  "var min = Math.floor(totalMs / 60000);",`,
      `  "var sec = Math.floor((totalMs % 60000) / 1000);",`,
      `  "var ms = Math.floor((totalMs % 1000) / 10);",`,
      `  "function pad(n) { return (n < 10 ? '0' : '') + n; }",`,
      `  "pad(min) + ':' + pad(sec) + '.' + pad(ms);",`,
      `].join('\\n');`,
      `tProp.expression = expr;`,
    ].join("\n");
  }
}
