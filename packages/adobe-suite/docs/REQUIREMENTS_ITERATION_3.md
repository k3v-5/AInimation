# Documento de Requerimientos: Iteración 3 - Realidad Adobe y DSL Dinámico

## 1. Objetivo de la Iteración

Conectar el orquestador abstracto con el entorno físico del sistema operativo. Esto implica crear un validador dinámico para transformar JSONs complejos en Grafos (DAG), hackear la "caja negra" de Character Animator mediante manipulación de archivos `.chproj` y macros de sistema, y reemplazar la percepción simulada por inspectores de disco y procesos.

## 2. Alcance

**Incluye:**
1. **Parser Dinámico de DSL:** Implementación de validación de esquemas (JSON Schema / Zod) para transformar Intents complejos en nodos del DAG.
2. **Character Animator Layer 0:** Scripts en Python (expansión de `adobe-mcp`) o Node.js para manipular proyectos `.chproj` a nivel de carpetas e inyectar atajos de teclado/SO.
3. **Percepción Basada en Sistema (Real Perception):** Validadores de estado que leen el sistema de archivos (existencia, tamaño, fechas de modificación) y procesos en ejecución.

**No incluye (Movido a Iteración 4):**
* Implementación completa de proveedores adicionales (Photoshop, Illustrator, After Effects), aunque se prepararán sus interfaces vacías.

## 3. Requerimientos Técnicos Detallados

### Req 1: Parser Dinámico y Validación Estricta (Strict DSL)
* **Descripción:** El sistema debe abandonar los *mocks* de cadenas de texto y aceptar un JSON estructurado que defina escenas, actores y la línea de tiempo.
* **Especificaciones:**
  * Integrar **Zod** (o un validador JSON Schema equivalente) en el `IntentParser`.
  * Definir el esquema estricto del *Animation Intent* (ej. `Scene`, `Characters`, `AudioTracks`, `Actions`).
  * El Parser debe mapear dinámicamente este JSON validado y desglosarlo en múltiples `Operations`, inyectándolas en el `WorkflowGraphEngine` respetando las dependencias (ej. *Importar Audio* y *Crear Puppet* son paralelos, *Lip Sync* depende de ambos).

### Req 2: Integración "Caja Negra" (Layer 0 Commands)
* **Descripción:** Al carecer Character Animator de una API oficial, el `CharacterAnimatorProvider` y el puente `adobe-mcp` deben operar a nivel de sistema operativo y manipulación de archivos.
* **Especificaciones:**
  * **Manipulación de Proyectos:** El motor debe clonar una carpeta/plantilla base `.chproj` para iniciar un proyecto nuevo y modificar la estructura de directorios internos (copiar puppets y audios directamente a las carpetas `Ch Media` o similares si aplica).
  * **Automatización de SO (Macros):** Usar librerías nativas en el puente Python para forzar el foco en la ventana de Character Animator e inyectar secuencias de teclas (ej. `CTRL+E` para exportar, `CTRL+I` para importar).
  * **(Opcional/Investigación):** Explorar el uso de After Effects (vía *Dynamic Link*) como "troyano" para comandar Character Animator si ExtendScript en AE lo permite.

### Req 3: Capa de Percepción Física (Real Perception Layer)
* **Descripción:** El *Observed State* ya no será un booleano falso, sino el resultado de un escaneo de eventos del sistema.
* **Especificaciones:**
  * Implementar un `FileSystemObserver` dentro de la Perception Layer.
  * **Validación de Importación:** Verificar que un archivo (ej. `.puppet`) copiado en la ruta del proyecto adquiera el lock del sistema o genere los archivos temporales correspondientes.
  * **Validación de Exportación:** Monitorear la carpeta de salida (Outbox). El estado cambiará de `EXECUTING` a `SUCCESS` solo cuando el archivo de video final se cree y su tamaño en bytes deje de incrementar (indicando que el render finalizó).

## 4. Criterios de Aceptación (AC)

* **AC-07 (DSL Dinámico):**
  * **Dado:** El servidor MCP corriendo.
  * **Cuando:** La IA envía un JSON estructurado con 1 personaje, 1 audio y la acción "lip_sync".
  * **Entonces:** Zod valida el JSON, el Parser crea un DAG con al menos 3 nodos (Import Puppet, Import Audio, Compute LipSync), y el motor los ejecuta respetando la asincronía.

* **AC-08 (Manipulación Layer 0):**
  * **Dado:** Una petición para iniciar un nuevo proyecto de animación.
  * **Cuando:** El motor ejecuta el nodo `project.create`.
  * **Entonces:** El sistema clona exitosamente un archivo `.chproj` en el disco local, lanza el ejecutable de Adobe Character Animator apuntando a ese proyecto, y la aplicación se abre en pantalla.

* **AC-09 (Percepción por Sistema de Archivos):**
  * **Dado:** El motor ejecutando un nodo `render.export`.
  * **Cuando:** El macro de teclado inyecta el comando de renderizado.
  * **Entonces:** La Perception Layer entra en un ciclo de `polling` (observando el disco). Solo reporta `SUCCESS` cuando detecta el archivo `.mp4` en el directorio de salida y verifica que el archivo ha liberado el *lock* de escritura del sistema operativo.

## 5. Entregables de la Iteración 3
1. **Módulo Zod/Parser:** Esquemas validados y lógica de construcción dinámica del DAG.
2. **Scripts Python OS-Level:** Extensión en `adobe-mcp` para clonar proyectos `.chproj` y gestionar ventana/teclado.
3. **Inspectores de Disco:** Clases utilitarias en Node.js o Python para vigilar cambios de archivos, pesos y *locks*.
