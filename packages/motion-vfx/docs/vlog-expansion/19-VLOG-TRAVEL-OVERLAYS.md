# Vlog Travel Overlays

**Archivo:** `19-VLOG-TRAVEL-OVERLAYS.md`  
**Versión:** `1.0.0`  
**Estado:** DRAFT TÉCNICO  
**Sistema:** Motor Audiovisual v3.4.0 + Vlog & Multilingual Expansion  
**Dependencias:** Documentos 1–18  
**Consumidores:** Timeline Engine, Typography Engine, Audio Engine, Multi-Aspect Reframing Engine, After Effects JSX Exporter, MCP Server  

---

## 1. Objetivo

Definir el sistema responsable de generar automáticamente gráficos y overlays visuales para vlogs de viaje, documentales, lifestyle, food vlogs, guías de ciudad, travel shorts, contenido geográfico y contenido multilingüe.

El módulo producirá elementos visuales deterministas y parametrizables:
- `Geo-Badge`
- `Time-Badge`
- `Location Card`
- `Route Map`
- `Animated Route`
- `Destination Marker`
- `Distance Badge`
- `Travel Progress`
- `Polaroid Freeze-Frame`
- `Photo Stack`
- `Chapter Card`
- `Establishing Location Card`

---

## 2. Principio Arquitectónico

Los overlays fluyen en etapas desacopladas:
$$\text{DATA} \longrightarrow \text{OVERLAY MODEL} \longrightarrow \text{LAYOUT ENGINE} \longrightarrow \text{STYLE ENGINE} \longrightarrow \text{TIMELINE EVENTS} \longrightarrow \text{AFTER EFFECTS JSX}$$
Prohibido generar código JSX directamente desde datos crudos.

---

## 3. Separación de Responsabilidades

- **Data Layer:** Ubicación, hora, fecha, coordenadas, distancia, duración, idioma y etiquetas.
- **Overlay Layer:** Selección de tipo de gráfico, momento de aparición, duración y contenido semántico.
- **Layout Layer:** Posicionamiento en pantalla, tamaño, márgenes de seguridad (*safe zones*), alineación y escala.
- **Style Layer:** Paleta cromática, familias tipográficas, sombras, bordes e iconografía.
- **Export Layer:** Compilación del modelo visual en scripts JSX nativos para After Effects.

---

## 4. Overlay Base Contract

```typescript
interface VlogOverlay {
  id: string;
  type: VlogOverlayType;
  start: number;
  end: number;
  zIndex: number;
  visible: boolean;
  stylePreset?: string;
  language?: LanguageCode;
  safeZonePolicy: SafeZonePolicy;
  animation: OverlayAnimation;
  metadata: Record<string, unknown>;
}
```

---

## 5. Overlay Types

```typescript
type VlogOverlayType =
  | "GEO_BADGE"
  | "TIME_BADGE"
  | "LOCATION_CARD"
  | "ROUTE_MAP"
  | "ROUTE_LINE"
  | "DESTINATION_MARKER"
  | "DISTANCE_BADGE"
  | "TRAVEL_PROGRESS"
  | "POLAROID_FREEZE"
  | "PHOTO_STACK"
  | "CHAPTER_CARD"
  | "ESTABLISHING_CARD";
```

---

## 6. Identidad Determinista

Identificadores estables y secuenciales:
$$\text{vlog\_overlay\_<type>\_<sequence>} \quad (\text{ejemplo: } \text{vlog\_overlay\_geo\_0042})$$

---

## 7. Geo-Badge

Tarjeta compacta de localización (ej. *📍 Guadalajara, Jalisco • 8:42 PM*).

---

## 8. GeoBadge Contract

```typescript
interface GeoBadgeData {
  city: string;
  state?: string;
  country?: string;
  latitude?: number;
  longitude?: number;
  localTime?: string;
  timezone?: string;
  icon?: string;
}
```

---

## 9. GeoBadge Display Policy

Políticas configurables: `CITY`, `CITY, STATE`, `CITY, COUNTRY`, `CITY, STATE • TIME`.

---

## 10. Never Hardcode Location Formatting

La composición textual se gobierna exclusivamente mediante `GeoBadgeFormatPolicy`.

---

