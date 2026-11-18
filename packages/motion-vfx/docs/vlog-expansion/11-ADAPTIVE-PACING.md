# ⚖️ ADAPTIVE PACING ENGINE
## ESPECIFICACIÓN TÉCNICA DEL MÓDULO (v3.5.3)
**Documento:** `docs/vlog-expansion/11-ADAPTIVE-PACING.md`  
**Capa:** `v3.5.x Vlog Intelligence Layer`  
**Estado:** `FUENTE ÚNICA DE VERDAD (SSOT) — ESPECIFICACIÓN TÉCNICA`  
**Versión:** `1.0.0`  
**Fecha:** `2026-09-01`  

---

## 1. Propósito
Resolver las diferencias de duración entre el idioma original y los idiomas localizados mediante la resolución de contratos temporales, ajustando de forma no destructiva la duración de tomas B-Roll y aplicando dilataciones acotadas de audio sin deformar la voz ni romper el ritmo visual.

## 2. Alcance
- Resolución del contrato temporal entre `SpeechSegment` original y `LocalizedAudioTrack`.
- Ajuste y extensión de tomas B-Roll como primera prioridad de compensación temporal.
- Inserción de tomas B-Roll secundarias si la extensión excede la duración del clip físico.
- Aplicación de dilatación temporal de voz (*TTS stretch*) estrictamente acotada a $[0.95\text{x}, 1.05\text{x}]$.
- Emisión del `FinalVlogEditPlan` para cada idioma.

## 3. No Alcance
- No recorta arbitrariamente las palabras de la locución.
- No muta la velocidad del A-Roll hablante a cámara más allá de los límites perceptuales de seguridad.

## 4. Entradas
- `basePlan: BaseVlogEditPlan`: Montaje conceptual original.
- `localizedPackage: LocalizedVlogPackage`: Pistas de audio y transcripciones por idioma.
- `shotManifest: ShotManifest`: Catálogo de tomas B-Roll disponibles.
- `config?: AdaptivePacingConfig`: Parámetros de ritmo y límites.

## 5. Salidas
- `FinalVlogEditPlan`:
  - `language: SupportedLanguage`
  - `primaryTrack: VlogEditSegment[]`
  - `overlayTrack: BrollPlacement[]`
  - `totalDurationSec: number`
  - `pacingAdjustments: PacingAdjustmentEvent[]`

## 6. Interfaces
```typescript
export interface PacingAdjustmentEvent {
  readonly segmentId: string;
  readonly originalDurationSec: number;
  readonly targetDurationSec: number;
  readonly voiceDilationRatio: number; // Acotado a [0.95, 1.05]
  readonly brollTimeDeltaSec: number;
  readonly action: "broll_extended" | "broll_inserted" | "voice_stretched";
}

export interface FinalVlogEditPlan {
  readonly id: string;
  readonly language: SupportedLanguage;
  readonly primaryTrack: VlogEditSegment[];
  readonly overlayTrack: BrollPlacement[];
  readonly totalDurationSec: number;
  readonly pacingAdjustments: PacingAdjustmentEvent[];
}
```

## 7. Configuración
```typescript
export interface AdaptivePacingConfig {
  readonly minVoiceDilationRatio: number; // 0.95x
  readonly maxVoiceDilationRatio: number; // 1.05x
  readonly maxBrollExtensionSec: number;  // 3.00 s
  readonly preferBrollExtension: boolean; // true
}

export const DEFAULT_ADAPTIVE_PACING_CONFIG: AdaptivePacingConfig = {
  minVoiceDilationRatio: 0.95,
  maxVoiceDilationRatio: 1.05,
  maxBrollExtensionSec: 3.0,
  preferBrollExtension: true,
};
```

## 8. Algoritmo
1. **Comparación de Duraciones:** Para cada segmento de habla $i$, calcular $\Delta t = T_{\text{localizado}} - T_{\text{original}}$.
2. **Caso $\Delta t > 0$ (Idioma destino más largo, ej. Español vs Inglés):**
   - Si hay B-roll activo durante el segmento:
     - Extender la duración del B-roll en $\min(\Delta t, \text{maxBrollExtensionSec})$.
     - Si la extensión no cubre todo $\Delta t$, insertar una segunda toma B-Roll del `ShotManifest`.
   - Si no hay B-roll (A-Roll puro):
     - Aplicar dilatación leve de voz hasta el límite de seguridad de $1.05\text{x}$.
3. **Caso $\Delta t < 0$ (Idioma destino más corto, ej. Inglés vs Español):**
   - Acortar la duración del B-roll correspondiente.
   - O comprimir levemente la voz hasta $0.95\text{x}$.
4. **Reconstrucción del Timeline:** Recalcular `timelineStart` y `timelineEnd` de todos los elementos posteriores garantizando continuidad perfecta.
5. **Emisión:** Retornar `FinalVlogEditPlan`.

## 9. Reglas de Negocio
- **RN-AP01 (Límites Estrictos de Voz):** Queda estrictamente prohibido dilatar la voz por debajo de $0.95\text{x}$ o por encima de $1.05\text{x}$.
- **RN-AP02 (Jerarquía de Compensación):**
  1. Extensión de B-Roll (Preferida).
  2. Inserción de B-Roll complementario (Segunda opción).
  3. Modificación de A-Roll (Evitar siempre que sea posible).

## 10. Invariantes
- **INV-AP01:** $\forall A \in \text{pacingAdjustments}: 0.95 \le A.\text{voiceDilationRatio} \le 1.05$.
- **INV-AP02:** La pista de salida mantiene continuidad estricta sin huecos.

## 11. Casos Normales
- Frase en español (10.0s) traducida a inglés (8.2s): el B-roll superpuesto se ajusta a 8.2s y la siguiente toma entra exactamente en el nuevo tiempo de finalización.

## 12. Casos Límite
- **Diferencia Extrema ($\Delta t > 5.0\text{s}$):** Se insertan 2 tomas B-Roll adicionales del catálogo para rellenar el espacio visual sin deformar la voz.

## 13. Errores
- `PacingConstraintViolationError`: Imposibilidad de resolver el contrato temporal dentro de los límites de seguridad.

## 14. Recuperación
- Fallback a división proporcional de B-roll y preservación de velocidad original con micro-fade.

## 15. Determinismo
- 100% determinista y repetible.

## 16. Rendimiento
- Resolución del plan temporal en $< 15\text{ms}$.

## 17. Dependencias
- `types.ts` de la capa vlog.

## 18. Compatibilidad
- Compatible con el compilador JSX y el motor de Time Remap de v3.4.0.

## 19. Seguridad
- Verificación de límites temporales contra overflow o valores NaN.

## 20. Tests
- Tests unitarios en `src/tests/automation/vlog/pacing/AdaptivePacingEngine.test.ts`.

## 21. Fixtures
- Planes de edición con discrepancias temporales simuladas ($\pm 20\%$).

## 22. Golden Tests
- Snapshot de `FinalVlogEditPlan` verificado.

## 23. Integración
- Envía el `FinalVlogEditPlan` a `TravelOverlayEngine` y `AfterEffectsJSXCompiler`.

## 24. Definition of Done
- Tests de pacing adaptativo pasando al 100% con verificación de límites $[0.95\text{x}, 1.05\text{x}]$.
