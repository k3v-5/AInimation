# UAF-81: BACKLOG DE FASES PENDIENTES & HOJA DE RUTA ESTRATÉGICA

**Estado:** Documento de Planificación y Registro de Pendientes  
**Programa:** Universal Asset Factory (AOE / UAF)  
**Dependencias Previas Completadas:** UAF-81.0 → UAF-81.95 (100% verificado y certificado)  

Este documento registra formalmente las fases estratégicas identificadas y pendientes de ejecución para expandir la autonomía y profundidad del Universal Asset Framework en conjunción con Unreal Engine 5.

---

## 📋 Resumen del Backlog

| Fase | Título | Dominio Técnico | Prioridad / Estado |
| :--- | :--- | :--- | :--- |
| **UAF-81.93** | Dynamic Economy, Weapon Affixes & Procedural Loot Fabric | Progresión RPG, Loot Tables, Affixes, GAS & UE5 DataTables | ✅ **COMPLETADO & CERTIFICADO** |
| **UAF-81.94** | Procedural Interactive Audio, Spatial Acoustics & MetaSounds | Síntesis interactiva, Acústica $RT_{60}$, MetaSounds & Quartz | ✅ **COMPLETADO & CERTIFICADO** |
| **UAF-81.95** | Real-Time In-Engine Co-Piloting & Live Synchronization | WebSocket / gRPC LiveLink bidireccional AOE $\leftrightarrow$ UE5 | ✅ **COMPLETADO & CERTIFICADO** |
| **UAF-81.96** | Autonomous Gameplay Playtesting & AI QA Simulation | Agentes headless de QA, detección de softlocks y telemetría | ✅ **COMPLETADO & CERTIFICADO** |
| **UAF-81.97** | Procedural Cinematics, CineCamera Director & UE5 Sequencer | Encuadres dinámicos, Rule of Thirds, auto-DOF, LevelSequence | ✅ **COMPLETADO & CERTIFICADO** |
| **UAF-81.98** | Procedural Quest Graph, Branching Narrative & Dialogue Trees | Diálogos ramificados, skill checks, reputación y CommonUI | ✅ **COMPLETADO & CERTIFICADO** |
| **UAF-81.99** | Physics, Voronoi Fracturing & Chaos Destruction System | Fracturación Voronoi, UE5 Chaos GeometryCollection, escombros | ✅ **COMPLETADO & CERTIFICADO** |
| **UAF-81.100** | Volumetric Weather Cycles, Dynamic Day/Night & Atmosphere | Ciclos día/noche, SkyAtmosphere, niebla volumétrica y shaders | ✅ **COMPLETADO & CERTIFICADO** |
| **UAF-81.101** | Universal DCC & Engine Bridge Tools (UE5 & Blender) | Paleta Slate en UE5, Addon N-Panel Blender y Dispatcher | ✅ **COMPLETADO & CERTIFICADO** |
| **UAF-81.102** | One-Click Full Vertical Slice Builder (Macro-Orchestrator) | Pipeline unificado de nivel completo listo para jugar en UE5 | ✅ **COMPLETADO & CERTIFICADO** |

---

## 1. UAF-81.93: DYNAMIC ECONOMY, WEAPON AFFIXES & PROCEDURAL LOOT FABRIC

### 1.1 Misión y Objetivos
Construir el sistema de economía procedural, itemización y generación de armas/equipo con presupuesto matemático de daño y atributos, exportable a **Gameplay Ability System (GAS)** y Data Tables de Unreal Engine 5.

### 1.2 Componentes Arquitectónicos
1. **Presupuesto de Poder (Power Budget Math)**:
   - Cálculo determinista del DPS, cadencia de fuego, dispersión, retroceso y masa según el nivel del item ($L$) y su nivel de rareza ($R \in \{\text{Common, Uncommon, Rare, Epic, Legendary}\}$):
     $$\text{Budget}(L, R) = \text{BasePower} \cdot (1 + 0.12 \cdot L) \cdot \text{RarityMultiplier}(R)$$
2. **Generador de Afijos (Prefijos y Sufijos)**:
   - Modificadores aleatorios balanceados que alteran atributos (e.g., *Criogénico*, *Perforador de Blindaje*, *Recarga Rápida*).
   - Sinérgias elementales (Fuego, Electricidad, Veneno, Corrosión) con mitigación según armaduras de enemigos (UAF-81.92).
