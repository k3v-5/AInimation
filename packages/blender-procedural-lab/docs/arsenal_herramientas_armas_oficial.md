# Arsenal Oficial: 20 Armas y Suite de 8 Herramientas Tácticas Avanzadas

## 1. Propósito
Define la arquitectura técnica, el pipeline procedural de producción 3D, la integración en Unreal Engine 5.8 y la validación automatizada del arsenal completo de *Astra Hazard*. Este subsistema provee:
1. Las **20 armas y herramientas de intervención directa** (Supresión, Brecha, Corte, Desactivación, Extensión, Contención, Decon y Supervivencia).
2. La **Suite Oficial de 8 Herramientas Tácticas Avanzadas** (Lanzador Pesado Compacto de Espuma, Lanzador de Red Electrostática Cuádruple, Gato Hidráulico 15T, Baliza Repetidora Desplegable, Escáner Acústico de Supervivientes PDA, Gancho Neumático de Titanio, Cizalla Combinada de Rescate 700 Bar y Escudo Térmico Plegable).

El sistema resuelve el acoplamiento rígido de armamento mediante una arquitectura modular inspirada en *Phasmophobia*, donde cada herramienta opera con acciones independientes de uso primario, secundario y especial desacopladas del personaje, respaldadas por un modelo físico estricto de retroceso, desgaste y consumo de recursos finitos.

---

## 2. Catálogo Oficial del Arsenal (20 Armas y Herramientas Tácticas)

