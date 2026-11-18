# 🏆 Golden Project Specification: `GOLDEN-PROJECT-001`

El **Golden Project `GOLDEN-PROJECT-001`** es el juez supremo de certificación del sistema. Es un proyecto de prueba sintético y determinista diseñado para someter a estrés extremo todas las capacidades del motor simultáneamente.

---

## 📦 1. Composición del Proyecto Golden

```
GOLDEN-PROJECT-001/
├── Assets Requeridos:
│   ├── 20 clips de video de acción/paisajes (resoluciones mixtas 1080p, 4K; 24fps, 30fps, 60fps)
│   ├── 8 clips de concierto con iluminación estroboscópica y sujetos en escenario
│   ├── 2 clips con texto impreso/quemado para forzar Video OCR y evasión de colisión
│   ├── 1 pista maestra de audio multicanal WAV (PCM 16-bit 44.1kHz con transientes claros)
├── Estructuras de Producción:
│   ├── Pistas de video con Auto-Reframe (16:9 -> 9:16)
│   ├── Depth Layer Sandwich (texto 3D detrás del cantante)
│   ├── Rack Focus Transition (desenfoque progresivo de fondo)
│   ├── Subtitulado dinámico palabra por palabra (Word Karaoke Pop-In)
│   ├── Pistas de diseño de sonido (SFX Whooshes, Booms, Ticks) con Auto-Ducking (-3.5dB)
│   ├── Gradación de color cinemática (Hollywood Teal & Orange)
│   ├── Speed Ramping dinámico (3.0x -> 0.3x -> 2.5x)
│   ├── Safe Zones estrictas (TikTok, Reels, Shorts)
│   └── 3 Composiciones de salida simultáneas (9:16, 16:9, 1:1)
```

---

## 🔄 2. Ciclo de Ejecución E2E del Golden Test

El test automatizado ejecuta la secuencia completa sin intervención humana:

$$\text{BRIEF} \longrightarrow \text{ANALYZE} \longrightarrow \text{PLAN} \longrightarrow \text{DRY-RUN} \longrightarrow \text{VALIDATE} \longrightarrow \text{TRANSACTION} \longrightarrow \text{COMPILE} \longrightarrow \text{AE BRIDGE} \longrightarrow \text{RECONCILE} \longrightarrow \text{QA} \longrightarrow \text{AUTO-REPAIR} \longrightarrow \text{RENDER} \longrightarrow \text{EXPORT}$$

---

## 🎯 3. Criterios de Aceptación y Firmas Criptográficas

Para que `GOLDEN-PROJECT-001` sea marcado como **`PASS`**, el sistema debe verificar:

1. **`STRUCTURE PASS`:** El árbol jerárquico de composiciones y capas coincide exactamente con la firma esperada.
2. **`TIMING PASS`:** Cero discrepancias en puntos de entrada ($in$), salida ($out$) y keyframes ($\Delta t = 0$).
3. **`RECONCILIATION PASS`:** Las posiciones reales reportadas por After Effects coinciden con la IR con tolerancia $\epsilon \le 0.05\text{px}$.
4. **`VISUAL QA PASS`:** Score de QA $\ge 95.0\%$, cero fotogramas negros no intencionales, cero colisiones de texto.
5. **`AUDIO PASS`:** Envolvente de Auto-Ducking aplicada correctamente sin saturación ($< 0\text{dBFS}$).
6. **`OMNI-EXPORT PASS`:** Las 3 composiciones maestras (9:16, 16:9, 1:1) son creadas y exportables.