3. **Economía y Curvas de Inflación**:
   - Precios de compra/venta dinámicos vinculados a la escasez de suministros regulada por el Director de Ritmo (UAF-81.90).
   - Reciclaje de chatarra (*scrap conversion rate*).
4. **Exportación UE5**:
   - Exportación de `UDataTable` (CSV y JSON estructurados) listos para `FWeaponItemDefinition`.
   - Mapeo directo a `UGameplayEffect` y `UAttributeSet` para integración nativa con el **Gameplay Ability System (GAS)**.

---

## 2. UAF-81.94: PROCEDURAL INTERACTIVE AUDIO, SPATIAL ACOUSTICS & METASOUNDS

### 2.1 Misión y Objetivos
Completar el ciclo audiovisual dinámico del motor mediante generación y orquestación adaptativa de audio, acústica física de reverberación calculada sobre la topología de niveles y exportación de parches de **MetaSounds**.

### 2.2 Componentes Arquitectónicos
1. **Motor de Música Adaptativa por Capas (Stems)**:
   - Sincronización rítmica por compás y compases fraccionarios (reloj de cuantización Quartz).
   - Fundido cruzado de stems según la fase del `DynamicPacingDirector` (UAF-81.90): `CALM`, `BUILDUP`, `PEAK`, `COOLDOWN`.
2. **Propagación Acústica Espacial Topológica**:
   - Cálculo del tiempo de reverberación $RT_{60}$ basado en la fórmula de Sabine y Eyring sobre las dimensiones y materiales de las habitaciones de WFC:
     $$RT_{60} = \frac{0.161 \cdot V}{\sum S_i \alpha_i}$$
   - Oclusión de sonido a través de esquinas del grafo topológico y puertas cerradas (Lock-and-Key).
3. **Exportador UE5**:
   - Generación de grafos `.json` y presets para **MetaSounds Source Assets**.
   - Parámetros dinámicos expuestos (`StressIntensity`, `RoomVolume`, `OcclusionAlpha`).

---

## 3. UAF-81.95: REAL-TIME IN-ENGINE CO-PILOTING & LIVE SYNCHRONIZATION

### 3.1 Misión y Objetivos
Establecer un puente bidireccional continuo en tiempo real (vía WebSockets / gRPC) entre el orquestador headless de AOE/UAF y el editor activo de Unreal Engine 5.

### 3.2 Componentes Arquitectónicos
1. **Servidor y Cliente WebSocket/gRPC**:
   - `aoe-copilot-daemon`: Servicio ligero en segundo plano.
   - Integración con el plugin `UAFBridge` en UE5 para recibir comandos sin reiniciar ni pausar el editor.
2. **Edición Bidireccional en Vivo**:
   - Cambios de semillas o reglas en AOE actualizan el terreno y los spawners en el viewport de UE5 en menos de 500ms.
   - Movimiento de volúmenes o marcadores por el diseñador humano en UE5 se retroalimenta al grafo topológico de AOE.

---

## 4. UAF-81.96: AUTONOMOUS GAMEPLAY PLAYTESTING & AI QA SIMULATION

### 4.1 Misión y Objetivos
Validación autónoma del nivel y las mecánicas mediante agentes IA que juegan partidas completas en modo headless, detectando softlocks, picos de dificultad injustos o cuellos de botella de rendimiento.

### 4.2 Componentes Arquitectónicos
1. **Agente Simulador de Jugador (Headless QA Bot)**:
   - Simula movimiento, combate y resolución de puzzles (llaves y puertas de UAF-81.90).
   - Reporta caminos bloqueados o fallas de navegación.
2. **Telemetría y Mapas de Calor (Heatmaps)**:
   - Generación de mapas de calor de muertes de jugador, gasto de munición y tiempo por sala.
   - Feedback en bucle cerrado al `DynamicPacingDirector` para auto-calibración de la dificultad antes del empaquetado final.

---

## 5. UAF-81.97: PROCEDURAL CINEMATICS, CINECAMERA DIRECTOR & UE5 SEQUENCER

### 5.1 Misión y Objetivos
Generar secuencias cinemáticas in-engine y tomas dinámicas de cámara para hitos narrativos, introducciones de jefes, descubrimientos de salas WFC y cámaras de acción/combate.

### 5.2 Componentes Arquitectónicos
1. **Motor de Composición y Encuadre (`CinematicFramingEngine`)**:
   - Reglas de composición cinematográfica: regla de tercios, proporción áurea, encuadres *over-the-shoulder* y planos contraplano para diálogos.