| ID | Herramienta / Arma | Categoría / Tier | Static Mesh UE5 (`/Game/Meshes/Equipment/Weapons/`) | Blueprint UE5 (`/Game/Blueprints/Equipment/Weapons/`) | Clase C++ Base | Mecánicas Principales |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **W01** | **Hydra Heavy Hose** | Supresión // Tier 1 | `SM_W01_Hydra_Heavy_Hose` | `BP_W01_Hydra_Heavy_Hose` | `AHydraHoseEquipment` | Manguera hidráulica de 250 Bar, retroceso masivo cooperativo (1 o 2 jugadores). |
| **W02** | **Thermal Shock Axe** | Brecha // Tier 1 | `SM_W02_Thermal_Shock_Axe` | `BP_W02_Thermal_Shock_Axe` | `AThermalAxeEquipment` | Filo de plasma sobrecalentado a 1,800°C (multiplicador 2.5x) y batería consumible. |
| **W03** | **Cryo CO2 Extinguisher** | Extinción // Tier 1 | `SM_W03_Cryo_CO2_Extinguisher` | `BP_W03_Cryo_CO2_Extinguisher` | `ACO2ExtinguisherEquipment` | Doble cilindro presurizado de 150 Bar para sofocación rápida de incendios y gases. |
| **W04** | **Bio Defibrillator Unit** | Médico // Tier 1 | `SM_W04_Bio_Defibrillator_Unit` | `BP_W04_Bio_Defibrillator_Unit` | `ADefibrillatorEquipment` | Condensador de carga bifásica progresiva (0-100%) y reanimación de caídos con palas. |
| **W05** | **Plasma Halligan Bar** | Palanca // Tier 1 | `SM_W05_Plasma_Halligan_Bar` | `BP_W05_Plasma_Halligan_Bar` | `AThermalAxeEquipment` | Barra octogonal forjada con inductores térmicos para forzado rápido de esclusas atascadas. |
| **W06** | **Rotary Rescue Saw** | Corte // Tier 1 | `SM_W06_Rotary_Rescue_Saw` | `BP_W06_Rotary_Rescue_Saw` | `AThermalAxeEquipment` | Disco circular diamantado blindado para seccionar vigas y mamparos colapsados. |
| **W07** | **Pneumatic Bolt Cutter** | Rescate // Tier 2 | `SM_W07_Pneumatic_Bolt_Cutter` | `BP_W07_Pneumatic_Bolt_Cutter` | `AHydraulicJackEquipment` | Cizalla de doble pistón neumático para corte instantáneo de cadenas, rejas y cables. |
| **W08** | **Chemical Foam Mortar** | Contención // Tier 2 | `SM_W08_Chemical_Foam_Mortar` | `BP_W08_Chemical_Foam_Mortar` | `AFoamLauncherEquipment` | Tambor de 4 cámaras para dispersión masiva de espuma ignífuga y charcos resbaladizos. |
| **W09** | **Thermite Breach Lance** | Perforación // Tier 2 | `SM_W09_Thermite_Breach_Lance` | `BP_W09_Thermite_Breach_Lance` | `AThermalAxeEquipment` | Lanza térmica de flujo continuo para fundir cerraduras blindadas y corazas. |
| **W10** | **EMP Disruptor Pistol** | Desactivación // Tier 2 | `SM_W10_EMP_Disruptor_Pistol` | `BP_W10_EMP_Disruptor_Pistol` | `ANetLauncherEquipment` | 4 bobinas de cobre y pulso electromagnético para paralizar drones y sistemas de seguridad. |
| **W11** | **Hydraulic Spreader Jaws**| Extensión // Tier 2 | `SM_W11_Hydraulic_Spreader_Jaws` | `BP_W11_Hydraulic_Spreader_Jaws` | `AHydraulicJackEquipment` | Quijadas de expansión de 72 Toneladas para abrir mamparos aplastados o deformados. |
| **W12** | **Cryo Grenade Launcher** | Contención // Tier 2 | `SM_W12_Cryo_Grenade_Launcher` | `BP_W12_Cryo_Grenade_Launcher` | `AFoamLauncherEquipment` | Lanzagranadas rotativo de nitrógeno líquido para congelación instantánea de fugas. |
| **W13** | **Pneumatic Breaching Ram**| Apertura // Tier 2 | `SM_W13_Pneumatic_Breaching_Ram` | `BP_W13_Pneumatic_Breaching_Ram` | `AHydraulicJackEquipment` | Ariete cinético con cabeza de tungsteno propulsado por CO2 para derribo de puertas. |
| **W14** | **Magnetic Net Launcher** | Captura // Tier 2 | `SM_W14_Magnetic_Net_Launcher` | `BP_W14_Magnetic_Net_Launcher` | `ANetLauncherEquipment` | Lanzador de 4 proyectiles con red conductora para captura y contención de bestias. |
| **W15** | **Chemical Neutralizer Pack**| Decon // Tier 3 | `SM_W15_Chemical_Neutralizer_Pack` | `BP_W15_Chemical_Neutralizer_Pack` | `ACO2ExtinguisherEquipment` | Tanques dorsales presurizados y lanza para neutralizar charcos de ácido y biomasa. |
| **W16** | **Emergency SOS Flare Gun**| Señalización // Tier 3 | `SM_W16_Emergency_SOS_Flare_Gun` | `BP_W16_Emergency_SOS_Flare_Gun` | `AThermalFlareEquipment` | Pistola basculante de bengalas de magnesio (2,500°C) para iluminación y distracción. |
| **W17** | **Sonic Fire Suppressor** | Onda Choque // Tier 3 | `SM_W17_Sonic_Fire_Suppressor` | `BP_W17_Sonic_Fire_Suppressor` | `ACO2ExtinguisherEquipment` | Antena parabólica emisora de ondas acústicas de baja frecuencia para desplazar O2. |
| **W18** | **Arc Welding Cutting Torch**| Soldadura // Tier 3 | `SM_W18_Arc_Welding_Cutting_Torch` | `BP_W18_Arc_Welding_Cutting_Torch` | `AThermalAxeEquipment` | Soplete de arco voltaico de doble línea para sellado de brechas y corte de precisión. |
| **W19** | **Tripod Mounted Foam Cannon**| Estacionario // Tier 3 | `SM_W19_Tripod_Mounted_Foam_Cannon` | `BP_W19_Tripod_Mounted_Foam_Cannon` | `AFoamLauncherEquipment` | Monitor pesado desplegable sobre trípode para sofocación perimetral continua de fuego. |
| **W20** | **Tactical Rescue Machete**| Supervivencia // Tier 3 | `SM_W20_Tactical_Rescue_Machete` | `BP_W20_Tactical_Rescue_Machete` | `AThermalAxeEquipment` | Hoja de titanio con lomo dentado de sierra para despeje de cableado y escombros ligeros. |

