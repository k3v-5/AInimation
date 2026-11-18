# 🗺️ TRAVEL OVERLAYS & GRAPHIC PRIMITIVES
## ESPECIFICACIÓN TÉCNICA DEL MÓDULO (v3.5.4)
**Documento:** `docs/vlog-expansion/12-TRAVEL-OVERLAYS.md`  
**Capa:** `v3.5.x Vlog Intelligence Layer`  
**Estado:** `FUENTE ÚNICA DE VERDAD (SSOT) — ESPECIFICACIÓN TÉCNICA`  
**Versión:** `1.0.0`  
**Fecha:** `2026-09-01`  

---

## 1. Propósito
Definir y generar primitivas gráficas declarativas de viaje (`GeoBadge`, `RouteMap`, `PolaroidFreeze`, `LocationCard`, `ChapterCard`) para inyectar elementos visuales contextuales en el montaje de vlog y compilarlos a código After Effects ExtendScript JSX con animación nativa.

## 2. Alcance
- Generación declarativa de `GeoBadge` (tarjeta flotante con ubicación y hora).
- Generación declarativa de `RouteMap` (trazado animado de ruta entre dos puntos geográficos).
- Generación declarativa de `PolaroidFreeze` (fotograma congelado con marco blanco, sombra y sonido de obturador).
- Generación declarativa de `ChapterCard` (tarjeta de separación de acto o capítulo).
- Soporte de Safe Zones para plataformas verticales (TikTok, Reels, Shorts) y horizontales (YouTube).

## 3. No Alcance
- No renderiza imágenes rasterizadas estáticas en disco; genera capas de formas vectoriales (`ShapeLayer`), sólidos y capas de texto dentro de After Effects.
- No utiliza JSX manual cableado; genera estructuras declarativas consumibles por el compilador.

## 4. Entradas
- `overlays: TravelOverlayInstance[]`: Lista de overlays declarativos solicitados.
- `compositionResolution: { width: number; height: number }`: Dimensiones (ej. $1080\times 1920$ o $1920\times 1080$).
- `safeZoneProfile?: string`: Perfil de zona segura.

## 5. Salidas
- `TravelOverlayRenderSpec[]`: Estructuras compilables listas para inyectar en el `ProjectIR` y After Effects JSX.

## 6. Interfaces
```typescript
export interface GeoBadgeOverlay {
  readonly type: "geo_badge";
  readonly id: string;
  readonly locationText: string;
  readonly timeText?: string;
  readonly startTimeSec: number;
  readonly durationSec: number;
  readonly position: "bottom-left" | "bottom-right" | "top-left" | "top-right";
  readonly accentColorHex?: string;
}

export interface RouteMapOverlay {
  readonly type: "route_map";
  readonly id: string;
  readonly origin: string;
  readonly destination: string;
  readonly startTimeSec: number;
  readonly durationSec: number;
  readonly lineProgressDurationSec: number;
}

export interface PolaroidFreezeOverlay {
  readonly type: "polaroid_freeze";
  readonly id: string;
  readonly freezeTimestampSec: number;
  readonly durationSec: number;
  readonly captionText?: string;
  readonly rotationDeg?: number;
  readonly playShutterSound: boolean;
}

export type TravelOverlayInstance =
  | GeoBadgeOverlay
  | RouteMapOverlay
  | PolaroidFreezeOverlay;
```

## 7. Configuración
```typescript
export interface TravelOverlayConfig {
  readonly defaultBadgeDurationSec: number;     // 3.50 s
  readonly defaultPolaroidDurationSec: number;  // 2.50 s
  readonly defaultRouteMapDurationSec: number;  // 4.00 s
  readonly defaultAccentColor: string;          // "#FF1424" (TIME Crimson)
  readonly defaultFontFamily: string;           // "Impact"
}

export const DEFAULT_TRAVEL_OVERLAY_CONFIG: TravelOverlayConfig = {
  defaultBadgeDurationSec: 3.50,
  defaultPolaroidDurationSec: 2.50,
  defaultRouteMapDurationSec: 4.00,
  defaultAccentColor: "#FF1424",
  defaultFontFamily: "Impact",
};
```

## 8. Algoritmo
1. **Validación de Intervalos:** Comprobar que `startTimeSec >= 0` y `durationSec > 0`.
2. **Cálculo de Safe Zone:** Posicionar el elemento dentro de los márgenes seguros según el aspecto (ej. $108\text{px}$ del borde inferior en 9:16).
3. **Generación de Capas Vectoriales:**
   - Para `GeoBadge`: Crear contenedor redondeado (*Rounded Rectangle*), icono de pin vectorial, texto de ciudad y texto de hora.
   - Para `PolaroidFreeze`: Duplicar fotograma fuente en `freezeTimestampSec`, añadir marco blanco con sombra proyectada (*Drop Shadow*) y rotación sutil ($-3^\circ$ a $+3^\circ$).
   - Para `RouteMap`: Crear línea de recorrido con modificador *Trim Paths* animado de $0\%$ a $100\%$.
4. **Sincronización de Foley SFX:** Si `playShutterSound === true`, inyectar evento `camera_shutter.wav` en el timeline de audio.
5. **Compilación JSX:** Emitir fragmento ExtendScript universal compatible con After Effects en Español e Inglés.

## 9. Reglas de Negocio
- **RN-TO01 (No Obstrucción):** Los overlays nunca deben tapar la zona de subtítulos dinámicos de la voz principal.
- **RN-TO02 (Motion Blur Obligatorio):** Todas las capas de movimiento creadas deben tener `motionBlur = true`.

## 10. Invariantes
- **INV-TO01:** $\forall O: O.\text{durationSec} > 0$.
- **INV-TO02:** Las coordenadas finales siempre respetan los límites de la composición.

## 11. Casos Normales
- Inserción de GeoBadge `📍 Guadalajara • 8:42 PM` en $t=1.0\text{s}$ durante 3.5s en la esquina inferior izquierda.

## 12. Casos Límite
- **Texto de Ubicación Muy Largo ("Aeropuerto Internacional de Guadalajara Miguel Hidalgo y Costilla"):** Auto-escalado de fuente tipográfica para no desbordar el ancho de la pantalla.

## 13. Errores
- `InvalidOverlaySpecError`: Parámetros incompletos o duración negativa.

## 14. Recuperación
- Degradación a posición centrada por defecto si la posición requerida colisiona con otra capa activa.

## 15. Determinismo
- 100% determinista: mismas propiedades producen el mismo código JSX idéntico.

## 16. Rendimiento
- Generación de especificaciones de overlays en $< 2\text{ms}$.

## 17. Dependencias
- `SoundBankManager` (para efectos de sonido de cámara), `types.ts`.

## 18. Compatibilidad
- Compatible con After Effects CC 2022, 2023, 2024 y 2025 en Español e Inglés.

## 19. Seguridad
- Escape riguroso de cadenas de texto inyectadas en capas de After Effects.

## 20. Tests
- Tests unitarios en `src/tests/automation/vlog/overlays/TravelOverlays.test.ts`.

## 21. Fixtures
- Ejemplos de GeoBadges, mapas de ruta y fotos Polaroid.

## 22. Golden Tests
- Snapshot de código JSX de overlays verificado.

## 23. Integración
- Integrado en `FinalVlogEditPlan` y compilado por `AfterEffectsJSXCompiler`.

## 24. Definition of Done
- Pruebas de overlays pasando al 100% con render JSX validado.