## 11. GeoBadge Format Policy

```typescript
interface GeoBadgeFormatPolicy {
  includeCity: boolean;
  includeState: boolean;
  includeCountry: boolean;
  includeTime: boolean;
  includeDate: boolean;
  separator: string;
}
```

---

## 12. Default Format

$$\text{CITY, STATE • TIME} \quad (\text{según disponibilidad})$$

---

## 13. Missing Location Data

Omisión elegante de campos ausentes; prohibida la aparición de literales `undefined`, `null` o `NaN` en pantalla.

---

## 14. Coordinates

```typescript
interface Coordinates {
  latitude: number;
  longitude: number;
}
```

---

## 15. Coordinate Validation

$$-90.0 \le \text{latitude} \le +90.0, \quad -180.0 \le \text{longitude} \le +180.0$$

---

## 16. Invalid Coordinates

Coordenadas fuera de rango emiten `INVALID_COORDINATES` y se excluyen del motor cartográfico.

---

## 17. Timezone

La hora mostrada se deriva de la zona horaria geográfica explícita, nunca del reloj del sistema operativo anfitrión.

---

## 18. Time Formatting

```typescript
interface TimeFormatPolicy {
  hour12: boolean;
  showSeconds: boolean;
  locale: string;
}
```

---

## 19. Locale

Localización horaria adaptada a los 7 locales oficiales (`es-MX`, `es-ES`, `en-US`, `en-GB`, `pt-BR`, `fr-FR`, `de-DE`).

---

## 20. Time Badge

Gráfico de hora independiente (`8:42 PM` o `20:42`).

---

## 21. Location Card

Panel informativo extendido con ciudad, estado, país, fecha, hora y coordenadas GPS.

---

## 22. Location Card Layout

```
┌─────────────────────────────┐
│ 📍 GUADALAJARA               │
│ Jalisco, México              │
│ 20:42 • 01 SEP 2026          │
└─────────────────────────────┘
```

---

## 23. Location Card Animation

- Entrada: $\text{opacity } 0 \to 1, \; \text{translateX } -24\text{px} \to 0$
- Salida: $\text{opacity } 1 \to 0, \; \text{translateX } 0 \to -12\text{px}$

---

## 24. Default Animation

$$0.30\text{ s entrada} \longrightarrow \text{Hold dinámico} \longrightarrow 0.20\text{ s salida}$$

---

## 25. Route Map

Representación de trayectoria cinemática entre Punto A y Punto B.

---

## 26. Route Map Contract

```typescript
interface RouteMapData {
  origin: MapPoint;
  destination: MapPoint;
  intermediatePoints?: MapPoint[];
  routeStyle: RouteStyle;
  showLabels: boolean;
  showDistance: boolean;
}
```

---

## 27. Map Point

```typescript
interface MapPoint {
  id: string;
  latitude: number;
  longitude: number;
  label?: LocalizedString;
}
```

---

## 28. LocalizedString

```typescript
type LocalizedString = Record<LanguageCode, string>;
```

---

## 29. Route Style

```typescript
interface RouteStyle {
  lineColor: string;
  lineWidth: number;
  markerColor: string;
  markerRadius: number;
  glow: boolean;
  glowRadius?: number;
  dashed?: boolean;
}
```

---

## 30. Default Route Style

- Línea: `#FFFFFF`, ancho $4\text{ px}$
- Marcador: `#FF1424` (rojo carmesí), radio $10\text{ px}$
- Resplandor: `glow = true`

---

## 31. Map Projection

```typescript
interface MapProjection {
  project(point: Coordinates): Vector2;
  unproject(point: Vector2): Coordinates;
}
```

---

## 32. No Projection Hardcoding

El trazado cartográfico está desacoplado del algoritmo de proyección matemática.

---

## 33. Default Projection

Proyección conforme de Mercator para vistas regionales estándar.

---

## 34. Route Line

Animación progresiva de vector mediante Trim Paths ($0\% \to 100\%$).

---

## 35. Route Animation

Propiedad continua $p \in [0.0, 1.0]$.

---

## 36. Route Animation Duration

$$\text{duration} = 1.20\text{ s} \quad (\text{configurable})$$

---

## 37. Route Animation Easing