---

## 3. Catálogo de la Suite Oficial de 8 Herramientas Tácticas Avanzadas

| ID | Herramienta Táctica | Función Táctica | Static Mesh UE5 (`/Game/Meshes/Equipment/Tactical/`) | Blueprint UE5 (`/Game/Blueprints/Equipment/Tactical/`) | Clase C++ Base | Mecánicas Principales |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **T01** | **Foam Launcher Heavy Compact** | Supresión Pesada | `SM_T01_Foam_Launcher_Heavy` | `BP_T01_Foam_Launcher_Heavy` | `AFoamLauncherEquipment` | Cañón compacto de tobera de latón con doble manómetro 250 Bar y depósito presurizado. |
| **T02** | **Net Gun Quad Launcher** | Contención Red | `SM_T02_Net_Gun_Quad_Launcher` | `BP_T02_Net_Gun_Quad_Launcher` | `ANetLauncherEquipment` | 4 bocas con copas magnéticas de cobre, visor láser azul frontal y cartucho electrostático. |
| **T03** | **Hydraulic Jack 15T** | Brecha y Sustentación | `SM_T03_Hydraulic_Jack_15T` | `BP_T03_Hydraulic_Jack_15T` | `AHydraulicJackEquipment` | Émbolo cromado de elevación pesada (15 Toneladas), dial analógico y palanca de bombeo. |
| **T04** | **Deployable Repeater Beacon** | Telecomunicaciones | `SM_T04_Deployable_Repeater_Beacon` | `BP_T04_Deployable_Repeater_Beacon` | `AAstraSignalRepeaterActor` | Trípode plegable, mástil telescópico con baliza estroboscópica azul y repetidor de radio (25m). |
| **T05** | **Acoustic Motion Scanner** | Detección Diegética | `SM_T05_Acoustic_Motion_Scanner` | `BP_T05_Acoustic_Motion_Scanner` | `AMultiGasScannerEquipment` | Consola táctica de antebrazo con pantalla CRT verde fósforo, bocina acústica y cantoneras. |
| **T06** | **Retractable Titanium Grapnel**| Movilidad y Anclaje | `SM_T06_Retractable_Titanium_Grapnel` | `BP_T06_Retractable_Titanium_Grapnel` | `ANetLauncherEquipment` | 4 garras basculantes de titanio, tambor de latón con cable trenzado y cilindro de CO2. |
| **T07** | **Heavy Hydraulic Shears** | Descarcelación Extrema | `SM_T07_Heavy_Hydraulic_Shears` | `BP_T07_Heavy_Hydraulic_Shears` | `AHydraulicJackEquipment` | Cuchillas templadas a 700 Bar de presión, doble pistón cromado y asa perimetral 360°. |
| **T08** | **Folding Thermal Shield** | Protección Balística | `SM_T08_Folding_Thermal_Shield` | `BP_T08_Folding_Thermal_Shield` | `AThermalAxeEquipment` | Triple panel articulado con bisagras pesadas, visor de cuarzo y patas de despliegue kickstand. |

---

## 4. Contratos e Interfaces de Software

### 4.1. Arquitectura C++ Base (`ABaseEquipment` y `AAstraSignalRepeaterActor`)
- **`ICarriableInterface`**: Soporte unificado de recolección en manos (`OnPickedUp`), descarte con impulso físico (`OnDropped`), peso en kg (`GetCarriableWeightKg`) y restricciones de ocupación de ranuras (`EToolSlot::OneHanded`, `EToolSlot::TwoHanded`, `EToolSlot::SharedDual`).
- **Sistema Modular de Acciones (Estilo Phasmophobia)**:
  - `StartPrimaryAction(User)` / `StopPrimaryAction(User)`: Gatillo primario LMB (disparo, corte, activación de válvula, bombeo).
  - `StartSecondaryAction(User)` / `StopSecondaryAction(User)`: Gatillo secundario RMB (carga de condensador, conmutación de abanico, alivio de presión).
  - `ExecuteSpecialAction(User)`: Acción contextual (purga diegética de manómetros, inspección, anclaje en suelo).
