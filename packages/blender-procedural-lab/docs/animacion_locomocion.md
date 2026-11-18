# Subsistema de Animación y Locomoción del Bombero Espacial
## Proyecto: Astra Hazard - Rescue Squad

---

## 1. Propósito y Alcance del Módulo

El subsistema de animación y locomoción proporciona la infraestructura técnica y artística para dotar de vida cinemática al bombero espacial (`ASpaceFirefighterCharacter`), garantizando transiciones suaves, dinámicas y realistas entre los estados esenciales de rescate espacial:

1. **Reposo y Alerta (`Idle`):** Respiración rítmica y micro-oscilación en gravedad estándar o baja con brazos relajados anatómicamente a los costados.
2. **Marcha Bipedal Desarmada (`Walk`):** Ciclo a velocidad media (240 cm/s) con balanceo pendular natural de brazos opuesto a las piernas y bamboleo pélvico.
3. **Carrera Atlética Desarmada (`Run`):** Avance rápido (480 cm/s) con bombeo rítmico de brazos (codos flexionados a 60°), inclinación frontal del torso y zancada extendida.
4. **Locomoción Táctica con Herramienta Monomanual (`Walk_1H`, `Run_1H`):** Porte táctico en el brazo derecho (empuñadura firme en guardia lateral con despeje libre de piernas >20 cm) y balanceo natural del brazo izquierdo para contrarrestar la inercia corporal.
5. **Locomoción con Equipo Bimanual (`Walk_2H`, `Run_2H`, `Hose_Hold`):** Agarre bimanual simultáneo del cañón/fusil táctico a la altura del pecho sin desfase articular.
6. **Transporte de Carga Pesada (`Carry_Hold`, `Carry_Walk`):** Porte bimanual frontal para carros de soldadura y racks de baterías con despeje absoluto de extremidades inferiores (>20 cm).
7. **Agachado y Exploración en Conductos (`Crouch_Idle`, `Crouch_Walk`):** Reducción de perfil por debajo de 1.0 metro de altura para transitar por conductos de ventilación modulares (`SM_VentDuct_Straight_100x100`).

---

## 2. Arquitectura C++: `USpaceFirefighterAnimInstance`