2. **Planificador de Trayectorias de Cámara (`CameraTrajectorySolver`)**:
   - Curvas de spline continuas (Catmull-Rom) con prevención de colisiones contra mallas de salas WFC y orografía del terreno.
3. **Autofocus y Profundidad de Campo Dinámica (`AutoFocusDepthOfField`)**:
   - Control continuo de distancia focal y apertura de diafragma (*f-stop*) enfocando automáticamente al actor o amenaza de mayor relevancia táctica.
4. **Exportador UE5 Sequencer**:
   - Generación de assets `LevelSequence` nativos con tracks `MovieSceneCineCameraTrack`, canales de transformación y disparadores de eventos.

---

## 6. UAF-81.98: PROCEDURAL QUEST GRAPH, BRANCHING NARRATIVE & DIALOGUE TREES

### 6.1 Misión y Objetivos
Conectar el grafo de misiones de UAF-81.90 y el sistema de reputación de UAF-81.92 en un tejido narrativo procedural con ramificación de decisiones, árboles de diálogo interactivos y consecuencias de facción.

### 6.2 Componentes Arquitectónicos
1. **Grafo Narrativo Ramificado (`BranchingNarrativeDAG`)**:
   - Misiones primarias y contratos secundarios generados proceduralmente con bifurcaciones morales y resolución divergente.
2. **Compilador de Árboles de Diálogo (`DialogueTreeCompiler`)**:
   - Nodos de conversación con condiciones previas (*prerequisites*): nivel de reputación con la facción del NPC, ítems requeridos en inventario y tiradas de habilidad (*skill checks*).
3. **Registro de Banderas de Estado del Mundo (`WorldStateFlagRegistry`)**:
   - Seguimiento atómico de elecciones del jugador que alteran el comportamiento futuro de facciones e IA GOAP.
4. **Exportación UE5**:
   - Exportación a `UDataTable` compatibles con widgets de interfaz `CommonUI` y plugins estándar de diálogo.

---

## 7. UAF-81.99: PHYSICS, VORONOI FRACTURING & CHAOS DESTRUCTION SYSTEM

### 7.1 Misión y Objetivos
Transformar la geometría modular estática de WFC y props ambientales en componentes reactivos destruibles mediante fracturación física de Unreal Engine Chaos.

### 7.2 Componentes Arquitectónicos
1. **Generador de Fracturas Voronoi y Planares (`VoronoiFractureEngine`)**:
   - Pre-corte procedural de piezas modulares (paredes de hormigón, columnas, cristaleras) en racimos jerárquicos (macro-pedazos estructurales y micro-escombros).
2. **Compilador de GeometryCollection (`ChaosGeometryCollectionCompiler`)**:
   - Asignación matemática de umbríos de rotura (*DamageThresholds*), densidades de masa física y campos de anclaje (*Anchor Fields*) para evitar derrumbes irreales.
3. **Dispersión de Escombros y Polvo Reactivo (`DebrisFieldEmitter`)**:
   - Generación de capas de micro-escombros estáticos y emisores de partículas Niagara de polvo tras el colapso estructural.

---

## 8. UAF-81.100: VOLUMETRIC WEATHER CYCLES, DYNAMIC DAY/NIGHT & ATMOSPHERE

### 8.1 Misión y Objetivos
Integrar los biomas ecológicos de Whittaker (UAF-81.91) con la iluminación dinámica Lumen, niebla volumétrica y ciclos climáticos realistas en Unreal Engine 5.

### 8.2 Componentes Arquitectónicos
1. **Perfiles Atmosféricos por Bioma (`BiomeAtmosphereProfile`)**:
   - Parámetros de `SkyAtmosphere`, `ExponentialHeightFog` y capas de `VolumetricCloud` calibrados para cada bioma (ventiscas polares, calimas desérticas, nieblas densas de pantano, etc.).
2. **Controlador de Ciclo Día/Noche (`DayNightCycleController`)**:
   - Trayectoria celeste calculada con dispersión física de Rayleigh y Mie, iluminación lunar nocturna y curvas de exposición ocular adaptativa.
3. **Shader Layering Climático Procedural (`EnvironmentalShaderBlender`)**:
   - Capas de material blend (*vertex color* y máscaras de altitud/pendiente) que aplican acumulación de nieve cenital, efectos de charcos y humedad de lluvia sobre todas las superficies del nivel.
4. **Exportador UE5 (`UE5WeatherExporter`)**:
   - Exportación de manifiestos JSON, curvas flotantes para Sequencer y scripts de automatización Python para Unreal Engine 5.

