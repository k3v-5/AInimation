# 📜 ESPECIFICACIÓN TÉCNICA: BEAT SYNC ENGINE
## Sincronización Rítmica por Transientes de Audio y Montaje a Tempo

**Módulo:** `src/editorial/audio/beat-sync-engine.ts`  
**Estado:** `ESPECIFICACIÓN FORMAL v4.1.0`  
**Baseline:** `v4.0.0 (1,424 tests GREEN)`  
**Invariantes:** Determinista • Tolerancia Cero a Redes • Cero Drift Acústico ($\Delta t \le 10^{-6}\text{s}$) • Sin Huecos Negros  

---

## 1. Objetivo y Alcance

El **`BeatSyncEngine`** proporciona la infraestructura matemática y editorial para sincronizar automáticamente el flujo de corte y animación visual con la estructura rítmica y los transientes de una pista de audio (música, percusión, efectos rítmicos o voz estentórea).

### Capacidades:
1. **Detección de Transientes y Picos de Energía:** Identificación de onsets y transientes percusivos a partir de señales de amplitud instantánea o RMS.
2. **Generador Determinista de Cuadrícula de Tempo (BPM Grid):** Modelado métrico en compases $4/4$ o $3/4$ con cálculo de downbeats (primer tiempo del compás) y subdivisiones.
3. **Cuantizador y Alineador Temporal de Cortes Visuales:** Ajuste elástico de puntos de entrada y salida de planos para que coincidan de forma continua con los golpes rítmicos.
4. **Generador de Pulsos Visuales Reactivos (Punch-In Rítmico):** Cálculo de keyframes de escala centrada ($100\% \to 105\% \to 100\%$) al impacto de downbeats.
5. **Generador de Marcadores de Compás para After Effects:** Exportación de marcadores de línea de tiempo enriquecidos para inspección en el NLE.

---

## 2. Formulación Matemática

### 2.1. Función de Detección de Onsets (ODF) y Umbralización Adaptativa

Dada una secuencia de muestras de energía o amplitud $x[n]$ con frecuencia de muestreo $f_s$:
1. **Energía RMS Local:**
   $$E[m] = \sqrt{\frac{1}{W} \sum_{k=0}^{W-1} x[m \cdot H + k]^2}$$
   donde $W$ es el tamaño de ventana y $H$ el salto (*hop size*).

2. **Diferencia de Primer Orden (Derivada Rectificada de Energía):**
   $$\Delta E[m] = \max(0, E[m] - E[m-1])$$

3. **Umbral Dinámico Adaptativo:**
   $$\theta[m] = \mu_w[m] + k \cdot \sigma_w[m]$$
   donde $\mu_w[m]$ es la media móvil en una ventana de contexto de longitud $L_w$, $\sigma_w[m]$ es la desviación típica local, y $k \in [0.5, 2.5]$ es la constante de sensibilidad.

4. **Periodo Refractario:**
   Si se detecta un transiente en $t_i$, ningún nuevo transiente puede registrarse antes de:
   $$t_{i+1} \ge t_i + t_{\text{refractory}}, \quad t_{\text{refractory}} \ge 0.12\text{s}$$

---

### 2.2. Cuadrícula de Compás y Métrica Musical

Dado un tempo nominal $B$ en BPM y un offset inicial $t_{\text{offset}}$:
$$\Delta t_{\text{beat}} = \frac{60}{B}$$
El timestamp del beat $i$-ésimo viene dado por:
$$t_i = t_{\text{offset}} + i \cdot \Delta t_{\text{beat}}, \quad i \in \mathbb{N}_0$$

Para un compás de $N_{\text{beats}}$ tiempos (ej. $4/4 \Rightarrow N_{\text{beats}} = 4$):
$$\text{isDownbeat}(i) \iff (i \pmod{N_{\text{beats}}} == 0)$$

---

### 2.3. Alineación Elástica de Planos a Beats

Para una secuencia de clips candidatos $C_1, C_2, \dots, C_m$ que deben cubrir un intervalo $[0, T_{\text{total}}]$:
- Se seleccionan puntos de corte objetivo $t_1^*, t_2^*, \dots, t_m^*$ pertenecientes a los transientes detectados o a la cuadrícula de beats.
- Se impone la restricción de duración mínima de plano:
  $$\Delta t_{\text{clip}, j} = t_j^* - t_{j-1}^* \ge \tau_{\text{min}}, \quad \tau_{\text{min}} \ge 0.4\text{s}$$
- **Invariante de Continuidad:**
  $$t_j^{\text{end}} = t_{j+1}^{\text{start}} \quad \forall j \in [1, m-1]$$
  Garantizando ausencia estricta de huecos negros o fotogramas vacíos en la línea temporal.

---

## 3. Invariantes de Calidad y Blindaje

1. **Drift Absoluto Cero:** $|\text{cutTime} - \text{targetBeatTime}| \le 10^{-6}\text{s}$.
2. **Monotonía Estricta:** $t_0 < t_1 < t_2 < \dots < t_m$.
3. **Determinismo Idempotente:** La misma entrada de audio y clips genera exactamente el mismo hash SHA-256 del plan rítmico.
4. **Preservación de Metraje Bruto:** Los inPoints y outPoints no pueden exceder la duración real del archivo multimedia fuente disponible.