### 2.1 Archivos Fuente
- **Cabecera:** [`Source/AstraHazard/Public/Character/SpaceFirefighterAnimInstance.h`](file:///f:/Dev/Game/Source/AstraHazard/Public/Character/SpaceFirefighterAnimInstance.h)
- **Implementación:** [`Source/AstraHazard/Private/Character/SpaceFirefighterAnimInstance.cpp`](file:///f:/Dev/Game/Source/AstraHazard/Private/Character/SpaceFirefighterAnimInstance.cpp)

### 2.2 Responsabilidades y Ciclo de Vida
`USpaceFirefighterAnimInstance` hereda directamente de `UAnimInstance`. Actúa como puente optimizado entre el modelo de simulación física del actor (`ASpaceFirefighterCharacter`) y el grafo de animación (AnimGraph) de Unreal Engine 5.

- `NativeInitializeAnimation()`: Resuelve y cachea los punteros al personaje bombero (`FirefighterCharacter`) y su componente de movimiento (`MovementComponent`).
- `NativeUpdateAnimation(float DeltaSeconds)`: En cada tick del hilo de animación, extrae la velocidad lineal, aceleración, estado de caída, agachado, estado de físicas/ragdoll y estado del equipamiento actual acoplado a la mano.

### 2.4 Iluminación Táctica de Escafandra (`HelmetFlashlight`)
Para garantizar visibilidad inmersiva y diegética en cascos despresurizados y sin suministro eléctrico:
- `ASpaceFirefighterCharacter` incorpora un `USpotLightComponent` (`HelmetFlashlight`) acoplado directamente a la cámara de seguimiento `FollowCamera` (18,000 lm, 35m de alcance, temperatura de 6500K blanco frío).
- Se expone `ToggleHelmetFlashlight()` e `IsHelmetFlashlightOn()` para alternancia diegética por el usuario y los sistemas de pánico.

### 2.5 Métodos Estáticos Puros (Diseño Orientado a Pruebas)
Para cumplir con la filosofía de diseño desacoplado de `GEMINI.md`, toda la matemática cinemática se aísla en métodos estáticos puros y deterministas, evaluables sin depender de instancias vivas de mundo o render:

```cpp
/** Calcula la velocidad escalar en el plano XY ignorando Z */
UFUNCTION(BlueprintPure, Category = "Astra|Animation|Math")
static float CalculateGroundSpeed(const FVector& Velocity);

/** Calcula el ángulo de desplazamiento relativo a la orientación [-180, +180] */
UFUNCTION(BlueprintPure, Category = "Astra|Animation|Math")
static float CalculateMovementDirection(const FVector& Velocity, const FRotator& BaseRotation);

/** Evalúa si el personaje tiene aceleración activa de entrada */
UFUNCTION(BlueprintPure, Category = "Astra|Animation|Math")
static bool EvaluateIsAccelerating(const FVector& CurrentAcceleration);
```

### 2.4 Contrato de Variables Cinemáticas para el Grafo de Animación

| Variable | Tipo | Categoría | Propósito |
| :--- | :--- | :--- | :--- |
| `GroundSpeed` | `float` | Locomotion | Velocidad horizontal plana en cm/s para blend spaces (0 -> Walk 240 -> Run 480). |
| `MovementDirection` | `float` | Locomotion | Dirección de marcha relativa en grados [-180° a +180°] para strafing. |
| `bIsAccelerating` | `bool` | Locomotion | Detecta si el jugador presiona controles de desplazamiento analógico/teclas. |
| `bIsFalling` | `bool` | Locomotion | Detecta pérdida de contacto con suelo (saltos, pozos o despresurización). |
| `bIsCrouching` | `bool` | Locomotion | Activa transiciones hacia cuclillas y gateo para conductos de ventilación. |
| `bIsRagdollActive` | `bool` | Locomotion | Suprime animaciones estándar cuando el personaje es noqueado o entra en física activa. |
| `bHasEquippedTool` | `bool` | Equipment | Activa poses de empuñadura superior de herramientas y cañones. |
| `bIsFiringHose` | `bool` | Equipment | Activa la postura de contra-fuerza y microvibración por retroceso de la Hydra Mark-I. |
| `CurrentRescueState`| `EPlayerRescueState` | Equipment | Estado de rescate activo (`Normal`, `Carrying`, `Downed`, etc.). |
| `bIsCarrying` | `bool` | Equipment | Conmuta a locomoción con carga de camilla o víctima arrastrada. |

---

## 3. Pipeline Artístico y Generador de Animaciones (Blender 5.2)

### 3.1 Script de Generación
- **Ruta:** [`Art/Blender/generar_animaciones_locomocion_oficial.py`](file:///f:/Dev/Game/Art/Blender/generar_animaciones_locomocion_oficial.py)
- **Malla Base:** `SK_Firefighter_Official_Rigged.blend` (Esqueleto oficial de 21 huesos con jerarquía UE5 estándar).

### 3.2 Matriz de Estados de Animación Generados

```
+----------------------------------------------------------------------------------------------------+
|                         ASTRA HAZARD - POSE & LOCOMOTION MATRIX                                    |
+--------------------------+--------------------------+----------------------------------------------+
| 1. IDLE                  | 2. WALK                  | 3. RUN                                       |
|    60 frames (2.0s)      |    30 frames (1.0s)      |    24 frames (0.8s)                          |
|    Respiración torácica  |    Paso 240 cm/s         |    Carrera atlética 480 cm/s                 |
|    Micro-oscilación      |    Balanceo opuesto      |    Inclinación frontal 12°                   |
+--------------------------+--------------------------+----------------------------------------------+
| 4. CROUCH IDLE           | 5. CROUCH WALK           | 6. HOSE HOLD                                 |
|    60 frames (2.0s)      |    36 frames (1.2s)      |    60 frames (2.0s)                          |
|    Perfil < 1.0 m        |    Gateo en conducto     |    Agarre Hydra 2 manos                      |
|    Filtro SM_VentDuct    |    Shuffle en cuclillas  |    Micro-jitter retroceso                    |
+--------------------------+--------------------------+----------------------------------------------+
```

### 3.3 Corrección Cinemática de Extremidades Superiores (Erradicación de Brazos en A/T-Pose)
Para erradicar la postura con brazos extendidos hacia los lados en reposo y carrera (aspecto de "alas de avión"):
1. **Análisis de Rest Pose del Rig:**
   - En el esqueleto base `SK_Firefighter_Armature`, los huesos `upperarm_l` y `upperarm_r` nacen con un vector de reposo a 45° respecto a la columna torácica.
   - En rotaciones locales XYZ, una rotación positiva en Z en el brazo izquierdo (`upperarm_l`) y negativa en el derecho (`upperarm_r`) produce **aducción anatómica** hacia el torso.
2. **Postura de Reposo (`Idle`):**
   - Hombros y brazos caen relajados pegados a los costados del traje presurizado:
     * `upperarm_l`: `Euler((-14°, -5°, +24°))`
     * `upperarm_r`: `Euler((-14°, +5°, -24°))`
     * Codos sutilmente flexionados adelante: `lowerarm_l` a `+16°` Z, `lowerarm_r` a `-16°` Z.
3. **Cinemática de Carrera (`Run`):**
   - Bombeo atlético vigoroso en oposición rítmica a las piernas con codos a 75°-85°:
     * `upperarm_l`: `Euler((-s_l * 28° - 12°, -8°, +20°))`
     * `upperarm_r`: `Euler((-s_r * 28° - 12°, +8°, -20°))`
     * Codos flexionados adelante cerca de las costillas: `lowerarm_l` a `+55° + max(0, -s_l)*15°`, `lowerarm_r` a `-55° - max(0, -s_r)*15°`.
   - Se mantiene un despeje de 20° respecto al torso para evitar solapamiento con las placas de blindaje del pecho.
4. **Cinemática de Marcha (`Walk`):**
   - Oscilación cadenciosa moderada en oposición a los pasos:
     * `upperarm_l`: `Euler((-s_l * 16° - 12°, -6°, +22°))`
     * `upperarm_r`: `Euler((-s_r * 16° - 12°, +6°, -22°))`
5. **Agachado y Gateo (`Crouch_Idle` y `Crouch_Walk`):**
   - Extremidades replegadas y recogidas pegadas a las rodillas para permitir paso estricto por conductos de ventilación < 1m de altura.

### 3.4 Exportación FBX y Cargas
Cada animación se exporta de forma independiente con transformaciones locales normalizadas en `Art/FBX/Animations/`:
1. `A_Firefighter_Idle.fbx` (303 KB)
2. `A_Firefighter_Walk.fbx` (275 KB)
3. `A_Firefighter_Run.fbx` (263 KB)
4. `A_Firefighter_Crouch_Idle.fbx` (295 KB)
5. `A_Firefighter_Crouch_Walk.fbx` (270 KB)
6. `A_Firefighter_Hose_Hold.fbx` (291 KB)

---

## 4. Ingesta y Montaje en Unreal Engine 5.8

### 4.1 Script de Ingesta
- **Ruta:** [`Scripts/importar_animaciones_y_crear_abp.py`](file:///f:/Dev/Game/Scripts/importar_animaciones_y_crear_abp.py)
- **Ejecución:** Automatizada mediante `UnrealEditor-Cmd.exe` en modo batch.

### 4.2 Activos Generados en `/Game/Characters/`
- **Animation Blueprint:** `/Game/Characters/ABP_SpaceFirefighter`
  - **Clase Padre:** `USpaceFirefighterAnimInstance`
  - **Skeleton:** `/Game/Characters/SK_Firefighter_Official_Rigged_Skeleton`
- **Anim Sequences:** `/Game/Characters/Animations/A_Firefighter_*`
- **Gameplay Blueprint:** `/Game/Blueprints/BP_SpaceFirefighter`
  - Componente `Mesh`:
    - `SkeletalMeshAsset` = `SK_Firefighter_Official_Rigged`
    - `AnimationMode` = `AnimationBlueprint`
    - `AnimClass` = `ABP_SpaceFirefighter_C`

### 4.3 Pipeline de Texturizado PBR 2K y Desenvuelto UV del Bombero
Para solucionar la visualización en gris/beige monocromático y garantizar el renderizado PBR oficial:
1. **Desenvuelto UV en Blender 5.2 (`UVMap`):**
   - El modelo procedural en bmesh cuenta con una capa de proyección UV `UVMap` con empaquetado de islas (`island_margin = 0.02`), abarcando rangos UV $[0.013, 0.986]$ y mapeo de atlas/trimsheet 2048x2048.
2. **Generación Sintética de Mapas PBR 2K (2048x2048):**
   - `T_Firefighter_Suit_BaseColor`: Tejido Kevlar/Nomex Hi-Vis Orange (`RGB [226, 106, 19]`), bandas de alta reflectividad microprismáticas amarillas 3M (`RGB [255, 255, 110]`), placas de blindaje de aramida verde salvia (`RGB [72, 105, 62]`), visor metálico plateado (`RGB [84, 89, 94]`), mochila dorsal con rejillas de O2 y display torácico.
   - `T_Firefighter_Suit_Normal`: Mapa de relieve tangente en espacio DirectX con biselado de costuras, ranuras de blindaje y rejillas de ventilación.
   - `T_Firefighter_Suit_ORM`: Canal R (Ambient Occlusion, 0.65-0.88), Canal G (Roughness, 0.08 en visera hasta 0.70 en tela), Canal B (Metallic, 0.85 en visor/conectores, 0.0 en tela). Compresión: `TC_MASKS`.
   - `T_Firefighter_Suit_Emissive`: Indicadores luminiscentes y LEDs de estado torácico/oxígeno.
3. **Causa Raíz Diagnosticada y Solucionada:**
   - **Fallo de asignación persistente en Skeletal Mesh:** En Unreal Engine Python API, `sk.get_editor_property("materials")` retorna una copia por valor de la lista de structs `SkeletalMaterial`. Si no se invoca explícitamente `sk.set_editor_property("materials", mats)`, la asignación no persiste y `Slot 0` queda en `None`, provocando que UE5 caiga al `Default Material` (beige plano/cuadrícula).
   - **Conflicto de Sampler Type en ORM:** Dado que `T_Firefighter_Suit_ORM` usa compresión `TC_MASKS`, el nodo `TextureSampleParameter2D` requiere obligatoriamente `SAMPLERTYPE_MASKS` (el uso de `SAMPLERTYPE_COLOR` o `SAMPLERTYPE_LINEARCOLOR` causaba fallos silenciosos de compilación de shader en SM6).
   - **Colapso de cámara por SpringArm en interiores:** `CameraBoom` con `bDoCollisionTest = true` colisionaba con los mamparos traseros del spawn, colapsando la distancia a 0 cm y metiendo la cámara dentro de la cabeza del bombero.
4. **Implementación y Verificación Empírica (`Scripts/setup_clean_pbr_suit.py`):**
   - Shader `M_Firefighter_Suit_PBR` reconstruido y compilado limpiamente con `SAMPLERTYPE_MASKS` para ORM y conexiones PBR completas.
   - Asignación bidireccional permanente a `SK_Firefighter_Official_Rigged` (Slot 0), duplicado idéntico a `M_Firefighter_Suit_Official`, y asignación a `BP_SpaceFirefighter`.
   - Cámara configurada con `do_collision_test = False`, `target_arm_length = 350.0`, y `socket_offset = (0, 40, 40)`.
   - Verificado empíricamente con capturas en tiempo de ejecución en `-game` (`Saved/Screenshots/WindowsEditor/ScreenShot00000.png` y `Art/Renders/ScreenShot_PBR_Verified_Ingame.png`), certificando visualización nítida y vibrante 1:1 con el concept art.

### 4.4 Apertura y Navegabilidad Completa del Carguero Tier 1 (`Mission_Tier1_ChemicalFreighter`)
- **Problema Detectado:** El jugador aparecía en la esclusa de inserción a $Y = -400$, y un portón estático (`Freighter_BlastDoor_S1_S2`) con colisión rígida en $Y = -200$ bloqueaba el tránsito, dando la impresión de que la nave medía solo 50 pasos.
- **Resolución Arquitectónica:**
  - Se eliminaron las mallas de portón selladas y estáticas (`BlastDoor_S1_S2`, `BlastDoor_Mid_ChemEngine`, `BlastDoor_Bridge_Security`).
  - Los 5 sectores de la nave (60 metros de eslora total) quedaron completamente interconectados a través de los marcos de mamparo abiertos:
    1. Esclusa de Atraque (Docking Airlock, Sector 1)
    2. Corredor de Presión (Pressure Corridor, Sector 2)
    3. Bodega de Reactivos Químicos (Chemical Cargo Bay, Sector 3)
    4. Sala de Máquinas y Núcleo Criogénico (Engine Room & Core, Sector 4)
    5. Puente de Mando y Cabina de Pilotaje (Bridge & Helm, Sector 5)
  - Calibración de Iluminación: El foco cenital de inserción fue ajustado de 8,000 lm a 2,400 lm con temperatura cálida, y se añadió una luz de relleno posterior (`Freighter_Player_FillLight_Backpack`, 1,800 lm) para realzar el volumen del tanque dorsal de O2 y las texturas PBR sin deslumbrar la cámara.

### 2.5 Arquitectura Autoritativa de Enhanced Input y Modificadores de Eje (WASD + Mouse)
Para erradicar fallos de serialización de structs en Unreal Engine y garantizar movilidad omnidireccional fluida:
- `ASpaceFirefighterCharacter::ConfigureEnhancedInputMappings()` configura de forma determinista y nativa en C++:
  * **W (Avance Frontal):** `UInputModifierSwizzleAxis` con orden `YXZ` -> `MovementVector.Y = +1.0`.
  * **S (Retroceso Táctico):** `UInputModifierSwizzleAxis` (`YXZ`) + `UInputModifierNegate` (`bY = true`) -> `MovementVector.Y = -1.0`.
  * **A (Desplazamiento Izquierda):** `UInputModifierNegate` (`bX = true`) -> `MovementVector.X = -1.0`.
  * **D (Desplazamiento Derecha):** Mapeo directo -> `MovementVector.X = +1.0`.
  * **Mouse2D (Giro y Cabeceo):** `UInputModifierNegate` (`bY = true`) -> Control táctico suave y natural de Pitch y Yaw.
- El método se ejecuta en `BeginPlay()`, `PawnClientRestart()`, `PossessedBy()` y `SetupPlayerInputComponent()`.

### 2.6 Sistema Directo y Reactivo de Locomoción Animada (Cero Bind Pose / A-Pose)
Para impedir que el personaje quede estático en A-Pose / T-Pose por grafos no evaluados:
- `ASpaceFirefighterCharacter` gestiona directamente las secuencias importadas (`Idle`, `Walk`, `Run`, `Crouch_Idle`, `Crouch_Walk`, `Hose_Hold`).
- En `BeginPlay()`, el `SkeletalMeshComponent` inicializa inmediatamente `A_Firefighter_Idle` en modo `AnimationSingleNode`, dotando de respiración y dinamismo visual al astronauta desde el frame 0.
- `EvaluateTargetLocomotionAnimation()`: Función estática pura diseñada para pruebas unitarias deterministas que calcula en cada frame la animación objetivo:
  * Disparo de manguera Hydra presurizada -> `A_Firefighter_Hose_Hold` (Prioridad máxima).
  * Agachado en reposo / conductos -> `A_Firefighter_Crouch_Idle`.
  * Agachado en avance (> 15 cm/s) -> `A_Firefighter_Crouch_Walk`.
  * Carrera táctica (> 480 cm/s con LeftShift) -> `A_Firefighter_Run`.
  * Marcha normal (> 15 cm/s) -> `A_Firefighter_Walk`.
  * Reposo (<= 15 cm/s) -> `A_Firefighter_Idle`.
- Durante eventos de física violenta o tropiezo (`TriggerRagdoll`), la simulación de cuerpo rígido Chaos toma el control total, y al estabilizarse (`RecoverFromRagdoll`), se reanuda de forma transparente el ciclo de animación en `A_Firefighter_Idle`.

---

## 5. Razón de Diseño (Rationale) y Cumplimiento SOLID

1. **Single Responsibility Principle (SRP):**
   - `ASpaceFirefighterCharacter` gestiona las reglas del juego, salud, física y la selección determinista de la animación de locomoción.
   - `USpaceFirefighterAnimInstance` es responsable de extraer variables cinemáticas para la animación gráfica.
   - La matemática cinemática y la selección de animación se aíslan en funciones estáticas puras, ejecutables en pruebas unitarias en milisegundos.
2. **Open/Closed Principle (OCP):**
   - El modelo de datos expuesto (`GroundSpeed`, `MovementDirection`, `bIsCrouching`, `bIsFiringHose`) es estable y cerrado.
   - Las transiciones de animación y mapeos de input son configurables y ampliables mediante Blueprints derivados sin alterar los contratos C++.
3. **Liskov Substitution Principle (LSP):**
   - Cualquier subclase especializada de `ASpaceFirefighterCharacter` o `USpaceFirefighterAnimInstance` mantiene compatibilidad con todas las firmas cinemáticas y secuencias de animación.
4. **Interface Segregation Principle (ISP):**
   - Las interfaces `ICarriableInterface`, `IInteractableInterface` y el sistema de Enhanced Input permanecen desacoplados y cohesivos.
5. **Dependency Inversion Principle (DIP):**
   - El sistema depende de abstracciones y componentes desacoplados (`UCharacterMovementComponent`, `UInputMappingContext`, `UInputAction`), sin acoplamientos rígidos a instancias de nivel.

---

## 6. Pruebas de Calidad y Validación Automatizada

### 6.1 Suite de Pruebas Unitarias C++
En [`Source/AstraHazard/Private/Tests/AstraCoreAutomationTests.cpp`](file:///f:/Dev/Game/Source/AstraHazard/Private/Tests/AstraCoreAutomationTests.cpp):
1. **`FAstraFirefighterAnimMathTest` (`AstraHazard.Animation.LocomotionMathValidation`):**
   - Precisión del cálculo de velocidad horizontal XY ignorando componente Z.
   - Precisión angular en los 4 cuadrantes cardinales (Adelante 0°, Derecha +90°, Izquierda -90°, Atrás 180°).
   - Detección de aceleración activa con filtro de zona muerta.
2. **`FAstraFirefighterEnhancedInputModifiersTest` (`AstraHazard.Input.LocomotionModifiersValidation`):**
   - Validación de guard clauses fail-fast ante contextos o acciones nulas.
   - Verificación estricta de modificadores de eje: `SwizzleAxis` en W, `SwizzleAxis` + `Negate` en S, `Negate` en A y `Negate` en Pitch para `Mouse2D`.
3. **`FAstraFirefighterAnimationEvaluationTest` (`AstraHazard.Animation.LocomotionSelectionValidation`):**
   - Evaluación exhaustiva de todas las transiciones tácticas: reposo, caminata, carrera, agachado estático, agachado en movimiento y disparo de manguera presurizada.

### 6.2 Certificación de Ejecución
- **Total de pruebas automatizadas del subsistema:** 3/3 exitosas (100% Pass Rate).
- **Ejecución vía Unreal Automation Controller:** Exit Code 0 sin errores de enlace ni desincronización cinemática.

---

## 7. Conmutación de Cámara entre 3ª y 1ª Persona y Solución Estándar de la Industria para Obstrucción de Visor (`SetOwnerNoSee`)

En [`ASpaceFirefighterCharacter`](../../Source/AstraHazard/Public/Character/SpaceFirefighterCharacter.h):
- **Alternancia en Tiempo Real (`Teclas V y C`):**
  - El método `ToggleCameraPerspective()` / `SetFirstPersonCamera(bool bEnableFirstPerson)` permite alternar instantáneamente entre:
    1. **Vista en 3ª Persona Táctica (Por Defecto):** `TargetArmLength = 220.0f`, `SocketOffset = (0, 35, 30)`, `bDoCollisionTest = true`, `ProbeSize = 14.0f` (`ECC_Camera`), garantizando que la cámara nunca atraviese muros ni quede detrás de columnas.
    2. **Vista en 1ª Persona (Visor Despejado AAA):**
       - **Solución Estándar de la Industria (`GetMesh()->SetOwnerNoSee(true)`):** En Unreal Engine 5, colocar la cámara en los ojos del modelo en 3ª persona invariablemente provoca que la geometría interior del casco, la visera, la nuca o los hombros invadan la visual. La solución profesional desacoplada consiste en activar `SetOwnerNoSee(true)` sobre el Skeletal Mesh del bombero y los primitivos de `WristDeviceComponent` para el jugador local, al tiempo que se mantiene `bCastHiddenShadow = true` y `AlwaysTickPoseAndRefreshBones` para que el personaje siga proyectando su sombra completa sobre el entorno.
       - **Alineación de Herramienta (`UpdateEquippedToolAttachment` — 3ª Persona vs 1ª Persona Viewmodel):**
         - **Causa Raíz de la Distancia de 7.48 m en 1ª Persona:** Los huesos y sockets de `SK_Firefighter_Official_Rigged` (incluyendo `weapon_socket_r`) heredan una escala mundial de $(100, 100, 100)$ procedente de la conversión FBX de metros a centímetros. Al asignar `SetActorRelativeLocation(FVector(4.0f, 6.0f, 2.0f))` sobre el arma aún acoplada a `weapon_socket_r`, el motor multiplicaba el offset por $100\times$, desplazando el arma $(400, 600, 200)\text{ cm}$ ($7.48\text{ m}$ de distancia y cerca del techo).
         - **Solución Desacoplada en `ASpaceFirefighterCharacter::UpdateEquippedToolAttachment()`:**
           - **En 1ª Persona (`bIsFirstPersonCamera == true`):** El arma (`EquippedToolActor`) se acopla directamente a `FollowCamera` (cuya escala es $1:1$ en centímetros y que rota solidariamente con el Pitch y Yaw de la vista). Para `AHydraHoseEquipment`, se posiciona en `FVector(52.0f, 22.0f, -18.0f)` con rotación `FRotator(2.0f, 176.0f, 0.0f)` ($\sim 59.3\text{ cm}$ frente a la lente en el cuadrante inferior derecho, orientando la boca frontal `-X_mesh` hacia la retícula central sin recorte por plano cercano).
           - **En 3ª Persona (`bIsFirstPersonCamera == false`):** El arma se re-acopla a `GetMesh()` en el socket `weapon_socket_r` con `FVector::ZeroVector` y `FRotator(0.0f, -90.0f, 0.0f)` y escala mundial preservada en $1.0$.
       - **Postura Táctica de Dos Manos (`bUseHoseStance`):** La postura de dos manos `A_Firefighter_Hose_Hold` se activa inmediatamente al equipar la herramienta (`EquipTool` invoca `UpdateTacticalLocomotionAnimation(0.0f)`) así como al disparar o en reposo (`bUseHoseStance = Hose->IsFiring() || (GroundSpeed <= 15.0f && !bIsCrouching)`), garantizando que ambas manos sujeten firmemente el arma.
- **Comprobación Visual Empírica:**
  - `Verify_Fixed_1stPerson_Visor.png` y `Verify_HydraHose_1P_Viewmodel_Fixed.png`: Certifican que en 1ª persona el arma se sitúa ergonómicamente a $\sim 59\text{ cm}$ frente a la cámara en el cuadrante inferior derecho con la boquilla apuntando a la retícula y el chorro criogénico saliendo hacia adelante.
  - `Verify_HydraHose_3P_Fixed.png`: Certifica que en 3ª persona el bombero sujeta con ambas manos firmes el cañón extintor sin ningún poste vertical colgando hacia el suelo.
  - `Verify_Blender_Hose_Hold_Perfect.png`: Certifica la cinemática anatómica en Blender con empuñadura y guardamanos sujetos por ambas manos.

---

## 8. Arquitectura y Mapeos Oficiales de Enhanced Input (Unreal Engine 5.8)

### 8.1 Diagnóstico de la Ausencia de Acciones
En Unreal Engine 5.8, la propiedad reflectada `mappings` de `UInputMappingContext` fue marcada como obsoleta (`DeprecationWarning`), sustituida por el contenedor de datos estructurado `DefaultKeyMappings` (`InputMappingContextMappingData`). Al manipular el contexto desde Python utilizando el método heredado `map_key(...)`, la función retornaba structs `EnhancedActionKeyMapping` por copia de valor local. Al mutar los modificadores sobre la copia local sin serializar explícitamente el struct completo en `default_key_mappings`, el asset en disco guardaba 0 modificadores o quedaba desincronizado, impidiendo que el motor emitiera señales de eje o eventos disparados (`Triggered`/`Started`) hacia `SetupPlayerInputComponent`. Como consecuencia directa, el personaje no respondía a ninguna entrada de teclado o ratón (WASD, Mouse Look, Espacio, Shift, E, LMB, RMB, G, F).

### 8.2 Resolución Autoritativa y Persistente
Se implementó el pipeline de configuración oficial en [`Scripts/poblar_y_guardar_imc_oficial.py`](../../Scripts/poblar_y_guardar_imc_oficial.py), el cual:
1. Reconstruye de forma limpia y determinista todos los enlaces en `/Game/Input/IMC_Default`.
2. Asigna y serializa directamente los modificadores de eje dentro del struct `DefaultKeyMappings`:
   - **`IA_Move` (Axis2D):**
     * `W` y `Up`: `InputModifierSwizzleAxis` (Order: `YXZ`) -> Avance frontal vectorial (+Y).
     * `S` y `Down`: `InputModifierSwizzleAxis` (Order: `YXZ`) + `InputModifierNegate` (bY=True) -> Retroceso vectorial (-Y).
     * `A` y `Left`: `InputModifierNegate` (bX=True) -> Desplazamiento lateral izquierdo (-X).
     * `D` y `Right`: Mapeo directo -> Desplazamiento lateral derecho (+X).
   - **`IA_Look` (Axis2D):**
     * `Mouse2D` y `MouseXY`: `InputModifierNegate` (bY=True) -> Inversión de Pitch para cabeceo vertical táctico natural.
   - **Acciones Digitales Esenciales:**
     * `IA_Jump` (Boolean): Tecla `SpaceBar`.
     * `IA_Sprint` (Boolean): Tecla `LeftShift`.
     * `IA_Interact` (Boolean): Tecla `E`.
     * `IA_UseTool` (Boolean): `LeftMouseButton` (Acción primaria).
     * `IA_SecondaryTool` (Boolean): `RightMouseButton` (Acción secundaria / presurización).
     * `IA_DropTool` (Boolean): Tecla `G` (Soltar herramienta con impulso físico).
     * `IA_ToggleFlashlight` (Boolean): Tecla `F` (Linterna táctica LED de escafandra).
     * `ToggleCameraPerspective`: Teclas `V` y `C` enlazadas directamente a nivel de PlayerInputComponent.
3. Asigna de forma estricta las 9 referencias de `IA_*` y el mapping context `IMC_Default` en el Class Default Object (CDO) de `/Game/Blueprints/BP_SpaceFirefighter`, recompilando el Blueprint de gameplay y guardando todos los paquetes en disco de forma completamente libre de compilación C++.

### 8.3 Comprobación Visual Empírica en Tiempo de Ejecución (Regla 5 GEMINI.md)
Se ejecutó la validación en el mapa de misión `/Game/Maps/Mission_Tier1_ChemicalFreighter` mediante [`Scripts/capturar_verificacion_acciones_e_input.py`](../../Scripts/capturar_verificacion_acciones_e_input.py) con renderizado completo en Unreal Engine 5.8:
- **`Verify_EnhancedInput_Firefighter_ThirdPerson.png`:** Certifica que la cámara en 3ª persona sobre el hombro derecho encuadra limpiamente el corredor sin colisiones indeseadas contra paredes ni recorte del casco, con línea de visión despejada hacia los objetivos.
- **`Verify_EnhancedInput_Firefighter_TacticalReady.png`:** Certifica la postura erguida completa de cuerpo entero del bombero táctico en el punto de spawn (`PlayerStart`), con los pies firmemente asentados en la cubierta, la linterna frontal encendida y la manguera Hydra empuñada correctamente.

---

## 9. Cinemática de Marcha y Carrera con Empuñadura Táctica a Dos Manos (`Walk` y `Run`)

### 9.1 Diagnóstico del Problema de Suelta de Arma al Caminar
En `ASpaceFirefighterCharacter::UpdateTacticalLocomotionAnimation`, cuando la velocidad horizontal supera el umbral de reposo (`GroundSpeed > 15.0f`), el sistema conmuta de `A_Firefighter_Hose_Hold` a `A_Firefighter_Walk` (o `A_Firefighter_Run`). En la iteración inicial del generador de Blender (`generar_animaciones_locomocion_oficial.py`), `apply_walk_frame` y `apply_run_frame` animaban los brazos con balanceo pendular libre a los costados, provocando que al dar un paso el arma acoplada a `weapon_socket_r` se desalineara hacia abajo y la mano izquierda soltara el guardamanos.

### 9.2 Solución Cinemática en Blender 5.2 e Ingesta en UE 5.8
Se rediseñaron las funciones `apply_walk_frame` y `apply_run_frame` en [`Art/Blender/generar_animaciones_locomocion_oficial.py`](../../Art/Blender/generar_animaciones_locomocion_oficial.py) e [`Scripts/importar_animaciones_limpio.py`](../../Scripts/importar_animaciones_limpio.py):
1. **Tren Inferior Dinámico:** Las piernas (`thigh_l/r`, `calf_l/r`, `foot_l/r`) y la pelvis mantienen el ciclo completo de zancada bipedal (240 cm/s en `Walk` y 480 cm/s en `Run`).
2. **Tren Superior con Sujeción Firme a Dos Manos:**
   - **Mano Derecha (Gatillo Trasero):** `upperarm_r`, `lowerarm_r` y `hand_r` mantienen el cañón extintor nivelado hacia el frente compensando la inclinación del torso (`spine_01`, `spine_02`) y añadiendo una micro-oscilación amortiguada sincronizada con el paso (`bob`).
   - **Mano Izquierda (Guardamanos Frontal):** `clavicle_l`, `upperarm_l`, `lowerarm_l` y `hand_l` cruzan frente al peto para sostener el cilindro delantero de la manguera Hydra durante toda la locomoción.
3. **Certificación Visual Empírica:**
   - `Locomotion_Anim_Showcase_6states.png` (Blender 5.2) y `Verify_Final_2_Front34_TwoHandedWalk_Grip.png` (UE 5.8) certifican que el bombero camina y corre manteniendo ambas manos firmemente acopladas al arma.

---

## 10. Arquitectura Definitiva de Sujeción y Poses del Arsenal en Tercera Persona (3P)

### 10.1 Diagnóstico de la Causa Raíz
1. **Socket Erróneo Monolítico (`weapon_socket_r` vs `hand_r`):** En la implementación previa, todas las herramientas se acoplaban a `WeaponSocketName` (`weapon_socket_r`). Dicho socket es un hueso adicional auxiliar posicionado en Blender en el centro del pecho/cintura con el propósito exclusivo de centrar el cañón cilíndrico de la manguera pesada Hydra (`BP_HydraHose`) entre ambas manos. Al equipar herramientas tácticas monomanuales (`BP_ThermalAxe` o `BP_CO2Extinguisher`), el motor las anclaba a este socket en el aire, provocando que el arma flotara a $\sim 33\text{ cm}$ por debajo y delante de la mano derecha del bombero.
2. **Pose Incompatible Forzada:** En `ASpaceFirefighterCharacter::UpdateTacticalLocomotionAnimation`, cualquier herramienta equipada forzaba la bandera `bUseHoseStance = true` en reposo. Esto provocaba que al portar el hacha o el extintor, el bombero adoptara la pose `A_Firefighter_Hose_Hold`, levantando ambos brazos vacíos al pecho para sostener un cañón invisible mientras el hacha flotaba desconectada junto a la cadera.

### 10.2 Solución en C++ y Desacoplamiento de Sockets
En [`ASpaceFirefighterCharacter::UpdateEquippedToolAttachment()`](../../Source/AstraHazard/Private/Character/SpaceFirefighterCharacter.cpp) y [`UpdateTacticalLocomotionAnimation()`](../../Source/AstraHazard/Private/Character/SpaceFirefighterCharacter.cpp):
1. **Diferenciación de Sockets según Naturaleza de la Herramienta:**
   - **Herramientas Monomanuales (`BP_ThermalAxe`, `BP_CO2Extinguisher`):**
     * Se acoplan directamente al hueso real de la mano derecha (`FName("hand_r")`), eliminando cualquier dependencia de huesos auxiliares.
     * **Hacha Térmica (`BP_ThermalAxe`):** Desplazamiento relativo `FVector(0.0f, 0.0f, -0.22f)` y rotación `FRotator(45.0f, 0.0f, 0.0f)`. La empuñadura de caucho negro y anillos de absorción pasan exactamente por el puño cerrado del guante (distancia de la empuñadura al hueso: $0.0\text{ cm}$), con el filo sobrecalentado proyectado al frente en guardia táctica.
     * **Extintor Portátil de CO2 (`BP_CO2Extinguisher`):** Desplazamiento relativo `FVector(0.0f, 0.0f, -0.68f)` y rotación `FRotator(45.0f, 0.0f, 0.0f)`. El asa roja de transporte y la palanca superior quedan firmemente sujetas por el puño del bombero, y el cilindro presurizado cuelga ergonómicamente al costado.
   - **Herramientas Biparentales / a Dos Manos (`BP_HydraHose`, `BP_TandemStretcher`):**
     * Se acoplan a `weapon_socket_r` con soporte mutuo de ambos brazos.
     * **Manguera Hydra (`BP_HydraHose`):** `FVector::ZeroVector`, `FRotator(0.0f, -90.0f, 0.0f)`, sostenida por ambas manos con la boquilla hacia adelante.
     * **Camilla Tándem (`BP_TandemStretcher`):** `FVector(-0.95f, 0.25f, 0.05f)`, `FRotator(0.0f, 0.0f, 0.0f)`, con los asideros frontales en las manos y el lecho extendido horizontalmente a nivel de cintura sin tocar el suelo.
2. **Desacoplamiento de Postura de Locomoción:**
   * La bandera `bUseHoseStance` se restringe de forma estricta a `AHydraHoseEquipment` (al disparar o en reposo) y `ATandemStretcherActor` (en reposo).
   * Para herramientas monomanuales (`AThermalAxeEquipment`, `ACO2ExtinguisherEquipment`), `bUseHoseStance = false`, lo que permite que el bombero use su ciclo natural de animación (`A_Firefighter_Idle`, `A_Firefighter_Walk`, `A_Firefighter_Run`) con el brazo derecho sujetando el arma con firmeza anatómica.

### 10.3 Certificación Visual Empírica (Regla 5 de GEMINI.md)
Se ejecutó la certificación mediante [`Scripts/certificar_todo_oficial.py`](../../Scripts/certificar_todo_oficial.py) con inspección visual directa vía `view_file`:
- **`Certify_3P_ThermalAxe.png`:** Certifica que el hacha térmica está 100% empuñada dentro del guante derecho, con el pomo sobresaliendo por la base del puño, el vástago atravesando la palma y la hoja sobrecalentada apuntando al frente sin ningún centímetro de flotación.
- **`Certify_3P_CO2Extinguisher.png`:** Certifica que el extintor de CO2 está sujeto por su asa de acarreo en el guante derecho, descansando junto a la pierna sin flotar.
- **`Certify_3P_HydraHose.png`:** Certifica sujeción firme a dos manos de la manguera pesada de extinción.
- **`Certify_3P_TandemStretcher.png`:** Certifica sujeción a dos manos por los asideros frontales con el lecho nivelado horizontal a la cintura.
- **`Certify_1P_*`:** Certifica encuadre limpio en primera persona para todo el arsenal en `FollowCamera`.

---

## 11. Resolución de Acoplamiento y Locomoción de Carga Pesada (Carro de Soldadura TIG, Batería Portátil y Golpe Completo de Hacha 3P)

### 11.1 Diagnóstico de la Causa Raíz de Solapamiento con Extremidades Inferiores
1. **Desfase de Origen Geométrico en Malla del Carro (`SM_Arc_Welding_Rig_Cart`):**
   - La malla procedural `SM_Arc_Welding_Rig_Cart` posee un centro geométrico desfasado ($Y = +105.1\text{ cm}$, con el cuerpo del carro y cilindros en el rango $X \in [-34.8, +58.8]\text{ cm}$).
   - Al acoplar el carro directamente al `RootComponent` del bombero con posición relativa `(0, 0, 0)`, los dos cilindros verticales de argón quedaban exactamente intersecando los pies, pantorrillas y botas del personaje, y la unidad de soldadura quedaba encajada dentro del cuerpo.
2. **Incompatibilidad de Animación en Marcha (`WalkAnimSequence` vs `CarryHoldAnimSequence`):**
   - En `ASpaceFirefighterCharacter::UpdateTacticalLocomotionAnimation`, cuando el personaje se desplazaba con velocidad horizontal (`GroundSpeed > 15.0f`), el sistema forzaba la secuencia de marcha estándar `A_Firefighter_Walk`.
   - Dado que el personaje opera en modo `AnimationSingleNode`, la marcha provocaba un balanceo de brazos oscilante de cuerpo entero, atravesando repetidamente los cilindros y chasis del carro transportado, además de una velocidad de marcha no restringida incompatible con la inercia del equipo rodante.
3. **Causa Raíz de la Interrupción Prematura del Golpe de Hacha Térmica 3P:**
   - En `HandleUseToolStarted`, la duración de la animación `ToolSwingAnimDuration` estaba fijada estáticamente en `0.32\text{ s}`, valor calculado para la animación diegética de retroceso del viewmodel en 1P.
   - En 3P, la animación esquelética de ataque `A_Firefighter_Axe_Swing` dura $1.0\text{ s}$ ($24\text{ cuadros}$ a $24\text{ fps}$), ubicándose la anticipación en $t = 0.40\text{ s}$ y el impacto del tajo en $t = 0.73\text{ s}$. Al transcurrir $0.32\text{ s}$, `bIsToolSwinging` se restablecía prematuramente a `false`, permitiendo que la locomoción interrumpiera abruptamente el ataque en mitad del aire antes del contacto.

### 11.2 Solución Integral en C++ y Calibración Geométrica

1. **Compensación y Acoplamiento Frontal en 3ª Persona (`UpdateEquippedToolAttachment`):**
   - **Carro de Soldadura TIG (`AArcWeldingRigCartActor` / `BP_ArcWeldingRigCart`):**
     * Reconstrucción en Blender (`scratch/fix_cart_mesh.py`): el cilindro de gas argón se retranqueó $-0.28\text{ m}$ hacia el frente del chasis, normalizando toda la geometría para $Y \le 0.000\text{ m}$ con el manillar de agarre en $Y = 0.000\text{ m}$ y el cuerpo del carro extendiéndose hacia $-Y$.
     * Acoplado al `RootComponent` en `FVector(10.0f, 0.0f, -24.0f)` con rotación `FRotator(0.0f, -90.0f, 0.0f)`.
     * La rotación Yaw de $-90^\circ$ orienta el frente de la malla ($-Y$) con el frente canónico del personaje ($+X$).
     * La cota $Z = -24.0\text{ cm}$ asienta las 4 ruedas exactamente sobre el suelo ($Z = -88.0\text{ cm}$ respecto al piso de la cápsula), y sitúa el manillar a la altura natural de las manos ($Z \approx 98\text{ cm}$).
     * La holgura libre entre el cilindro de gas y las botas es superior a $20\text{ cm}$ en cualquier fase de la zancada.
   - **Batería Portátil de Emergencia (`APortableBatteryRackActor` / `BP_PortableBatteryRack`):**
     * Acoplada al `RootComponent` en `FVector(72.0f, 0.0f, 28.0f)` con rotación neutra `FRotator::ZeroRotator`.
     * Se sostiene a la altura del pecho/cintura con $>40\text{ cm}$ de despeje respecto a las piernas.
   - **Hacha Térmica (`AThermalAxeEquipment` / `BP_ThermalAxe`):**
     * Empuñadura en `weapon_socket_r` calibrada en coordenadas relativas a `FVector(0.0f, 0.0f, -0.28f)` con rotación `FRotator(0.0f, 35.0f, -78.0f)`.
     * El factor $100\times$ de escala del hueso/socket del esqueleto FBX traduce $-0.28\text{f}$ a exactamente $-28.0\text{ cm}$ en el espacio del mundo, centrando la empuñadura perfectamente en la palma de la mano derecha con despeje lateral anti-pierna y evitando que el arma caiga al vacío subterráneo.

2. **Control de Locomoción y Dualidad de Animación de Carga (`EPlayerRescueState::Carrying`):**
   - Al transportar equipo pesado rodante o en brazos, el personaje transiciona a `EPlayerRescueState::Carrying`.
   - **Restricción de Velocidad:** La velocidad máxima de marcha se limita a $260\text{ cm/s}$ y el sprint se topea en $280\text{ cm/s}$, modelando la resistencia inercial del carro.
   - **Dualidad Cinemática en Marcha y Reposo:** `UpdateTacticalLocomotionAnimation` selecciona dinámicamente `A_Firefighter_Carry_Walk` cuando la velocidad horizontal es mayor a $15.0\text{ cm/s}$ (manteniendo las manos en el manillar y piernas en zancada continua) y `A_Firefighter_Carry_Hold` en reposo ($\le 15.0\text{ cm/s}$), impidiendo que el tren superior bracee a través de la carga o que las piernas colisionen.
   - **Serialización en CDO:** `BP_SpaceFirefighter` tiene configuradas y guardadas ambas referencias (`CarryHoldAnimSequence` y `CarryWalkAnimSequence`) directamente en sus propiedades de clase.

3. **Ejecución Completa del Golpe en 3P:**
   - En `HandleUseToolStarted`, la duración en 3P se calcula dinámicamente mediante `AxeSwingAnimSequence->GetPlayLength()` ($1.0\text{ s}$), reservando los $0.35\text{ s}$ exclusivamente para la perspectiva 1P.
   - En `UpdateTacticalLocomotionAnimation`, la guarda `bIsToolSwinging && ToolSwingAnimElapsed < ToolSwingAnimDuration` impide cualquier interrupción de locomoción hasta la recuperación total del tajo.

### 11.3 Certificación Visual Empírica (Regla 5 de GEMINI.md)
Validación visual renderizada en `/Game/Maps/Mission_Tier1_ChemicalFreighter`:
- **`Cert_3P_WeldingCart_Side.png`:** Vista de perfil certificando holgura $>40\text{ cm}$ entre cilindros y botas, con ruedas asentadas sobre la cubierta.
- **`Cert_3P_WeldingCart_Perspective.png`:** Perspectiva 3/4 demostrando manos alineadas con el manillar y cero colisión con piernas.
- **`Cert_3P_WeldingCart_Rear.png`:** Vista en tercera persona idéntica a la cámara de juego demostrando visibilidad despejada hacia el frente.
- **`Cert_3P_BatteryRack_Side.png` & `Cert_3P_BatteryRack_Perspective.png`:** Porte bimanual de la batería a la altura del pecho sin solapamiento con el torso ni rodillas.
- **`Cert_3P_Axe_Guard.png`, `Cert_3P_Axe_Windup.png`, `Cert_3P_Axe_Impact.png`, `Cert_3P_Axe_Recovery.png`:** Secuencia cinemática completa del tajo de hacha en 3P validando anticipación aérea (0.40s), impacto descendente perpendicular (0.73s) y guardia de recuperación (1.0s).

---

## 12. Auditoría Matemática Frame-por-Frame Automatizada (Garantía de Calidad Continua)

Para dar estricto cumplimiento al mandato de calidad y estabilidad cinemática sin errores silenciosos ni popping esquelético, se implementó el pipeline de auditoría cuadro a cuadro en Unreal Engine 5.8 ([`Scripts/generate_contact_sheets_and_audit.py`](file:///f:/Dev/Game/Scripts/generate_contact_sheets_and_audit.py)).

### 12.1 Cuatro Invariantes Biomecánicos Verificados
1. **Preservación Estricta de Escala (1:1:1):**
   - En todos los huesos deformables (`pelvis`, `spine_01`, `hand_r`, `foot_l`, etc.), la escala local debe permanecer invariablemente en $(1.0, 1.0, 1.0)$.
   - Se excluyen las pistas contenedor FBX `*_armature` que absorben la conversión de unidades métricas Blender $\to$ UE.
   - **Resultado:** 0 anomalías de escala en el $100\%$ de las 13 animaciones.
2. **Velocidad Angular 3D Geodésica (Cuaterniones):**
   - Se utiliza la métrica geodésica $\Delta\theta = 2\arccos(|\text{clamp}(q_1 \cdot q_2, -1.0, 1.0)|)$ en lugar de sustracción directa de ángulos de Euler, evitando falsos positivos por Gimbal Lock cuando la inclinación ronda los $\pm 90^\circ$.
   - Umbral de tolerancia: $\Delta\theta < 35^\circ/\text{frame}$ para locomoción/reposo, y $\Delta\theta < 60^\circ/\text{frame}$ para acciones dinámicas de combate (tajo balístico de hacha a 24 FPS).
   - **Resultado:** Continuidad de arco garantizada sin tirones angulares en ningún hueso.
3. **Continuidad Cíclica de Bucle (Loop Continuity):**
   - En animaciones cíclicas (`A_Firefighter_Walk`, `Run`, `Idle`, `Crouch_Walk`, etc.), el error espacial $\|\mathbf{P}_0 - \mathbf{P}_{N-1}\| < 0.5\text{ cm}$ y el error angular $\Delta\theta < 2.0^\circ$.
   - **Resultado:** Todos los ciclos presentan un error posicional de $0.00\text{ cm}$ a $0.01\text{ cm}$, garantizando interpolación continua y sin saltos visibles.
4. **Cinemática de Golpe de Hacha (`A_Firefighter_Axe_Swing`):**
   - Validación de la curva de aceleración del extremo distal (`hand_r`):
     - Windup (Frame 7): Inclinación retrógrada a $-9.8^\circ$.
     - Impacto (Frame 12): Tajo descendente a $+22.2^\circ$ (Rango efectivo: $32.0^\circ$).
     - Recuperación (Frame 23): Retorno elástico a postura de guardia frontal.

### 12.2 Registro de Resultados de Auditoría (13/13 Animaciones Aprobadas)
Consulte el informe técnico completo en [`docs/reports/auditoria_frame_por_frame_animaciones.md`](file:///f:/Dev/Game/docs/reports/auditoria_frame_por_frame_animaciones.md).

---

## 13. Arquitectura Cinemática de 4 Posturas de Locomoción (Erradicación de Brazos Flotantes)

### 13.1 Diagnóstico de la Postura Fija Bimanual
Anteriormente, las secuencias `A_Firefighter_Walk` y `A_Firefighter_Run` estaban horneadas con una pose rígida a dos manos concebida exclusivamente para la manguera Hydra. Como consecuencia directa:
1. Al caminar desarmado, el bombero mantenía los brazos en alto sujetando un arma invisible.
2. Al portar herramientas monomanuales (hacha térmica, extintor CO2, desfibrilador, gato de 15T), el brazo izquierdo flotaba rígidamente en el aire apuntando a una empuñadura inexistente.

### 13.2 Desacoplamiento y Especificación de las 4 Posturas
Se refactorizó el subsistema en C++ ([`SpaceFirefighterCharacter.cpp`](file:///f:/Dev/Game/Source/AstraHazard/Private/Character/SpaceFirefighterCharacter.cpp)) para desacoplar de forma limpia 4 ramas de locomoción:

1. **Rama Desarmada (Unarmed):**
   - Reposo: `A_Firefighter_Idle` (brazos relajados a los costados).
   - Marcha: `A_Firefighter_Walk` (balanceo pendular anatómico: brazo derecho adelanta con pierna izquierda y viceversa).
   - Carrera: `A_Firefighter_Run` (bombeo enérgico con codos flexionados a 60°).
2. **Rama Monomanual (1-Handed Tactical):**
   - Reposo: `A_Firefighter_1H_Hold` (guardia táctica lateral con arma orientada al frente).
   - Marcha: `A_Firefighter_Walk_1H` (brazo derecho firme sujetando el arma con holgura $>20\text{ cm}$ del muslo; brazo izquierdo en balanceo pendular natural).
   - Carrera: `A_Firefighter_Run_1H` (brazo derecho estabilizado junto al torso; brazo izquierdo bombeando zancada).
3. **Rama Bimanual (2-Handed Tactical):**
   - Reposo: `A_Firefighter_Hose_Hold` (sujeción firme a 2 manos).
   - Marcha: `A_Firefighter_Walk_2H` (ambas manos sujetando cañón/fusil con amortiguación de paso).
   - Carrera: `A_Firefighter_Run_2H` (carrera táctica bimanual).
4. **Rama Carga Pesada (Heavy Carry):**
   - Reposo: `A_Firefighter_Carry_Hold` (manos en manillar, carro en piso).
   - Marcha: `A_Firefighter_Carry_Walk` (manos ancladas a manillar, piernas en paso con despeje $>20\text{ cm}$).

### 13.3 Certificación Visual Empírica (Regla 5 de GEMINI.md)
- `Test_Unarmed_Walk_Frame07.png`: Marcha desarmada validada con balanceo pendular natural de brazos.
- `Test_1H_Walk_Frame07_Axe.png` & `Test_1H_Walk_Frame22_Axe.png`: Marcha táctica monomanual con hacha térmica certificada en ambas fases de paso con cero penetración física y brazo opuesto coordinado.

---

## 14. Suite de Agachado en Conductos y Calibración de Umbrales de Carrera

### 14.1 Diagnóstico de la Suite de Agachado Legada
1. **Defecto de Gálibo y Pies Flotantes:**
   - En las versiones previas de `A_Firefighter_Crouch_Idle` y `A_Firefighter_Crouch_Walk`, la traslación del hueso `pelvis` permanecía fija en la cota de bipedestación ($Z \approx 0.72\text{ m}$). Al plegar las piernas hacia arriba sin bajar la pelvis, las plantas de las botas quedaban suspendidas a $+32\text{ cm}$ en el aire, mientras la cabeza y el casco alcanzaban $1.36\text{ m} - 1.48\text{ m}$, atravesando destructivamente el techo de los conductos de ventilación modulares de $1.00\text{ m}$ (`SM_VentDuct_Straight_100x100`).
2. **Defecto de Bloqueo de Animaciones de Carrera (`GroundSpeed > 480.0f`):**
   - El componente de movimiento de Unreal Engine (`UCharacterMovementComponent`) limitaba la velocidad máxima de marcha/sprint a exactamente $480.0\text{ cm/s}$. Al exigir una condición estricta de `GroundSpeed > 480.0f` en `EvaluateTargetLocomotionAnimation` y `UpdateTacticalLocomotionAnimation`, la velocidad nunca superaba numéricamente el límite, provocando que las animaciones de carrera (`Run`, `Run_1H`, `Run_2H`) quedaran bloqueadas y el personaje continuara reproduciendo las secuencias de marcha lenta aun esprintando.

### 14.2 Solución Cinemática y Calibración en C++
1. **Re-cálculo e IK Horneado de la Suite de Agachado (Blender 5.2):**
   - Mediante el script [`scratch/bake_and_export_crouch.py`](../../scratch/bake_and_export_crouch.py):
     * **Pelvis:** Descendida a $Z = 0.390\text{ m} - 0.404\text{ m}$ (un descenso de $-32\text{ cm}$ respecto a la postura bípeda).
     * **Extremidades Inferiores:** Muslos a $-60^\circ$, pantorrillas a $+92^\circ$ y pies a $-32^\circ$, apoyando las suelas sobre el plano del piso a $Z = +0.002\text{ m} - 0.010\text{ m}$ (cero penetración, cero flotación).
     * **Torso y Cabeza:** Columna torácica inclinada $31^\circ$ hacia adelante y cabeza alzada para mirar al frente del conducto, asegurando una cota superior con casco de $0.974\text{ m} - 1.000\text{ m}$ ($< 1.05\text{ m}$ de clearance con el techo).
     * **Horneado Exacto:** Limitación estricta de fotogramas (`A_Firefighter_Crouch_Idle` a 60 cuadros, `A_Firefighter_Crouch_Walk` a 36 cuadros) y reimportación limpia en `/Game/Characters/Animations/`.
2. **Calibración de Umbral de Carrera en C++:**
   - En `SpaceFirefighterCharacter.cpp`, se actualizaron todas las comprobaciones de carrera a `GroundSpeed >= 320.0f`:
     ```cpp
     // Punto de transición medio entre marcha (240 cm/s) y sprint (480 cm/s)
     if (GroundSpeed >= 320.0f && RunAnim)
     {
         return RunAnim;
     }
     ```
   - Este punto medio garantiza una transición reactiva e histéresis cinemática natural tan pronto el jugador acciona el sprint táctico.

### 14.3 Certificación Visual Empírica (Regla 5 de GEMINI.md)
- `FinalCert_A_Firefighter_Crouch_Idle_Side.png`: Perfil lateral demostrando cota inferior a 1.00m y suelas planas sobre el suelo.
- `FinalCert_A_Firefighter_Crouch_Idle_Front.png`: Vista frontal 3/4 demostrando extremidades replegadas dentro del gálibo del conducto.
- `FinalCert_A_Firefighter_Crouch_Walk_Frame09_StepLeft.png`: Fase de avance de pierna izquierda en gateo táctico con despeje dinámico.
- `FinalCert_A_Firefighter_Crouch_Walk_Frame27_StepRight.png`: Fase simétrica de pierna derecha con estabilidad pélvica garantizada.

---

## 15. Corrección de Cruce Bimanual (`Hose_Hold` / `2H`), Calibración 3P y Carrera de Inicialización en `BeginPlay`

### 15.1 Propósito
Corregir tres defectos observados en tiempo de ejecución real al iniciar con `BP_HydraHose`:
1. Antebrazos cruzados y anudados contra el pectoral en la postura de sujeción a dos manos (`A_Firefighter_Hose_Hold`).
2. Sobrescritura de la pose bimanual por `A_Firefighter_Idle` (brazos caídos en A-pose) al iniciarse la partida en `-game`.
3. Pistola (`SM_ExtinguisherCannon`) orientada hacia atrás/abajo en la cadera con el cono de chorro criogénico (`StreamJetMeshComponent`) disparando en diagonal hacia atrás y arriba.

### 15.2 Diagnóstico Técnico y Contratos Corregidos
- **Causa 1 (Ángulos Extremos en Antebrazos Bimanuales):** En [`generar_animaciones_locomocion_oficial.py`](../../Art/Blender/generar_animaciones_locomocion_oficial.py), `build_hose_hold` aplicaba rotaciones excesivas (`lowerarm_r Z = -89.0°`, `lowerarm_l Y = -60.0°`) que doblaban los codos hacia adentro sobre el torso. Se recalibraron `build_hose_hold`, `build_walk_2h` y `build_run_2h` con `upperarm_r (-52° / -54°)`, `lowerarm_r (-40° / -38°, 0°, -12°)` y `upperarm_l (-65° / -67°)`, `lowerarm_l (-45° / -43°, 0°, +24°)`, reexportando e importando limpiamente `A_Firefighter_Hose_Hold`, `A_Firefighter_Walk_2H` y `A_Firefighter_Run_2H` en `/Game/Characters/Animations/`.
- **Causa 2 (Carrera `PossessedBy` vs `BeginPlay`):** En Unreal Engine, `PossessedBy()` / `PawnClientRestart()` invocan `EquipDefaultStartingTool()` antes de `BeginPlay()`, equipando `BP_HydraHose` y activando `A_Firefighter_Hose_Hold`. Acto seguido, [`ASpaceFirefighterCharacter::BeginPlay`](../../Source/AstraHazard/Private/Character/SpaceFirefighterCharacter.cpp) ejecutaba incondicionalmente `PlayAnimation(IdleAnimSequence, true)` sobrescribiendo `CurrentActiveAnimSequence`, mientras `EquipDefaultStartingTool()` retornaba temprano porque `EquippedToolActor` ya existía.
  - **Contrato actualizado:** `BeginPlay()` sólo inicializa `IdleAnimSequence` si `!EquippedToolActor && !CurrentActiveAnimSequence`, habilita el tick del actor (`SetActorTickEnabled(true)`), y tras `EquipDefaultStartingTool()` fuerza `UpdateTacticalLocomotionAnimation(0.0f)` y `UpdateProceduralViewmodelAnimation(0.0f)`. Además `UpdateTacticalLocomotionAnimation()` registra en `LogAstraHazard` cada transición de secuencia activa.
- **Causa 3 (Rotación Legada de Socket `weapon_socket_r`):** Tanto `UpdateEquippedToolAttachment()` como `UpdateProceduralViewmodelAnimation()` (en 3ª persona cuando `bIsHydraHose == true`) utilizaban anteriormente `FRotator(0.0f, -90.0f, 0.0f)` sobre `weapon_socket_r`. Dado el marco rotado de `weapon_socket_r` en la postura de manguera, esa rotación invertía el cañón y `NozzleArrow` hacia atrás/arriba. Se fijó autoritativamente `FRotator(7.0f, 117.44f, 80.86f)` en ambos métodos.

### 15.3 Razón de Diseño (Rationale)
- Se conservó una única fuente de verdad para `A_Firefighter_Hose_Hold` (`UpdateTacticalLocomotionAnimation`) en lugar de forzar montajes adicionales en `PawnClientRestart`, asegurando simetría tanto cuando la herramienta se equipa antes de `BeginPlay` como cuando el jugador recoge o cambia armas durante la partida.
- Mantener la guardia `!EquippedToolActor && !CurrentActiveAnimSequence` cumple el principio Fail-Fast y evita sobrescrituras destructivas de estado ya válido.
- Validado empíricamente en modo `-game` real ([`Saved/Screenshots/WindowsEditor/HighresScreenshot00000.png`](../../Saved/Screenshots/WindowsEditor/HighresScreenshot00000.png)) y capturas 3P de reposo y disparo frontal/perfil.

---

## 16. Calibración Empírica de Herramientas 3P, Alineación de Linterna Frontal y Erradicación de Brazos Cruzados en Reposo

### 16.1 Propósito y Diagnóstico de Errores Reportados
En las pruebas visuales de juego real en 3ª persona, se detectaron 5 anomalías espaciales críticas:
1. **Animación de Reposo (`A_Firefighter_Idle`):** El bombero aparecía con los antebrazos doblados $90^\circ$ sobre el esternón como si temblara de frío.
   - *Causa raíz:* En [`generar_animaciones_locomocion_oficial.py`](../../Art/Blender/generar_animaciones_locomocion_oficial.py), la función `build_idle` aplicaba rotaciones de Euler no nulas sobre los ejes diagonales locales de `lowerarm_l` (`Euler((-12°, 4°, -16°))`) y `lowerarm_r` (`Euler((0°, 0°, 18°))`). Debido a la orientación diagonal de los ejes del rig, estos valores doblaban los antebrazos hacia el torso.
   - *Solución:* Brazos relajados anatómicamente a los costados con descenso gravitatorio puro (`upperarm_l` a $+12^\circ$ Z, `upperarm_r` a $-12^\circ$ Z) y codos/antebrazos totalmente libres en $0^\circ$.
2. **Desplazamiento Procedural de Herramientas 3P (`Resolve3PToolSocketTransform`):** En `SpaceFirefighterCharacter.cpp`, la función `UpdateProceduralToolOffsets()` sobrescribía cada cuadro las transformaciones del arma equipada con los valores de `Resolve3PToolSocketTransform()`. Dicha función utilizaba traslaciones en escala de metros incorrectas (`-0.1556f, 0.1482f, -0.0801f`) y rotaciones legadas invertidas (`FRotator(18.23f, -172.00f, 56.86f)` para manguera, `FRotator(32.21f, 59.73f, -56.88f)` para hacha y extintor).
   - Como resultado:
     - El cono criogénico de `BP_HydraHose` disparaba hacia arriba y atrás a $45^\circ$ hacia el techo.
     - `BP_ThermalAxe` quedaba suspendida en el aire flotando a 40 cm por debajo del guante.
     - `BP_CO2Extinguisher` atravesaba la axila en posición horizontal.
3. **Desalineación de Linterna Frontal (`HelmetFlashlight`):** El componente `USpotLightComponent` no coincidía con la lente amarilla superior del casco ni apuntaba hacia el frente visual.
   - *Causa raíz:* El hueso `head` del rig tiene una orientación local donde Z apunta al frente del personaje (+X mundo), -Y apunta hacia arriba (+Z mundo) y -X apunta hacia la derecha (+Y mundo). Al estar en escala 100x, un desfase de $0.216$ en Z equivale a $+21.6\text{ cm}$ en mundo.

### 16.2 Contratos y Transformaciones Matemáticas Calibradas

#### 1. Linterna de Casco (`HelmetFlashlight` en hueso `head`):
- `SetRelativeLocation(FVector(0.0f, -0.080f, 0.216f));`
- `SetRelativeRotation(FRotator(90.0f, 0.0f, 0.0f));`
- **Resultado:** Lámpara montada sobre la lente frontal a $X = +21.6\text{ cm}, Y = 0.0\text{ cm}, Z = +160.0\text{ cm}$, con vector frontal proyectado exactamente a $\vec{F} = (1.000, 0.000, 0.000)$ en espacio de mirada del personaje sin ambigüedad de bloqueo de cardán.

#### 2. Manguera Hydra (`BP_HydraHose`):
- `RelativeLocation = FVector(0.0f, 0.0f, 0.0f);`
- `RelativeRotation = FRotator(18.0f, -172.0f, -192.0f);`
- **Resultado:** Vector frontal de la boquilla a $\vec{F} = (0.999992, 0.003204, 0.002344)$, disparando horizontalmente recto hacia el frente de la retícula.

#### 3. Hacha Térmica (`BP_ThermalAxe`):
- `RelativeLocation = FVector(0.0f, 0.0f, -0.28f);`
- `RelativeRotation = FRotator(32.0f, 60.0f, -42.0f);`
- **Resultado:** Empuñadura centrada con precisión dentro de la palma del guante a $Z = -28\text{ cm}$ del socket, mango vertical hacia arriba $\vec{U} = (0.0045, 0.0063, 0.9999)$ y filo apuntando al frente $\vec{F} = (0.999989, 0.000539, -0.004553)$ con $0\text{ cm}$ de holgura.

#### 4. Extintor de CO2 (`BP_CO2Extinguisher`):
- `RelativeLocation = FVector(0.0f, 0.0f, -0.68f);`
- `RelativeRotation = FRotator(32.0f, 60.0f, -42.0f);`
- **Resultado:** Cilindro colgando verticalmente de la maneta superior dentro de la mano ($Z = -68\text{ cm}$), eje de cilindro $\vec{U} = (0.0045, 0.0063, 0.9999)$ y difusor apuntando al frente $\vec{F} = (0.999989, 0.000539, -0.004553)$ con chorro criogénico frontal horizontal.

#### 5. Gato Hidráulico (`BP_HydraulicJack`):
- `RelativeLocation = FVector(0.0f, 0.0f, -0.42f);`
- `RelativeRotation = FRotator(10.0f, -97.0f, -9.0f);`
- **Resultado:** Cilindro hidráulico vertical sujetado por el asa de transporte superior a $Z = -42\text{ cm}$, manómetro y mordazas hacia el frente $\vec{F} = (0.999950, -0.007303, -0.006761)$.

### 16.3 Razón de Diseño (Rationale) y Filosofía Fail-Fast
- **Aislamiento Funcional (SOLID - SRP):** Se mantiene `Resolve3PToolSocketTransform()` como el punto único autoritativo de resolución de desfases cinemáticos en 3ª persona. Ningún subsistema externo ni blueprint requiere hardcodear transformaciones en tiempo de ejecución.
- **Detección Temprana en CI (Fail-Fast):** Se integró la prueba automatizada `FAstra3PToolAndHeadlampCalibrationTest` en [`AstraCoreAutomationTests.cpp`](../../Source/AstraHazard/Private/Tests/AstraCoreAutomationTests.cpp), verificando que para cada tipo de herramienta (`EEquipmentType`), la transformación resuelta produzca un producto punto $\vec{F} \cdot \vec{X}_{\text{forward}} \ge 0.99$, impidiendo regresiones rotacionales futuras.