Curva estándar `easeInOut`.

---

## 38. Destination Marker

Aparición con micro-rebote cinemático: $\text{scale } 0.0 \to 1.15 \to 1.0$.

---

## 39. Destination Pulse

Pulsación armónica de radio y opacidad en bucle suave.

---

## 40. Origin Marker

Marcador de salida en color blanco `#FFFFFF`.

---

## 41. Destination Marker

Marcador de llegada en carmesí `#FF1424`.

---

## 42. Distance Badge

Indicador de desplazamiento ($12.4\text{ km}$ o $7.7\text{ mi}$).

---

## 43. Distance Unit Policy

```typescript
type DistanceUnit =
  | "METRIC"
  | "IMPERIAL";
```

---

## 44. Distance Calculation

Fórmula geodésica de Haversine:
$$a = \sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta\lambda}{2}\right), \quad c = 2\operatorname{atan2}\left(\sqrt{a}, \sqrt{1-a}\right), \quad d = R \cdot c$$

---

## 45. Earth Radius

Radio volumétrico medio de la Tierra:
$$R = 6371.0088\text{ km}$$

---

## 46. Route Distance

Suma integral sobre puntos intermedios: $d = \sum d(p_i, p_{i+1})$.

---

## 47. Travel Progress

Barra de desplazamiento de viaje: $\text{GUADALAJARA} \text{ ---●--- } \text{CDMX}$ o $\text{42\% COMPLETO}$.

---

## 48. Travel Progress Contract

```typescript
interface TravelProgressData {
  progress: number;
  origin: LocalizedString;
  destination: LocalizedString;
}
```

---

## 49. Progress Validation

$$0.0 \le \text{progress} \le 1.0$$

---

## 50. Polaroid Freeze-Frame

Congelación de fotograma, marco blanco cinemático, sombra proyectada, ligera inclinación orgánica y efecto de sonido de obturador sincronizado.

---

## 51. Polaroid Contract

```typescript
interface PolaroidFreezeData {
  sourceClipId: string;
  sourceTime: number;
  duration: number;
  caption?: LocalizedString;
  rotation: number;
  scale: number;
  shadow: ShadowStyle;
  border: BorderStyle;
  playShutterSfx: boolean;
}
```

---

## 52. Freeze Frame Validation

$$\text{clipStart} \le \text{sourceTime} < \text{clipEnd}$$

---

## 53. Polaroid Rotation

Inclinación aleatoria seeded:
$$\theta \in [-3^\circ, +3^\circ]$$

---

## 54. Randomness

Rotaciones y desfases regidos por semilla determinista (`seed`).

---

## 55. Polaroid Shadow

```typescript
interface ShadowStyle {
  color: string;
  opacity: number;
  blur: number;
  offsetX: number;
  offsetY: number;
}
```

---

## 56. Polaroid Border

```typescript
interface BorderStyle {
  color: string;
  width: number;
  bottomExtra: number;
}
```

---

## 57. Caption

Rótulo centrado en la franja inferior blanca del marco.

---

## 58. Caption Localization

Soporte de textos multilingües mediante `LocalizedString`.

---

## 59. Polaroid SFX

Disparo del audio `camera_shutter.wav` del banco de sonido local.

---

## 60. SFX Synchronization

Disparo del sonido al inicio exacto de la congelación ($\text{tolerancia } \pm 1\text{ frame}$).

---

## 61. Photo Stack

Composición de fotos apiladas simulando un mazo físico de capturas.

---

## 62. Photo Stack Limit

Máximo 5 imágenes simultáneas en el apilamiento.

---

## 63. Stack Offset

Desplazamiento incremental por foto: $\Delta x = 16\text{ px}, \; \Delta y = 12\text{ px}, \; \Delta\theta = \text{offset determinista}$.

---

## 64. No Collision

Verificación de que el apilamiento no invada zonas seguras ni áreas de subtítulo.

---

## 65. Chapter Card

Tarjeta de inicio de capítulo o bloque temático (`01 CENTRO HISTÓRICO`).

---

## 66. Chapter Card Contract

```typescript
interface ChapterCardData {
  number: number;
  title: LocalizedString;
  subtitle?: LocalizedString;
}
```

---

