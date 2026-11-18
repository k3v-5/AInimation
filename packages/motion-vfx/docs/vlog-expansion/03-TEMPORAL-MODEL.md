# Temporal Model — Vlog Intelligence Engine

**Documento:** `03-TEMPORAL-MODEL.md`  
**Versión:** `1.0.0`  
**Sistema:** Motor audiovisual v3.4.0 + Vlog Multilingual Expansion  
**Estado:** DRAFT  
**Implementación autorizada:** NO hasta aprobación  
**Dependencias:** `00-MASTER-SPECIFICATION.md`, `01-ARCHITECTURE.md`, `02-DATA-CONTRACTS.md`  

---

## 1. Propósito

Este documento establece la semántica temporal única de la expansión.

Define:
- representación del tiempo.
- intervalos.
- frames.
- subframes.
- precisión.
- redondeo.
- cuantización.
- duración.
- solapamientos.
- cortes.
- silencios.
- crossfades.
- speed ramps.
- time remapping.
- punch-ins.
- sincronización de voz.
- sincronización multilingüe.
- reglas de tolerancia.
- invariantes.
- resolución de conflictos temporales.

Todos los módulos deberán utilizar este modelo.

---

## 2. Principio fundamental

El motor tendrá una única representación lógica del tiempo:
$$\text{segundos reales}$$

Los frames serán una representación derivada.

Por tanto:
$$\text{TIME} \longrightarrow \text{FRAME}$$
y nunca:
$$\text{FRAME} \longrightarrow \text{TIME}$$
como fuente primaria del dominio.

---

## 3. Intervalos

Todos los intervalos utilizarán:
$$[t_{\text{start}}, t_{\text{end}})$$

Esto significa:
- `start` incluido
- `end` excluido

Ejemplo:
$$[2.000, 3.000)$$
representa exactamente un segundo.

---

## 4. Duración

Para cualquier intervalo válido:
$$\text{duration} = \text{end} - \text{start}$$

Siempre:
$$\text{duration} \ge 0$$

No se permitirá almacenar una duración incompatible con `start` y `end`.

---

## 5. Intervalos consecutivos

Dos segmentos pueden ser perfectamente adyacentes:
$$A = [0, 2), \quad B = [2, 5)$$

Esto significa:
$$A.\text{end} \equiv B.\text{start}$$

No existe gap. No existe overlap.

---

## 6. Gap

Existe gap cuando:
$$A.\text{end} < B.\text{start}$$

La duración del gap será:
$$\text{gap} = B.\text{start} - A.\text{end}$$

---

## 7. Overlap

Existe overlap cuando:
$$A.\text{end} > B.\text{start}$$

La duración será:
$$\text{overlap} = A.\text{end} - B.\text{start}$$

Los overlaps no serán automáticamente errores; su validez dependerá del tipo de track.

---

## 8. Tiempo negativo

Ningún timestamp de dominio podrá ser negativo:
$$t \ge 0$$

Los valores negativos sólo podrán existir internamente en algoritmos intermedios si están expresamente documentados y deberán normalizarse antes de entrar al dominio.

---

## 9. Precisión

Los cálculos internos deberán conservar precisión suficiente para evitar errores acumulativos. No se deberá redondear cada operación.

*Incorrecto:*
$$\text{operación} \longrightarrow \text{round} \longrightarrow \text{operación} \longrightarrow \text{round}$$

*Correcto:*
$$\text{operaciones completas} \longrightarrow \text{cuantización final}$$

---

## 10. Comparación temporal

No se deberán comparar floats de tiempo únicamente mediante igualdad exacta cuando exista cálculo numérico. Deberá utilizarse una función equivalente a:
```typescript
approximatelyEqual(a, b, epsilon)
```
La tolerancia deberá estar centralizada.

---

## 11. Epsilon

La tolerancia temporal no podrá definirse de manera arbitraria por módulo. Deberá existir una configuración común.

Conceptualmente:
```typescript
interface TemporalTolerance {
  absolute: number;
  relative: number;
}
```
El valor definitivo deberá ser validado mediante tests contra el comportamiento del motor v3.4.0.

