# UAF-81 — UNIVERSAL ASSET FACTORY

## MASTER ARCHITECTURE & DEVELOPMENT CHARTER

**Project:** Asset Orchestration Engine  
**Development Program:** UAF-81 — Universal Asset Factory  
**Document Type:** Master Architecture & Development Charter  
**Status:** FOUNDATIONAL  
**Version:** 1.0.0  
**Target:** Unreal Engine 5.x  
**Primary DCC Backend:** Blender 4.x/5.x  
**Parent System:** Asset Orchestration Engine (AOE)  

---

# 1. PURPOSE

UAF-81 — Universal Asset Factory establece la arquitectura y el marco de desarrollo para evolucionar Asset Orchestration Engine desde un sistema avanzado de generación y orquestación de assets hacia una **plataforma integral de producción procedural de contenido para Unreal Engine**.

El sistema deberá ser capaz de transformar especificaciones declarativas de producción en artefactos digitales reproducibles, verificables, optimizados y preparados para integración en un proyecto Unreal Engine.

El objetivo fundamental es permitir la producción sistemática de:

* personajes;
* criaturas;
* armas;
* vehículos;
* props;
* arquitectura;
* kits modulares;
* materiales;
* texturas;
* decals;
* rigs;
* animaciones;
* VFX;
* audio;
* terrenos;
* biomas;
* entornos;
* mapas;
* niveles;
* prefabs;
* assets de gameplay;
* metadata;
* dependencias;
* paquetes de entrega para Unreal Engine.

UAF-81 no se define como un único generador de geometría.

Se define como una **fábrica de producción digital**, donde la geometría representa solamente una de las capas del producto final.

---

# 2. VISION

La visión de UAF-81 es establecer un pipeline en el que una intención de producción pueda convertirse en un producto digital completo mediante un proceso:

```text
INTENT
   ↓
SPECIFICATION
   ↓
PLANNING
   ↓
GENERATION
   ↓
ASSEMBLY
   ↓
VALIDATION
   ↓
OPTIMIZATION
   ↓
PACKAGING
   ↓
UNREAL INTEGRATION
   ↓
PRODUCTION-READY ARTIFACT
```

El sistema deberá mantener trazabilidad entre todos los estados anteriores.

Ningún artefacto final deberá considerarse aislado de su especificación, generadores, dependencias, parámetros, versión y proceso de validación.

---

# 3. PRIMARY OBJECTIVE

El objetivo principal de UAF-81 es proporcionar una infraestructura capaz de producir contenido 3D y contenido asociado para Unreal Engine mediante procesos:

1. deterministas;
2. reproducibles;
3. parametrizables;
4. modulares;
5. versionables;
6. auditables;
7. validables;
8. optimizables;
9. recuperables;
10. extensibles.

El sistema deberá priorizar la **calidad y consistencia de producción** sobre la simple cantidad de contenido generado.

---

# 4. SECONDARY OBJECTIVES

UAF-81 deberá:

* reutilizar las capacidades existentes de AOE siempre que sean compatibles;
* evitar duplicar sistemas existentes;
* desacoplar la especificación de asset de su backend de generación;
* permitir múltiples estrategias de generación para una misma categoría;
* separar geometría, superficie, ensamblaje, comportamiento y presentación;
* representar explícitamente las dependencias entre assets;
* soportar variantes de un mismo asset;
* conservar trazabilidad completa de cada generación;
* permitir reconstrucción determinista de artefactos;
* proporcionar validación técnica y visual;
* producir resultados compatibles con las restricciones de producción de Unreal Engine;
* permitir reemplazar o incorporar backends sin modificar la especificación conceptual del asset.

---

# 5. NON-GOALS

UAF-81 no deberá intentar convertirse en:

* un reemplazo completo de Blender;
* un reemplazo completo de Unreal Engine;
* un editor generalista de modelado manual;
* un software generalista de pintura digital;
* un motor de videojuegos;
* un sistema autónomo de dirección artística;
* una plataforma limitada exclusivamente a personajes;
* una colección de scripts independientes sin contratos comunes.

Cuando una capacidad externa resulte superior a una implementación propia, UAF-81 deberá poder integrarla mediante una interfaz de backend apropiada.

---

# 6. CORE ARCHITECTURAL PRINCIPLES

## 6.1 Specification First

Toda producción deberá partir de una especificación formal.

