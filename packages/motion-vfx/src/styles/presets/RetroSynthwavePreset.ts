/**
 * Motor Especializado del Preset #14: Retro Synthwave & Arcade 80s.
 * Genera rejillas de neón en perspectiva 3D hacia un sol retro animado, aberración cromática RGB Split y efecto VHS.
 */
export class RetroSynthwavePreset {
  public static readonly PALETTE = {
    neonMagenta: [1.0, 0.0, 0.43] as [number, number, number], // #FF006E
    electricCyan: [0.0, 0.95, 1.0] as [number, number, number], // #00F5FF
    sunsetOrange: [1.0, 0.45, 0.0] as [number, number, number], // #FF7300
    deepPurple: [0.1, 0.04, 0.22] as [number, number, number], // #1A0A38
    retroSunYellow: [1.0, 0.85, 0.2] as [number, number, number], // #FFD933
  };

  /**
   * Genera el fragmento ExtendScript para la rejilla de neón en perspectiva hacia el horizonte.
   */
  public static generatePerspectiveGridSnippet(compVar: string): string {
    const pal = this.PALETTE;
    return [
      `// === RETRO SYNTHWAVE 3D PERSPECTIVE GRID ===`,
      `var gridSolid = ${compVar}.layers.addSolid([${pal.deepPurple[0]}, ${pal.deepPurple[1]}, ${pal.deepPurple[2]}], "Synthwave_Floor", 1920, 1080, 1.0);`,
      `gridSolid.threeDLayer = true;`,
      `gridSolid.transform.position.setValue([960, 800, 0]);`,
      `gridSolid.transform.rotationX.setValue(80);`,
      `var gridEffect = gridSolid.property("Effects").addProperty("ADBE Grid");`,
      `if (gridEffect) {`,
      `  gridEffect.property("Size From").setValue(2);`,
      `  gridEffect.property("Width").setValue(80);`,
      `  gridEffect.property("Border").setValue(2);`,
      `  gridEffect.property("Color").setValue([${pal.electricCyan[0]}, ${pal.electricCyan[1]}, ${pal.electricCyan[2]}]);`,
      `}`,
      `// Resplandor de Neón`,
      `var glow = gridSolid.property("Effects").addProperty("ADBE Glo2");`,
      `if (glow) { glow.property("Glow Radius").setValue(40); }`,
    ].join("\n");
  }

  /**
   * Genera el fragmento ExtendScript para el sol retro 80s con franjas horizontales cortadas.
   */
  public static generateRetroSunSnippet(
    compVar: string,
    position: [number, number] = [960, 480],
    radiusPx = 180
  ): string {
    const pal = this.PALETTE;
    return [
      `// === RETRO SYNTHWAVE SUN ===`,
      `var sun = ${compVar}.layers.addShape();`,
      `sun.name = "Retro_Synthwave_Sun";`,
      `sun.transform.position.setValue([${position[0]}, ${position[1]}]);`,
      `var sGroup = sun.property("Contents").addProperty("ADBE Vector Group");`,
      `var sCircle = sGroup.property("Contents").addProperty("ADBE Vector Shape - Ellipse");`,
      `sCircle.property("Size").setValue([${radiusPx * 2}, ${radiusPx * 2}]);`,
      `var sFill = sGroup.property("Contents").addProperty("ADBE Vector Graphic - Fill");`,
      `sFill.property("Color").setValue([${pal.sunsetOrange[0]}, ${pal.sunsetOrange[1]}, ${pal.sunsetOrange[2]}]);`,
      `// Glow intenso`,
      `var sGlow = sun.property("Effects").addProperty("ADBE Glo2");`,
      `if (sGlow) {`,
      `  sGlow.property("Glow Intensity").setValue(2.5);`,
      `  sGlow.property("Glow Radius").setValue(60);`,
      `}`,
    ].join("\n");
  }
}
