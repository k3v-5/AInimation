# Documento de Diseño Técnico: Fase 25 — Multi-Aspect Ratio Adapter, Platform Audio Compliance & Social Delivery Packaging (v2.5.0)

## 1. Arquitectura del Adaptador y Empaquetador

```
                         ┌─────────────────────────────┐
                         │   Canonical Base IR (e.g. 9:16)│
                         └──────────────┬──────────────┘
                                        │
                         ┌──────────────▼──────────────┐
                         │    AspectRatioAdapter       │
                         │(LayoutReframer + SafeZones) │
                         └──────────────┬──────────────┘
                                        │
           ┌────────────────────────────┼────────────────────────────┐
           ▼                            ▼                            ▼
   [ Format: 9:16 ]             [ Format: 16:9 ]              [ Format: 1:1 ]
 (TikTok / Reels)            (YouTube Desktop / TV)       (Instagram / LinkedIn)
           │                            │                            │
           ├────────────────────────────┴────────────────────────────┤
           │
           ▼
 ┌──────────────────────────────┐
 │   Platform Audio Profiles    │
 │ (LoudnessNormalizer -14/-16) │
 └──────────────┬───────────────┘
                │
                ▼
 ┌──────────────────────────────┐
 │   ThumbnailSelector          │
 │ (Top 3 High-Impact Keyframes)│
 └──────────────┬───────────────┘
                │
                ▼
 ┌──────────────────────────────┐
 │   SocialDeliveryPackager     │
 │  (PlatformManifest.json)     │
 └──────────────────────────────┘
```

---

## 2. Contratos y Fórmulas Matemáticas

### 2.1 Mapeo y Reencuadre Espacial (`LayoutReframer`)
Dado un canvas base $(W_0, H_0)$ y un canvas objetivo $(W_1, H_1)$:
- $\text{Scale Factor (Fit): } S_{\text{fit}} = \min\left(\frac{W_1}{W_0}, \frac{H_1}{H_0}\right)$
- $\text{Scale Factor (Fill): } S_{\text{fill}} = \max\left(\frac{W_1}{W_0}, \frac{H_1}{H_0}\right)$
- $\text{Offset de Centrado: } \Delta X = \frac{W_1 - W_0 \cdot S}{2}, \quad \Delta Y = \frac{H_1 - H_0 \cdot S}{2}$
- Posición reescalada de elemento: $(X_1, Y_1) = (X_0 \cdot S + \Delta X, Y_0 \cdot S + \Delta Y)$.

### 2.2 Normalización de Sonoridad y Ganancia (`LoudnessNormalizer`)
$$\text{Gain (dB)} = \text{TargetLUFS} - \text{MeasuredLUFS}$$
$$\text{LinearMultiplier} = 10^{\frac{\text{Gain}}{20}}$$
$$\text{Sample}_{\text{norm}}(t) = \min\left(0.891, \text{Sample}(t) \cdot \text{LinearMultiplier}\right) \quad (\text{Limitado a } -1.0\text{ dBTP})$$

### 2.3 Selección de Miniaturas (`ThumbnailScorer`)
$$\text{ImpactScore}(t) = 0.4 \cdot \text{VisualDensity}(t) + 0.3 \cdot \text{ContrastRatio}(t) + 0.3 \cdot \text{TypographyVisibility}(t)$$

---

## 3. Jerarquía de Errores Tipados (`src/delivery/core/DeliveryErrors.ts`)
- `DeliveryError` (base)
- `UnsupportedAspectRatioError`
- `SafeZoneViolationError`
- `LoudnessOutOfRangeError`
- `ThumbnailExtractionError`
- `PackagingIntegrityError`
- `InvalidPlatformProfileError`
- `DeliveryManifestError`

---

## 4. Estrategia de Pruebas de 7 Capas
1. **Capa 1 (Modelos & AspectRatios):** Validación Zod de relaciones de aspecto estándar y plataformas.
2. **Capa 2 (AspectRatioAdapter & Reframer):** Reencuadres 9:16 $\to$ 16:9, 16:9 $\to$ 9:16, 9:16 $\to$ 1:1, 4:5 y 21:9.
3. **Capa 3 (SafeZone Compliance):** Verificación de márgenes seguros para UI de TikTok, Reels y Shorts.
4. **Capa 4 (Audio Compliance & True Peak):** Normalización exacta a -14, -16 y -23 LUFS con True Peak $\le -1.0\text{ dBTP}$.
5. **Capa 5 (Thumbnail Selector):** Extracción determinista de los mejores 3 frames ordenados por `ImpactScore`.
6. **Capa 6 (Property-Based Testing `fast-check`):** Invariantes de conservación de área y no-mutación de la IR base.
7. **Capa 7 (E2E & Benchmarks):** Empaquetado completo de 5 formatos simultáneos en $< 250\text{ms}$.
