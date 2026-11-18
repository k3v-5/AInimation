# Catálogo Modular de 90 Activos Arquitectónicos Oficiales y Hardware Táctico Expandido

## 1. Propósito y Alcance
Este subsistema define la arquitectura, parametrización y pipeline de generación procedural en Blender 5.2 LTS para el **Catálogo Completo de 90 Activos Arquitectónicos Modulares** de *Astra Hazard*, así como la suite expandida de **6 Sistemas de Hardware Táctico de Estación y Mando**. Resuelve la necesidad de dotar al entorno de juego de variedad visual a gran escala, modularidad geométrica estricta (grillas de 100cm, 400cm y 350cm de despeje vertical) y renderizado heroico de alta fidelidad basado en PBR estilizado con entintado Freestyle tipo novela gráfica de cómic.

---

## 2. Organización Modular de los 90 Activos

Para permitir trabajo concurrente de agentes y renderizado modular por lotes, los 90 activos se distribuyen en **3 Lotes Operativos de 30 activos cada uno** y **5 Kits Temáticos de 18 activos cada uno**:

### 2.1. Desglose por Lotes de Producción
- **Lote A (Activos 01 al 30): Estructuras Industriales y Boiserie Art Déco**
  - *Generador*: [`Art/Blender/generar_catalogo_modular_90_loteA.py`](file:///F:/Dev/Game/Art/Blender/generar_catalogo_modular_90_loteA.py)
  - *Escena 3D*: [`Art/Blender/Catalogo_Modular_90_LoteA.blend`](file:///F:/Dev/Game/Art/Blender/Catalogo_Modular_90_LoteA.blend)
  - *Render Oficial*: [`Art/Renders/Showcase_Catalogo_Modular_90_LoteA.png`](file:///F:/Dev/Game/Art/Renders/Showcase_Catalogo_Modular_90_LoteA.png)
  - *Activos 01-18 (Kit 1)*: Muros ciegos reforzados, portones de mamparo con junta de presión, suelos de rejilla antideslizante, vigas I-beam de techo, pasarelas con barandilla hazard, escaleras de gato, canalizaciones triples de fluidos, contenedor estándar TEU, trincheras de decantación ácida, compuertas blast de titanio, grúas puente de taller, columnas estructurales, louvers de ventilación forzada, bandejas de cableado trifásico, cámaras de esclusa cilíndricas, escotillas de suelo con volante, riostras diagonales y bolardos de advertencia.
  - *Activos 19-30 (Kit 2)*: Paneles boiserie de nogal noble, portales con arco de latón dorado, solados de mármol Carrara en damero, artesonados con molduras neoclásicas, columnas corintias con capitel foliado, sofás Chesterfield capitoné, sillones orejeros de cuero, balaustradas de hierro forjado y oro, lámparas araña de cristal, ojos de buey de gran formato, apliques tipo concha y vitrinas de caoba blindada.

- **Lote B (Activos 31 al 60): Mobiliario Palaciego, Refinería de Plasma y Cuarentena BioLab**
  - *Generador*: [`Art/Blender/generar_catalogo_modular_90_loteB.py`](file:///F:/Dev/Game/Art/Blender/generar_catalogo_modular_90_loteB.py)
  - *Escena 3D*: [`Art/Blender/Catalogo_Modular_90_LoteB.blend`](file:///F:/Dev/Game/Art/Blender/Catalogo_Modular_90_LoteB.blend)
  - *Render Oficial*: [`Art/Renders/Showcase_Catalogo_Modular_90_LoteB.png`](file:///F:/Dev/Game/Art/Renders/Showcase_Catalogo_Modular_90_LoteB.png)
  - *Activos 31-36 (Kit 2)*: Escaleras imperiales alfombradas, puertas de ascensor pillbox, consolas de tocador con cubierta de malaquita, biombos acústicos de latón repujado, barras de bar cocktail y pedestales para escultura.
  - *Activos 37-54 (Kit 3)*: Vasijas de confinamiento magnético para reactores de fusión, bobinas toroidales Tokamak, pilones de chispa Tesla, transformadores de pulso gigavatio, baterías de enfriamiento criogénico por nitrógeno líquido, racks de condensadores rápidos, conductos apantallados de plasma, vertederos de escoria iónica, toberas de enfoque magnético, turbocompresores de gas inerte, celdas electroquímicas de deuterio, pupitres de telemetría analógica, valvulería de diafragma electromagnético, bobinas solenoides axiales, conectores trifásicos reforzados, radiadores disipadores de cobre, barreras de arco interlock y racks de carga inductiva rápida.
  - *Activos 55-60 (Kit 4)*: Módulos de estasis criogénica vertical, cilindros de observación microbiológica con visor de borosilicato, arcos de descontaminación forzada por aspersión, esclusas de presión negativa, vitrinas de bioseguridad BSL-4 con guantes estancos y mesas de autopsia forense con desagüe perimetral.

- **Lote C (Activos 61 al 90): Bio-Análisis Avanzado, Hábitat de Tripulación y Puente de Mando**
  - *Generador*: [`Art/Blender/generar_catalogo_modular_90_loteC.py`](file:///F:/Dev/Game/Art/Blender/generar_catalogo_modular_90_loteC.py)
  - *Escena 3D*: [`Art/Blender/Catalogo_Modular_90_LoteC.blend`](file:///F:/Dev/Game/Art/Blender/Catalogo_Modular_90_LoteC.blend)
  - *Render Oficial*: [`Art/Renders/Showcase_Catalogo_Modular_90_LoteC.png`](file:///F:/Dev/Game/Art/Renders/Showcase_Catalogo_Modular_90_LoteC.png)
  - *Activos 61-72 (Kit 4)*: Centrífugas clínicas robotizadas, columnas de neutralización de gases halogenados, incineradores pirolíticos de riesgo biológico, mamparas de contención de cristal laminado, módulos de desinfección UV-C ambiental, cabinas de extracción de vapores pesados, estaciones de lavado ocular de emergencia, ultracongeladores criogénicos a -80°C, camas de intervención quirúrgica robotizada, dispensadores volumétricos automáticos de reactivos, brazos articulados de muestreo remoto y bordillos estancos de contención de vertidos tóxicos.
  - *Activos 73-90 (Kit 5)*: Módulos de descanso con literas abatibles, sintetizadores moleculares de alimentos y raciones, módulos sanitarios de vacío, casilleros estancos de efectos personales, mesas colectivas de oficiales, atriles de pilotaje orbital con esferas inerciales, mesas tácticas de proyección volumétrica, butacas pivotantes de mando con arneses de cuatro puntos, transceptores cuánticos de onda guiada, paneles de supervisión de sensores de radar de aproximación, tubos de inyección directa a cápsulas de salvamento, armeros de intervención pesada, bahías de recarga de trajes EVA, conductos registrables de mantenimiento técnico, depuradores de CO2 por zeolitas regenerativas, cúpulas geodésicas de observación astronómica, persianas balísticas de guillotina para mamparos y rampas mecánicas de estiba rápida de carga.

---

## 3. Hardware Táctico Expandido (6 Sistemas) - Pipeline Unreal Engine 5.8

El hardware táctico se expande a **6 dispositivos clave** implementados en [`Art/Blender/generar_hardware_tactico_expandido_oficial.py`](file:///F:/Dev/Game/Art/Blender/generar_hardware_tactico_expandido_oficial.py) con su render maestro [`Showcase_Hardware_Tactico_Expandido_Master.png`](file:///F:/Dev/Game/Art/Renders/Showcase_Hardware_Tactico_Expandido_Master.png). El pipeline completo de exportación FBX, ingesta Nanite, instanciación de Blueprints, showroom Lumen y validación automatizada en Unreal Engine 5.8 está 100% operativo:

### 3.1. Especificación Técnica de Activos y Contratos C++

| ID | Activo Static Mesh | Clase C++ Base | Blueprint Oficial | Dimensiones (X×Y×Z) | Propósito y Contrato Táctico |
|:---|:---|:---|:---|:---|:---|
| **HW01** | `SM_HW01_Stasis_Pod_Cryo` | `ATraumaKitCabinetActor` | `BP_HW01_Stasis_Pod_Cryo` | 1.60 × 1.70 × 2.80 m | Cámara criogénica presurizada con monitor ECG, soporte de perfusión y cúpula de cristal templado. Estabilización de signos vitales de supervivientes. |
| **HW02** | `SM_HW02_Holographic_Table_3D` | `AStationTerminalConsoleActor` | `BP_HW02_Holographic_Table_3D` | 2.66 × 2.66 × 1.80 m | Mesa de navegación táctica octogonal con proyector volumétrico holográfico para cartografía y control de purga forzada y aislamiento sectorial. |
| **HW03** | `SM_HW03_Wrist_PDA_Scanner` | `AStationTerminalConsoleActor` | `BP_HW03_Wrist_PDA_Scanner` | 0.60 × 1.02 × 1.02 m | Computadora táctica de muñeca y atril de diagnóstico biométrico con telemetría multigas (`FAstraScannerTelemetryData`), PPM y gradiente térmico. |
| **HW04** | `SM_HW04_Signal_Repeater_Station` | `AAstraSignalRepeaterActor` | `BP_HW04_Signal_Repeater_Station` | 1.14 × 1.28 × 2.46 m | Plataforma de radioenlace y retransmisión SOS de largo alcance (35m) con mástil telescópico, antena parabólica orientable y LED diegético. |
| **HW05** | `SM_HW05_Tactical_Drone_Dock_Station` | `AStationTerminalConsoleActor` | `BP_HW05_Tactical_Drone_Dock_Station` | 1.80 × 0.54 × 2.20 m | Bahía de acoplamiento vertical y recarga inductiva de drones de rescate/reconocimiento con diagnósticos de batería y enlace de telemetría. |
| **HW06** | `SM_HW06_Atmospheric_Purification_Pylon` | `ADecontaminationShowerActor` | `BP_HW06_Atmospheric_Purification_Pylon` | 1.20 × 1.20 × 2.28 m | Torre de purificación y filtrado de gases tóxicos con anillos iónicos de triple etapa, baliza estroboscópica y ciclos temporizados de descontaminación. |

### 3.2. Rutas del Pipeline en Disco y Content Browser
- **Escena Blender Maestra**: [`Art/Blender/Hardware_Tactico_Expandido_Oficial.blend`](file:///F:/Dev/Game/Art/Blender/Hardware_Tactico_Expandido_Oficial.blend)
- **Script Exportador FBX**: [`Art/Blender/exportar_6_hardware_tactico_fbx.py`](file:///F:/Dev/Game/Art/Blender/exportar_6_hardware_tactico_fbx.py)
- **Directorio FBX con Colisión UCX**: [`Art/FBX/Environment/Hardware/`](file:///F:/Dev/Game/Art/FBX/Environment/Hardware/)
- **Script Ingesta UE 5.8**: [`Scripts/importar_6_hardware_tactico_ue5.py`](file:///F:/Dev/Game/Scripts/importar_6_hardware_tactico_ue5.py)
- **Mallas e Intercambio PBR en Content**: `/Game/Meshes/Environment/Hardware/`
- **Script Creación Blueprints**: [`Scripts/crear_blueprints_hardware_ue5.py`](file:///F:/Dev/Game/Scripts/crear_blueprints_hardware_ue5.py)
- **Blueprints en Content**: `/Game/Blueprints/Environment/Hardware/`
- **Script Construcción Showroom**: [`Scripts/construir_gym_hardware_ue5.py`](file:///F:/Dev/Game/Scripts/construir_gym_hardware_ue5.py)
- **Nivel Showroom Interactivo**: [`Content/Maps/Gym_Hardware_Showcase.umap`](file:///F:/Dev/Game/Content/Maps/Gym_Hardware_Showcase.umap) (`/Game/Maps/Gym_Hardware_Showcase`)
- **Suite de Pruebas Automatizadas**: `AstraHazard.Environment.TacticalHardwareSuiteValidation` en [`Source/AstraHazard/Private/Tests/AstraCoreAutomationTests.cpp`](file:///F:/Dev/Game/Source/AstraHazard/Private/Tests/AstraCoreAutomationTests.cpp).

---

## 4. Pipeline Unreal Engine 5.8: Catálogo Modular de 90 Activos Oficiales

Los 90 activos arquitectónicos han sido completamente integrados a Unreal Engine 5.8 mediante un flujo de ingeniería automatizado, tipado estricto y desacoplamiento SOLID:

### 4.1. Clase C++ Base: `AAstraModularPieceActor`
- **Cabecera e Implementación**: [`Source/AstraHazard/Public/Environment/Modular/AstraModularPieceActor.h`](file:///F:/Dev/Game/Source/AstraHazard/Public/Environment/Modular/AstraModularPieceActor.h) y [`Source/AstraHazard/Private/Environment/Modular/AstraModularPieceActor.cpp`](file:///F:/Dev/Game/Source/AstraHazard/Private/Environment/Modular/AstraModularPieceActor.cpp).
- **Tipado Estricto (`EAstraModularKitType`)**:
  - `IndustrialDerelict` (K1: Activos 01 a 18): Muros 400x350, mamparos, rejillas de suelo, pasarelas, vigas I-beam.
  - `ArtDecoBoiserie` (K2: Activos 19 a 36): Boiserie nogal, mármol Carrara, columnas corintias, portales dorados, mobiliario.
  - `PlasmaRefinery` (K3: Activos 37 a 54): Reactores, anillos magnéticos, pilones Tesla, transformadores, radiadores.
  - `BioLabQuarantine` (K4: Activos 55 a 72): Cápsulas de estasis, cilindros de muestras, autoclaves, centrífugas, lavaojos.
  - `CrewHabitatCommand` (K5: Activos 73 a 90): Literas, sintetizadores, holomapas, timón de puente, armeros y cúpulas.
- **Componentes e Invariantes**:
  - `TObjectPtr<UStaticMeshComponent> ModularMeshComponent`: Raíz de simulación y colisión física con perfil `BlockAll`.
  - Validación Fail-Fast: `checkf(ModularMeshComponent != nullptr)` al inicializar y en `BeginPlay()`.
  - Snapping Métrico: `IsPositionAlignedToGrid()` y `SnapLocationToGrid()` con tolerancia submétrica para garantizar ensamblaje modular hermético en múltiplos de 100cm / 400cm y despeje vertical de 350cm.

### 4.2. Rutas del Pipeline en Disco y Content Browser
- **Escena Blender Maestra**: [`Art/Blender/Catalogo_Activos_Modulares_90_Oficial.blend`](file:///F:/Dev/Game/Art/Blender/Catalogo_Activos_Modulares_90_Oficial.blend)
- **Script Exportador FBX**: [`Art/Blender/exportar_90_activos_modulares_fbx.py`](file:///F:/Dev/Game/Art/Blender/exportar_90_activos_modulares_fbx.py) (centrado en $Z_{\text{base}} = 0$, colisiones convexas `UCX_` y mallas unificadas).
- **Directorio FBX**: [`Art/FBX/Environment/Modular/`](file:///F:/Dev/Game/Art/FBX/Environment/Modular/) (90 archivos `.fbx`).
- **Script Ingesta UE 5.8**: [`Scripts/importar_90_activos_modulares_ue5.py`](file:///F:/Dev/Game/Scripts/importar_90_activos_modulares_ue5.py).
- **Mallas e Intercambio PBR Nanite**: `/Game/Meshes/Environment/Modular/` (90 Static Meshes).
- **Script Creación Blueprints**: [`Scripts/crear_blueprints_modulares_ue5.py`](file:///F:/Dev/Game/Scripts/crear_blueprints_modulares_ue5.py).
- **Blueprints de Activos Modulares**: `/Game/Blueprints/Environment/Modular/` (`BP_SM_Mod_01_...` a `BP_SM_Mod_90_...`).
- **Script Construcción Showroom**: [`Scripts/construir_gym_modulares_ue5.py`](file:///F:/Dev/Game/Scripts/construir_gym_modulares_ue5.py).
- **Nivel Showroom Interactivo**: [`Content/Maps/Gym_ModularAssets_Showcase.umap`](file:///F:/Dev/Game/Content/Maps/Gym_ModularAssets_Showcase.umap) (`/Game/Maps/Gym_ModularAssets_Showcase`) distribuido en 5 grandes avenidas temáticas por Kit arquitectónico.
- **Suite de Pruebas Automatizadas**: `AstraHazard.Environment.ModularAssetsCatalogValidation` en [`Source/AstraHazard/Private/Tests/AstraCoreAutomationTests.cpp`](file:///F:/Dev/Game/Source/AstraHazard/Private/Tests/AstraCoreAutomationTests.cpp).

---

## 5. Razón de Diseño (Rationale) y Arquitectura de Código

1. **SOLID - Single Responsibility Principle (SRP):** Cada clase, script y nivel aísla responsabilidades. `AAstraModularPieceActor` se encarga exclusivamente de la lógica espacial y geométrica de ensamblaje modular, delegando la simulación de soporte vital o interactividad a subsistemas y actores dedicados.
2. **SOLID - Open/Closed Principle (OCP):** El diseño modular permite expandir los 5 kits temáticos o añadir nuevos estilos arquitectónicos sin alterar el contrato base de alineación y colisión.
3. **SOLID - Liskov Substitution Principle (LSP):** Cualquier pieza modular especializada puede sustituir a `AAstraModularPieceActor` en el mundo garantizando compatibilidad con el sistema de grid snapping y límites físicos.
4. **SOLID - Interface Segregation Principle (ISP):** Las piezas con interactividad implementan `IInteractableInterface` de forma aislada sin forzar sobrecargas en piezas puramente estructurales (muros, forjados, pilares).
5. **SOLID - Dependency Inversion Principle (DIP):** Los niveles y generadores procedurales dependen de la abstracción `AAstraModularPieceActor` y su componente genérico de malla, desacoplados de los uassets FBX concretos.
6. **Filosofía Fail-Fast y Prevención de Desalineaciones:** Validación rigurosa de punteros de componentes mediante `checkf()`, y validación matemática de grid bounds para evitar filtraciones de vacío o desalineaciones en la arquitectura de la estación espacial.

---

## 6. Renders e Infografías Maestras Verificadas
- Lámina Maestra de 90 Activos: [`Showcase_Catalogo_Modular_90_Master.png`](file:///F:/Dev/Game/Art/Renders/Showcase_Catalogo_Modular_90_Master.png)
- Lámina de Lote A (01-30): [`Showcase_Catalogo_Modular_90_LoteA.png`](file:///F:/Dev/Game/Art/Renders/Showcase_Catalogo_Modular_90_LoteA.png)
- Lámina de Lote B (31-60): [`Showcase_Catalogo_Modular_90_LoteB.png`](file:///F:/Dev/Game/Art/Renders/Showcase_Catalogo_Modular_90_LoteB.png)
- Lámina de Lote C (61-90): [`Showcase_Catalogo_Modular_90_LoteC.png`](file:///F:/Dev/Game/Art/Renders/Showcase_Catalogo_Modular_90_LoteC.png)
- Lámina de Hardware Táctico: [`Showcase_Hardware_Tactico_Expandido_Master.png`](file:///F:/Dev/Game/Art/Renders/Showcase_Hardware_Tactico_Expandido_Master.png)

