# 🗣️ MULTILINGUAL TTS & TTS PROVIDER PATTERN
## ESPECIFICACIÓN TÉCNICA DEL MÓDULO (v3.5.2)
**Documento:** `docs/vlog-expansion/09-MULTILINGUAL-TTS.md`  
**Capa:** `v3.5.x Vlog Intelligence Layer`  
**Estado:** `FUENTE ÚNICA DE VERDAD (SSOT) — ESPECIFICACIÓN TÉCNICA`  
**Versión:** `1.0.0`  
**Fecha:** `2026-09-01`  

---

## 1. Propósito
Definir la arquitectura de abstracción y los proveedores de síntesis de voz neuronal multi-idioma (Español, Inglés, Portugués, Francés, Alemán) funcionando 100% en local y a **$0 coste recurrente de APIs**, permitiendo generar pistas de voz sincronizadas con marcas de tiempo a nivel de palabra.

## 2. Alcance
- Definición formal de la interfaz desacoplada `TTSProvider`.
- Implementación de proveedores locales (Piper TTS local, Edge-TTS local y Mock/Deterministic Provider para pruebas).
- Generación de archivos de audio estándar PCM WAV de 16-bit / 44.1kHz.
- Extracción de marcas de tiempo fonéticas por palabra (`LocalizedWordTiming[]`).

## 3. No Alcance
- No traduce texto (eso corresponde a `LocalizationPipeline`).
- No ajusta la duración del timeline visual (eso corresponde a `AdaptivePacingEngine`).
- No depende de servicios cloud de pago por carácter o llamada.

## 4. Entradas
- `text: string`: Texto en el idioma destino.
- `language: SupportedLanguage`: Código de idioma (`"es"`, `"en"`, `"pt"`, `"fr"`, `"de"`).
- `voiceId?: string`: Identificador de la voz neuronal deseada.
- `options?: TTSOptions`: Velocidad, tono y directorio de salida.

## 5. Salidas
- `LocalizedAudioTrack`:
  - `language: SupportedLanguage`
  - `audioFilePath: string`: Ruta al archivo .wav generado en disco.
  - `durationSec: number`: Duración total exacta del audio sintetizado.
  - `wordTimings: LocalizedWordTiming[]`: Lista de palabras con $[w_{\text{start}}, w_{\text{end}})$.

## 6. Interfaces
```typescript
export type SupportedLanguage = "es" | "en" | "pt" | "fr" | "de";

export interface LocalizedWordTiming {
  readonly word: string;
  readonly start: number;
  readonly end: number;
}

export interface LocalizedAudioTrack {
  readonly language: SupportedLanguage;
  readonly audioFilePath: string;
  readonly durationSec: number;
  readonly wordTimings: LocalizedWordTiming[];
}

export interface TTSProvider {
  readonly name: string;
  synthesize(
    text: string,
    language: SupportedLanguage,
    outputFilePath: string
  ): Promise<LocalizedAudioTrack>;
}
```

## 7. Configuración
```typescript
export interface TTSConfig {
  readonly defaultLanguage: SupportedLanguage;  // "es"
  readonly sampleRate: number;                  // 44100
  readonly defaultVoiceMap: Record<SupportedLanguage, string>;
  readonly maxTextLengthChars: number;          // 50000
}

export const DEFAULT_TTS_CONFIG: TTSConfig = {
  defaultLanguage: "es",
  sampleRate: 44100,
  defaultVoiceMap: {
    es: "es_MX-ald-medium",
    en: "en_US-lessac-medium",
    pt: "pt_BR-edresson-low",
    fr: "fr_FR-siwis-medium",
    de: "de_DE-thorsten-medium",
  },
  maxTextLengthChars: 50000,
};
```

## 8. Algoritmo
1. **Validación de Texto:** Verificar que el texto no esté vacío y que el idioma esté soportado.
2. **Selección de Proveedor:** Instanciar el `TTSProvider` configurado (ej. Piper local).
3. **Síntesis Acústica:** Invocar el binario local generando el archivo `.wav`.
4. **Extracción Fonética:** Obtener los timestamps de cada palabra mediante alineación fonética o salida de Whisper local sobre el audio generado.
5. **Normalización PCM:** Asegurar formato estándar 16-bit 44.1kHz mono mediante FFmpeg si es requerido.
6. **Retorno de Contrato:** Devolver `LocalizedAudioTrack`.

## 9. Reglas de Negocio
- **RN-TTS01 (Cero Coste Recurrente):** Queda prohibida la dependencia obligatoria de APIs comerciales de pago.
- **RN-TTS02 (Pistas WAV Estándar):** Toda pista generada debe ser PCM WAV compatible nativamente con After Effects.

## 10. Invariantes
- **INV-TTS01:** $\text{track}.\text{durationSec} > 0$.
- **INV-TTS02:** $\forall W \in \text{wordTimings}: W.\text{end} \le \text{track}.\text{durationSec}$.

## 11. Casos Normales
- Síntesis de un párrafo en inglés: produce `voice_en.wav` de 8.4s con 22 palabras temporizadas.

## 12. Casos Límite
- **Texto con Números o Símbolos ($100, %, #):** Normalizados verbalmente ("cien dólares", "por ciento") antes de sintetizar.
- **Texto Muy Breve ("Sí."):** Genera audio válido con duración $> 0.3\text{s}$.

## 13. Errores
- `UnsupportedLanguageError`: Idioma no soportado.
- `TTSSynthesisError`: Fallo en la ejecución del sintetizador local.

## 14. Recuperación
- En modo pruebas o fallback, se utiliza el `DeterministicMockTTSProvider` que genera audio sintetizado procedural con duraciones teóricas exactas sin fallar.

## 15. Determinismo
- Mismo texto y modelo neuronal produce el mismo audio con idéntica duración a nivel de milisegundo.

## 16. Rendimiento
- Síntesis neuronal en tiempo real ($1.0\text{x}$ a $3.0\text{x}$ realtime en CPU estándar sin requerir GPU dedicada).

## 17. Dependencias
- `piper-tts` (binario local), `fs`, `path`.

## 18. Compatibilidad
- Pistas `.wav` importables de forma universal en After Effects, Premiere Pro y Final Cut.

## 19. Seguridad
- Sanitización de texto para prevenir inyecciones de escape en comandos de terminal.

## 20. Tests
- Tests unitarios en `src/tests/automation/vlog/localization/MultilingualTTS.test.ts`.

## 21. Fixtures
- Frases de prueba en los 5 idiomas soportados.

## 22. Golden Tests
- Comparación de timestamps de palabras generadas por el mock determinista.

## 23. Integración
- Invocado por `LocalizationPipeline` y consumido por `AdaptivePacingEngine`.

## 24. Definition of Done
- Interfaz `TTSProvider` implementada, pruebas multi-idioma pasando al 100% y cero costes recurrentes de APIs.