## 67. Chapter Number

Formateo numérico a dos dígitos (`01`, `02`, `03`).

---

## 68. Chapter Title

Procesado por el `Typography Engine` existente para kerning y jerarquía visual.

---

## 69. Establishing Card

Placa tipográfica mayor para presentación de nueva ciudad o región.

---

## 70. Overlay Safe Zones

Todo overlay respeta la directiva `SafeZonePolicy`.

---

## 71. SafeZonePolicy

```typescript
interface SafeZonePolicy {
  top: number;
  right: number;
  bottom: number;
  left: number;
}
```

---

## 72. Social Safe Zones

Reserva de márgenes obligatorios para elementos UI en TikTok, Reels y Shorts en 9:16.

---

## 73. Aspect Ratio Adaptation

Renderizado adaptado a 16:9, 9:16, 1:1, 4:5 y 21:9.

---

## 74. Anchor Position

Posicionamiento declarativo: `TOP_LEFT`, `TOP_CENTER`, `TOP_RIGHT`, `CENTER`, `BOTTOM_LEFT`, `BOTTOM_CENTER`, `BOTTOM_RIGHT`.

---

## 75. Dynamic Anchor

Anclajes dinámicos: `FOLLOW_SAFE_ZONE`, `FOLLOW_FACE`, `FOLLOW_SPEAKER`, `FOLLOW_OBJECT`.

---

## 76. Geo-Badge Default Anchor

$$\text{anchor} = \text{BOTTOM\_LEFT}$$

---

## 77. Location Card Default Anchor

$$\text{anchor} = \text{TOP\_LEFT}$$

---

## 78. Route Map Default Anchor

$$\text{anchor} = \text{BOTTOM\_RIGHT}$$

---

## 79. Polaroid Default Anchor

$$\text{anchor} = \text{CENTER}$$

---

## 80. Overlay Collision

Detección de interferencias entre overlays, subtítulos, rostros y zonas seguras.

---

## 81. Collision Resolution

Prioridad estricta:
$$\text{Subtítulos} > \text{Overlays Críticos} > \text{Rostros Principales} > \text{Overlays Estándar} > \text{Elementos Decorativos}$$

---

## 82. Automatic Reposition

Desplazamiento elástico automático de elementos secundarios ante colisión.

---

## 83. Maximum Reposition

Desplazamiento acotado a un máximo del $10\%$ del ancho y alto del encuadre.

---

## 84. Collision Failure

Falta de espacio libre emite `OVERLAY_LAYOUT_CONFLICT`.

---

## 85. Typography

Todos los textos son procesados exclusivamente por el `Typography Engine` existente.

---

## 86. Font Fallback

Sustitución automática hacia fuentes alternativas compatibles ante caracteres no soportados.

---

## 87. Emoji

Soporte del glifo `📍` con reemplazo vectorial si el sistema de composición carece del emoji nativo.

---

## 88. Emoji Failure

Prohibida la aparición de caracteres de reemplazo corruptos (`□`, ``).

---

## 89. Animation Contract

```typescript
interface OverlayAnimation {
  inDuration: number;
  holdDuration?: number;
  outDuration: number;
  inEasing: EasingType;
  outEasing: EasingType;
}
```

---

## 90. Animation Defaults

$$\text{inDuration} = 0.30\text{ s}, \quad \text{outDuration} = 0.20\text{ s}$$

---

## 91. Overlay Lifetime

Permanencia en pantalla calculada para garantizar lectura confortable.

---

## 92. Minimum Read Time

Función dependiente de la longitud de caracteres y velocidad promedio de lectura.

---

## 93. Reading Speed

Cadencia base: $15\text{ caracteres / segundo}$ (configurable).

---

## 94. Multilingual Readability

Ajuste dinámico de duración según la densidad gráfica de cada idioma.

---

## 95. No Text Truncation

Prohibido truncar silenciosamente topónimos o nombres de capítulo.

---

## 96. Long Text Strategy

$$\text{Salto de línea} \longrightarrow \text{Reducción de tracking} \longrightarrow \text{Escalado de fuente} \longrightarrow \text{Ampliación de caja} \longrightarrow \text{Reubicación}$$

---

## 97. Maximum Font Reduction