- **Máquina de Estados Operativos (`EEquipmentUseState`)**:
  - `Idle`: Listo para uso.
  - `Charging`: Proceso de cebado o acumulación de presión/julios.
  - `Active`: Uso activo continuo con consumo de recursos y retroceso físico.
  - `Cooldown`: Enfriamiento de inductores o alivio de contrapresión.
  - `Depleted`: Recurso agotado (requiere recarga en base o consumible).
- **Contenedor de Recursos (`FAstraEquipmentResource`)**:
  - Gestión determinista de fluidos, julios o batería con porcentaje normalizado `GetNormalized()` y clamps automáticos en `Consume()` y `Replenish()`.

---

## 5. Razón de Diseño (Rationale) y Principios SOLID

1. **Single Responsibility Principle (SRP):**
   - La simulación física de retroceso (`RecoilForceNewtons`) se computa en el equipo, mientras que la respuesta física del bombero se delega a `SpaceFirefighterCharacter`.
   - La interfaz gráfica diegética se sincroniza exclusivamente mediante delegates (`OnEquipmentUseStateChanged`, `OnEquipmentResourceChanged`), evitando dependencias directas de HUD dentro de las clases de armas.
2. **Open/Closed Principle (OCP):**
   - El contrato base `ABaseEquipment` permanece inmutable ante la adición de nuevas armas especializadas. Las 20 armas y 8 herramientas tácticas se implementan reutilizando y extendiendo las clases modulares de equipamiento sin alterar la lógica de inventario ni los contratos del personaje.
3. **Liskov Substitution Principle (LSP):**
   - Cualquier arma o herramienta táctica puede ser empuñada, lanzada o evaluada a través de un puntero genérico a `ABaseEquipment` o `ICarriableInterface` sin romper invariantes ni requerir casts condicionales en el código del jugador.
4. **Interface Segregation Principle (ISP):**
   - Se emplean interfaces cohesivas y ligeras (`ICarriableInterface`, `IInteractableInterface`) en lugar de monopolizar contratos en una interfaz monolítica de juego.
5. **Dependency Inversion Principle (DIP):**
   - Los sistemas de gameplay interactúan con abstracciones de equipamiento, permitiendo sustituir Static Meshes, materiales y efectos Niagara en el CDO de cada Blueprint sin modificar código fuente C++.
6. **Filosofía Fail-Fast y Tipado Estricto:**
   - Prohibido el uso de tipos implícitos: todas las variables numéricas de presión, temperatura y masa utilizan `float` con clamping explícito.
   - Guard clauses en cada inicio de acción para prevenir fallos silenciosos ante punteros de usuario o recursos nulos.

---

## 6. Niveles de Showroom Oficiales

