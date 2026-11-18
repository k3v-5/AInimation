# Documento de Requerimientos: Iteración 4 - Control Robótico (Cierre de P0)

## 1. Objetivo de la Iteración

Lograr el control absoluto y desatendido sobre Adobe Character Animator (P0). El sistema debe ser capaz de ejecutar comandos internos de la interfaz (como "Generar Lip Sync" o "Exportar Video") sin intervención humana, utilizando automatización a nivel de Sistema Operativo o puentes de *Dynamic Link*, cerrando oficialmente el flujo de valor de la primera aplicación objetivo.

## 2. Alcance

**Incluye:**
1. **Investigación Definitiva (Spike Layer 0):** Determinar y probar el método final de control robótico (Automatización de UI con `pyautogui`/`pywinauto` vs. Puente JSX a través de After Effects *Dynamic Link*).
2. **Motor de Macros (UI Automation):** Implementación de secuencias de teclado y ratón precisas para desencadenar acciones en Character Animator.
3. **Calibración de Foco y Tiempos:** Sistema de *delays* inteligentes y validación de foco de ventana (Window Handle) para asegurar que los comandos del OS impacten en la aplicación correcta.

**No incluye (Desplazado a Fase 5):**
* Ejecución nativa de flujos en Photoshop e Illustrator.
* Paso de contexto automático entre múltiples aplicaciones (Multi-App Orchestration).

## 3. Requerimientos Técnicos Detallados

### Req 1: Definición e Implementación del Puente de Control
* **Descripción:** El script debe ser capaz de manipular la interfaz de Character Animator.
* **Especificaciones:**
  * Implementar un módulo de automatización en Python.
  * Si se elige `pyautogui`/`pywinauto`: El script debe ser capaz de encontrar la ventana activa por su nombre de proceso (`Character Animator.exe` / `Character Animator.app`), traerla al frente (Focus) y ejecutar secuencias de atajos de teclado (ej. `Timeline > Compute Lip Sync from Scene Audio`).
  * Si se elige *Dynamic Link* (AE Bridge): Configurar un script ExtendScript (.jsx) que se comunique con After Effects, importe el proyecto `.chproj` dinámicamente y renderice desde AE, saltándose la UI de Character Animator por completo.

### Req 2: Secuencias de Comandos Estandarizadas (Operation DSL)
* **Descripción:** Traducir los nodos del DAG a las rutinas de macros correspondientes.
* **Especificaciones:**
  * Crear una librería de macros para las operaciones P0:
    * `ch.import_audio`
    * `ch.compute_lip_sync`
    * `ch.export_video`
  * Cada macro debe incluir un mecanismo de *fallback* si el atajo de teclado no responde (ej. reintento de inyección de teclas tras 500ms).

### Req 3: Resiliencia de la Interfaz (UI State Validation)
* **Descripción:** La automatización de UI es inherentemente frágil. El sistema debe asegurar que está en el estado correcto antes de teclear.
* **Especificaciones:**
  * Antes de ejecutar una macro, el sistema debe confirmar que Character Animator es la ventana activa (`ActiveWindow` en el OS).
  * El motor no debe enviar atajos de teclado mientras otro proceso intensivo (ej. un renderizado en curso) tenga congelada la UI de la aplicación.

## 4. Criterios de Aceptación (AC)

* **AC-10 (Control Robótico de Lip Sync):**
  * **Dado:** Un proyecto de Character Animator abierto mediante el nodo `project.create`.
  * **Cuando:** El DAG ejecuta el nodo `ch.compute_lip_sync`.
  * **Entonces:** El motor enfoca la ventana de Character Animator, inyecta la secuencia de atajos correspondiente, y la aplicación genera los *visemas* en la línea de tiempo sin requerir un solo clic del usuario.

* **AC-11 (Exportación Desatendida):**
  * **Dado:** Una animación lista en la línea de tiempo de Character Animator.
  * **Cuando:** El nodo `ch.export_video` se vuelve activo en el DAG.
  * **Entonces:** El motor ejecuta los atajos de exportación (ej. invocar Adobe Media Encoder o exportación rápida), define la ruta de salida (hacia la carpeta de Artifacts configurada) y la capa de percepción física valida el archivo `.mp4` resultante.

* **AC-12 (Prevención de Errores de Foco):**
  * **Dado:** El motor a punto de inyectar una macro de teclado.
  * **Cuando:** El usuario final cambia el foco a su navegador web (Chrome) justo antes de la inyección.
  * **Entonces:** El módulo de automatización detecta que Character Animator ya no tiene el foco, pausa la ejecución, intenta recuperar el foco de la aplicación y solo inyecta las teclas cuando es seguro hacerlo.