---

## 12. Frames

Un frame $n$ a FPS $F$ tendrá como instante inicial:
$$t = \frac{n}{F}$$

Su intervalo será:
$$\left[ \frac{n}{F}, \frac{n+1}{F} \right)$$

---

## 13. Frame index

El frame que contiene un timestamp $t$ se calculará mediante:
$$\text{frameIndex} = \lfloor t \cdot \text{FPS} \rfloor$$
siempre que $t \ge 0$.

---

## 14. Duración de frame

Para FPS constante:
$$\text{frameDuration} = \frac{1}{\text{FPS}}$$

Ejemplo conceptual:
$$30\text{ FPS} \longrightarrow 0.033333\dots \text{ segundos/frame}$$

---

## 15. Tiempo vs frame

Un timestamp puede caer entre dos límites de frame. El dominio no deberá destruir esa información.

Por tanto:
$$12.015\text{ s}$$
seguirá siendo:
$$12.015\text{ s}$$
aunque el proyecto utilice 30 FPS. La cuantización se realizará únicamente cuando el destino lo requiera.

---

## 16. Cuantización

Cuando After Effects o un formato de salida requiera límites discretos, se utilizará una operación explícita:
```typescript
quantize(time, fps, mode)
```
Los modos deberán definirse explícitamente:
- `FLOOR`
- `CEIL`
- `NEAREST`

Nunca deberá elegirse el modo implícitamente.

---

## 17. Regla de edición

El `EditPlan` conservará timestamps lógicos. La exportación será responsable de convertirlos a la representación temporal requerida por el destino.

---

## 18. Cambio de FPS

Un cambio de FPS no deberá alterar la duración lógica del contenido.

Ejemplo:
- `source:` 30 FPS, duration = 10.0s
- `target:` 60 FPS, duration = 10.0s

Sólo cambia la representación de frames.

---

## 19. Speed Factor

Un factor de velocidad positivo:
$$\text{speed} > 0$$
representa:
- $\text{speed} = 1.0$: velocidad normal.
- $\text{speed} = 2.0$: doble velocidad.
- $\text{speed} = 0.5$: media velocidad.

---

## 20. Duración bajo speed

Para un segmento de duración $D$:
$$\text{outputDuration} = \frac{D}{\text{speed}}$$
si no existen otras restricciones.

---

## 21. Speed = 0

No se permite $\text{speed} = 0$ como velocidad de reproducción. Un freeze-frame deberá representarse mediante un mecanismo de freeze explícito, no mediante $\text{speed} = 0$.

---

## 22. Speed negativo

La reproducción inversa no forma parte del alcance inicial. Por tanto:
$$\text{speed} < 0$$
deberá rechazarse salvo que una futura especificación habilite reverse playback.

---

## 23. Time Remapping

Una operación de time remap representa:
$$\text{sourceTime} = f(\text{outputTime})$$

La función deberá ser monotónica no decreciente para reproducción normal. No deberá existir un remapeo que produzca saltos temporales inesperados sin que el contrato lo permita.

---

## 24. Speed Ramp

Un speed ramp estará definido por segmentos de velocidad o una función continua:
$$\text{speed}(t)$$

La duración final deberá calcularse mediante la transformación temporal correspondiente, no mediante una simple multiplicación arbitraria.

---

## 25. Ramp Boundaries

Los cambios de velocidad deberán ser continuos o explícitamente discontinuos según el tipo.

Ejemplo:
$$1.0\text{x} \longrightarrow 2.0\text{x} \longrightarrow 0.5\text{x} \longrightarrow 1.0\text{x}$$

Cada cambio deberá tener timestamps y parámetros explícitos.

---

## 26. Jump Cut

Un Jump Cut elimina un intervalo:
$$\text{remove} = [t_{\text{start}}, t_{\text{end}})$$

El material posterior deberá desplazarse:
$$\text{shift} = t_{\text{end}} - t_{\text{start}}$$

