export interface DeviceMockupConfig {
  deviceType: "laptop" | "mobile" | "browser";
  screenImageLayer: string;
  widthPx?: number;
  heightPx?: number;
  cornerRoundingPx?: number;
}

/**
 * Motor Especializado del Preset #11: SaaS & Tech Interface Showcase.
 * Genera maquetas 3D de dispositivos (Glassmorphism), cursores interactivos con ondas de clic y degradados Stripe.
 */
export class SaaSTechShowcasePreset {
  public static readonly PALETTE = {
    stripePurple: [0.545, 0.361, 0.965] as [number, number, number], // #8B5CF6
    stripeBlue: [0.231, 0.51, 0.965] as [number, number, number], // #3B82F6
    glassBg: [0.98, 0.98, 1.0] as [number, number, number], // #FAFAFF
    slateText: [0.12, 0.16, 0.24] as [number, number, number], // #1F293D
    pureWhite: [1.0, 1.0, 1.0] as [number, number, number], // #FFFFFF
  };

  /**
   * Genera el fragmento ExtendScript para un cursor animado con onda de clic expansiva (Click Ripple).
   */
  public static generateCursorClickSnippet(
    compVar: string,
    clickPoint: [number, number],
    clickTimeSec: number
  ): string {
    const pal = this.PALETTE;
    return [
      `// === SAAS INTERACTIVE CURSOR CLICK ===`,
      `var ripple = ${compVar}.layers.addShape();`,
      `ripple.name = "Cursor_Ripple_${clickTimeSec}";`,
      `ripple.inPoint = ${clickTimeSec};`,
      `ripple.transform.position.setValue([${clickPoint[0]}, ${clickPoint[1]}]);`,
      `var rGroup = ripple.property("Contents").addProperty("ADBE Vector Group");`,
      `var rCircle = rGroup.property("Contents").addProperty("ADBE Vector Shape - Ellipse");`,
      `rCircle.property("Size").setValue([100, 100]);`,
      `var rStroke = rGroup.property("Contents").addProperty("ADBE Vector Graphic - Stroke");`,
      `rStroke.property("Color").setValue([${pal.stripePurple[0]}, ${pal.stripePurple[1]}, ${pal.stripePurple[2]}]);`,
      `rStroke.property("Stroke Width").setValue(3);`,
      `// Animación de expansión y desvanecimiento`,
      `ripple.transform.scale.setValueAtTime(${clickTimeSec}, [0, 0]);`,
      `ripple.transform.scale.setValueAtTime(${clickTimeSec + 0.4}, [180, 180]);`,
      `ripple.transform.opacity.setValueAtTime(${clickTimeSec}, 100);`,
      `ripple.transform.opacity.setValueAtTime(${clickTimeSec + 0.4}, 0);`,
    ].join("\n");
  }

  /**
   * Genera el fragmento ExtendScript para una ventana de software con efecto Glassmorphism y sombra multicapa.
   */
  public static generateGlassWindowSnippet(
    compVar: string,
    windowTitle: string,
    position: [number, number],
    size: [number, number] = [1200, 720]
  ): string {
    const pal = this.PALETTE;
    return [
      `// === SAAS GLASSMORPHISM WINDOW FRAME ===`,
      `var win = ${compVar}.layers.addSolid([${pal.glassBg[0]}, ${pal.glassBg[1]}, ${pal.glassBg[2]}], "GlassWindow_${windowTitle}", ${size[0]}, ${size[1]}, 1.0);`,
      `win.transform.position.setValue([${position[0]}, ${position[1]}]);`,
      `// Sombra multicapa de elevación tecnológica`,
      `var ds = win.property("Effects").addProperty("ADBE Drop Shadow");`,
      `ds.property("Opacity").setValue(12);`,
      `ds.property("Distance").setValue(30);`,
      `ds.property("Softness").setValue(60);`,
    ].join("\n");
  }
}