Reducción máxima de tipografía de hasta un $15\%$ sin override.

---

## 98. Color Accessibility

Verificación de contraste visual entre texto y fondo.

---

## 99. Contrast Failure

Contraste insuficiente emite `LOW_CONTRAST_WARNING`.

---

## 100. Background Treatment

Fondos configurables: `solid`, `gradient`, `blur`, `glass`, `shadow`, `outline`.

---

## 101. Glass Background

Parámetros desacoplados de opacidad, desenfoque de fondo (*backdrop blur*), borde y sombra.

---

## 102. Dark Background

Fondo oscuro estándar: `rgba(0, 0, 0, 0.65)`.

---

## 103. Light Background

Fondo claro estándar: `rgba(255, 255, 255, 0.90)`.

---

## 104. Style Preset Integration

Herencia tipográfica y cromática de presets maestros (`TIME Editorial`, `Cinematic Travel`, `Johnny Harris`, `Vox`).

---

## 105. Override Hierarchy

$$\text{Global} \longrightarrow \text{Style Preset} \longrightarrow \text{Project} \longrightarrow \text{Overlay Type} \longrightarrow \text{Individual Overlay}$$

---

## 106. Data Validation

Validación formal del esquema de datos antes del ensamblado de capas.

---

## 107. Required Validation

Comprobación de `id`, `type`, `start`, `end`, `zIndex`, `safeZone`, `animation` y `metadata`.

---

## 108. Temporal Validation

$$\text{start} \ge 0, \quad \text{end} > \text{start}$$

---

## 109. Overlay Overlap

Solapamiento admitido entre overlays de diferente categoría funcional y capas z compatibles.

---

## 110. Z-Index

Jerarquía de capas recomendada:
- Video A-Roll: $0\text{ a }99$
- B-Roll: $100\text{ a }199$
- Overlays Gráficos: $200\text{ a }399$
- Subtítulos: $400\text{ a }499$
- UI Crítica: $500\text{ a }599$

---

## 111. Subtitle Priority

Los subtítulos se ubican siempre en planos visuales superiores a los overlays decorativos.

---

## 112. Export to After Effects

Generación de capas semánticas modulares (`[GEO] Background`, `[GEO] Icon`, `[GEO] City`, etc.).

---

## 113. Layer Naming

Formato determinista estricto:
$$\text{VLOG\_<TYPE>\_<ID>\_<COMPONENT>} \quad (\text{ejemplo: } \text{VLOG\_GEO\_vlog\_overlay\_geo\_0042\_CITY})$$

---

## 114. Match Names

Empleo obligatorio de Match Names universales (`ADBE Root Vectors Group`, `ADBE Text Document`) en el código JSX.

---

## 115. No UI-Name Dependency

Prohibida la dependencia de nombres de menú traducidos o cadenas dependientes del idioma de After Effects.

---

## 116. Geo-Badge AE Structure

```
GEO Badge
├── Background Shape
├── Location Icon
├── City Text
├── State Text
└── Time Text
```

---

## 117. Route Map AE Structure

```
Route Map
├── Map Background
├── Route Path
├── Origin Marker
├── Destination Marker
├── Labels
└── Distance
```

---

## 118. Polaroid AE Structure

```
Polaroid
├── Frozen Frame
├── White Frame
├── Shadow
├── Caption
└── Optional SFX
```

---

## 119. Shape Layers

Elementos vectoriales (marcos, líneas, fondos) implementados como Shape Layers nativas.

---

## 120. Raster Assets

Archivos rasterizados limitados a fotografías congeladas y texturas cartográficas.

---

## 121. Map Source

Compatibilidad con mapas base preexistentes en imagen local o composiciones vectoriales.

---

## 122. Offline Requirement

Generación de overlays 100% offline sin conectividad a servicios web.

---

## 123. Map Generation

Soporte para mapas estáticos, mapas procedimentales o cartografía importada localmente.

---

## 124. No API Requirement

La carencia de servicios cartográficos remotos no interrumpe la producción del overlay.

---

## 125. Missing Map

Sin imagen de mapa disponible, emisión en modo `ROUTE_MAP_DATA_ONLY` con trazado sobre fondo neutro.

---

## 126. Localized Labels

