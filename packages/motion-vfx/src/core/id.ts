/**
 * Generador de IDs determinista para Compositions y Layers.
 * Permite reproducibilidad absoluta en serialización y pruebas.
 */

let compCounter = 0;
let layerCounter = 0;

export function generateDeterministicCompId(): string {
  compCounter += 1;
  return `comp_${compCounter}`;
}

export function generateDeterministicLayerId(): string {
  layerCounter += 1;
  return `layer_${layerCounter}`;
}

/**
 * Reinicia los contadores deterministas (útil entre ejecuciones de tests).
 */
export function resetIdGenerators(): void {
  compCounter = 0;
  layerCounter = 0;
}
