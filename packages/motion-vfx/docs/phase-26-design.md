# Documento de Diseño Técnico: Fase 26 — Deep After Effects JSX Compiler & Bidirectional Bridge (v2.6.0)

## 1. Arquitectura del Compilador Avanzado y Puente Bidireccional

```
                     ┌─────────────────────────────┐
                     │     Canonical Project IR    │
                     └──────────────┬──────────────┘
                                    │
           ┌────────────────────────┼────────────────────────┐
           ▼                        ▼                        ▼
 ┌───────────────────┐    ┌───────────────────┐    ┌───────────────────┐
 │AEExpressionBuilder│    │ AEShapeCompiler   │    │  AEBridgeManager  │
 │ (wiggle, loop, etc)│    │(TrimPaths,Repeater│    │ (Markers, Cameras)│
 └─────────┬─────────┘    └─────────┬─────────┘    └─────────┬─────────┘
           │                        │                        │
           └────────────────────────┼────────────────────────┘
                                    │
                                    ▼
                     ┌─────────────────────────────┐
                     │ Extended JSX Script Output  │
                     └──────────────┬──────────────┘
                                    │
                                    ▼
                     ┌─────────────────────────────┐
                     │    AETemplateImporter       │
                     │ (Reverse JSX -> Project IR) │
                     └─────────────────────────────┘
```

---

## 2. Modelado de Expresiones Nativas de After Effects (`AEExpressionBuilder`)

- **`wiggle(freq, amp)`:** Generación paramétrica con octavas opcionales (`wiggle(freq, amp, octaves, amp_mult, t)`).
- **`loopOut(type, numKeyframes)`:** Soporte para `cycle`, `pingpong`, `offset`, `continue`.
- **`linear(t, tMin, tMax, val1, val2)` & `ease(...)`:** Mapeo de rangos con interpolaciones suaves.
- **`valueAtTime(time)`:** Muestreo de desfases temporales (delay trails).
- **`inertia / bounce`:** Expresión física determinista de rebote elástico tras keyframe.

---

## 3. Shape Layers Compiladas (`AEShapeCompiler`)

- Generación ExtendScript para:
  - `ADBE Vector Shape - Group`
  - `ADBE Vector Graphic - Fill`
  - `ADBE Vector Graphic - Stroke`
  - `ADBE Vector Filter - Trim` (`start`, `end`, `offset`)
  - `ADBE Vector Filter - Repeater` (`copies`, `offset`, `transform`)
  - `ADBE Vector Graphic - G-Fill` (Linear & Radial Gradients)

---

## 4. Importador Bidireccional (`AETemplateImporter`)

- Parseo determinista de scripts ExtendScript que definen composiciones, capas, keyframes y textos, convirtiéndolos a instancias de `Composition`, `TextElement`, `ShapeElement` y `Property<T>`.