No deberá existir una ruta de producción crítica basada exclusivamente en parámetros implícitos, estado global o configuración manual no registrada.

---

## 6.2 Determinism First

Una misma especificación, utilizando las mismas versiones de generadores y dependencias y la misma semilla, deberá producir un resultado equivalente y reproducible.

El sistema deberá registrar como mínimo:

```text
AssetID
SpecificationVersion
GeneratorVersion
Seed
DependencyVersions
BackendVersion
EngineTarget
PlatformTarget
GenerationParameters
```

---

## 6.3 Artifact First

El objetivo de una operación de generación no será simplemente ejecutar código.

El objetivo será producir un artefacto identificable, verificable y trazable.

---

## 6.4 Validation First

Todo artefacto deberá atravesar las validaciones aplicables antes de ser marcado como utilizable.

La existencia física de un archivo no constituye evidencia de que el asset sea válido.

---

## 6.5 Unreal First

Unreal Engine constituye el target de producción prioritario de UAF-81.

Las decisiones de generación deberán considerar desde el diseño:

* escala;
* materiales;
* UV;
* colisiones;
* LOD;
* Nanite;
* skeletal meshes;
* sockets;
* animaciones;
* shaders;
* memoria;
* rendimiento;
* packaging;
* estructura de contenido;
* compatibilidad con el proyecto objetivo.

---

## 6.6 Backend Independence

La especificación de un asset no deberá depender directamente de una herramienta concreta.

Conceptualmente:

```text
Asset Specification
        ↓
Generation Plan
        ↓
Backend
        ↓
Artifact
```

Los backends iniciales podrán incluir:

```text
Blender
Unreal Engine
Procedural Geometry
Texture/Material Systems
External Specialized Tools
```

---

## 6.7 Modular Generation

Los assets complejos deberán poder construirse mediante componentes especializados.

Un personaje, por ejemplo, no deberá estar obligado a utilizar una única estrategia geométrica.

---

## 6.8 Surface Independence

La geometría y la apariencia deberán poder evolucionar independientemente siempre que sus contratos lo permitan.

Una modificación de material no deberá requerir necesariamente regenerar la geometría.

---

## 6.9 Explicit Dependencies

Toda dependencia relevante deberá estar representada explícitamente.

Un asset complejo deberá poder expresarse como un grafo:

```text
CHARACTER
├── SKELETON
├── BODY
├── CLOTHING
├── ARMOR
├── EQUIPMENT
├── MATERIALS
├── TEXTURES
├── ANIMATIONS
└── VFX
```

---

## 6.10 Fail Closed

Cuando una validación crítica no pueda determinarse de forma fiable, el sistema deberá tratar el resultado como no validado.

No deberán utilizarse estados ambiguos como sustituto de una validación inexistente.

---

## 6.11 Traceability

Toda transformación relevante deberá poder relacionarse con:

```text
Input
→ Operation
→ Generator
→ Version
→ Output
→ Validation
```

---

# 7. UNIVERSAL ASSET MODEL

UAF-81 deberá utilizar un modelo conceptual común para todos los assets.

Un asset deberá poder representarse mediante las siguientes capas:

```text
ASSET
│
├── IDENTITY
├── SPECIFICATION
├── COMPONENTS
├── GEOMETRY
├── SURFACE
├── RIG
├── ANIMATION
├── BEHAVIOR
├── PRESENTATION
├── COLLISION
├── OPTIMIZATION
├── VALIDATION
├── DEPENDENCIES
└── ARTIFACTS
```

No todos los tipos de asset requerirán todas las capas.

Cada categoría deberá declarar cuáles son obligatorias, opcionales o prohibidas.

---

# 8. ASSET TAXONOMY

La taxonomía inicial de UAF-81 será:

```text
CHARACTER
CREATURE
WEAPON
VEHICLE
PROP
MODULAR_KIT
ARCHITECTURE
ENVIRONMENT
TERRAIN
WORLD
MATERIAL
TEXTURE
DECAL
RIG
ANIMATION
VFX
AUDIO
GAMEPLAY_ASSET
PREFAB
LEVEL
```

La taxonomía deberá ser extensible.

Una categoría nueva no deberá requerir modificar el núcleo del sistema cuando pueda implementarse mediante los contratos existentes.

---

# 9. CHARACTER PRODUCTION MODEL