Traducción y localización dinámica de rótulos geográficos.

---

## 127. Language Fallback

$$\text{Locale solicitado} \longrightarrow \text{Idioma base} \longrightarrow \text{Idioma fuente} \longrightarrow \text{Valor original}$$

---

## 128. No Empty Labels

Etiquetas sin traducción disponible se ocultan limpiamente (`label.hidden = true`).

---

## 129. Date Localization

Formateo de fechas adecuado al locale lingüístico activo.

---

## 130. Number Localization

Separadores de miles y decimales adecuados a cada región.

---

## 131. Decimal Precision

Distancias $< 10\text{ km}$: 1 decimal; distancias $\ge 10\text{ km}$: sin decimales.

---

## 132. Currency

Código ISO, locale y valor almacenados en campos independientes.

---

## 133. Travel Metadata

```typescript
interface TravelMetadata {
  location?: GeoBadgeData;
  route?: RouteMapData;
  date?: string;
  localTime?: string;
  weather?: string;
  temperature?: number;
  distance?: number;
}
```

---

## 134. Weather

Campo meteorológico opcional desacoplado del núcleo obligatorio.

---

## 135. Overlay Trigger

Activación por marcadores manuales, guion, cambio de ciudad, etiqueta de B-roll o giro de capítulo.

---

## 136. Automatic Location Trigger

Detección de metadatos geográficos en un clip dispara la tarjeta Geo-Badge correspondiente.

---

## 137. Trigger Cooldown

Intervalo mínimo de enfriamiento entre badges consecutivos: $20.0\text{ s}$.

---

## 138. Significant Location Change

Disparo automático ante desplazamientos superiores al umbral o cambio de ciudad.

---

## 139. Default Location Threshold

$$\text{locationDeltaThreshold} = 5.0\text{ km}$$

---

## 140. Narrative Trigger

Mención verbal de un topónimo en la locución con confianza semántica $\ge 0.80$.

---

## 141. Confidence

$$\text{minimumTriggerConfidence} = 0.80$$

---

## 142. Duplicate Suppression

Supresión de tarjetas redundantes de la misma ubicación salvo prioridad `CRITICAL`.

---

## 143. Critical Location

Ubicaciones críticas se muestran obligatoriamente ignorando el cooldown temporal.

---

## 144. Overlay Analytics

Monitoreo de cantidad total de overlays, duraciones en pantalla y reubicaciones por colisión.

---

## 145. Debug Mode

Modo `DEBUG_OVERLAYS=true` para inspección visual de cajas de colisión y áreas seguras.

---

## 146. Debug Rendering

Los elementos de diagnóstico nunca se incluyen en el render final entregable.

---

## 147. Determinism

Entradas, metadatos y semillas idénticas producen un resultado visual exactamente reproducible.

---

## 148. No Hidden Randomness

Prohibido el uso de `Math.random()` sin semilla inicial (`seed`).

---

## 149. Error Codes

- `INVALID_COORDINATES`
- `INVALID_TIME_RANGE`
- `INVALID_ROUTE`
- `OVERLAY_LAYOUT_CONFLICT`
- `LOW_CONTRAST_WARNING`
- `GRAPHIC_TEXT_OVERFLOW`
- `MISSING_LOCALIZATION`
- `MISSING_MAP_SOURCE`
- `POLAROID_SOURCE_OUT_OF_RANGE`
- `INVALID_PROGRESS`

---

## 150. Warning vs Error

Las advertencias permiten proseguir; los errores de render detienen la etapa específica del overlay.

---

## 151. Unit Tests

Cobertura de formateo de badges, validación de coordenadas, cálculo de Haversine y anclajes seguros.

---

## 152. Property-Based Tests

Coordenadas aleatorias generan distancias positivas: $\text{distance} \ge 0$.

---

## 153. Property-Based Route Test

$$\text{routeDistance} \ge \text{straightLineDistance} - \epsilon$$

---

## 154. Property-Based Overlay Test

$$\text{end} > \text{start}$$

---

## 155. Property-Based Localization Test

Ausencia absoluta de textos corruptos (`undefined`, `null`, `NaN`) en los renders resultantes.

---

## 156. Aspect Ratio Tests