Por tanto:
$$\text{sourceTime} \ge t_{\text{end}} \implies \text{outputTime} = \text{sourceTime} - \text{shift}$$

---

## 27. Múltiples Jump Cuts

Para múltiples eliminaciones:
$$R_1, R_2, R_3, \dots$$
las regiones deberán procesarse en orden temporal. Cada segmento deberá considerar el desplazamiento acumulado.

---

## 28. Regiones de eliminación

Dos regiones de eliminación:
$$A = [1, 2), \quad B = [2, 3)$$
pueden fusionarse:
$$[1, 3)$$
antes de aplicar el desplazamiento.

---

## 29. Overlapping removals

Si:
$$A = [1, 3), \quad B = [2, 4)$$
las regiones se deberán normalizar a:
$$[1, 4)$$
No se permitirá restar dos veces el mismo intervalo.

---

## 30. Silencio mínimo para eliminación

El `VlogJumpCutEngine` tendrá un threshold configurable.

Valor inicial:
$$\text{threshold} = 0.25\text{ s}$$

Regla:
$$\text{silence.duration} > \text{threshold}$$
podrá convertirse en candidato de eliminación.

La igualdad exacta:
$$\text{silence.duration} \equiv \text{threshold}$$
no será eliminada salvo que la configuración lo indique explícitamente.

---

## 31. Protección de palabras

Nunca se deberá cortar una palabra por defecto. Un silencio detectado deberá evaluarse respecto a:
$$\text{previousWord.end} \quad \text{y} \quad \text{nextWord.start}$$
El intervalo eliminado deberá respetar los límites lingüísticos.

---

## 32. Respiraciones

Una respiración podrá formar parte del intervalo eliminado únicamente si el algoritmo editorial determina que es prescindible. La detección acústica no equivale automáticamente a permiso de eliminación.

---

## 33. Crossfade

El crossfade editorial por defecto para Jump Cuts será:
$$10\text{ ms} \quad (0.010\text{ s})$$

---

## 34. Validación de crossfade

El crossfade deberá cumplir:
$$\text{crossfadeDuration} \ge 0$$
y no podrá exceder las duraciones disponibles de los segmentos implicados.

Si no existe material suficiente:
$$\text{fallback} = \text{hard cut}$$
o la estrategia explícita configurada. No se permitirá crear un crossfade inválido.

---

## 35. Crossfade y solapamiento

Un crossfade requiere solapamiento temporal controlado de los medios. Por tanto, el overlap generado por un crossfade será válido únicamente dentro del contexto de composición.

---

## 36. Punch-In

Un Punch-In será un cambio de escala/encuadre sobre un intervalo.

Valores iniciales:
- $\text{normal} = 1.00$
- $\text{punch} = 1.15$

---

## 37. Punch-In Timing

Un Punch-In deberá definir:
- `start`
- `end`
- `scale`
- `focusPoint`
- `easing`

El retorno a $1.00$ deberá ser explícito o derivable de la duración del evento.

---

## 38. Focus Point

Las coordenadas serán normalizadas:
$$x \in [0, 1], \quad y \in [0, 1]$$
El cambio de resolución no deberá modificar el punto lógico de interés.

---

## 39. Transiciones

Toda transición deberá tener:
- `type`
- `start`
- `end`
- `duration`

Una transición no podrá extenderse fuera de los límites válidos de los clips implicados.

---

## 40. Duración mínima de segmento

No se definirá un mínimo universal en este documento porque depende del tipo de contenido. Cada módulo deberá definir sus restricciones específicas.

Sin embargo:
$$\text{duration} > 0$$
será obligatorio para cualquier segmento que represente material reproducible.

---

## 41. Sincronización palabra/audio

Para una palabra:
$$\text{word} = [t_{\text{start}}, t_{\text{end}})$$
la duración será $t_{\text{end}} - t_{\text{start}}$. El audio localizado deberá mantener una relación temporal equivalente para su propia pista.

---

## 42. Localización

