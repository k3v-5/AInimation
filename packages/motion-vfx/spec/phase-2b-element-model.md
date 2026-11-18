# Especificación Técnica: Fase 2B — Element Model

**Documento:** `spec/phase-2b-element-model.md`  
**Estado:** VIGENTE / CONGELADO  
**Versión de Arquitectura:** `0.2.0-2B`

---

## 0. Propósito y Alcance

La **Fase 2B** implementa el modelo de entidades audiovisuales que transforma el Core Temporal en un sistema capaz de representar composiciones reales de motion graphics:

```
Composition 1080×1920
│
├── Background (ShapeElement)
├── MainVideo (VideoElement)
├── TitleGroup (GroupElement)
│   ├── TextElement
│   └── ShapeElement
├── Logo (ImageElement)
└── Music (AudioElement)
```

---

## 1. Principios Arquitectónicos e Invariantes

1. **El Core no renderiza píxeles:** Un `TextElement` describe texto y tipografía, pero no lo rasteriza. Un `VideoElement` y `ImageElement` describen el recurso y tiempo de fuente, pero no decodifican buffers.
2. **Jerarquía Unificada y Tipada:**
   - Todos los elementos derivan de `BaseElement`.
   - Cada tipo concreto posee exclusivamente sus propiedades especializadas (sin objetos monolíticos con campos opcionales no tipados).
3. **Identidad Estable:** `id` es único e inmutable; modificar el `name` humano nunca altera el `id`.
4. **Timing de Intervalo $[ \text{startTime}, \text{startTime} + \text{duration} )$:**
   - `startTime`: Segundo de inicio global ($\ge 0$).
   - `duration`: Duración del elemento en segundos ($> 0$).
   - `getLocalTime(globalTime)` $= \text{globalTime} - \text{startTime}$.
   - `isActive(globalTime)` $\iff \text{visible} \land (\text{globalTime} \ge \text{startTime}) \land (\text{globalTime} < \text{startTime} + \text{duration})$.
5. **Visibilidad vs Opacidad:**
   - `visible: boolean` (Habilitado/Deshabilitado en la composición).
   - `opacity: Property<number>` (Grado de transparencia $[0.0, 1.0]$).
6. **Clonado con ID Determinista:** `element.clone()` genera una copia profunda con un nuevo ID único generado de forma determinista.
7. **Pila de Apilamiento (Stacking Order) Separada del Parenting:**
   - Parenting determina el árbol de transformaciones espaciales ($M_{\text{world}}$).
   - Stacking order (`moveBefore`, `moveAfter`, `bringToFront`, `sendToBack`) determina el orden de dibujado en la composición.

---

## 2. Tipos de Elementos y Estructura

### 2.1. `BaseElement`
```typescript
abstract class BaseElement {
  readonly id: string;
  name: string;
  abstract readonly type: ElementType;
  startTime: number;
  duration: number;
  visible: boolean;
  transform: Transform;
  parentId?: string;

  getLocalTime(globalTime: number): number;
  isActive(globalTime: number): boolean;
  abstract clone(): BaseElement;
  abstract evaluate(globalTime: number, parentTransform?: EvaluatedTransform): EvaluatedElement;
}
```

### 2.2. `TextElement`
```typescript
interface TextStyle {
  fontFamily: string;
  fontSize: number;
  fontWeight: number;
  color: Color;
  lineHeight: number;
  letterSpacing: number;
  textAlign: "left" | "center" | "right";
}

class TextElement extends BaseElement {
  readonly type = "text";
  text: string;
  style: TextStyle;
}
```

### 2.3. `ImageElement`
```typescript
class ImageElement extends BaseElement {
  readonly type = "image";
  assetId: string;
}
```

### 2.4. `VideoElement`
```typescript
class VideoElement extends BaseElement {
  readonly type = "video";
  assetId: string;
  sourceStartTime: number; // Offset de inicio en el video fuente
}
```

### 2.5. `AudioElement`
```typescript
class AudioElement extends BaseElement {
  readonly type = "audio";
  assetId: string;
  sourceStartTime: number;
  volume: Property<number>; // Animable para fades de volumen
}
```

### 2.6. `ShapeElement`
```typescript
type ShapeType = "rectangle" | "ellipse" | "line";

interface ShapeStyle {
  fill?: Color;
  stroke?: Color;
  strokeWidth?: number;
}

class ShapeElement extends BaseElement {
  readonly type = "shape";
  shapeType: ShapeType;
  shapeData: RectangleShapeData | EllipseShapeData | LineShapeData;
  style: ShapeStyle;
}
```

### 2.7. `GroupElement`
```typescript
class GroupElement extends BaseElement {
  readonly type = "group";
  addChild(element: BaseElement): void;
  removeChild(id: string): boolean;
  getChild(id: string): BaseElement | undefined;
  getChildren(): BaseElement[];
}
```

---

## 3. ElementFactory
```typescript
class ElementFactory {
  static createText(options: TextOptions): TextElement;
  static createImage(options: ImageOptions): ImageElement;
  static createVideo(options: VideoOptions): VideoElement;
  static createAudio(options: AudioOptions): AudioElement;
  static createShape(options: ShapeOptions): ShapeElement;
  static createGroup(options: GroupOptions): GroupElement;
  static fromJSON(data: unknown, registry?: AssetRegistry): BaseElement;
}
```
