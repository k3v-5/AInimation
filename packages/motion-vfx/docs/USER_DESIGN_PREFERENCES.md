# 🎨 Guía de Estilo, Estándares Visuales y Gustos del Usuario
## Motion Graphics Engine & Adobe After Effects MCP

Este documento define las **reglas de oro estéticas, compositivas y tipográficas** que cualquier agente de IA o módulo generador debe seguir obligatoriamente para complacer el estándar de calidad visual del usuario.

---

## 🚫 1. Anti-Patrones Estrictamente Prohibidos (Lo que NO se debe hacer)

1. **PROHIBIDO el uso de fuentes Serif genéricas por defecto:**
   - Nunca permitir que After Effects recurra a `Times New Roman` o `Minion Pro`.
   - Se debe forzar explícitamente la fuente en el `Source Text` del script.

2. **PROHIBIDO el diseño de formas planas estilo "PowerPoint" / Wireframe:**
   - Nada de rectángulos y círculos sólidos de colores básicos primarios (amarillo chillón o cian plano sin gradiente ni desenfoque) con trazos gruesos desproporcionados.
   - Nada de composiciones rígidas donde todos los elementos están amontonados o desfasados del eje óptico.

3. **PROHIBIDO texto con alineación desfasada:**
   - Todo texto centrado debe usar obligatoriamente `textDoc.justification = ParagraphJustification.CENTER_JUSTIFY;`.
   - El punto de anclaje debe coincidir con el centro geométrico del elemento.

4. **PROHIBIDO renderizar sin Motion Blur:**
   - Las animaciones sin desenfoque de movimiento se ven baratas y robóticas.
   - Siempre activar `comp.motionBlur = true` y `layer.motionBlur = true`.

---

## 🏆 2. Estilo Maestro Preferido: Editorial Poster / High-Impact (TIME Style)

Este es el estilo visual **favorito y aprobado por el usuario** (inspirado en portadas icónicas, posters tipográficos y motion graphics editoriales de alto impacto):

```
┌─────────────────────────────────────────────────────────────┐
│                       ✦ CAPÍTULO 01 ✦                       │ ← Sub-tag de contexto
│                                                             │
│             ╔═════════════════════════════════╗             │
│             ║            EL ARTE              ║             │ ← Blanco Puro / Masivo
│             ╚═════════════════════════════════╝             │
│                                                             │
│       ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─       │
│      │        ( DIAL DE RELOJ / TICKS VECTORIALES )  │      │ ← Gráfico sutil en rotación
│      │                                               │      │
│      │                  DISFRUTAR                    │      │ ← ROJO CARMESÍ GIGANTE
│      │                                               │      │   (Ultra-condensado estirado)
│       ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─       │
│                                                             │
│             [ VIVE LA EXPERIENCIA // 2026 ]                 │ ← Badge de cierre
└─────────────────────────────────────────────────────────────┘
```

### 2.1 Tipografía y Escala Masiva
- **Fuentes aprobadas (Fallback list):**
  ```javascript
  var fonts = ["Impact", "Arial-Black", "Haettenschweiler", "Anton", "BebasNeue", "SegoeUI-Black", "Arial-BoldMT"];
  ```
- **Escala:** Tipografía gigante que ocupa entre el $70\%$ y el $95\%$ del ancho del canvas vertical ($1080\text{ px}$).
- **Proporción:** Estiramiento vertical intencional (`scale: [100, 120]` a `[100, 150]`) con **tracking negativo** ($-10$ a $-20$) para un aspecto compacto y contundente.
- **Paleta de Color de Alto Contraste:**
  - **Rojo Carmesí Neón Editorial:** `[1.0, 0.08, 0.14]` (`#FF1424`).
  - **Blanco Puro:** `[0.98, 0.98, 0.98]` (`#FAFAFA`).
  - **Negro Profundo / Slate:** `[0.03, 0.03, 0.05]` (`#08080D`).

### 2.2 Ritmo y Animación Palabra por Palabra (Word-by-Word Kinetic Pacing)
- En lugar de mostrar bloques largos de texto, las palabras deben entrar **secuencialmente al ritmo del habla**:
  - `EL ARTE` ($0.2\text{s} - 1.5\text{s}$)
  - `DE` ($1.5\text{s} - 2.2\text{s}$)
  - `DISFRUTAR` ($2.2\text{s} - 4.8\text{s}$) [Texto héroe masivo rojo]
  - `LOS` ($4.8\text{s} - 5.5\text{s}$)
  - `FESTIVALES` ($5.5\text{s} - 8.0\text{s}$) [Póster Slam final]
- **Física de Entrada:** Rebote elástico punchy (`inertiaBounce(0.04, 7.0, 4.0)` o snap zoom de escala $180\% \to 100\%$).

