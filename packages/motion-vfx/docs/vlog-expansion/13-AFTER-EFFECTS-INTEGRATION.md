# 🎬 AFTER EFFECTS INTEGRATION & COMPILER
## ESPECIFICACIÓN TÉCNICA DEL MÓDULO (v3.5.x)
**Documento:** `docs/vlog-expansion/13-AFTER-EFFECTS-INTEGRATION.md`  
**Capa:** `v3.5.x Vlog Intelligence Layer`  
**Estado:** `FUENTE ÚNICA DE VERDAD (SSOT) — ESPECIFICACIÓN TÉCNICA`  
**Versión:** `1.0.0`  
**Fecha:** `2026-09-01`  

---

## 1. Propósito
Compilar el plan de edición de vlog final (`FinalVlogEditPlan`), incluyendo pistas de video A-Roll con jump cuts, punch-ins de escala, capas de B-Roll superpuestas, pistas de audio multi-lenguaje independientes, subtítulos cinemáticos y overlays de viaje en un script ExtendScript ejecutable `.jsx` para Adobe After Effects, con soporte bilingüe nativo para instalaciones en Español e Inglés.

## 2. Alcance
- Compilación de cortes de A-Roll y Time Remapping en After Effects.
- Inyección de keyframes de escala ($100\% \to 115\%$) y posición centrada.
- Creación de pistas de audio independientes por idioma con muteable switches.
- Generación de capas de texto con justificación centrada estricta (`ParagraphJustification.CENTER_JUSTIFY`) y Universal Match Names (`ADBE Text Properties`).
- Activación obligatoria de `comp.motionBlur = true`.

## 3. No Alcance
- No ejecuta After Effects directamente (eso lo gestiona `HeadlessRenderOrchestrator` vía `aerender`).
- No genera archivos binarios `.aep` directamente (emite el código ExtendScript `.jsx` que After Effects evalúa para construir el `.aep`).

## 4. Entradas
- `plan: FinalVlogEditPlan`: Plan de montaje resuelto.
- `localizedPackage: LocalizedVlogPackage`: Pistas de audio y subtítulos.
- `overlays: TravelOverlayInstance[]`: Primitivas gráficas de viaje.
- `options?: AECompilerOptions`: Opciones de resolución, FPS y salida.

## 5. Salidas
- `jsxScriptContent: string`: Código ExtendScript (.jsx) completo y ejecutable.
- `manifestFilePath: string`: Manifiesto JSON complementario del proyecto.

## 6. Interfaces
```typescript
export interface AECompilerOptions {
  readonly projectName: string;
  readonly width: number;
  readonly height: number;
  readonly fps: number;
  readonly language: SupportedLanguage;
  readonly includeAllLanguagesAsMutedTracks: boolean;
}
```

## 7. Configuración
```typescript
export interface AEIntegrationConfig {
  readonly defaultWidth: number;   // 1080
  readonly defaultHeight: number;  // 1920 (9:16) o 1080 (16:9)
  readonly defaultFps: number;     // 60.0
  readonly autoMotionBlur: boolean;// true
}

export const DEFAULT_AE_INTEGRATION_CONFIG: AEIntegrationConfig = {
  defaultWidth: 1080,
  defaultHeight: 1920,
  defaultFps: 60.0,
  autoMotionBlur: true,
};
```

## 8. Algoritmo
1. **Inicialización ExtendScript:** Generar encabezado `app.beginUndoGroup("Compile Vlog Master")`.
2. **Creación de Composición Maestra:** Añadir composición con resolución, duración total y `motionBlur = true`.
3. **Importación de Recursos:** Generar código para importar archivos de video crudo, pistas de audio WAV y assets SFX en carpetas de proyecto organizadas.
4. **Montaje de Capas A-Roll:** Generar capas cortadas con sus puntos `inPoint`, `outPoint`, `startTime` y transformaciones de escala calculadas por el `DynamicPunchIn`.
5. **Montaje de Capas B-Roll:** Superponer las capas B-Roll sobre la pista A-Roll respetando los intervalos del plan.
6. **Inyección de Audio:** Crear capas de audio para la voz del idioma activo y pistas secundarias muteadas.
7. **Inyección de Overlays:** Generar las capas vectoriales de `GeoBadge`, `RouteMap` y `PolaroidFreeze`.
8. **Cierre:** Añadir bloque `app.endUndoGroup()` y retorno de script.

## 9. Reglas de Negocio
- **RN-AE01 (Universal Match Names Obligatorios):** Prohibido usar `property("Contents")` o `property("Source Text")` directos. Usar `property("ADBE Root Vectors Group")` y `property("ADBE Text Properties").property("ADBE Text Document")` para compatibilidad con After Effects en Español (`es_ES` / `es_LA`).
- **RN-AE02 (Motion Blur Obligatorio):** Todo script generado debe activar `comp.motionBlur = true`.

## 10. Invariantes
- **INV-AE01:** Todo string inyectado en JSX debe estar escapado contra comillas y caracteres nulos.
- **INV-AE02:** La duración de la composición coincide exactamente con `plan.totalDurationSec`.

## 11. Casos Normales
- Generación de script `.jsx` para un vlog de 3 minutos en 9:16 con 45 jump cuts, 8 punch-ins y 6 tomas B-Roll.

## 12. Casos Límite
- **After Effects en Español:** Funciona sin errores de `TypeError: null no es un objeto`.

## 13. Errores
- `JSXCompilationError`: Fallo durante el ensamblado del código ExtendScript.

## 14. Recuperación
- Fallback con bloque `try/catch` nativo en el script `.jsx` que muestra alertas diagnósticas si falla un asset.

## 15. Determinismo
- Mismo `FinalVlogEditPlan` produce exactamente el mismo código JSX caracter por caracter.

## 16. Rendimiento
- Generación del script JSX en $< 10\text{ms}$.

## 17. Dependencias
- `AfterEffectsJSXCompiler` de v3.4.0.

## 18. Compatibilidad
- Compatible con After Effects 2021 a 2025.

## 19. Seguridad
- Rutas de archivo normalizadas con barras inclinadas (`/`) seguras.

## 20. Tests
- Tests de compilación JSX en `src/tests/automation/vlog/ae/AEIntegration.test.ts`.

## 21. Fixtures
- Planes de edición resueltos.

## 22. Golden Tests
- Snapshot del archivo `.jsx` generado verificado contra golden master.

## 23. Integración
- Es el consumidor final de la cadena de decisiones de la capa vlog.

## 24. Definition of Done
- Código JSX generado validado sintácticamente y probado en After Effects.