Pruebas en 16:9 ($1920\times1080$), 9:16 ($1080\times1920$), 1:1 ($1080\times1080$), 4:5 ($1080\times1350$) y 21:9 ($2560\times1080$).

---

## 157. Safe Zone Tests

Verificación estricta de que el bounding box del gráfico se aloja dentro de las zonas seguras activas.

---

## 158. Collision Tests

Validación de que los overlays estándar se desplazan o ceden el paso ante subtítulos principales.

---

## 159. After Effects Export Test

El JSX compilado se analiza y ejecuta creando capas y keyframes sin fallos de Match Name.

---

## 160. AE Spanish Test

Compatibilidad verificada sobre After Effects en español.

---

## 161. AE English Test

Compatibilidad verificada sobre After Effects en inglés.

---

## 162. Snapshot Tests

Comparación determinista mediante snapshots estructurados de los modelos de overlay.

---

## 163. Regression Fixture

Fixture de referencia `travel_overlays_reference` con 2 Geo-Badges, 1 Location Card, 1 Route Map, 1 Distance Badge, 1 Travel Progress, 2 Polaroids, 1 Chapter Card y 1 Establishing Card.

---

## 164. Multilingual Regression

Generación y validación del fixture en los 7 idiomas (`es-MX`, `es-ES`, `en-US`, `en-GB`, `pt-BR`, `fr-FR`, `de-DE`).

---

## 165. Expected Result

Estructura visual idéntica con textos, fechas y unidades geográficas correctamente localizadas.

---

## 166. Performance Requirement

Generación incremental ultrarrápida sin recalcular overlays no modificados.

---

## 167. Incremental Update

Editar el texto de un Geo-Badge no invalida el Route Map ni las Polaroids existentes.

---

## 168. Cache

Caché persistente de geometrías de ruta, distancias precalculadas y textos formateados.

---

## 169. Cache Key

$$\text{SHA-256}(\text{dataHash} + \text{language} + \text{preset} + \text{aspectRatio} + \text{safeZonePolicy} + \text{styleVersion})$$

---

## 170. MCP Tool

Exposición de la herramienta `create_vlog_overlay`.

---

## 171. MCP Input

```typescript
interface CreateVlogOverlayRequest {
  projectId: string;
  type: VlogOverlayType;
  start: number;
  end: number;
  language?: LanguageCode;
  data: Record<string, unknown>;
  stylePreset?: string;
  aspectRatio?: AspectRatio;
}
```

---

## 172. MCP Output

```typescript
interface CreateVlogOverlayResponse {
  overlayId: string;
  type: VlogOverlayType;
  start: number;
  end: number;
  warnings: string[];
}
```

---

## 173. MCP Batch

Soporte para operaciones agrupadas mediante `create_vlog_overlays_batch`.

---

## 174. DSL

Sintaxis declarativa de alto nivel:

```text
OVERLAY GEO_BADGE {
  location = "Guadalajara"
  state = "Jalisco"
  time = "20:42"
  start = 12.4
  duration = 3.2
}
```

---

## 175. Route DSL

```text
ROUTE {
  origin = A
  destination = B
  animate = true
  duration = 1.2
}
```

---

## 176. Polaroid DSL

```text
POLAROID {
  source = "clip_042"
  time = 18.24
  duration = 2.5
  shutter = true
}
```

---

## 177. Rendering Contract

El módulo entrega el modelo vectorial, eventos de línea temporal e instrucciones JSX al motor de render.

---

## 178. Integration Pipeline

```
Footage Metadata
        ↓
Narrative Analysis
        ↓
Travel Metadata
        ↓
VlogTravelOverlays
        ↓
Layout Engine
        ↓
Typography Engine
        ↓
Timeline Engine
        ↓
Audio/SFX Engine
        ↓
AE JSX Exporter
```

---

## 179. Atomicity

Los overlays compuestos se generan de forma atómica; el fallo de un componente esencial invalida el gráfico.

---

## 180. No Partial Silent Output

Prohibido emitir un Geo-Badge sin texto de ciudad y marcar la operación como completada.

---

## 181. Fallback

Fallo en componentes accesorios los suprime emitiendo advertencia sin abortar el overlay.

---

## 182. Accessibility