Cada idioma podrá producir una duración distinta. Por tanto:
$$\text{duration}(\text{es}) \ne \text{duration}(\text{en})$$
no constituye un error. La duración visual podrá adaptarse.

---

## 43. Anclaje semántico

Los elementos editoriales deberán poder anclarse a:
- `WORD`
- `SPEECH_SEGMENT`
- `SHOT`
- `TIMECODE`

Ejemplo:
```typescript
PunchIn: { anchor: speechSegmentId }
```

---

## 44. Pacing multilingüe

El motor deberá considerar:
- `masterDuration`
- `localizedVoiceDuration`
- `visualConstraints`

La reconciliación no deberá asumir una proporción lingüística fija. El supuesto:
$$\text{español} = \text{inglés} \times 1.20$$
podrá utilizarse como heurística inicial, pero nunca como regla matemática universal. La duración real de la locución será la fuente de verdad.

---

## 45. Voice Stretching

El rango inicial permitido será:
$$0.95\text{x} \le \text{stretch} \le 1.05\text{x}$$

Fuera de ese rango, el voice stretch no deberá aplicarse automáticamente. Deberá intentarse primero una estrategia visual alternativa.

---

## 46. Orden de adaptación

El algoritmo deberá poder aplicar una jerarquía configurable. Estrategia inicial:
1. Reasignar duración B-Roll
2. Extender/recortar clips compatibles
3. Reordenar candidatos equivalentes
4. Ajustar transiciones
5. Voice stretch $0.95\text{x} - 1.05\text{x}$
6. Declarar conflicto si no es posible

No se deberá deformar audio automáticamente más allá de los límites establecidos.

---

## 47. Conflicto temporal

Si no existe solución válida:
$$\text{TemporalConflictError}$$
deberá producirse. El sistema no deberá solucionar un conflicto mediante clipping silencioso.

---

## 48. Propagación temporal

Una modificación temporal deberá propagarse a los elementos dependientes:
$$\text{Jump Cut} \longrightarrow \text{A-Roll duration} \longrightarrow \text{B-Roll positions} \longrightarrow \text{Overlay positions} \longrightarrow \text{Audio events}$$

Los elementos anclados a contenido eliminado deberán resolverse mediante una política explícita.

---

## 49. Elementos eliminados

- Si un overlay está completamente dentro de una región eliminada: $\text{overlay} \longrightarrow \text{REMOVE}$.
- Si está parcialmente dentro: $\text{overlay} \longrightarrow \text{TRIM / REANCHOR}$ según su tipo.

La política concreta se definirá por tipo de overlay.

---

## 50. Anclajes

Los elementos podrán estar anclados a:
- `ABSOLUTE_TIME`: No cambia cuando cambia el montaje.
- `SOURCE_TIME`: Se relaciona con el material fuente.
- `EDIT_TIME`: Se mueve con el montaje.
- `ENTITY`: Se recalcula según el elemento semántico asociado.

---

## 51. Regla de prioridad

Cuando exista conflicto entre `source timing`, `edit timing` y `semantic anchor`, el contrato del objeto deberá indicar cuál tiene prioridad. No se deberá inferir.

---

## 52. Reencuadre

El reencuadre existente deberá continuar trabajando con el modelo temporal del core. Los nuevos Punch-Ins serán eventos compatibles con ese sistema. No deberá existir un segundo motor independiente de transformación espacial/temporal.

---

## 53. FPS Variable

El soporte específico para VFR deberá tratarse como una etapa de ingestión. El dominio editorial deberá trabajar sobre tiempo continuo. La conversión a una representación CFR, cuando sea necesaria, deberá producir metadata explícita.

---

## 54. Audio Sample Rate

El sample rate del audio no define el tiempo lógico del dominio. El tiempo seguirá expresándose en segundos. La conversión de samples:
$$\text{sampleIndex} / \text{sampleRate}$$
será responsabilidad del adaptador de audio.

---

## 55. Precisión de audio

