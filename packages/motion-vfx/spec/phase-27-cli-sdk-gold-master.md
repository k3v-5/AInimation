# Especificación Técnica Maestra: Fase 27 — Standalone CLI, Public TypeScript SDK & Gold Master Certification (v3.0.0)

## 0. Propósito y Principio Rector

La **Fase 27** representa la culminación del proyecto, empaquetando todo el motor audiovisual en un **CLI Standalone ejecutable**, un **SDK TypeScript público de primer nivel** y la **Certificación Gold Master v3.0.0**.

---

## 1. Comandos y Sintaxis del CLI

| Comando | Argumentos Principales | Descripción |
|---|---|---|
| `render` | `<file> -o <out.mp4> [--fps 60]` | Renderiza una composición a video o secuencia de frames |
| `export-ae` | `<file> -o <script.jsx> [--strict]` | Exporta la composición a script ExtendScript JSX para After Effects |
| `export-social` | `<file> -o <dir> [--ratios 9:16,16:9,1:1]` | Genera el paquete social completo con audio normalizado y miniaturas |
| `qa` | `<file> [--threshold 0.8]` | Ejecuta la batería de QA de 7 familias y QA perceptual |
| `validate` | `<file>` | Valida la estructura e integridad de la IR canónica |
| `version` | N/A | Muestra la versión del motor (`3.0.0-gold-master`) |

---

## 2. Definición del SDK Público (`MotionEngine`)

El SDK encapsula la complejidad de las 27 Fases del motor en métodos estáticos tipados, deterministas e inmutables.

---

## 3. Criterios de Aceptación y Definition of Done
1. `motion-engine` CLI procesa argumentos con banderas cortas y largas y emite códigos de salida UNIX válidos.
2. `MotionEngineSDK` proporciona una API limpia para creación, render, exportación, QA y validación.
3. El paquete expone `bin/motion-engine.js` ejecutable con `npx` o globalmente.
4. La versión global se actualiza a `3.0.0` y la suite de pruebas completa supera los 600 tests al 100% en verde.
