export interface GPSHUDConfig {
  latitude: number;
  longitude: number;
  timestampUTC: string;
  codename: string;
}

export interface ScanningLaserConfig {
  color?: [number, number, number];
  scanDurationSec: number;
  startYScalingPct?: number;
}

/**
 * Motor Especializado del Preset #4: The Minimalist Cipher (Lemmino / ColdFusion Style).
 * Genera overlays de HUD de coordenadas GPS, líneas láser de escaneo vertical y tipografía minimalista espacial.
 */
export class MinimalistCipherPreset {
  public static readonly PALETTE = {
    absoluteBlack: [0.0, 0.0, 0.0] as [number, number, number], // #000000
    steelGray: [0.443, 0.443, 0.478] as [number, number, number], // #71717A
    iceBlue: [0.22, 0.741, 0.973] as [number, number, number], // #38BDF8
    radarGreen: [0.133, 0.773, 0.369] as [number, number, number], // #22C55E
    textWhite: [0.941, 0.941, 0.941] as [number, number, number], // #F0F0F0
  };

  /**
   * Formatea coordenadas geográficas a estándar militar decimal/grados.
   */
  public static formatCoordinates(lat: number, lon: number): string {
    const latDir = lat >= 0 ? "N" : "S";
    const lonDir = lon >= 0 ? "E" : "W";
    return `${Math.abs(lat).toFixed(4)}° ${latDir}, ${Math.abs(lon).toFixed(4)}° ${lonDir}`;
  }

  /**
   * Genera el fragmento ExtendScript para el overlay de HUD de coordenadas GPS y metadatos.
   */
  public static generateGPSHUDOverlaySnippet(
    compVar: string,
    config: GPSHUDConfig,
    position: [number, number] = [80, 80]
  ): string {
    const pal = this.PALETTE;
    const coordStr = this.formatCoordinates(config.latitude, config.longitude);
    const fullText = `[ ${config.codename.toUpperCase()} ]  ${coordStr}  //  ${config.timestampUTC}`;

    return [
      `// === MINIMALIST CIPHER GPS HUD OVERLAY ===`,
      `var hudLayer = ${compVar}.layers.addText("${fullText}");`,
      `hudLayer.name = "HUD_Coordinates";`,
      `hudLayer.transform.position.setValue([${position[0]}, ${position[1]}]);`,
      `var tProp = hudLayer.property("Source Text");`,
      `var tDoc = tProp.value;`,
      `tDoc.fontSize = 24;`,
      `tDoc.font = "DIN-Light";`,
      `tDoc.fillColor = [${pal.iceBlue[0]}, ${pal.iceBlue[1]}, ${pal.iceBlue[2]}];`,
      `tDoc.tracking = 35;`,
      `tProp.setValue(tDoc);`,
    ].join("\n");
  }

  /**
   * Genera el fragmento ExtendScript para la línea láser de escaneo vertical.
   */
  public static generateScanningLaserSnippet(
    compVar: string,
    startTimeSec: number,
    durationSec = 3.0
  ): string {
    const pal = this.PALETTE;
    return [
      `// === SCANNING LASER LINE ===`,
      `var laser = ${compVar}.layers.addSolid([${pal.iceBlue[0]}, ${pal.iceBlue[1]}, ${pal.iceBlue[2]}], "Laser_Scanner", 1920, 2, 1.0);`,
      `laser.transform.position.setValueAtTime(${startTimeSec}, [960, 0]);`,
      `laser.transform.position.setValueAtTime(${startTimeSec + durationSec}, [960, 1080]);`,
      `var glow = laser.property("Effects").addProperty("ADBE Glo2");`,
      `if (glow) {`,
      `  glow.property("Glow Threshold").setValue(15);`,
      `  glow.property("Glow Radius").setValue(25);`,
      `  glow.property("Glow Intensity").setValue(2.0);`,
      `}`,
    ].join("\n");
  }
}
