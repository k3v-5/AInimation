export interface SkyMaskTransitionConfig {
  incomingVideoLayer: string;
  outgoingVideoLayer: string;
  featherPx?: number; // default: 120px
  durationSec?: number; // default: 1.2s
}

/**
 * Motor Especializado del Preset #10: Cinematic Flow Vlogging (Sam Kolder Style).
 * Genera transiciones orgánicas de máscara de cielo (Sky Mask), speed ramping fluido y gradación Hollywood Teal & Orange.
 */
export class CinematicFlowVlogPreset {
  public static readonly PALETTE = {
    tealShadow: [0.05, 0.35, 0.4] as [number, number, number], // #0D5966
    warmGoldHighlight: [0.98, 0.75, 0.4] as [number, number, number], // #FAC066
    deepNavy: [0.04, 0.08, 0.15] as [number, number, number], // #0A1426
    pureWhite: [1.0, 1.0, 1.0] as [number, number, number], // #FFFFFF
  };

  /**
   * Genera el fragmento ExtendScript para una transición de máscara de cielo (Sky Replacement / Wipe).
   */
  public static generateSkyMaskTransitionSnippet(
    compVar: string,
    config: SkyMaskTransitionConfig,
    transitionTimeSec: number
  ): string {
    const dur = config.durationSec ?? 1.2;
    const feather = config.featherPx ?? 120;

    return [
      `// === SEAMLESS SKY MASK TRANSITION ===`,
      `var inLayer = ${compVar}.layer("${config.incomingVideoLayer}");`,
      `if (inLayer) {`,
      `  inLayer.startTime = ${transitionTimeSec};`,
      `  var mask = inLayer.property("Masks").addProperty("ADBE Mask Atom");`,
      `  mask.property("Mask Feather").setValue([${feather}, ${feather}]);`,
      `  // Animación de barrido vertical del cielo hacia abajo`,
      `  mask.property("Mask Opacity").setValueAtTime(${transitionTimeSec}, 0);`,
      `  mask.property("Mask Opacity").setValueAtTime(${transitionTimeSec + dur}, 100);`,
      `}`,
    ].join("\n");
  }

  /**
   * Genera el fragmento ExtendScript para un título 3D anclado en el horizonte del paisaje.
   */
  public static generateHorizonTitleSnippet(
    compVar: string,
    titleText: string,
    position: [number, number, number] = [960, 450, 400]
  ): string {
    const pal = this.PALETTE;
    return [
      `// === CINEMATIC HORIZON 3D TITLE ===`,
      `var txt = ${compVar}.layers.addText("${titleText}");`,
      `txt.name = "Horizon_Title";`,
      `txt.threeDLayer = true;`,
      `txt.transform.position.setValue([${position[0]}, ${position[1]}, ${position[2]}]);`,
      `var tProp = txt.property("Source Text");`,
      `var tDoc = tProp.value;`,
      `tDoc.fontSize = 90;`,
      `tDoc.font = "Futura-Bold";`,
      `tDoc.fillColor = [${pal.pureWhite[0]}, ${pal.pureWhite[1]}, ${pal.pureWhite[2]}];`,
      `tDoc.tracking = 15;`,
      `tProp.setValue(tDoc);`,
    ].join("\n");
  }
}