Cuando un evento de audio deba alinearse con una muestra:
$$\text{sampleIndex} = \text{quantize}(\text{time} \cdot \text{sampleRate})$$
La operación deberá realizarse en la frontera del sistema de audio, no en el dominio editorial.

---

## 56. Freeze Frame

Un freeze frame deberá representarse explícitamente:
```typescript
interface FreezeFrame {
  sourceTime: number;
  outputRange: TimeRange;
}
```
No se representará como $\text{speed} = 0$.

---

## 57. Duración de Freeze Frame

La duración visual será independiente del instante fuente.

Ejemplo:
- `sourceTime` = 15.234
- `output` = [20.000, 21.500)

---

## 58. Time Stretch

El time stretch de voz deberá conservar los límites de calidad definidos por el módulo de audio. El factor no podrá modificarse silenciosamente para resolver un conflicto.

---

## 59. Orden de operaciones

Las transformaciones temporales deberán tener un orden determinista:

$$\text{SOURCE} \longrightarrow \text{SOURCE ANALYSIS} \longrightarrow \text{CUT / REMOVE} \longrightarrow \text{REMAP} \longrightarrow \text{EDITORIAL PLACEMENT} \longrightarrow \text{LOCALIZATION} \longrightarrow \text{PACING} \longrightarrow \text{OVERLAYS} \longrightarrow \text{EXPORT QUANTIZATION}$$

El orden exacto deberá ser respetado salvo especificación de una excepción.

---

## 60. No acumulación de errores

Las transformaciones no deberán calcularse sucesivamente sobre timestamps ya redondeados.

Preferido:
$$\text{original source time} + \text{transformations} = \text{final time}$$
en lugar de redondear recursivamente.

---

## 61. Invariantes temporales

Toda operación deberá preservar:
$$\text{start} \ge 0, \quad \text{end} \ge \text{start}, \quad \text{duration} = \text{end} - \text{start}$$
Además:
- `source references` válidas.
- no `NaN`, no `Infinity`.

---

## 62. Invariantes de speed

Siempre $\text{speed} > 0$ para reproducción normal.

---

## 63. Invariantes de factor

Para stretch: $\text{factor} > 0$. Para el auto voice-stretch inicial:
$$0.95 \le \text{factor} \le 1.05$$

---

## 64. Invariantes de coordenadas

$$0 \le x \le 1, \quad 0 \le y \le 1$$

---

## 65. Invariantes de duración total

Un `EditPlan` final deberá tener $\text{duration} \ge 0$ y todos los elementos deberán estar contenidos o explícitamente marcados como elementos fuera del timeline.

---

## 66. Timeline Validation

Antes de exportar deberá ejecutarse una validación temporal global. Deberá detectar:
- segmentos negativos.
- segmentos invertidos.
- NaN / Infinity.
- referencias temporales inválidas.
- crossfades imposibles.
- overlaps prohibidos.
- tracks incompatibles.
- elementos fuera del timeline.
- duración global incorrecta.

---

## 67. Property-Based Testing

Se deberán generar automáticamente intervalos aleatorios y comprobar:
$$\text{start} \ge 0, \quad \text{end} \ge \text{start}, \quad \text{duration} = \text{end} - \text{start}$$
También:
$$\text{merge}(A, B)$$
deberá preservar la cobertura temporal.

---

## 68. Property: Jump Cut

Para cualquier conjunto válido de regiones eliminadas:
$$\text{outputDuration} = \text{inputDuration} - \sum \text{uniqueRemovedDuration}$$
cuando no existan otros efectos temporales.

---

## 69. Property: Idempotencia de normalización

Aplicar normalización dos veces deberá producir el mismo resultado:
$$\text{normalize}(\text{normalize}(\text{ranges})) \equiv \text{normalize}(\text{ranges})$$

---

## 70. Property: FPS conversion

Convertir un tiempo a frame y volver a representar el intervalo deberá respetar el error de cuantización permitido.

---

## 71. Property: Speed

Para una duración positiva: $D / \text{speed}$ deberá ser positivo cuando $\text{speed} > 0$.

---

## 72. Property: Localization