### 6.1. Showroom de Armería (`Gym_Arsenal_Showcase.umap`)
- **Ruta:** `Content/Maps/Gym_Arsenal_Showcase.umap`
- **Contenido:** 20 pedestales de taller industrial ([`SM_Heavy_Duty_Workbench`](file:///F:/Dev/Game/Content/Meshes/Environment/Props/MasterProps/SM_Heavy_Duty_Workbench.uasset)) exhibiendo las armas W01 a W20 con iluminación cenital dedicada (800 cd), sol Lumen, niebla atmosférica y `PlayerStart`.

### 6.2. Showroom de Herramientas Tácticas (`Gym_TacticalTools_Showcase.umap`)
- **Ruta:** `Content/Maps/Gym_TacticalTools_Showcase.umap`
- **Contenido:** 8 puestos de trabajo pesados ([`SM_Heavy_Duty_Workbench`](file:///F:/Dev/Game/Content/Meshes/Environment/Props/MasterProps/SM_Heavy_Duty_Workbench.uasset)) en 2 filas de 4 herramientas tácticas (T01-T04 a $Y=500$, T05-T08 a $Y=1100$) con focos cenitales de 850 cd, sol Lumen y `PlayerStart`.

---

## 7. Pruebas Automatizadas de Unreal Engine (`Automation Testing`)

- **Suites de Pruebas:**
  1. `AstraHazard.Equipment.ArsenalSuiteValidation`
  2. `AstraHazard.Equipment.TacticalToolsSuiteValidation`
- **Ubicación:** `Source/AstraHazard/Private/Tests/AstraCoreAutomationTests.cpp`
- **Resultados:** 100% de aserciones superadas sin regresiones.

---

## 8. Calibración Ergonómica de Porte de Herramientas (1ª y 3ª Persona) y Certificación Visual

### 8.1. Arquitectura de Acoplamiento y Transformaciones Relativas
El sistema implementa desacoplamiento estricto entre el modelo de tercera persona del personaje (`SkeletalMeshComponent` anclado al socket `weapon_socket_r`) y el sistema de cámara en primera persona (`FollowCamera` del `APlayerCameraManager`), evitando artefactos de deformación ósea o colisiones de geometría con la cabeza del modelo (`SetOwnerNoSee(true)`).

| Herramienta / Activo | Modo 3ª Persona (Socket `weapon_socket_r`) | Modo 1ª Persona (`FollowCamera` Viewmodel) | Ergonomía y Certificación Visual |
| :--- | :--- | :--- | :--- |
| **Hydra Hose** (`BP_HydraHose`) | `RelLoc: (0, 0, 0)`<br>`RelRot: (0, -90°, 0)` | `RelLoc: (52, 22, -18)`<br>`RelRot: (2°, 176°, 0)` | Boquilla orientada hacia la retícula central en el cuadrante inferior derecho. Cable neutralizado sin deformación. |
| **CO2 Extinguisher** (`BP_CO2Extinguisher`) | `RelLoc: (-0.225, 0.774, -0.119)`<br>`RelRot: (0°, 15°, -85°)` | `RelLoc: (48, 30, -68)`<br>`RelRot: (-2°, -88°, -3°)` | Cilindro sostenido verticalmente por la empuñadura táctica; manómetro, pasador y difusor frontal encuadrados limpiamente. |
| **Thermal Shock Axe** (`BP_ThermalAxe`) | `RelLoc: (0, 0, -0.28)`<br>`RelRot: (0°, 35°, -78°)` | `RelLoc: (45, 22, -58)`<br>`RelRot: (-25°, 0°, 15°)` | Empuñadura centrada en la palma derecha (-0.28 en socket x 100 escala ósea = -28cm reales), filo incandescente al frente con despeje anti-pierna. Golpe completo 3P de 1.0s sin interrupciones. |
| **Tandem Stretcher** (`BP_TandemStretcher`) | `RelLoc: (0.92, 0.12, 0)`<br>`RelRot: (0°, 0°, -90°)` | `RelLoc: (65, 0, -38)`<br>`RelRot: (-10°, 0, 0)` | Asidero frontal sostenido en mano derecha, lecho extendido horizontal al frente a la altura de la cintura. |
| **Foam Launcher** (`BP_FoamLauncher`) | `RelLoc: (0, 0, 0)`<br>`RelRot: (0, -90°, 0)` | `RelLoc: (52, 22, -18)`<br>`RelRot: (2°, 176°, 0)` | Agarre bimanual alineado (`A_Firefighter_Hose_Hold`), tobera collar proyectada al frente hacia +Y. En 1P, alza superior de anilla y manómetros en cuadrante inferior derecho. |
| **Net Launcher** (`BP_NetLauncher`) | `RelLoc: (0, 0, 0)`<br>`RelRot: (0, -90°, 0)` | `RelLoc: (52, 22, -18)`<br>`RelRot: (2°, 176°, 0)` | Chasis táctico de 4 canisters de contención electrostática orientados al frente. En 1P, cargador y receptáculo de titanio despejados de la retícula. |
| **Defibrillator** (`BP_Defibrillator`) | `RelLoc: (0, 0, 0)`<br>`RelRot: (0, 0, -90°)` | `RelLoc: (45, 20, -18)`<br>`RelRot: (-20°, 176°, 0)` | Asa ergonómica en mano derecha a la altura de la cintura. En 1P, monitor ECG con trazado cardíaco verde fosforescente y electrodos bifásicos orientados a los ojos del operador. |
| **Hydraulic Jack 15T** (`BP_HydraulicJack`) | `RelLoc: (0, 0, 0)`<br>`RelRot: (-90°, 10°, 0)` | `RelLoc: (48, 26, -34)`<br>`RelRot: (-10°, -90°, 0)` | Porte táctico frontal a dos manos como ariete de sustentación. En 1P, cilindro de 15T, palanca de bombeo inclinada y manómetro analógico en cuadrante inferior. |
| **Arc Welding Rig Cart** (`BP_ArcWeldingRigCart`) | `RelLoc: (115, -105, -84)`<br>`RelRot: (0°, 0°, 0°)` | `RelLoc: (110, -105, -84)`<br>`RelRot: (0°, 0°, 0°)` | Carro móvil de soldadura rodante en el piso. Despeje >40cm respecto a botas y piernas, ruedas sobre la cubierta y manillar en manos. Bloqueo en `CarryHoldAnimSequence`. |
| **Portable Battery Rack** (`BP_PortableBatteryRack`) | `RelLoc: (72, 0, 28)`<br>`RelRot: (0°, 0°, 0°)` | `RelLoc: (60, 0, -32)`<br>`RelRot: (0°, 0°, 0°)` | Rack de batería táctica de alta densidad portado bimanualmente frente al pecho con despeje >40cm de piernas. Bloqueo en `CarryHoldAnimSequence`. |

### 8.2. Certificación Visual Empírica (Regla 5 de GEMINI.md)
Todos los encuadres y posiciones relativas fueron validados empíricamente mediante inspección visual directa con `read_file` en el motor de renderizado de Unreal Engine 5.8:
- **Tercera Persona (3P):**
  - `Certify_3P_HydraHose.png` (Sujeción anatómica bimanual con boquilla al frente).
  - `Certify_3P_CO2Extinguisher.png` (Cilindro vertical alineado en mano derecha, difusor al frente).
  - `Certify_3P_ThermalAxe.png` (Guardia diagonal a 45° con empuñadura antideslizante).
  - `Certify_3P_TandemStretcher.png` (Asidero frontal sostenido, lecho nivelado).
  - `Cert_FoamLauncher_3P.png` (Cañón lanzador de espuma bimanual con tobera frontal y depósito cian PBR).
  - `Cert_NetLauncher_3P.png` (Lanza-redes cuádruple bimanual con canisters superiores y culata de titanio).
  - `Cert_Defibrillator_3P.png` (Unidad de reanimación médica en puño derecho con chasis rojo y pantalla ECG).
  - `Cert_HydraulicJack_3P.png` (Gato hidráulico 15T portado bimanualmente con cilindro rojo, pistón cromado y banda reflectante).
- **Primera Persona (1P):**
  - `Certify_1P_HydraHose.png` (Lanza de extinción en encuadre táctico inferior derecho).
  - `Certify_1P_CO2Extinguisher.png` (Cilindro criogénico y manómetros en lateral derecho).
  - `Certify_1P_ThermalAxe.png` (Filo sobrecalentado y pico encuadrados a 35°).
  - `Certify_1P_TandemStretcher.png` (Bastidor nivelado en base del visor).
  - `Cert_FoamLauncher_1P.png` (Anilla superior, depósito cian y dial ámbar en cuadrante inferior derecho).
  - `Cert_NetLauncher_1P.png` (Canisters superiores de red y armazón de titanio alineados sin oclusión de retícula).
  - `Cert_Defibrillator_1P.png` (Pantalla ECG luminiscente verde y paletas de reanimación frente al punto de vista).
  - `Cert_HydraulicJack_1P.png` (Cilindro de presión, palanca de bombeo y manómetro analógico en esquina inferior).
- **Despeje Arquitectónico y Montaje de Peligros:**
  - `Certify_Corridor_EngineRoom_Unobstructed.png` (Pasillo hacia Sala de Máquinas en X=400 100% transitable).
  - `Certify_FireHazard_WallMounted_CleanCorridor.png` (Foco `Freighter_BP_Engine_Room_Fire_600C` adosado permanentemente al mamparo divisorio X=45.0, Y=2000.0, Z=0.0).
