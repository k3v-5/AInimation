# Especificación Técnica: Fase 3C — Advanced Motion

**Documento:** `spec/phase-3c-advanced-motion.md`  
**Estado:** VIGENTE / CONGELADO  
**Módulos:** `src/animation/motion/`

---

## 0. Propósito y Alcance

La **Fase 3C** introduce el sistema de **Motion Functions** y dinámicas físicas analíticas avanzadas.

A diferencia del Easing estándar (acotado rígidamente a $[0, 1]$), una `MotionFunction` puede sobrepasar los límites de destino ($> 1$ o $< 0$) para producir efectos orgánicos de alta gama:

```
Progress [0, 1] ───> MotionFunction ───> Modified Progress (ej. 1.12, -0.05) ───> Unclamped Interpolator ───> Value
```

---

## 1. Reglas e Invariantes Matemáticos y Arquitectónicos

1. **Diferenciación Conceptual (Easing vs Motion Function):**
   - **Easing:** Progresión temporal estándar acotada estrictamente a $[0, 1]$.
   - **Motion Function:** Transformador de progreso continuo y dinámico que soporta sobrepasos (overshoot), oscilaciones físicas y oscilaciones sinusoidales amortiguadas.
2. **Soluciones Analíticas Cerradas (Cero Simulación Frame-by-Frame):**
   Todas las físicas (Spring, Bounce, Elastic) se resuelven analíticamente como funciones deterministas continuas $f(t)$. No existe acumulación numérica de Euler/Verlet susceptible a variaciones de framerate.
3. **Determinismo Absoluto en Perturbaciones (Shake & Wiggle):**
   Prohibido el uso de `Math.random()`. Shake y Wiggle utilizan combinaciones armónicas sinusoidales y pseudo-ruido determinista con semilla.
4. **No Clamping Prematuro:**
   El pipeline de interpolación respeta valores fuera de $[0, 1]$ producidos por `MotionFunction`.
5. **Registro Centralizado y Metadatos (`MotionRegistry`):**
   Todas las funciones de movimiento están auto-descritas con esquemas de parámetros y metadata consultable por agentes de IA.

---

## 2. Formulaciones Matemáticas

### 2.1. Overshoot (Back Dynamics)
Dado el parámetro $s \ge 0$ (overshoot amount, default $s = 1.70158$ o factor escalado):
$$f_{\text{out}}(p) = (p - 1)^3 + s \cdot (p - 1)^2 + 1$$
$$f(0) = 0, \quad f(1) = 1, \quad \max_{p \in [0, 1]} f(p) > 1 \text{ si } s > 0$$

### 2.2. Spring Physics (Oscilador Armónico Amortiguado Analítico)
Parámetros: masa $m > 0$, rigidez $k > 0$, amortiguamiento $c \ge 0$.
Frecuencia natural $\omega_0 = \sqrt{k / m}$, factor de amortiguamiento $\zeta = \frac{c}{2\sqrt{m k}}$.
- **Sub-amortiguado ($\zeta < 1$):**
  $$\omega_d = \omega_0 \sqrt{1 - \zeta^2}$$
  $$f(t) = 1 - e^{-\zeta \omega_0 t} \left( \cos(\omega_d t) + \frac{\zeta \omega_0}{\omega_d} \sin(\omega_d t) \right)$$
- **Críticamente amortiguado ($\zeta = 1$):**
  $$f(t) = 1 - e^{-\omega_0 t} (1 + \omega_0 t)$$
- **Sobre-amortiguado ($\zeta > 1$):**
  $$\omega_1 = -\omega_0 (\zeta - \sqrt{\zeta^2 - 1}), \quad \omega_2 = -\omega_0 (\zeta + \sqrt{\zeta^2 - 1})$$
  $$f(t) = 1 - \frac{\omega_2 e^{\omega_1 t} - \omega_1 e^{\omega_2 t}}{\omega_2 - \omega_1}$$

### 2.3. Bounce (Impactos Parabólicos Decadentes)
Simula rebotes gravitacionales secuenciales mediante tramos parabólicos con factor de restitución / decaimiento $d \in (0, 1)$.

### 2.4. Elastic (Oscilación Exponencialmente Amortiguada)
$$f(p) = 2^{-10 p} \cdot \sin\left((p \cdot 10 - 0.75) \cdot \frac{2\pi}{3}\right) + 1$$

### 2.5. Deterministic Shake
Combinación de armónicos pseudo-aleatorios deterministas con envolvente de decaimiento exponencial o lineal:
$$S(t) = \text{envelope}(t) \cdot \sum_{i=1}^{n} a_i \sin(2\pi f_i t + \phi_i)$$

---

## 3. Interfaces de API

```typescript
export interface MotionFunction {
  readonly type: string;
  evaluate(progress: number): number;
  toJSON(): Record<string, unknown>;
}

export interface MotionMetadata {
  type: string;
  name: string;
  description: string;
  parameters: Record<string, { type: string; default: unknown; min?: number; max?: number }>;
}
```
