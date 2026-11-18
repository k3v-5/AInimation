# Especificación Técnica: Fase 18 — Production Orchestration, Revision Control & Render QA

**Versión:** `1.8.0`  
**Módulo:** `src/production/`  
**Estado:** Formal / Aprobado  

---

## 0. Propósito y Principios

La Fase 18 implementa una capa de orquestación de producción audiovisual reproducible y determinista sobre la IR canónica construida en las Fases 1–17.

### Principios Fundamentales
1. **La IR Canónica es la Única Fuente de Verdad:** Todas las operaciones de edición y QA operan sobre la IR sin introducir modelos secundarios.
2. **Determinismo Absoluto:** Prohibido el uso de `Math.random()`, `Date.now()`, `new Date()` o `crypto.randomUUID()` en la identidad o contenido de la IR y revisiones.
3. **Inmutabilidad de Revisiones:** Cada revisión histórica es permanente e inmutable. Las mutaciones y rollbacks crean nuevas revisiones atómicas preservando todo el historial.
4. **Validación Multi-Capa Pre-Render:** Ningún render se emite sin validación estructural, temporal, de assets, audio, captions y capacidades de exportación.
5. **Render QA Automático:** Muestreo determinista de frames (`key-events`, `uniform`, `hybrid`) evaluando 15 reglas obligatorias de calidad visual y composición.

---

## 1. 15 Reglas Obligatorias de Render QA
1. `canvas-overflow`: Detecta elementos que exceden los límites del canvas sin máscara de recorte.
2. `caption-safe-zone`: Detecta captions que entran en zonas prohibidas de TikTok, Reels y Shorts (header, UI buttons, bottom bar).
3. `caption-overflow`: Detecta texto de subtítulos truncado o que excede el ancho visual disponible.
4. `missing-asset`: Detecta referencias a media files que no existen en el AssetRegistry.
5. `invalid-transform`: Detecta valores no finitos (`NaN`, `Infinity`) en matrices de transformación 2D.
6. `invalid-opacity`: Detecta opacidades fuera del rango $[0, 1]$.
7. `invalid-scale`: Detecta factores de escala no finitos o negativos inválidos.
8. `invalid-color`: Detecta componentes de color RGBA fuera de rango $[0, 1]$ o strings malformados.
9. `empty-text`: Detecta capas de texto sin contenido o con strings vacíos.
10. `offscreen-element`: Detecta capas colocadas completamente fuera del viewport durante todo su tiempo visible sin animación de entrada.
11. `temporal-gap`: Detecta silencios o huecos visuales no intencionados en la pista principal.
12. `temporal-overlap`: Detecta solapamientos no permitidos en tracks exclusivos.
13. `unsupported-export-feature`: Detecta features de la IR no soportadas por el exporter destino (según `CapabilityMatrix`).
14. `audio-clipping`: Detecta niveles de audio pico superiores a $0\text{ dBFS}$ ($\text{amplitud} > 1.0$).
15. `invalid-frame`: Detecta fotogramas que no pueden evaluarse limpiamente en el tiempo $t$.