Los personajes deberán tratarse como composiciones de múltiples subsistemas.

Modelo conceptual:

```text
CHARACTER
│
├── SPECIES
├── BODY
├── HEAD
├── SKELETON
├── CLOTHING
├── ARMOR
├── EQUIPMENT
├── MATERIALS
├── TEXTURES
├── RIG
├── ANIMATION
├── COLLISION
├── LODS
└── METADATA
```

UAF-81 deberá permitir múltiples estrategias de generación.

Ejemplo:

```text
CharacterGenerationStrategy
│
├── Primitive
├── Anatomical
├── HardSurface
├── Modular
├── Creature
└── Hybrid
```

La estrategia deberá seleccionarse en función de las características de la especificación.

El sistema no deberá asumir que una única técnica geométrica es adecuada para todos los personajes.

---

# 10. HYBRID CHARACTER GENERATION

Los personajes complejos deberán poder combinar diferentes representaciones.

Ejemplo:

```text
Human Base
    ↓
Anatomical Mesh
    +
Procedural Armor
    +
Modular Clothing
    +
Curve-Based Cables
    +
Hard-Surface Components
    +
Procedural Materials
    +
Skeleton
    +
Skinning
```

La arquitectura deberá soportar esta composición sin convertir todos los componentes en una única representación geométrica prematuramente.

---

# 11. GEOMETRY FACTORY

El sistema geométrico deberá soportar múltiples estrategias:

```text
PRIMITIVES
CURVES
PARAMETRIC MESHES
HARD SURFACE
SDF
VOXEL
REMESH
MODULAR ASSEMBLY
GEOMETRY NODES
SPECIALIZED GENERATORS
```

Cada estrategia deberá utilizarse para el problema para el que resulte apropiada.

El voxel/remesh existente deberá conservarse como una estrategia válida, especialmente para:

* criaturas;
* cuerpos abstractos;
* formas orgánicas;
* biomecánica;
* masas volumétricas;
* prototipos;
* determinadas formas de boss.

No deberá convertirse en la representación universal del sistema.

---

# 12. SURFACE & MATERIAL FACTORY

La apariencia deberá modelarse como un sistema independiente de la geometría.

Un Surface Definition deberá poder describir:

```text
BASE COLOR
METALLIC
ROUGHNESS
NORMAL
AO
HEIGHT
EMISSIVE
MASKS
WEAR
DIRT
SCRATCHES
DAMAGE
DECALS
```

Las superficies deberán poder generar variantes mediante parámetros y semillas deterministas.

Ejemplo conceptual:

```text
IndustrialMetal
    ↓
    ├── Clean
    ├── Used
    ├── Scratched
    ├── Damaged
    ├── Burned
    └── Abandoned
```

---

# 13. MODULAR KIT FACTORY

UAF-81 deberá soportar la creación y ensamblaje de kits modulares.

Una pieza modular deberá poder declarar:

```text
Dimensions
Grid
Sockets
Collision
Material Slots
Allowed Connections
Orientation
Tags
```

Ejemplo:

```text
WALL
├── wall_L
├── wall_R
├── floor
└── ceiling
```

Los sistemas de arquitectura y construcción deberán utilizar contratos de compatibilidad explícitos.

---

# 14. WORLD FACTORY

Los mundos y niveles deberán modelarse como estructuras composicionales.

Conceptualmente:

```text
WORLD
│
├── REGIONS
│
├── ZONES
│
├── ROOMS
│
├── CORRIDORS
│
├── BUILDINGS
│
├── TERRAIN
│
├── PROPS
│
├── LIGHTING
├── VFX
├── AUDIO
└── GAMEPLAY
```

La generación de mundos deberá basarse en una representación intermedia denominada conceptualmente:

```text
WORLD GRAPH
```

El World Graph deberá describir relaciones, conexiones, restricciones y propiedades del mundo antes de producir la representación final.

---

# 15. ASSET LIFECYCLE

Todo asset deberá seguir un lifecycle formal.

```text
REQUESTED
    ↓
SPECIFIED
    ↓
PLANNED
    ↓
GENERATING
    ↓
ASSEMBLING
    ↓
VALIDATING
    ↓
OPTIMIZING
    ↓
PACKAGING
    ↓
READY
```

Estados de fallo:

