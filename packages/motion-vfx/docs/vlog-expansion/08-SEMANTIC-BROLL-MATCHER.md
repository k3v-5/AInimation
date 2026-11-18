# 🧩 SEMANTIC B-ROLL MATCHER
## ESPECIFICACIÓN TÉCNICA DEL MÓDULO (v3.5.1)
**Documento:** `docs/vlog-expansion/08-SEMANTIC-BROLL-MATCHER.md`  
**Capa:** `v3.5.x Vlog Intelligence Layer`  
**Estado:** `FUENTE ÚNICA DE VERDAD (SSOT) — ESPECIFICACIÓN TÉCNICA`  
**Versión:** `1.0.0`  
**Fecha:** `2026-09-01`  

---

## 1. Propósito
Emparejar algorítmicamente las palabras y conceptos hablados en el audio A-Roll con las tomas de apoyo visual B-Roll disponibles en el `ShotManifest`, determinando qué clips B-Roll deben sobreponerse sobre la pista de voz y en qué rangos temporales exactos.

## 2. Alcance
- Cálculo de puntuación de afinidad semántica (Jaccard / Cosine similarity sobre tags).
- Asignación de tomas B-Roll sobre la voz sin cortar la pista de audio principal (L-cuts y J-cuts).
- Control de duración de tomas B-Roll entre $[1.50\text{s}, 5.00\text{s}]$.
- Prevención de repetición inmediata de la misma toma B-Roll.

## 3. No Alcance
- No altera el corte del audio ni elimina silencios (eso ya lo resolvió `VlogJumpCutEngine`).
- No sintetiza voz ni traduce idiomas (eso corresponde a `MultilingualTTS` y `AdaptivePacing`).

## 4. Entradas
- `jumpCutResult: VlogJumpCutResult`: Segmentos de voz A-Roll cortados y continuos.
- `transcript: TranscriptAnalysis`: Palabras habladas con sus timestamps.
- `shotManifest: ShotManifest`: Catálogo de tomas B-Roll disponibles con sus tags.
- `config?: SemanticMatcherConfig`: Parámetros de matching.

## 5. Salidas
- `BaseVlogEditPlan`:
  - `primaryTrack: VlogEditSegment[]`: Pista principal de voz A-Roll con sus punch-ins.
  - `overlayTrack: BrollPlacement[]`: Tomas B-Roll superpuestas con `sourceIn`, `sourceOut`, `timelineStart`, `timelineEnd`.
  - `totalDurationSec: number`: Duración global del montaje.

## 6. Interfaces
```typescript
export interface BrollPlacement {
  readonly id: string;
  readonly shotId: string;
  readonly sourceFilePath: string;
  readonly sourceStart: number;
  readonly sourceEnd: number;
  readonly timelineStart: number;
  readonly timelineEnd: number;
  readonly duration: number;
  readonly matchedTags: string[];
  readonly affinityScore: number;
}

export interface BaseVlogEditPlan {
  readonly id: string;
  readonly primaryTrack: VlogEditSegment[];
  readonly overlayTrack: BrollPlacement[];
  readonly totalDurationSec: number;
  readonly matchedBrollCount: number;
}
```

## 7. Configuración
```typescript
export interface SemanticMatcherConfig {
  readonly minBrollDurationSec: number;     // 1.80 s
  readonly maxBrollDurationSec: number;     // 4.50 s
  readonly minAffinityScore: number;        // 0.40
  readonly brollDensityIntervalSec: number; // 6.00 s (máximo espacio sin B-Roll)
  readonly avoidRepeatWindowSec: number;    // 30.0 s
}

export const DEFAULT_SEMANTIC_MATCHER_CONFIG: SemanticMatcherConfig = {
  minBrollDurationSec: 1.80,
  maxBrollDurationSec: 4.50,
  minAffinityScore: 0.40,
  brollDensityIntervalSec: 6.00,
  avoidRepeatWindowSec: 30.0,
};
```

## 8. Algoritmo
1. **Indexación de Palabras Clave:** Extraer entidades y sustantivos del transcript en la línea de salida.
2. **Ventanas de Oportunidad B-Roll:** Identificar bloques de A-Roll de más de $4.0\text{s}$ donde una toma de apoyo mantenga el dinamismo.
3. **Scoring de Afinidad:** Para cada ventana temporal $[t_{\text{start}}, t_{\text{end}}]$:
   - Extraer tags del habla: $T_{\text{speech}}$.
   - Para cada shot B-Roll disponible:
     $$\text{Score}(B) = \frac{|T_{\text{speech}} \cap B.\text{tags}|}{|T_{\text{speech}} \cup B.\text{tags}|} \times B.\text{visualScore}$$
4. **Selección y Asignación:** Elegir el shot con mayor puntuación que no se haya usado en los últimos $30\text{s}$.
5. **Cálculo de In/Out de B-Roll:** Ajustar `sourceStart` y `sourceEnd` dentro de los límites del archivo físico.
6. **Emisión de `BaseVlogEditPlan`:** Ensamblar pistas primaria y de superposición.

## 9. Reglas de Negocio
- **RN-BM01 (Audio Ininterrumpido):** La inserción de B-Roll es solo visual; la pista de audio A-Roll nunca se corta durante un B-Roll.
- **RN-BM02 (No Tomas Fuera de Límite):** `sourceEnd - sourceStart <= shot.duration`.

## 10. Invariantes
- **INV-BM01:** $\forall B \in \text{overlayTrack}: B.\text{timelineEnd} \le \text{totalDurationSec}$.
- **INV-BM02:** $\forall B \in \text{overlayTrack}: B.\text{duration} \ge \text{minBrollDurationSec}$.

## 11. Casos Normales
- El vlogger dice "caminando por el centro histórico": el matcher busca shots con tag `centro` o `calle` y coloca un B-roll de 3.2s sobre la voz.

## 12. Casos Límite
- **Zero B-Roll Disponible:** El plan se genera con `overlayTrack: []` (todo el video queda en A-Roll limpio con punch-ins).
- **Afinidad Débil (Score < 0.40):** Si no hay coincidencia temática pero han pasado $> 8\text{s}$ de A-Roll continuo, inserta un B-roll genérico de alto `visualScore`.

## 13. Errores
- `InvalidEditPlanError`: Tiempos de B-roll que desbordan la duración del timeline.

## 14. Recuperación
- Si una toma B-Roll referenciada no existe, se degrada elegantemente a mostrar el A-Roll subyacente.

## 15. Determinismo
- 100% determinista dado el mismo `ShotManifest` y `Transcript`.

## 16. Rendimiento
- Resolución de un plan de 10 minutos en $< 20\text{ms}$.

## 17. Dependencias
- `types.ts` del módulo vlog.

## 18. Compatibilidad
- Mapea directamente a capas de video de nivel superior en After Effects JSX.

## 19. Seguridad
- Verificación estricta de rutas de archivos.

## 20. Tests
- Tests unitarios en `src/tests/automation/vlog/matcher/SemanticBrollMatcher.test.ts`.

## 21. Fixtures
- Transcript de viaje con tags emparejados a shots sintéticos.

## 22. Golden Tests
- Snapshot de `BaseVlogEditPlan` verificado.

## 23. Integración
- Pasa su resultado a `AdaptivePacingEngine`.

## 24. Definition of Done
- Tests de matching semántico pasando al 100% sin solapamientos inválidos.