### 8.3 Estado de Certificación y Verificación
- **Paquete:** `src/uaf/weather_atmosphere/`
- **Suite de Pruebas:** `tests/uaf/test_acceptance_uaf81_100.py` (16/16 tests PASS - 100%).
- **Certificación:** ✅ **COMPLETADO & CERTIFICADO** sin regresiones en el framework global.

---

## 9. UAF-81.101: UNIVERSAL DCC & ENGINE BRIDGE TOOLS (UE5 & BLENDER)

### 9.1 Misión y Objetivos
Proporcionar herramientas de control procedimental nativas, desacopladas y portables para Unreal Engine 5 y Blender, permitiendo a los diseñadores disparar e inspeccionar cualquier pipeline de generación de AOE directamente desde el viewport sin salir del motor.

### 9.2 Componentes Arquitectónicos
1. **Generador de Paleta para Unreal Engine 5 (`UE5StudioPaletteGenerator`)**:
   - Generación de scripts autónomos de Editor Utility / Slate (`aoe_ue5_palette.py`) integrables en el menú de ventana de cualquier proyecto de UE5.
   - Controles para Macro-Paisaje, WFC, Clima Lumen, Chaos Destruction y Audio MetaSounds con ejecución en-proceso o vía LiveLink.
2. **Generador de Panel N para Blender (`BlenderStudioPanelGenerator`)**:
   - Addon ligero (`aoe_blender_addon.py`) que añade la pestaña 'AOE Studio' al panel lateral 3D.
   - Operadores nativos para verificación de geometría manifold, alineación de pivote en origen y exportación FBX con convenciones de Unreal (Z-up, escala métrica).
3. **Despachador Central de Acciones (`StudioActionDispatcher`)**:
   - Enrutador desacoplado con validación estricta de rangos paramétricos y soporte para handlers procedimentales personalizados.

### 9.3 Estado de Certificación y Verificación
- **Paquete:** `src/uaf/engine_tools/`
- **Suite de Pruebas:** `tests/uaf/test_acceptance_uaf81_101.py` (16/16 tests PASS - 100%).
- **Certificación:** ✅ **COMPLETADO & CERTIFICADO** sin regresiones en el framework global.

---

## 10. UAF-81.102: ONE-CLICK FULL VERTICAL SLICE BUILDER (MACRO-ORCHESTRATOR)

### 10.1 Misión y Objetivos
Diseñar el macro-orquestador definitivo que une todos los subsistemas (paisaje, interior WFC, IA de combate, economía, audio, clima y compuertas de calidad) bajo una única invocación ejecutable de punta a punta.

### 10.2 Componentes Arquitectónicos
1. **Orquestador Maestro (`VerticalSliceMasterOrchestrator`)**:
   - Pipeline secuencial síncrono de 8 etapas: Macro-Landscape, Spatial Constraint Solver, WFC Modular Interior, Tactical AI Squads, Volumetric Weather, Chaos Voronoi Destruction, MetaSounds Audio y Autonomous QA Audit.
   - Generación determinista gobernada por `VerticalSliceConfig` y `SliceSize` (resoluciones de $64\times 64$ a $256\times 256$, tamaños WFC de $4\times 4$ a $12\times 12$).
2. **Solucionador de Restricciones Espaciales (`SpatialConstraintSolver`)**:
   - Algoritmo de detección de mesetas óptimas (`find_optimal_facility_plateau`), excavación/aplanamiento de cimientos con blend cosine (`carve_foundation_pad`) y orientación de esclusas frontales con carreteras conectadas.
3. **Empaquetador Maestro (`MasterPackageIntegrator`)**:
   - Serialización de paquetes portables con heightfields binarios `.r16` (16-bit little-endian), manifiestos por subsistema, archivos zip y script de automatización universal para Unreal Engine 5 (`import_full_vertical_slice.py`).
4. **Herramienta de Línea de Comandos (`slice_cli.py`)**:
   - Comando `aoe build-slice` con parámetros `--name`, `--size`, `--biome`, `--seed`, `--output-dir`, `--zip` y flags de bypass selectivo.

### 10.3 Estado de Certificación y Verificación
- **Paquetes:** `src/uaf/macro_orchestrator/`
- **Suite de Pruebas:** `tests/uaf/test_acceptance_uaf81_102.py` (16/16 tests PASS - 100%).
- **Certificación:** ✅ **COMPLETADO & CERTIFICADO**. Todos los objetivos de la hoja de ruta estratégica UAF-81 han sido completados al 100% sin regresiones.