```text
GENERATION_FAILED
VALIDATION_FAILED
OPTIMIZATION_FAILED
PACKAGING_FAILED
INVALIDATED
```

Los estados deberán ser persistentes y auditables.

---

# 16. GENERATION PLAN

La especificación conceptual no deberá ejecutar directamente las operaciones de generación.

Deberá producirse un plan intermedio:

```text
Asset Specification
        ↓
Generation Plan
```

El Generation Plan deberá definir:

* componentes;
* orden de operaciones;
* estrategias;
* backends;
* parámetros;
* dependencias;
* validaciones;
* outputs esperados.

Esto permitirá separar intención de ejecución.

---

# 17. ARTIFACT MODEL

UAF-81 distinguirá explícitamente entre:

```text
SPECIFICATION
GENERATION
ARTIFACT
BUILD
PACKAGE
```

### Specification

Describe qué debe producirse.

### Generation

Describe cómo se produjo.

### Artifact

Es el resultado generado.

### Build

Es una transformación controlada del artifact para un target específico.

### Package

Es la unidad final de entrega.

---

# 18. VERSIONING

El sistema deberá versionar independientemente:

```text
Asset
Specification
Generator
Backend
Material
Skeleton
Dependencies
Build Configuration
```

Una actualización de cualquiera de estos elementos deberá poder detectarse.

Los cambios deberán permitir determinar si un artifact continúa siendo válido o requiere reconstrucción.

---

# 19. SEED MANAGEMENT

Toda operación procedural que dependa de aleatoriedad deberá utilizar una fuente de seed explícita.

Las seeds deberán formar parte de la identidad reproducible de la generación.

No deberá dependerse de:

* random global;
* timestamps;
* estado oculto;
* orden accidental de ejecución;
* valores no registrados.

---

# 20. DEPENDENCY GRAPH

UAF-81 deberá mantener un grafo explícito de dependencias.

Ejemplo:

```text
Character_A
│
├── Skeleton_A
│   └── AnimationSet_A
│
├── Body_A
│   └── Material_A
│       └── TextureSet_A
│
├── Armor_A
│   └── Material_B
│
└── Weapon_A
    └── Material_C
```

El sistema deberá poder determinar:

* qué depende de qué;
* qué debe reconstruirse;
* qué quedó obsoleto;
* qué artifacts pueden reutilizarse;
* qué cambios afectan a qué assets.

---

# 21. VALIDATION ARCHITECTURE

La validación deberá dividirse como mínimo en:

```text
STRUCTURAL QA
GEOMETRIC QA
MATERIAL QA
TEXTURE QA
RIG QA
ANIMATION QA
UNREAL QA
PERFORMANCE QA
DEPENDENCY QA
VISUAL QA
```

Cada categoría deberá producir resultados estructurados.

Ejemplo:

```text
CHECK
STATUS
SEVERITY
MEASURED_VALUE
EXPECTED_VALUE
MESSAGE
EVIDENCE
```

---

# 22. VISUAL QA

La validación visual deberá considerarse una dimensión independiente.

Un asset podrá ser técnicamente válido y artísticamente insuficiente.

Por lo tanto:

```text
TECHNICAL VALIDATION ≠ VISUAL VALIDATION
```

La arquitectura deberá permitir métricas visuales y revisiones independientes.

---

# 23. PRODUCTION-READY STATUS

Un asset solamente podrá recibir:

```text
PRODUCTION_READY
```

cuando haya superado todas las validaciones obligatorias de su categoría y target.

Conceptualmente:

```text
Generation
    ↓
Technical QA
    ↓
Visual QA
    ↓
Optimization QA
    ↓
Unreal QA
    ↓
Packaging QA
    ↓
PRODUCTION_READY
```

---

# 24. OPTIMIZATION

La optimización deberá considerarse parte del lifecycle, no una operación posterior opcional.

Dependiendo de la categoría deberá evaluarse:

* polygon budget;
* texture memory;
* material complexity;
* shader complexity;
* draw calls;
* collision complexity;
* LODs;
* Nanite;
* skeletal complexity;
* animation cost;
* VFX cost;
* audio cost;
* world streaming cost.

Los límites deberán ser configurables por proyecto y plataforma.

---

# 25. UNREAL INTEGRATION

UAF-81 deberá considerar Unreal como un target de producción real y no solamente como un destino de exportación.

La integración deberá poder contemplar:

