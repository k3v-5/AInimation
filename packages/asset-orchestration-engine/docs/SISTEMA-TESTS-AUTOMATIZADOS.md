# Sistema de Tests Automatizados de DarX

> **Comando Único de Validación**: `.\ejecutar_tests.ps1`

## 1. Propósito y Filosofía
Este sistema garantiza que **cualquier cambio futuro en C++, Blueprints, Shaders, Mallas o Niveles** pueda ser verificado de forma matemática y empírica en segundos, evitando regresiones silenciosas o roturas en el motor.

---

## 2. Componentes del Sistema

### A. Ejecutor Centralizado (`ejecutar_tests.ps1`)
Script en la raíz del proyecto que realiza el ciclo completo:
1. **Compilación C++ Limpia**: Invoca `compilar.ps1 -Esperar` y detiene el proceso si hay errores de sintaxis o enlazado.
2. **Ejecución en Unreal Engine (Modo Headless)**: Lanza `UnrealEditor-Cmd.exe` sin interfaz gráfica (`-NullRHI`) ejecutando la suite en Python.
3. **Parseo y Reporte en Consola**: Lee `Art/Tests/reporte_tests.json` y genera una tabla coloreada con estado `[PASS]` / `[FAIL]`.

### B. Suite de Pruebas en Python (`Art/Tests/test_suite_darx.py`)
Ejecuta las siguientes 7 categorías de validación en tiempo real dentro del motor:

| Categoría | Prueba | Criterio de Aprobación |
| :--- | :--- | :--- |
| **Shaders / PBR** | 16 Master Materials PBR | Todos existen, son `unreal.Material` y tienen `used_with_instanced_static_meshes = True`. |
| **Mallas / 3D** | 14 Mallas Modulares y Estructuras | Tienen colisiones válidas, bounds $>20\text{ cm}$ y materiales vinculados. |
| **Nivel / Geometría** | Limpieza de Plantilla | Cero actores `StaticMeshActor_...` o `Floor_...` de la plantilla antigua. |
| **WorldGen / Incursión** | Generación Procedural | Calabozo conexo sin islas huérfanas, validado por QA Flood-Fill, spawn seguro. |
| **WorldGen / Sandbox** | Generación Sandbox | 15,759 instancias PBR activas, arena de combate lista. |
| **WorldGen / Sandbox** | Spawn Seguro en Sandbox | Coordenadas en zona abierta $(1050, 5050, 421)$ con despeje $>600\text{ cm}$. |
| **Arquitectura / C++** | Clases Core C++ | `DarxProyectGameMode`, `DarxHUD` y `DarxProyectCharacter` vinculados. |

---

## 3. Uso en el Flujo de Trabajo
Cada vez que se modifique código o assets:
```powershell
# Ejecutar suite completa (Compilación C++ + Tests en UE)
.\ejecutar_tests.ps1

# Ejecutar solo tests en Python (si ya compilaste previamente)
.\ejecutar_tests.ps1 -SoloPython
```