### 2.3 Elementos Gráficos de Acompañamiento
- **Diales y Marcas Horarias Minimalistas:** Anillos vectoriales ultrafinos ($2\text{ px}$) con marcas de reloj (*ticks* usando `Repeater` de 24 o 60 copias) rotando a baja velocidad (`time * 15`).
- **Etiquetas y Badges:** Formato `✦ SECCIÓN ✦` o `[ CATEGORÍA // AÑO ]` con interletraje expandido ($+25$ a $+40$).

---

## 💎 3. Segundo Estilo Aprobado: Minimal Luxury / Tech (Apple / Linear)

Para interfaces de producto, dashboards, métricas y SaaS:

1. **Fondo:** Graphite OLED / Dark Slate (`#08080C`) con resplandor ambiental suave al $35\%$.
2. **Tipografía:** `SegoeUI-Black` o `Arial-Black`, interletraje negativo, colores blanco y azul hielo eléctrico (`#00E5FF`).
3. **Glassmorphism:** Tarjetas oscuras con esquinas redondeadas ($32\text{ px}$ - $40\text{ px}$), relleno al $80\%$ de opacidad y borde fino resplandeciente ($1.5\text{ px}$).
4. **Botón CTA:** Cápsula alargada con esquinas completamente redondeadas (*pill shape*), micro-rebote al aparecer y pulso de respiración armónico.

---

## 🎥 4. Reglas de Integración sobre Video Real (.mp4 / .mov)

Cuando se superpongan gráficos sobre un video de fondo del usuario:
1. **Auto-Cover:** Escalar el video con `Math.max(scaleX, scaleY)` para garantizar $100\%$ de cobertura sin bandas negras.
2. **Viñeteado de Contraste Obligatorio:** Capa sólida oscura al $35\% - 45\%$ de opacidad colocada entre el video y los textos para garantizar legibilidad WCAG.
3. **Safe Zones Verticales:** Mantener los textos principales entre $Y = 320\text{ px}$ y $Y = 1580\text{ px}$ (dejando espacio libre para la interfaz de TikTok / Reels).

---

## 🎬 5. Catálogo Maestro de los 15 Presets de Creadores de YouTube y Estilos Profesionales

Todos estos motores residen en `src/styles/presets/` y están integrados de forma determinista en `StyleProfileManager`:

| # | Preset | Módulo Especializado | Referencia / Estilo Visual | Paleta Principal |
|---|---|---|---|---|
| **1** | `The Investigative Cartographer` | [`InvestigativeCartographerPreset`](file:///F:/Dev/after-effects-mcp/src/styles/presets/InvestigativeCartographerPreset.ts) | **Johnny Harris / Vox** — Mapas 3D topográficos, resaltadores analógicos (`Trim Paths` Multiply `#FFE500`), rutas discontinuas y recortes con chinchetas inerciales. | Amarillo `#FFE500`, Negro Tinta `#1A1A1A`, Rojo Conflicto `#E63946` |
| **2** | `Dark Noir Business Empire` | [`DarkNoirBusinessPreset`](file:///F:/Dev/after-effects-mcp/src/styles/presets/DarkNoirBusinessPreset.ts) | **MagnatesMedia / Neo** — 3D Photo Parallax Cutouts, destello anamórfico (`CC Light Sweep`), títulos dorados `Cinzel` y contadores de riqueza Ease-Out. | Oro Metálico `#D4AF37`, Negro Carbón `#0D0D0D`, Rojo Sangre `#9E1B1B` |
| **3** | `Scientific Blueprint & 3D Isometric` | [`ScientificBlueprintPreset`](file:///F:/Dev/after-effects-mcp/src/styles/presets/ScientificBlueprintPreset.ts) | **Veritasium / Kurzgesagt** — Cuadrícula milimétrica (`ADBE Grid`), cotas de medición vectorial animadas y fórmulas científicas. | Cyan Neón `#06B6D4`, Azul Pizarra `#0F172A`, Naranja Láser `#F97316` |
| **4** | `The Minimalist Cipher` | [`MinimalistCipherPreset`](file:///F:/Dev/after-effects-mcp/src/styles/presets/MinimalistCipherPreset.ts) | **Lemmino / ColdFusion** — Overlays de HUD de coordenadas GPS, escaneo láser vertical y tipografía delgada `DIN-Light`. | Azul Hielo `#38BDF8`, Verde Radar `#22C55E`, Negro `#000000` |
| **5** | `Productivity Papercraft` | [`ProductivityPapercraftPreset`](file:///F:/Dev/after-effects-mcp/src/styles/presets/ProductivityPapercraftPreset.ts) | **Ali Abdaal / Thomas Frank** — Tarjetas Notion flotantes con sombra suave y física de resorte $S(t) = 100(1 - e^{-8t}\cos(20t))$. | Amarillo Notion `#FEE68A`, Blanco Papel `#FAFAFA`, Grafito `#262626` |
| **6** | `High-End Agency & Luxury Monocromo` | [`AgencyLuxuryPreset`](file:///F:/Dev/after-effects-mcp/src/styles/presets/AgencyLuxuryPreset.ts) | **Iman Gadzhi** — Revista de alta moda, marcos de negativo 16mm/35mm con grano fotográfico y titulares `Bodoni MT`. | Blanco Puro `#FAFAFA`, Negro Puro `#050505`, Verde Esmeralda `#10B981` |
| **7** | `Hyper-Retention Beast` | [`HyperRetentionBeastPreset`](file:///F:/Dev/after-effects-mcp/src/styles/presets/HyperRetentionBeastPreset.ts) | **MrBeast / Ryan Trahan** — Títulos 3D gigantes con borde negro 14px y flechas con rebote sinusoidal $y(t) = y_0 + 20\sin(12t)$. | Amarillo Beast `#FACC15`, Rojo Beast `#EF4444`, Verde `#22C55E` |
| **8** | `Cashflow Direct-to-Camera` | [`HormoziCashflowPreset`](file:///F:/Dev/after-effects-mcp/src/styles/presets/HormoziCashflowPreset.ts) | **Alex Hormozi** — Subtítulos `The Bold Font` en cajas adaptativas split-box, palabras clave amarillo/verde y punch zooms súbitos. | Amarillo Neón `#EAB308`, Verde Dólar `#22C55E`, Blanco `#FFFFFF` |
| **9** | `True Crime & Cold Case Evidence` | [`TrueCrimeEvidencePreset`](file:///F:/Dev/after-effects-mcp/src/styles/presets/TrueCrimeEvidencePreset.ts) | **True Crime Documentaries** — Pizarra de corcho con fotos Polaroid, hilos rojos elásticos y sellos `CLASSIFIED` a $-12^\circ$. | Marrón Corcho `#5C402E`, Rojo Evidencia `#D91E1E`, Polaroid `#F0EDE6` |
| **10**| `Cinematic Flow Vlogging` | [`CinematicFlowVlogPreset`](file:///F:/Dev/after-effects-mcp/src/styles/presets/CinematicFlowVlogPreset.ts) | **Sam Kolder** — Transiciones orgánicas de máscara de cielo (*Sky Mask Feather 120px*), Teal & Orange y títulos 3D en el horizonte. | Teal Sombra `#0D5966`, Oro Cálido `#FAC066`, Blanco `#FFFFFF` |
| **11**| `SaaS & Tech Interface Showcase` | [`SaaSTechShowcasePreset`](file:///F:/Dev/after-effects-mcp/src/styles/presets/SaaSTechShowcasePreset.ts) | **Linear / Stripe SaaS** — Maquetas 3D con Glassmorphism, ondas expansivas de clic de ratón y degradados modernos. | Púrpura Stripe `#8B5CF6`, Azul `#3B82F6`, Pizarra `#1F293D` |
| **12**| `Wall Street Quantum Finance` | [`WallStreetFinancePreset`](file:///F:/Dev/after-effects-mcp/src/styles/presets/WallStreetFinancePreset.ts) | **Bloomberg / Trading Desk** — Velas japonesas animadas con mechas de sombra y tickers bursátiles con fluctuación de precios. | Verde Alcista `#10B981`, Rojo Bajista `#EF4444`, Deep Navy `#0A0F1A` |
| **13**| `Sports Energy & Fitness Adrenaline` | [`SportsEnergyPreset`](file:///F:/Dev/after-effects-mcp/src/styles/presets/SportsEnergyPreset.ts) | **Nike / Red Bull** — Cronómetros deportivos continuos de milisegundos (`MM:SS.ms`) y tipografía `Teko` ultra-pesada ($130\%$). | Amarillo Volt `#CCFF00`, Naranja Blaze `#FF5722`, Carbón `#141414` |
| **14**| `Retro Synthwave & Arcade 80s` | [`RetroSynthwavePreset`](file:///F:/Dev/after-effects-mcp/src/styles/presets/RetroSynthwavePreset.ts) | **Outrun / Synthwave** — Suelo 3D de rejilla en perspectiva ($X = 80^\circ$) hacia un sol retro animado con resplandor intenso. | Magenta Neón `#FF006E`, Cyan Eléctrico `#00F5FF`, Naranja Ocaso `#FF7300` |
| **15**| `The TIME Editorial News Poster` | [`TimeEditorialPosterPreset`](file:///F:/Dev/after-effects-mcp/src/styles/presets/TimeEditorialPosterPreset.ts) | **TIME Magazine (Estilo Insignia Maestro)** — Impact ultra-condensada estirada al $140\%$, marco rojo carmesí `#FF1424`, diales vectoriales y motion blur total. | Rojo Carmesí `#FF1424`, Blanco Puro `#FFFFFF`, Negro Carbón `#0A0A0A` |