```text
STATIC MESH
SKELETAL MESH
MATERIAL
MATERIAL INSTANCE
TEXTURE
PHYSICS ASSET
ANIMATION
NIAGARA
SOUND
BLUEPRINT-RELATED ASSETS
DATA ASSETS
LEVEL
WORLD
```

El sistema deberá conservar la identidad y trazabilidad del artifact durante la integración.

---

# 26. BACKEND ARCHITECTURE

Los backends deberán implementar contratos comunes.

Conceptualmente:

```text
UAF CORE
   │
   ├── Geometry Backend
   ├── Blender Backend
   ├── Unreal Backend
   ├── Material Backend
   ├── Texture Backend
   ├── World Backend
   └── Specialized Backends
```

El Core no deberá depender de detalles específicos de implementación de un backend.

---

# 27. OBSERVABILITY

Toda operación importante deberá producir información suficiente para:

* diagnóstico;
* auditoría;
* reproducción;
* debugging;
* performance analysis;
* failure recovery.

El sistema deberá registrar:

```text
START
INPUTS
PLAN
OPERATIONS
WARNINGS
ERRORS
OUTPUTS
VALIDATION
DURATION
RESOURCE USAGE
FINAL STATUS
```

---

# 28. RECOVERY

Las operaciones largas deberán poder recuperarse cuando sea técnicamente posible.

El sistema deberá utilizar checkpoints, transacciones o mecanismos equivalentes para evitar que un fallo obligue a reconstruir innecesariamente todo el pipeline.

Las operaciones parcialmente completadas deberán poder identificarse de forma segura.

---

# 29. SECURITY AND GOVERNANCE

Las operaciones de generación deberán respetar los mecanismos existentes de permisos y governance de AOE.

Cada operación deberá ejecutarse dentro de un scope definido.

Los backends externos no deberán recibir acceso ilimitado al sistema.

---

# 30. PROJECT PORTABILITY

UAF-81 deberá evitar rutas de almacenamiento dependientes de una máquina concreta.

Las rutas deberán resolverse mediante configuración, variables de entorno o mecanismos equivalentes.

No deberán existir rutas absolutas de producción codificadas como dependencias arquitectónicas.

---

# 31. TESTING REQUIREMENTS

Cada capacidad deberá incorporar pruebas adecuadas a su nivel.

Como mínimo:

```text
UNIT TESTS
INTEGRATION TESTS
CONTRACT TESTS
DETERMINISM TESTS
REGRESSION TESTS
VALIDATION TESTS
END-TO-END TESTS
```

Las capacidades críticas deberán disponer además de artifacts de prueba verificables.

---

# 32. DETERMINISM TEST

Toda capacidad procedural crítica deberá poder demostrar:

```text
INPUT A
+
SEED X
+
VERSION V
        ↓
ARTIFACT H1
```

y posteriormente:

```text
INPUT A
+
SEED X
+
VERSION V
        ↓
ARTIFACT H2
```

donde:

```text
H1 == H2
```

o donde cualquier diferencia permitida esté formalmente definida.

---

# 33. ARTIFACT IDENTITY

Cada artifact deberá disponer de una identidad estable.

Conceptualmente:

```text
ArtifactIdentity
│
├── AssetID
├── ArtifactType
├── SpecificationHash
├── GeneratorHash
├── DependencyHash
├── BuildHash
└── ContentHash
```

El mecanismo concreto de hashing deberá definirse durante la arquitectura detallada.

---

# 34. REUSABILITY

UAF-81 deberá favorecer la reutilización.

Una vez producido un componente válido, deberá poder utilizarse como dependencia de múltiples assets.

Ejemplo:

```text
Material_Obsidian
        ↓
        ├── Character_A
        ├── Character_B
        ├── Weapon_A
        ├── Prop_A
        └── Building_A
```

No deberá regenerarse innecesariamente un componente idéntico.

---

# 35. VARIANT SYSTEM

El sistema deberá permitir derivar variantes sin duplicar innecesariamente la totalidad del asset.

Ejemplo:

```text
CHARACTER_BASE
│
├── DEFAULT
├── DAMAGED
├── ELITE
├── CORRUPTED
└── BOSS
```

Las variantes deberán declarar explícitamente qué componentes cambian.

---

# 36. QUALITY TIERS

UAF-81 deberá permitir definir diferentes niveles de producción.

