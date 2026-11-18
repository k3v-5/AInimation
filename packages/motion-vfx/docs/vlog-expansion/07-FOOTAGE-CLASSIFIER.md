# 🎞️ FOOTAGE CLASSIFIER & SHOT MANIFEST
## ESPECIFICACIÓN TÉCNICA DEL MÓDULO (v3.5.1)
**Documento:** `docs/vlog-expansion/07-FOOTAGE-CLASSIFIER.md`  
**Capa:** `v3.5.x Vlog Intelligence Layer`  
**Estado:** `FUENTE ÚNICA DE VERDAD (SSOT) — ESPECIFICACIÓN TÉCNICA`  
**Versión:** `1.0.0`  
**Fecha:** `2026-09-01`  

---

## 1. Propósito
Analizar e indexar el catálogo de archivos de video sin editar (metraje crudo de una carpeta de proyecto) y generar un manifiesto estructurado, inmutable y cacheable (`ShotManifest.json`) clasificando cada toma según su rol editorial (`A_ROLL`, `B_ROLL`, `TIMELAPSE`, `ACTION`).

## 2. Alcance
- Clasificación determinista de tomas por presencia de rostro, nivel de movimiento óptico y duración.
- Asignación de etiquetas semánticas (*tags*) basadas en metadatos, nombres de archivo o visión.
- Extracción de geolocalización básica (GPS/Exif si existe en el contenedor).
- Serialización a `ShotManifest.json` reutilizable entre múltiples idiomas.

## 3. No Alcance
- No decide dónde cortar el metraje ni qué tomas colocar en la línea de tiempo (eso es responsabilidad de `SemanticBrollMatcher` y `VlogEditPlanner`).
- No modifica los archivos de video originales en disco.

## 4. Entradas
- `sourceDirectory: string`: Directorio con archivos de video (.mp4, .mov).
- `videoFiles: Array<{ filePath: string; durationSec: number; width: number; height: number }>`: Metadatos de los clips.
- `hints?: Record<string, { tags?: string[]; forcedType?: ShotType }>`: Pistas opcionales.

## 5. Salidas
- `ShotManifest`:
  - `schemaVersion: "1.0.0"`
  - `sourceDirectory: string`
  - `analyzedAt: string`
  - `shots: VlogShot[]`: Colección de tomas clasificadas con `visualScore`, `motionScore`, `faceScore`, `type` y `semanticTags`.

## 6. Interfaces
```typescript
export type ShotType = "A_ROLL" | "B_ROLL" | "TIMELAPSE" | "ACTION";

export interface VlogShot {
  readonly id: string;
  readonly sourceFilePath: string;
  readonly start: number;
  readonly end: number;
  readonly duration: number;
  readonly type: ShotType;
  readonly semanticTags: string[];
  readonly visualScore: number;
  readonly motionScore?: number;
  readonly faceScore?: number;
  readonly location?: GeoLocation;
}

export interface ShotManifest {
  readonly schemaVersion: "1.0.0";
  readonly sourceDirectory: string;
  readonly analyzedAt: string;
  readonly shots: VlogShot[];
}
```

## 7. Configuración
```typescript
export interface FootageClassifierConfig {
  readonly minBrollDurationSec: number;     // 1.50 s
  readonly maxBrollDurationSec: number;     // 8.00 s
  readonly facePresenceThreshold: number;   // 0.60
  readonly motionActionThreshold: number;   // 0.75
  readonly timelapseSpeedRatio: number;     // 4.0x
}

export const DEFAULT_FOOTAGE_CLASSIFIER_CONFIG: FootageClassifierConfig = {
  minBrollDurationSec: 1.50,
  maxBrollDurationSec: 8.00,
  facePresenceThreshold: 0.60,
  motionActionThreshold: 0.75,
  timelapseSpeedRatio: 4.0,
};
```

## 8. Algoritmo
1. **Escaneo de Directorio:** Enumerar archivos de video válidos (.mp4, .mov) en orden determinista.
2. **Extracción de Metadatos:** Obtener duración, resolución y tasa de fotogramas mediante FFprobe.
3. **Clasificación por Rol:**
   - Si `faceScore >= facePresenceThreshold` y pista de audio continua $\to$ `A_ROLL`.
   - Si `motionScore >= motionActionThreshold` $\to$ `ACTION`.
   - Si flujo temporal muy acelerado $\to$ `TIMELAPSE`.
   - Por defecto para tomas de paisaje, objetos o ambiente $\to$ `B_ROLL`.
4. **Extracción Semántica de Tags:** Derivar tags del nombre del archivo, directorio y pistas visuales (ej. `["guadalajara", "night", "street", "food"]`).
5. **Generación de ID Determinista:** `shot_` + SHA-256 parcial de `sourceFilePath`.
6. **Emisión y Guardado:** Escribir `ShotManifest.json` validado con Zod en el directorio del proyecto.

## 9. Reglas de Negocio
- **RN-FC01 (Reutilización Inter-Idioma):** El archivo `ShotManifest.json` generado es universal y debe ser idéntico para las versiones en Español, Inglés o cualquier otro idioma.
- **RN-FC02 (No Tomas de 0s):** Cualquier clip con duración $\le 0.10\text{s}$ o corrupto es excluido del catálogo.

## 10. Invariantes
- **INV-FC01:** `ShotManifestSchema.safeParse(manifest).success === true`.
- **INV-FC02:** $\forall S \in \text{shots}: S.\text{end} - S.\text{start} == S.\text{duration} > 0$.

## 11. Casos Normales
- Carpeta con 1 video principal de vlogger hablando (A-Roll) y 10 tomas de comida y calles (B-Roll): Se clasifica correctamente el A-Roll y se etiquetan los 10 B-rolls.

## 12. Casos Límite
- **Carpeta sin B-Roll (Solo A-Roll):** Manifiesto generado con 1 solo shot de tipo `A_ROLL`.
- **Archivos No de Video (ej. .txt, .ds_store):** Ignorados silenciosamente.

## 13. Errores
- `InvalidDirectoryError`: El directorio indicado no existe o no tiene permisos de lectura.
- `EmptyFootageError`: No se encontraron archivos de video válidos.

## 14. Recuperación
- Si un archivo está parcialmente dañado pero FFprobe puede leer su duración, se incluye con `visualScore = 0.3` en lugar de abortar todo el lote.

## 15. Determinismo
- Mismo directorio de archivos ordenados alfabéticamente produce el mismo `ShotManifest.json` idéntico bit a bit.

## 16. Rendimiento
- Escaneo y clasificación de 100 clips en menos de $200\text{ms}$ si los metadatos están cacheados.

## 17. Dependencias
- `zod`, `path`, `fs`.

## 18. Compatibilidad
- Rutas normalizadas con barras inclinadas (`/`) compatibles con Windows, macOS y Linux.

## 19. Seguridad
- Bloqueo de rutas relativas con `../` maliciosos fuera del árbol del proyecto.

## 20. Tests
- Tests unitarios en `src/tests/automation/vlog/footage/FootageClassifier.test.ts`.

## 21. Fixtures
- Carpeta simulada con archivos y metadatos JSON controlados.

## 22. Golden Tests
- Snapshot de `ShotManifest.json` para el set de prueba de Guadalajara.

## 23. Integración
- Consumido por `SemanticBrollMatcher` y el planificador editorial `VlogEditPlanner`.

## 24. Definition of Done
- Esquema Zod validado, tests pasando al 100% y archivo `ShotManifest.json` cacheable.
