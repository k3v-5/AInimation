# UAF-81.89 — ADVANCED NEXT-GEN VFX, FLUID SIMULATION & ENVIRONMENTAL COUPLING SYSTEM

**Estado:** Fase normativa activa  
**Dependencias obligatorias:** UAF-81.84 Runtime VFX & Niagara Engine, UAF-81.85 Dynamic Lighting & Atmosphere, UAF-81.86 Profiling & Diagnostics, UAF-81.87 UE5 LiveLink Bridge, UAF-81.88 Golden Vertical Slice System.

---

# 1. OBJETIVO GENERAL

UAF-81.89 extiende el subsistema de efectos visuales de AOE/UAF incorporando capacidades de simulación física avanzada, interacción persistente con el entorno y compilación de shaders en tiempo real al nivel de motores de producción AAA como Unreal Engine 5.5 Niagara, Houdini Engine y Frostbite.

El sistema comprende:
1. **Solvers Fluidodinámicos Eulerianos 2D y 3D**: Simulación de fluidos incompresibles basada en Navier-Stokes con advección MacCormack/BFECC, flotabilidad térmica de Boussinesq, confinamiento de vorticidad y proyección de presión libre de divergencia (\(\nabla \cdot \mathbf{u} = 0\)).
2. **Muestreo de Geometría Viva y Fracturas**: Emisión de partículas sobre mallas esqueléticas animadas mediante Linear Blend Skinning (LBS), herencia de velocidad angular y tangencial de huesos, y acoplamiento directo con fracturas geométricas de Voronoi y Chaos Destruction.
3. **Interacción Persistente con Superficies y Follaje**: Render targets dinámicos para quemaduras con carbonización y enfriamiento, simulación de charcos con viscosidad y flujo gravitacional sobre pendientes (\(\mathbf{v} = \mathbf{g} - (\mathbf{g} \cdot \mathbf{n})\mathbf{n}\)), y buffer de deflexión elástica de vegetación ante ondas expansivas.
4. **Volumetría Avanzada con Auto-Sombreado y Particle Lights**: Integración de la ley de Beer-Lambert para Deep Shadow Maps internos en columnas densas de humo, y agrupamiento celular espacial de partículas incandescentes (Clustered Particle Lights) compatibles con los presupuestos de iluminación.
5. **Arcos Dieléctricos y Fenómenos Ópticos No Lineales**: Generación de relámpagos mediante el modelo de crecimiento laplaciano de Niemeyer-Pietronero-Wiesmann (árboles de Lichtenberg) con retorno de descarga ionizada, y buffer de refracción cromática radial para ondas de choque.
6. **Acoplamiento Espectral Audiovisual (Audio-Reactive VFX)**: Análisis espectral FFT en 6 bandas de frecuencia psicoacústicas modulando emisores a través de envolventes dinámicas ADSR.
7. **Memoria Struct-of-Arrays (SoA) y Compilación JIT a Compute Shaders**: Organización de datos de partículas en memoria contigua alineada para eficiencia de caché L1/L2 y compilador JIT del grafo de efectos a código HLSL para compute shaders GPU.
8. **Puente Avanzado con Unreal Engine 5 Niagara**: Mapeo directo a `UNiagaraDataInterfaceGrid3DCollection`, `UNiagaraDataInterfaceSkeletalMesh` y renderers de luces de partículas.

---

# 2. SUBFASES NORMATIVAS

## 81.89.0: Fundamentos Matemáticos, Topología MAC Grid y Seguridad Numérica
- Definición de grilla estalonada Marker-and-Cell (MAC):
  - Velocidades en las caras: \(u_{i+1/2, j, k}\), \(v_{i, j+1/2, k}\), \(w_{i, j, k+1/2}\).
  - Escalares en centros de celda: \(p_{i,j,k}\), \(\rho_{i,j,k}\), \(T_{i,j,k}\).
- Condición de estabilidad Courant-Friedrichs-Lewy (CFL):
  \[
  C = \frac{\max(|u|, |v|, |w|)\Delta t}{\Delta x} \le 1.0
  \]
  Subcycling automático cuando \(C > C_{max}\).
- Tipos de datos inmutables y sanitización de NaNs e infinitos.