Contraste y tamaño de letra auditados para legibilidad en pantallas móviles reducidas.

---

## 183. Small-Screen Rule

En 9:16 se aplican tamaños mínimos de fuente y rigurosidad extrema en zonas seguras.

---

## 184. Shorts Optimization

En formatos verticales, rostros y subtítulos se priorizan sobre elementos gráficos secundarios.

---

## 185. Long-Form Optimization

En 16:9 se admite mayor densidad informativa y tarjetas compuestas.

---

## 186. Cinematic Travel Override

Preset con bandas letterbox, tipografía espaciada y transiciones sutiles.

---

## 187. Johnny Harris Override

Preset con énfasis cartográfico, etiquetas editoriales y texturas orgánicas.

---

## 188. Minimalist Override

Preset depurado sin sombras decorativas ni elementos accesorios.

---

## 189. Localization Safety

La localización de textos no altera coordenadas numéricas, identificadores ni timestamps.

---

## 190. Data/Text Separation

Separación de datos puros (`city: "Guadalajara"`) y representaciones textuales (`displayText`).

---

## 191. Source of Truth

La estructura de datos es la única fuente de verdad; el texto es una vista derivada.

---

## 192. No Parsing From Display Text

Prohibido deducir coordenadas o distancias a partir de cadenas de texto ya formateadas.

---

## 193. Final Validation

Validación formal de esquema, tiempos, safe zones, localización y compatibilidad JSX antes de exportar.

---

## 194. Definition of Done

- [ ] Geo-Badge
- [ ] Time-Badge
- [ ] Location Card
- [ ] Route Map
- [ ] Route Line
- [ ] Origin Marker
- [ ] Destination Marker
- [ ] Distance Badge
- [ ] Travel Progress
- [ ] Polaroid Freeze-Frame
- [ ] Photo Stack
- [ ] Chapter Card
- [ ] Establishing Card
- [ ] Localized text
- [ ] Localized dates
- [ ] Localized times
- [ ] Metric/imperial units
- [ ] Coordinate validation
- [ ] Haversine distance
- [ ] Route distance
- [ ] Map projection abstraction
- [ ] Safe zones
- [ ] Aspect ratio adaptation
- [ ] Collision detection
- [ ] Subtitle collision priority
- [ ] Face collision support
- [ ] Dynamic reposition
- [ ] Typography integration
- [ ] Animation system
- [ ] SFX integration
- [ ] Camera shutter synchronization
- [ ] Timeline integration
- [ ] AE JSX integration
- [ ] Spanish AE compatibility
- [ ] English AE compatibility
- [ ] Offline operation
- [ ] Determinism
- [ ] Seeded randomness
- [ ] Cache
- [ ] Incremental rebuild
- [ ] Unit tests
- [ ] Property-based tests
- [ ] Integration tests
- [ ] Regression fixtures
- [ ] Multilingual tests
- [ ] Aspect-ratio tests
- [ ] Safe-zone tests
- [ ] AE export tests
- [ ] MCP tool
- [ ] MCP batch tool
- [ ] DSL support
- [ ] Validation
- [ ] Error codes
- [ ] Warning system
- [ ] Debug mode

---

## 195. Estado Final del Documento

**Documento:** `19-VLOG-TRAVEL-OVERLAYS.md`  
**Versión:** `1.0.0`  
**Estado:** `DRAFT`  
**Implementación autorizada:** `NO`  

---

## 196. Regla de Implementación

Este documento define el contrato completo de los overlays de viaje. No deberá implementar dentro de este módulo traducción, TTS, clasificación de video, detección facial, geolocalización GPS, render final ni mapas remotos. Esos subsistemas entregan datos estructurados mediante contratos definidos.

---

## 197. Criterio de Integridad

El módulo será considerado incompleto si produce visualmente un overlay correcto pero:
- rompe safe zones;
- pierde localización;
- genera texto corrupto;
- desincroniza SFX;
- depende del idioma de After Effects;
- altera otros idiomas;
- produce resultados no deterministas;
- ignora conflictos de layout;
- genera datos geográficos inválidos.

La implementación solo se considerará concluida cuando todos los puntos del Definition of Done estén cubiertos y la suite de pruebas permanezca 100% en verde.
