# Especificación de API: Fase 2 — Element Model API Reference

**Documento:** `spec/elements-api.md`  
**Estado:** VIGENTE / CONGELADO  
**Versión:** `0.2.0`

---

## 1. Módulo Matemático y Transform (`src/math/matrix2d.ts`, `src/elements/transform.ts`)

### 1.1. Matriz Afín 2D (`Matrix2D`)
Representa una matriz de transformación afín $3 \times 3$ en coordenadas homogéneas:
$$\begin{pmatrix} a & c & tx \\ b & d & ty \\ 0 & 0 & 1 \end{pmatrix}$$
- `Matrix2D.identity()`
- `Matrix2D.translation(tx, ty)`
- `Matrix2D.rotation(degrees)`
- `Matrix2D.scale(sx, sy)`
- `Matrix2D.multiply(m1, m2)`
- `Matrix2D.transformPoint(m, point: Vector2): Vector2`

### 1.2. Clase `Transform`
```typescript
export interface TransformOptions {
  position?: Vector2;
  scale?: Vector2;
  rotation?: number;
  opacity?: number;
  anchorPoint?: Vector2;
}

export interface EvaluatedTransform {
  position: Vector2;
  scale: Vector2;
  rotation: number;
  opacity: number;
  anchorPoint: Vector2;
  localMatrix: Matrix2D;
  worldMatrix: Matrix2D;
  worldOpacity: number;
}
```

---

## 2. Sistema de Recursos (`src/assets/`)

```typescript
export interface AssetMetadata {
  width?: number;
  height?: number;
  duration?: number;
  fps?: number;
  sampleRate?: number;
  channels?: number;
  [key: string]: unknown;
}

export interface AssetReference {
  id: string;
  type: "image" | "video" | "audio";
  path?: string;
  metadata?: AssetMetadata;
}

export class AssetRegistry {
  add(asset: AssetReference): void;
  remove(id: string): boolean;
  get(id: string): AssetReference | undefined;
  has(id: string): boolean;
  list(): AssetReference[];
}
```

---

## 3. Jerarquía de Elementos (`src/elements/`)

### 3.1. `BaseElement`
```typescript
export type ElementType = "text" | "image" | "video" | "audio" | "shape" | "group";

export interface BaseElementOptions {
  id?: string;
  name?: string;
  startTime?: Time;
  endTime?: Time;
  enabled?: boolean;
}

export interface BaseElementState {
  id: string;
  name: string;
  type: ElementType;
  active: boolean;
}

export abstract class BaseElement {
  readonly id: string;
  name: string;
  startTime: Time;
  endTime: Time;
  enabled: boolean;
  abstract readonly type: ElementType;

  isActive(time: Time): boolean;
  abstract evaluate(time: Time, parentTransform?: EvaluatedTransform): BaseElementState;
}
```

### 3.2. `VisualElement`
```typescript
export abstract class VisualElement extends BaseElement {
  transform: Transform;
}
```

### 3.3. `TextElement`
```typescript
export type TextAlignment = "left" | "center" | "right";

export interface TextElementOptions extends BaseElementOptions {
  text?: string;
  fontFamily?: string;
  fontSize?: number;
  fontWeight?: number;
  color?: Color;
  alignment?: TextAlignment;
  lineHeight?: number;
  letterSpacing?: number;
}

export class TextElement extends VisualElement {
  readonly type = "text";
  text: Property<string>;
  fontFamily: string;
  fontSize: Property<number>;
  fontWeight: number;
  color: Property<Color>;
  alignment: TextAlignment;
  lineHeight: Property<number>;
  letterSpacing: Property<number>;
}
```

### 3.4. `ImageElement`
```typescript
export interface ImageElementOptions extends BaseElementOptions {
  source: AssetReference | string; // Objeto o ID de asset
}

export class ImageElement extends VisualElement {
  readonly type = "image";
  source: AssetReference;
}
```

### 3.5. `VideoElement`
```typescript
export interface VideoElementOptions extends BaseElementOptions {
  source: AssetReference | string;
  sourceStartTime?: Time;
  sourceEndTime?: Time;
  playbackRate?: number;
  loop?: boolean;
}

export class VideoElement extends VisualElement {
  readonly type = "video";
  source: AssetReference;
  sourceStartTime: Time;
  sourceEndTime?: Time;
  playbackRate: Property<number>;
  loop: boolean;

  getSourceTime(compTime: Time): Time;
}
```

### 3.6. `AudioElement`
```typescript
export interface AudioElementOptions extends BaseElementOptions {
  source: AssetReference | string;
  volume?: number;
  playbackRate?: number;
}

export class AudioElement extends BaseElement {
  readonly type = "audio";
  source: AssetReference;
  volume: Property<number>;
  playbackRate: Property<number>;
}
```

### 3.7. `ShapeElement`
```typescript
export type ShapeType = "rectangle" | "ellipse" | "line";

export interface RectangleShapeData {
  width: number;
  height: number;
  cornerRadius: number;
}

export interface EllipseShapeData {
  width: number;
  height: number;
}

export interface LineShapeData {
  start: Vector2;
  end: Vector2;
}

export class ShapeElement extends VisualElement {
  readonly type = "shape";
  shapeType: ShapeType;
  shapeData: RectangleShapeData | EllipseShapeData | LineShapeData;
  fill: Property<Color>;
  stroke: Property<Color>;
  strokeWidth: Property<number>;
}
```

### 3.8. `GroupElement`
```typescript
export class GroupElement extends VisualElement {
  readonly type = "group";
  children: BaseElement[];

  addElement(element: BaseElement): void;
  removeElement(id: string): boolean;
  getElement(id: string): BaseElement | undefined;
}
```