## 81.89.1: Grillas Fluidodinámicas Eulerianas 2D/3D & Solvers Navier-Stokes
- Ecuaciones de Navier-Stokes incompresibles:
  \[
  \frac{\partial \mathbf{u}}{\partial t} + (\mathbf{u} \cdot \nabla)\mathbf{u} = -\frac{1}{\rho_0}\nabla p + \nu \nabla^2 \mathbf{u} + \mathbf{f}
  \]
  \[
  \nabla \cdot \mathbf{u} = 0
  \]
- Advección MacCormack con corrector BFECC y clamping por mínimos y máximos vecinos.
- Flotabilidad térmica: \(\mathbf{f}_{buoyancy} = \left(-\alpha \rho + \beta (T - T_{amb})\right) \mathbf{g}\).
- Confinamiento de vorticidad para preservar micro-remolinos: \(\mathbf{f}_{vort} = \epsilon_{vort} \Delta x (\boldsymbol{\eta} \times \boldsymbol{\omega})\).
- Solución del Poisson de presión con iteración Jacobi y soporte de celdas sólidas Neumann.
- Modelo de combustión acoplada de combustible, fuego y humo.

## 81.89.2: Muestreo de Geometría Viva y Fracturas
- Distribución uniforme sobre mallas triangulares mediante CDF de área superficial.
- Transformación por Linear Blend Skinning (LBS): \(\mathbf{v}' = \sum_b w_b \mathbf{M}_b \mathbf{v}\).
- Velocidad tangencial heredada: \(\mathbf{v} = \boldsymbol{\omega}_{bone} \times \mathbf{r} + \mathbf{v}_{bone}\).
- Acoplador de fracturas de Voronoi: emisión direccional orientada por normales de corte y centroides de escombros.

## 81.89.3: Superficies Persistentes y Follaje
- Buffer de impacto 2D: quemaduras con decaimiento térmico y carbonización.
- Simulación de charcos y viscosidad.
- Flujo de líquidos en pendientes: componente tangencial a la normal \(\mathbf{v}_{flow} = \mathbf{g} - (\mathbf{g} \cdot \mathbf{n})\mathbf{n}\).
- Grid de interacción de follaje: deflexión elástica de hojas y briznas de hierba ante ondas de viento.

## 81.89.4: Volumetría Avanzada, Auto-Sombreado y Particle Lights
- Ley de Beer-Lambert para transmitancia volumétrica: \(T(s) = \exp(-\sum_i \sigma_t \rho_i \Delta s)\).
- Deep Shadow Maps generados a partir de campos de densidad volumétrica.
- Agrupamiento de partículas emisoras en luces puntuales agrupadas (Clustered Particle Lights).

## 81.89.5: Arcos Dieléctricos y Fenómenos Ópticos No Lineales
- Crecimiento laplaciano de Lichtenberg con probabilidad proporcional al gradiente de potencial: \(P \propto (\Delta \phi)^\eta\).
- Descarga de retorno de alta luminosidad hacia conductores y tierra.
- Buffer de distorsión refractiva con dispersión cromática angular (\(n_{red} \ne n_{green} \ne n_{blue}\)).

## 81.89.6: Acoplamiento Espectral Audiovisual (Audio-Reactive VFX)
- Filtro en 6 bandas de frecuencia: Sub-Bass, Bass, Low-Mid, Mid, High, Air.
- Envolventes ADSR (Attack, Decay, Sustain, Release) analíticas para modular suavemente el comportamiento de los emisores.

## 81.89.7: Compilador JIT de Grafos a Compute Shaders & Optimización SoA
- Memoria Struct-of-Arrays (SoA) contigua para alineación SIMD y GPU.
- Compilador JIT a código HLSL para compute shaders con plegado de constantes y eliminación de código muerto.

## 81.89.8: Puente Avanzado con Niagara en UE5
- Mapeo hacia `UNiagaraDataInterfaceGrid3DCollection` y `UNiagaraDataInterfaceSkeletalMesh`.
- Exportación de parámetros de luces de partículas y shaders de refracción.

## 81.89.9: Suite de Aceptación y Certificación Golden
- 20+ pruebas unitarias e integradas con validación de estabilidad numérica, condición CFL, divergencia cero y no regresión.
