# 🌐 LOCALIZATION PIPELINE
## ESPECIFICACIÓN TÉCNICA DEL MÓDULO (v3.5.2)
**Documento:** `docs/vlog-expansion/10-LOCALIZATION-PIPELINE.md`  
**Capa:** `v3.5.x Vlog Intelligence Layer`  
**Estado:** `FUENTE ÚNICA DE VERDAD (SSOT) — ESPECIFICACIÓN TÉCNICA`  
**Versión:** `1.0.0`  
**Fecha:** `2026-09-01`  

---

## 1. Propósito
Orquestar la traducción semántica y la generación de subtítulos y contratos de voz localizados para múltiples idiomas objetivo, manteniendo la coherencia temporal de cada bloque de habla respecto al montaje conceptual.

## 2. Alcance
- Traducción de segmentos de texto del idioma origen a idiomas destino (`es`, `en`, `pt`, `fr`, `de`).
- Coordinación con `TTSProvider` para generar pistas de audio localizadas.
- Generación de documentos de subtítulos multilingües (`CaptionDocument`) compatibles con el motor de tipografía de Fase 16.

## 3. No Alcance
- No recalcula la duración del B-roll (eso es responsabilidad exclusiva de `AdaptivePacingEngine`).
- No introduce llamadas cloud de pago obligatorias.

## 4. Entradas
- `basePlan: BaseVlogEditPlan`: Montaje en idioma original.
- `transcript: TranscriptAnalysis`: Transcripción original.
- `targetLanguages: SupportedLanguage[]`: Idiomas a los que se desea exportar el vlog.
- `ttsProvider: TTSProvider`: Proveedor de voz configurado.

## 5. Salidas
- `LocalizedVlogPackage`:
  - `originalLanguage: string`
  - `localizedTracks: Record<SupportedLanguage, LocalizedAudioTrack>`
  - `localizedCaptions: Record<SupportedLanguage, CaptionDocument>`
  - `speechSegments: SpeechSegment[]`

## 6. Interfaces
```typescript
export interface LocalizedVlogPackage {
  readonly originalLanguage: string;
  readonly localizedTracks: Record<SupportedLanguage, LocalizedAudioTrack>;
  readonly localizedCaptions: Record<SupportedLanguage, CaptionDocument>;
  readonly speechSegments: SpeechSegment[];
}
```

## 7. Configuración
```typescript
export interface LocalizationConfig {
  readonly supportedLanguages: SupportedLanguage[];
  readonly maxDurationDeviationRatio: number; // 0.25 (máxima desviación de duración estimada)
  readonly safeZoneProfile: string;           // "tiktok_reels_safe"
}

export const DEFAULT_LOCALIZATION_CONFIG: LocalizationConfig = {
  supportedLanguages: ["es", "en", "pt", "fr", "de"],
  maxDurationDeviationRatio: 0.25,
  safeZoneProfile: "tiktok_reels_safe",
};
```

## 8. Algoritmo
1. **Segmentación de Origen:** Descomponer el transcript en bloques oracionales (`SpeechSegment[]`).
2. **Traducción por Segmento:** Traducir cada bloque al idioma destino preservando el sentido y densidad silábica.
3. **Invocación TTS:** Sintetizar el audio localizado mediante `TTSProvider.synthesize(...)`.
4. **Construcción de Subtítulos:** Generar `CaptionDocument` con timestamps de palabras localizadas.
5. **Empaquetado:** Retornar `LocalizedVlogPackage`.

## 9. Reglas de Negocio
- **RN-LOC01 (Independencia de Idioma):** Cada idioma tiene su propio `CaptionDocument` y `LocalizedAudioTrack` completamente aislados.

## 10. Invariantes
- **INV-LOC01:** Todas las pistas localizadas tienen `durationSec > 0`.
- **INV-LOC02:** El número de segmentos traducidos coincide exactamente con el número de segmentos de origen.

## 11. Casos Normales
- Vlog en Español exportado a Inglés y Portugués: genera 2 pistas de audio `.wav` y 2 archivos de subtítulos sincronizados.

## 12. Casos Límite
- **Traducción con Gran Disparidad de Longitud:** Si la traducción es demasiado corta o larga, se marca con flag `requiresPacingAdjustment = true` para que `AdaptivePacingEngine` resuelva la diferencia.

## 13. Errores
- `TranslationError`: Fallo en la traducción de un segmento.

## 14. Recuperación
- Fallback a traducción literal determinista o conservación de texto original con advertencia.

## 15. Determinismo
- 100% reproducible dado el mismo modelo de traducción y voz.

## 16. Rendimiento
- Procesamiento de un vlog de 5 minutos en $< 5\text{s}$ en modo local.

## 17. Dependencias
- `TTSProvider`, `CaptionDocument` (Fase 16).

## 18. Compatibilidad
- Subtítulos compatibles con After Effects Text Layers y Universal Match Names.

## 19. Seguridad
- Escape de caracteres especiales en subtítulos para prevenir errores de compilación ExtendScript.

## 20. Tests
- Tests unitarios en `src/tests/automation/vlog/localization/LocalizationPipeline.test.ts`.

## 21. Fixtures
- Guiones de prueba bilingües.

## 22. Golden Tests
- Snapshot de `LocalizedVlogPackage` verificado.

## 23. Integración
- Pasa su resultado a `AdaptivePacingEngine` y `AfterEffectsJSXCompiler`.

## 24. Definition of Done
- Pipeline de localización implementado con soporte multi-idioma verificado.
