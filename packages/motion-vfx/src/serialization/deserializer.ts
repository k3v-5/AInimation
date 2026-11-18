import { Composition } from "../core/composition.js";
import { Layer } from "../core/layer.js";
import { Property } from "../core/property.js";
import { EasingName } from "../core/types.js";
import { ElementFactory } from "../elements/index.js";
import { SerializationError } from "../errors/index.js";
import { validateId, validateNonNegativeNumber, validatePositiveNumber, validateTime } from "../validation/validators.js";
import { SerializedCompositionData, SerializedLayer, SerializedProject, SerializedProperty } from "./serializer.js";

const VALID_EASINGS = new Set<string>(["linear", "easeIn", "easeOut", "easeInOut"]);

/**
 * Deserializa una propiedad animable desde su representación JSON.
 */
export function deserializeProperty(data: unknown, propName: string): Property<unknown> {
  if (!data || typeof data !== "object") {
    throw new SerializationError(`Property '${propName}' must be an object.`);
  }

  const serialized = data as Partial<SerializedProperty>;
  if (serialized.baseValue === undefined || serialized.baseValue === null) {
    throw new SerializationError(`Property '${propName}' is missing required 'baseValue'.`);
  }

  const prop = new Property<unknown>(serialized.baseValue);

  if (Array.isArray(serialized.keyframes)) {
    for (let i = 0; i < serialized.keyframes.length; i++) {
      const kf = serialized.keyframes[i];
      if (!kf || typeof kf !== "object") {
        throw new SerializationError(`Keyframe at index ${i} in property '${propName}' is malformed.`);
      }
      const time = validateTime(kf.time, `keyframe.time in '${propName}'`);
      if (kf.value === undefined || kf.value === null) {
        throw new SerializationError(`Keyframe at time ${time} in property '${propName}' has null or undefined value.`);
      }
      let easing: EasingName | undefined;
      if (kf.easing !== undefined) {
        if (typeof kf.easing !== "string" || !VALID_EASINGS.has(kf.easing)) {
          throw new SerializationError(`Invalid easing '${String(kf.easing)}' at time ${time} in '${propName}'.`);
        }
        easing = kf.easing as EasingName;
      }
      prop.addKeyframe({
        time,
        value: kf.value,
        easing,
        spatialIn: kf.spatialIn,
        spatialOut: kf.spatialOut,
        spatialInterpolation: kf.spatialInterpolation,
      });
    }
  }

  return prop;
}

/**
 * Deserializa una capa desde su representación JSON (Fase 1).
 */
export function deserializeLayer(data: unknown): Layer {
  if (!data || typeof data !== "object") {
    throw new SerializationError("Layer data must be an object.");
  }

  const rawLayer = data as Partial<SerializedLayer>;
  const id = validateId(rawLayer.id, "layer.id");
  const name = rawLayer.name || id;
  const startTime = validateNonNegativeNumber(rawLayer.startTime ?? 0, "layer.startTime");
  const endTime =
    rawLayer.endTime === undefined || rawLayer.endTime === Infinity || rawLayer.endTime === null
      ? Infinity
      : validateNonNegativeNumber(rawLayer.endTime, "layer.endTime");

  const layer = new Layer({ id, name, startTime, endTime });

  if (rawLayer.properties && typeof rawLayer.properties === "object") {
    for (const [propName, propData] of Object.entries(rawLayer.properties)) {
      const deserializedProp = deserializeProperty(propData, propName);
      const layerProps = layer.getProperties();
      layerProps.set(propName, deserializedProp);
    }
  }

  return layer;
}

/**
 * Deserializa una composición completa desde un JSON del formato Motion Engine (soporta v0.1.0 y v0.2.0).
 */
export function deserializeComposition(data: unknown): Composition {
  if (!data || typeof data !== "object") {
    throw new SerializationError("Root project data must be a JSON object.");
  }

  const project = data as Partial<SerializedProject>;

  // Validar versión de esquema
  if (!project.schemaVersion) {
    throw new SerializationError("Missing 'schemaVersion' in JSON data.");
  }
  if (project.schemaVersion !== "0.1.0" && project.schemaVersion !== "0.2.0") {
    throw new SerializationError(`Unsupported schemaVersion '${project.schemaVersion}'. Expected '0.1.0' or '0.2.0'.`);
  }

  if (!project.composition || typeof project.composition !== "object") {
    throw new SerializationError("Missing 'composition' object in project data.");
  }

  const rawComp = project.composition as Partial<SerializedCompositionData>;
  const id = rawComp.id ? validateId(rawComp.id, "composition.id") : undefined;
  const name = rawComp.name;
  const width = validatePositiveNumber(rawComp.width, "composition.width");
  const height = validatePositiveNumber(rawComp.height, "composition.height");
  const fps = validatePositiveNumber(rawComp.fps, "composition.fps");
  const duration = validateNonNegativeNumber(rawComp.duration, "composition.duration");

  const composition = new Composition({ id, name, width, height, fps, duration });

  // 1. Deserializar Assets (v0.2.0)
  if (Array.isArray(project.assets)) {
    for (const asset of project.assets) {
      composition.assets.add(asset);
    }
  }

  // 2. Deserializar Elements (v0.2.0)
  if (Array.isArray(project.elements)) {
    for (const elementData of project.elements) {
      const element = ElementFactory.fromJSON(elementData, composition.assets);
      composition.addElement(element);
    }
  }

  // 3. Deserializar Layers (v0.1.0 backward compatibility)
  if (Array.isArray(rawComp.layers)) {
    for (const layerData of rawComp.layers) {
      const layer = deserializeLayer(layerData);
      composition.addLayer(layer);
    }
  }

  return composition;
}
