# 💡 Calibración de Iluminación, Shaders PBR y Control Visual en Vivo (DarX)

Este documento detalla la arquitectura de iluminación, la calibración de emisivos LED en los Master Materials PBR, la configuración de la cámara en primera persona y los controles en tiempo real del menú de Desarrollo.

---

## 1. El Problema de la Iluminación en Espacios Cerrados Cúbicos
En Unreal Engine 5 con Lumen:
1. **Peligro de Exposición Manual en Cero (`AEM_Manual`)**: Si un mapa interior procedural no cuenta con miles de lúmenes de sol exterior o luces puntuales artificiales, la exposición manual fija en $0.0\text{ EV}$ renderiza la escena en **oscuridad absoluta ($0\text{ lux}$ / pantalla en negro)**.
2. **Peligro de Emisivos Hiper-Saturados**: Si los shaders asignan valores de `Emissive > 5.0` (por ejemplo $15.0 - 18.0$) en combinación con el Bloom predeterminado de UE5, se genera una **niebla blanca cegadora (*glow wash*)** que oculta el arma, la retícula y la geometría de la sala.

---

## 2. Solución Arquitectónica Aplicada

### A. Auto-Exposición Adaptativa de la Cámara (`AEM_Histogram`)
La cámara principal del jugador (`FirstPersonCameraComponent` en `ADarxProyectCharacter`) utiliza un histograma adaptativo con rango calibrado:
- `AutoExposureMethod = EAutoExposureMethod::AEM_Histogram;`
- `AutoExposureMinBrightness = 0.05f;` (Permite ver en pasillos oscuros sin quemar blancos)
- `AutoExposureMaxBrightness = 4.0f;` (Evita deslumbramientos ante explosiones o destellos)
- `AutoExposureBias = +1.2f;` (Punto de partida nítido y legible)
- `BloomIntensity = 0.25f;` (Resplandor sutil sin desenfoque excesivo)
- `BloomThreshold = 0.80f;` (Solo emiten destello las fuentes de luz genuinas)

### B. Iluminación Táctica del Exo-Traje
En lugar de sembrar luces artificiales flotantes por los niveles, el propio traje del jugador incorpora su sistema de visión:
- **Linterna Táctica Frontal (`USpotLightComponent`)**: Cono de luz colimado de $2500\text{ lm}$, ángulo interior de $25^\circ$, exterior de $48^\circ$ y radio de $25\text{ m}$.
- **Luz de Relleno Ambiental (`UPointLightComponent`)**: Esfera de luz suave difusa de $400\text{ lm}$ y radio de $10\text{ m}$ que evita sombras negras duras en las esquinas.

---

## 3. Calibración de Master Materials PBR
Los 16 Master Materials de los biomas (`/Game/DarX/World/Biomas/` y `/Game/DarX/Characters/`) mantienen emisiones templadas:
- `M_Robo_Core`: Emissive `(0.75, 0.04, 0.02)` (Rojo reactor de energía).
- `M_Bio_Acid`: Emissive `(0.08, 0.80, 0.15)` (Verde bioluminiscente).
- `M_Quant_Neon`: Emissive `(0.00, 0.75, 0.90)` (Cian de resonancia cuántica).
- Todos los materiales cuentan con el flag `used_with_instanced_static_meshes = true` para renderizado masivo por GPU Nanite/ISM.

---

## 4. Panel de Calibración en Vivo en el Menú de Desarrollo
En el menú de pausa (`[ Esc ]` / `[ P ]` $\rightarrow$ **Desarrollo** $\rightarrow$ **💡 ILUMINACIÓN & LEDS**), se exponen controles interactivos en tiempo real:

1. **Brillo de LEDs y Emisivos**:
   - `[ 0.2x ]` `[ 0.5x ]` `[ 1.0x (Normal) ]` `[ 1.8x ]` `[ 3.0x ]` `[ 5.0x (Máximo) ]`
2. **Claridad y Exposición (EV Bias)**:
   - `[ -1.0 EV ]` `[ 0.0 EV ]` `[ +1.2 EV ]` `[ +2.5 EV ]` `[ +4.0 EV ]` `[ +6.0 EV ]`
3. **Resplandor / Bloom Intensity**:
   - `[ 0.00 ]` `[ 0.15 ]` `[ 0.25 ]` `[ 0.50 ]` `[ 1.00 ]` `[ 2.00 ]`
4. **Luz Táctica del Traje**:
   - Toggle interactivo `[ ENCENDIDA / APAGADA ]` y potencia `[ 800 lm ]` `[ 2500 lm ]` `[ 5000 lm ]` `[ 10000 lm ]`.
5. **Presets Rápidos**:
   - `[ 🌟 PRESET ÓPTIMO DARX ]`: Restaura la calibración recomendada con un solo clic.
   - `[ 💡 PRESET MÁXIMA CLARIDAD ]`: Activa alta visibilidad para testing.
