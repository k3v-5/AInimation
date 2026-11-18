# Especificación Técnica Maestra: Fase 25 — Multi-Aspect Ratio Adapter, Platform Audio Compliance & Social Delivery Packaging (v2.5.0)

## 0. Propósito y Principio Rector

La **Fase 25** extiende el motor audiovisual para convertir una composición canónica base en un **paquete de entrega multi-plataforma completo (Social Delivery Package)**, adaptando de forma determinista la relación de aspecto, el reencuadre de capas, las zonas seguras tipográficas, los perfiles de audio LUFS y la extracción de miniaturas de alto impacto.

$$\text{Canonical Base IR} \xrightarrow{\text{AspectRatioAdapter}} \{\text{9:16, 16:9, 1:1, 4:5}\} \xrightarrow{\text{AudioCompliance}} \xrightarrow{\text{Thumbnails}} \text{SocialDeliveryPackage}$$

---

## 1. Contratos y Dimensiones Estándar

| Relación de Aspecto | Resolución Estándar | Plataformas Principales | Estrategia de Reencuadre |
|---|---|---|---|
| `9:16` | $1080 \times 1920$ | TikTok, Instagram Reels, YouTube Shorts | Vertical Native / SafeZone Protected |
| `16:9` | $1920 \times 1080$ | YouTube Horizontal, TV, Desktop | Horizontal Scale + Smart Pan / Center |
| `1:1` | $1080 \times 1080$ | Instagram Feed Post, LinkedIn, Twitter/X | Square Crop / Centered Fit |
| `4:5` | $1080 \times 1350$ | Instagram Portrait Feed | Portrait Scale + Margin Adjustment |
| `21:9` | $2560 \times 1080$ | Ultrawide Cinematic | Cinematic Pillarbox / Expand |

---

## 2. Perfiles de Sonoridad por Plataforma (`PlatformAudioProfile`)

- **`youtube_horizontal` / `spotify`:** $-14.0\text{ LUFS} \pm 0.5$, $\text{True Peak} \le -1.0\text{ dBTP}$.
- **`tiktok` / `reels` / `shorts`:** $-16.0\text{ LUFS} \pm 0.5$, $\text{True Peak} \le -1.0\text{ dBTP}$.
- **`broadcast` (EBU R128):** $-23.0\text{ LUFS} \pm 0.5$, $\text{True Peak} \le -1.0\text{ dBTP}$.

---

## 3. Criterios de Aceptación y Definition of Done
1. El `AspectRatioAdapter` genera composiciones derivadas válidas para los 5 formatos sin mutar la composición base.
2. Los textos y subtítulos son reubicados automáticamente respetando los márgenes seguros de cada plataforma.
3. El `LoudnessNormalizer` aplica ganancias deterministas y limitación True Peak sin distorsión armónica.
4. El `ThumbnailSelector` extrae los 3 mejores fotogramas basados en densidad visual y visibilidad tipográfica.
5. El `SocialDeliveryPackager` genera un `PlatformManifest` serializable y verificable criptográficamente.
6. La suite completa de pruebas pasa al 100% en verde sin regresiones.