La localización podrá modificar duración, pero no deberá producir `negative duration` ni timestamps fuera de los límites válidos.

---

## 73. Golden Tests

Deberán existir casos canónicos para:
- simple cut
- multiple cuts
- adjacent cuts
- overlapping cuts
- 10ms crossfade
- punch-in
- speed ramp
- freeze frame
- localized timing
- voice stretch

---

## 74. Caso límite: silencio de exactamente 250 ms

Con configuración inicial $\text{threshold} = 0.25$ y regla estricta $\text{duration} > \text{threshold}$:
$$\text{Un silencio de } 0.250\text{ s NO se elimina.}$$

---

## 75. Caso límite: silencio de 250.001 ms

Un silencio ligeramente superior al threshold será candidato:
$$0.250001\text{ s} > 0.25\text{ s}$$
La decisión final seguirá dependiendo de las reglas de protección editorial.

---

## 76. Caso límite: palabra pegada al silencio

Si:
$$\text{word.end} \equiv \text{silence.start}$$
la palabra queda intacta. Si existe una discrepancia inferior a la tolerancia temporal, se deberá aplicar la política central de epsilon.

---

## 77. Caso límite: video de duración cero

Un medio con $\text{duration} = 0$ no podrá producir segmentos reproducibles. Deberá rechazarse en ingestión si el formato de entrada exige contenido audiovisual.

---

## 78. Caso límite: overlay fuera del timeline

Un overlay que no pueda reconciliarse deberá producir `TemporalConflictError` o ser descartado únicamente si su política permite explícitamente `DROP`.

---

## 79. Caso límite: TTS demasiado largo

Si la voz localizada no cabe dentro de las restricciones visuales después de aplicar todas las estrategias permitidas:
$$\text{LocalizationTimingConflict}$$
deberá producirse.

---

## 80. Caso límite: TTS demasiado corto

El sistema podrá:
- prolongar B-Roll.
- añadir planos compatibles.
- extender ambient audio.
- ajustar silencios editoriales.

No deberá introducir pausas artificiales dentro de palabras.

---

## 81. Caso límite: FPS extremo

Los valores de FPS deberán validarse antes de entrar al dominio. $\text{FPS} \le 0$ será inválido. Los límites máximos deberán definirse en el contrato de ingestión.

---

## 82. Caso límite: floating-point drift

Las comparaciones cercanas a límites deberán utilizar la política central de tolerancia. Los tests deberán incluir casos donde $0.1 + 0.2$ no sea exactamente representable.

---

## 83. Prohibiciones

No se permitirá:
- usar frames como unidad primaria.
- redondear cada operación.
- cortar palabras sin autorización explícita.
- utilizar `speed = 0` para freeze.
- utilizar factores negativos para reverse.
- crear crossfades imposibles.
- modificar timestamps mediante truncamiento silencioso.
- ignorar conflictos temporales.
- asumir que todos los idiomas tienen la misma duración.

---

## 84. Definition of Done

- [ ] Unidad temporal definida
- [ ] Intervalos definidos
- [ ] FPS definido
- [ ] Frames definidos
- [ ] Subframes preservados
- [ ] Cuantización definida
- [ ] Epsilon definido conceptualmente
- [ ] Jump Cuts definidos
- [ ] Crossfade definido
- [ ] Punch-In definido
- [ ] Speed definido
- [ ] Time Remap definido
- [ ] Speed Ramp definido
- [ ] Freeze Frame definido
- [ ] Localization timing definido
- [ ] Voice stretch definido
- [ ] Anclajes definidos
- [ ] Propagación definida
- [ ] Conflictos definidos
- [ ] Invariantes definidos
- [ ] Property tests definidos
- [ ] Golden tests definidos
- [ ] Casos límite definidos

---

## 85. Estado del documento

**Documento:** `03-TEMPORAL-MODEL.md`  
**Versión:** `1.0.0`  
**Estado:** `DRAFT`  
**Implementación autorizada:** `NO`  

La implementación deberá esperar hasta que este documento sea aprobado.
