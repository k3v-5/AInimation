# Especificación Técnica: Fase 4B — Text Animation System

**Documento:** `spec/phase-4b-text-animation.md`  
**Estado:** VIGENTE / CONGELADO  
**Módulos:** `src/text/`

---

## 0. Propósito y Filosofía Arquitectónica

La **Fase 4B** establece el sistema de animación tipográfica para motion graphics (estilo TikTok, YouTube Shorts y kinetic typography).

### Principio Fundamental: Subtargets Virtuales
Para evitar la explosión del árbol de la escena (*Scene Graph*), un texto de $10,000$ caracteres **NO se convierte en $10,000$ elementos individuales**. En su lugar, el `TextElement` mantiene un desglose de layout con **subtargets virtuales** accesibles mediante selectores canónicos:

- **Element:** `${elementId}`
- **Word:** `${elementId}:word:${wordIndex}`
- **Character:** `${elementId}:char:${charIndex}` o `${elementId}:word:${wIndex}:char:${cIndex}`

```
TextElement ("ESTO ES INCREÍBLE")
    │
    ├── Word 0 ("ESTO")
    │    ├── Char 0 ("E")
    │    ├── Char 1 ("S")
    │    ├── Char 2 ("T")
    │    └── Char 3 ("O")
    │
    ├── Word 1 ("ES")
    │    ├── Char 4 ("E")
    │    └── Char 5 ("S")
    │
    └── Word 2 ("INCREÍBLE")
         ├── Char 6 ("I")
         └── ...
```

---

## 1. Segmentación Unicode y Grapheme Clusters

Un "carácter" para animación es un **grapheme cluster visual**, no un byte ni un char de UTF-16.
El `TextSegmenter` utiliza `Intl.Segmenter` con granularidad de grafemas y palabras:
- Manejo exacto de emojis compuestos (`👨‍👩‍👧‍👦`, `👍🏽`).
- Combinación canónica de tildes y diacríticos (`e` + `\u0301` vs `é`).
- Preservación de espacios y puntuación en el layout.

---

## 2. TextSelector y TextStagger

### 2.1. Alcances (`TextScope`)
- `"element"` | `"line"` | `"word"` | `"character"`

### 2.2. Órdenes (`TextOrder`)
- `"forward"` | `"reverse"` | `"random"` (con semilla determinista `seed`) | `"center"` | `"edges"`

### 2.3. Fórmula de Stagger Anidado
Para animar palabras con retraso $D_w$ y caracteres internos con retraso $D_c$:
$$\text{delay}(w, c) = \text{baseDelay} + (w \cdot D_w) + (c \cdot D_c)$$

---

## 3. Integración con Animation Engine y DSL

Un nodo de animación de texto en el DSL:
```json
{
  "type": "textAnimation",
  "target": "title",
  "scope": "character",
  "order": "forward",
  "animation": {
    "type": "slideIn",
    "direction": "up",
    "distance": 40
  },
  "stagger": {
    "delay": 0.04
  }
}
```
se compila deterministamente en un `ParallelAnimation` que contiene instancias del movimiento aplicadas a cada subtarget virtual.
