# 🎲 Especificación de Determinismo y Eliminación de No-Determinismo

**Estándar:** `Autonomous After Effects MCP — Multi-Level Determinism Specification`  
**Referencia:** `REQ-005`, `REQ-006`, `REQ-007`, `REQ-008`  

---

## 1. Los 4 Niveles Formales de Determinismo

El motor categoriza y certifica el determinismo en 4 niveles rigurosos:

### Nivel A: Determinismo Lógico (100% Obligatorio)
- Dadas dos ejecuciones con idéntica entrada $\text{IR}$ y configuración, el sistema produce exactamente el mismo grafo de operaciones, el mismo plan y el mismo hash SHA-256 de proyecto:
  $$\text{Input}_1 = \text{Input}_2 \implies \text{Hash}(\text{IR}_1) = \text{Hash}(\text{IR}_2)$$

### Nivel B: Determinismo Estructural (100% Obligatorio)
- Mismo orden de capas, mismos IDs estables, mismos valores numéricos de keyframes y matrices de transformación afín $2\text{D}/3\text{D}$ evaluadas con precisión de flotantes ($\epsilon \le 10^{-10}$).

### Nivel C: Determinismo Perceptual (100% Obligatorio en Render)
- Fotogramas renderizados idénticos bajo métricas perceptuales objetivas:
  - $\text{SSIM} \ge 0.999$ (Structural Similarity Index)
  - $\Delta E_{00} \le 0.5$ (Diferencia de color CIE Delta E)
  - $\text{PSNR} \ge 45.0\text{ dB}$ (Peak Signal-to-Noise Ratio)

### Nivel D: Determinismo Binario (Garantizado en Formatos Deterministas)
- Generación de bytes idénticos en disco ($\text{Hash}(\text{File}_1) = \text{Hash}(\text{File}_2)$) para scripts JSX, esquemas JSON y audio WAV PCM sin compresión.
- *Nota Normativa:* En video codificado por hardware (NVENC / H.264), el determinismo se garantiza a Nivel C (Perceptual) debido a pequeñas variaciones heurísticas de encoders GPU.

---

## 2. Fuentes de No-Determinismo Prohibidas

Queda terminantemente prohibido el uso de:
- `Math.random()` sin generador determinista basado en semillas (PRNG).
- `Date.now()` o `new Date()` como fuente de identificadores o decisiones lógicas.
- Iteraciones no ordenadas sobre mapas o conjuntos (`Object.keys()` sin `.sort()`).
- Variables dependientes de la latencia de red o hardware.
