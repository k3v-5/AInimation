# Especificación Técnica Maestra: Fase 26 — Deep After Effects JSX Compiler & Bidirectional Bridge (v2.6.0)

## 0. Propósito y Principio Rector

La **Fase 26** eleva la integración con Adobe After Effects a su nivel definitivo:
1. **Compilador de Expresiones Nativas:** Permite que las animaciones generadas por la IA y el motor se traduzcan en código de expresiones de After Effects (`wiggle`, `loopOut`, `linear`, `ease`, `valueAtTime`, `bounce/inertia`).
2. **Soporte Completo de Vector Shape Layers:** Compilación a ExtendScript de trazados Bezier, Trim Paths, Repeaters y rellenos de degradado.
3. **Importador Bidireccional:** Capacidad de importar templates JSX de After Effects hacia la IR canónica del Motion Engine.

---

## 1. Gramática de Expresiones Soportadas

| Tipo de Expresión | Sintaxis ExtendScript Generada | Parámetros |
|---|---|---|
| `wiggle` | `wiggle(freq, amp)` | `freq: number, amp: number` |
| `loopOut` | `loopOut("cycle", 0)` | `type: "cycle" \| "pingpong" \| "offset", numKeyframes: number` |
| `linear` | `linear(time, inMin, inMax, outMin, outMax)` | Mapeo de rangos numéricos |
| `ease` | `ease(time, inMin, inMax, outMin, outMax)` | Mapeo sigmoidal de rangos |
| `valueAtTime` | `thisComp.layer("L").transform.position.valueAtTime(time - delay)` | `layerName: string, prop: string, delay: number` |
| `inertia_bounce` | Código de rebote elástico basado en amortiguamiento y frecuencia | `amp: number, freq: number, decay: number` |

---

## 2. Definición de Shape Modifiers para After Effects

- **Trim Paths:** Modificador paramétrico de revelado (`start`, `end`, `offset`) con soporte para modos simultáneos e individuales.
- **Repeater:** Duplicador paramétrico con matriz de transformación relativa (`copies`, `offset`, `position`, `scale`, `rotation`).

---

## 3. Criterios de Aceptación y Definition of Done
1. `AEExpressionBuilder` genera código sintácticamente válido para todas las expresiones estándar.
2. `AEShapeCompiler` genera bloques ExtendScript para Shape Layers con Trim Paths y Repeaters.
3. `AETemplateImporter` parsea scripts JSX simples y reconstruye la estructura `Composition` correspondiente.
4. La suite completa de pruebas de 7 capas pasa al 100% en verde sin romper ninguna de las 25 fases anteriores.