Conceptualmente:

```text
PROTOTYPE
GAMEPLAY
PRODUCTION
HERO
CINEMATIC
```

Cada tier podrá modificar:

* resolución;
* geometría;
* materiales;
* texturas;
* LOD;
* optimización;
* QA;
* tiempo máximo de generación;
* requisitos de exportación.

---

# 37. PROJECT PROFILES

Las restricciones de producción deberán poder definirse mediante perfiles.

Ejemplo:

```text
ProjectProfile
│
├── TargetEngine
├── TargetPlatform
├── VisualStyle
├── PolygonBudgets
├── TextureBudgets
├── MaterialBudgets
├── PerformanceBudgets
├── NamingRules
├── FolderRules
└── ValidationRules
```

Esto permitirá que UAF-81 produzca assets adecuados para distintos proyectos sin alterar el núcleo.

---

# 38. STYLE SYSTEM

La identidad visual deberá separarse de la lógica de generación.

Un estilo deberá poder definir:

```text
Color Language
Material Language
Shape Language
Surface Detail
Wear
Lighting
Emissive Rules
Proportion Rules
```

La estética DarX deberá convertirse en un perfil de estilo, no en una dependencia rígida del núcleo.

---

# 39. EXTENSIBILITY

El sistema deberá poder incorporar nuevas:

* categorías;
* estrategias;
* backends;
* validadores;
* optimizadores;
* exporters;
* perfiles;
* estilos;
* plataformas.

La extensión deberá producirse mediante contratos formales.

---

# 40. DEVELOPMENT PHILOSOPHY

El desarrollo de UAF-81 deberá evitar la creación de capacidades aisladas.

Cada nueva capacidad deberá integrarse en el lifecycle completo cuando corresponda:

```text
SPECIFY
→ PLAN
→ GENERATE
→ ASSEMBLE
→ VALIDATE
→ OPTIMIZE
→ PACKAGE
```

Una función de generación sin integración en el lifecycle no deberá considerarse una capacidad de producción completa.

---

# 41. DEFINITION OF DONE

Una fase o capacidad de UAF-81 solamente podrá considerarse completada cuando exista evidencia suficiente de:

```text
IMPLEMENTATION
+
ARCHITECTURE
+
SPECIFICATION
+
TESTS
+
VALIDATION
+
DOCUMENTATION
+
DETERMINISM
+
ARTIFACT EVIDENCE
```

Los requisitos exactos podrán variar según la categoría, pero ningún componente crítico deberá declararse terminado únicamente por haber sido implementado.

---

# 42. MASTER SUCCESS CRITERION

UAF-81 será considerado exitoso cuando AOE pueda transformar una especificación de producción en un conjunto coherente de artifacts para Unreal Engine manteniendo:

```text
TRACEABILITY
REPRODUCIBILITY
QUALITY
CONSISTENCY
PERFORMANCE
PORTABILITY
VERSION CONTROL
DEPENDENCY CONTROL
VALIDATION
```

El resultado final deberá ser utilizable dentro de un flujo profesional de producción.

---

# 43. FINAL ARCHITECTURAL STATEMENT

UAF-81 no deberá entenderse como un nuevo generador.

Debe entenderse como una **infraestructura universal de fabricación de contenido digital**.

La unidad fundamental del sistema no será la malla.

Será el:

```text
PRODUCTION ASSET
```

Un Production Asset podrá estar compuesto por múltiples artifacts, dependencias y representaciones.

Por tanto, la arquitectura deberá evolucionar desde:

```text
INPUT
 ↓
GENERATE MODEL
 ↓
EXPORT
```

hacia:

```text
INTENT
 ↓
ASSET SPECIFICATION
 ↓
ASSET GRAPH
 ↓
GENERATION PLAN
 ↓
SPECIALIZED GENERATORS
 ↓
ASSEMBLY
 ↓
SURFACE
 ↓
RIG / ANIMATION / BEHAVIOR
 ↓
VALIDATION
 ↓
OPTIMIZATION
 ↓
PACKAGING
 ↓
UNREAL INTEGRATION
 ↓
PRODUCTION-READY ASSET
```

Esta arquitectura constituye la base de las fases posteriores de UAF-81.

Toda fase futura deberá ser compatible con este documento o justificar explícitamente cualquier desviación arquitectónica.
