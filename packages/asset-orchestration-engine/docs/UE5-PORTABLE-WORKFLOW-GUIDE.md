# Guía de Flujo Desacoplado: AOE (Headless) ↔ Unreal Engine 5 (Workstation)

Esta guía describe cómo utilizar **Asset Orchestration Engine (AOE)** en un entorno donde Unreal Engine 5 **no está instalado localmente**, y cómo transferir e ingerir los assets generados en tu máquina principal de desarrollo con UE5 con **cero fricción**.

---

## 1. Concepto Arquitectónico

```
┌─────────────────────────────────────────────────────────┐
│              MÁQUINA 1: FÁBRICA HEADLESS                │
│                 (Esta Máquina con AOE)                  │
│                                                         │
│  • Ejecuta AOE en Python 3.10+                          │
│  • No requiere GPU potente ni Unreal Engine instalado   │
│  • Genera mundos, personajes, shaders, VFX y audio      │
│  • Valida QA con bots y calcula presupuestos            │
│  • Empaqueta todo en un archivo portable .ZIP           │
└────────────────────────────┬────────────────────────────┘
                             │
            Transferencia vía Git, Red local o USB
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│             MÁQUINA 2: ESTACIÓN DE TRABAJO              │
│               (Tu Máquina con Unreal Engine 5)          │
│                                                         │
│  • Abre tu proyecto (<TuProyecto>.uproject)             │
│  • Plugin Plugins/UAFBridge activo                      │
│  • Ingestión automática en 1 clic:                      │
│      - Mallas con Nanite activado automáticamente       │
│      - Shaders PBR y Virtual Texturing                  │
│      - Sistemas Niagara y Sound Cues                    │
│      - Spawn de PlayerStart y enemigos en el nivel      │
└─────────────────────────────────────────────────────────┘
```

---

## 2. En Esta Máquina (Generar y Exportar el Bundle)

Desde la terminal en esta máquina, ejecuta el comando de exportación:

```powershell
# Exportar el paquete completo a un archivo ZIP portable
py -3.13 -m uaf.golden_slice.cli export-bundle --output dist/AOE_UE5_Bundle.zip
```

Esto creará el archivo `dist/AOE_UE5_Bundle.zip` con la siguiente estructura interna:
```
AOE_UE5_Bundle/
├── Plugins/
│   └── UAFBridge/             <-- Plugin C++/Python para tu Unreal
│       ├── UAFBridge.uplugin
│       ├── Source/...
│       └── Content/Python/...
├── Content/
│   └── AOE/                   <-- Assets, manifiestos y scripts de ingestión
│       ├── Manifests/
│       │   └── golden_slice_manifest.json
│       ├── Meshes/
│       ├── Textures/
│       ├── Audio/
│       └── Scripts/
│           └── run_ingest.py
├── bundle_manifest.json       <-- Checksums SHA-256 de integridad
└── LEEME_INSTRUCCIONES.txt    <-- Resumen rápido de instalación
```

---

## 3. En Tu Máquina con Unreal Engine 5 (Instalación e Ingestión)

Transfiere el archivo `AOE_UE5_Bundle.zip` a tu máquina con UE5 y descomprímelo:

### Paso 3.1: Copiar el Plugin UAFBridge
Copia la carpeta:
```
Plugins/UAFBridge/
```
dentro de la carpeta `Plugins/` de tu proyecto de Unreal:
```
<RutaDeTuProyecto>/Plugins/UAFBridge/
```
*(Si la carpeta `Plugins/` no existe en la raíz de tu proyecto, créala).*

### Paso 3.2: Copiar la Carpeta de Assets
Copia la carpeta:
```
Content/AOE/
```
dentro de la carpeta `Content/` de tu proyecto de Unreal:
```
<RutaDeTuProyecto>/Content/AOE/
```

### Paso 3.3: Abrir Unreal Engine 5 y Ejecutar la Ingestión
1. Abre tu proyecto en **Unreal Engine 5** (5.3, 5.4 o 5.5).
2. Si es la primera vez que añades el plugin, Unreal te pedirá compilar los módulos C++; pulsa **Yes**.
3. En la barra superior del editor verás el nuevo menú **AOE**:
   * Haz clic en **`AOE -> Ingest AOE Bundle`**.
4. El script de automatización (`aoe_editor_ingest.py`) se ejecutará en segundo plano en el editor:
   * Importará todos los modelos 3D activando **Nanite** automáticamente.
   * Configurará las texturas con Virtual Texturing.
   * Conectará los emisores Niagara y sound cues.
   * Colocará en el nivel activo el `PlayerStart`, los 4 enemigos (`SCOUT`, `MELEE`, `HEAVY`, `RANGED`), la iluminación solar y la atmósfera.

---

## 4. Ingestión Alternativa por Consola de Python en Unreal

También puedes ejecutar la ingestión en cualquier momento desde la ventana de Python en Unreal Editor (`Output Log` -> `Cmd` -> cambiar a `Python`):

```python
from aoe_editor_ingest import AOEUnrealIngestionPipeline
AOEUnrealIngestionPipeline().run_pipeline()
```
