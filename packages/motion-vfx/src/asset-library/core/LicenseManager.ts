import { LicenseType } from "../types/index.js";

/**
 * Gestor de licencias y procedencia de activos audiovisuales (Fase 10).
 */
export class LicenseManager {
  /**
   * Determina si un tipo de licencia es apto para inclusión en renders comerciales finales.
   */
  public static isCommercialSafe(license: LicenseType): boolean {
    return license === "royalty-free" || license === "licensed";
  }

  /**
   * Valida si un activo puede ser incluido en el render según la política solicitada.
   */
  public static canUseInRender(
    license: LicenseType,
    allowRestricted = false
  ): boolean {
    if (license === "restricted" && !allowRestricted) {
      return false;
    }
    return true;
  }
}
