import { cloneValue, detectValueType } from "../animation/interpolation.js";
import { Asset } from "../assets/index.js";
import { Composition } from "../core/composition.js";
import { Layer } from "../core/layer.js";
import { Property } from "../core/property.js";
import { EasingName, PropertyTypeName, SpatialInterpolationType, SpatialTangent, Time } from "../core/types.js";
import {
  AudioElement,
  BaseElement,
  GroupElement,
  ImageElement,
  ShapeElement,
  TextElement,
  VideoElement,
} from "../elements/index.js";
import { Transform } from "../transform/index.js";

export interface SerializedKeyframe {
  time: Time;
  value: unknown;
  easing?: EasingName;
  spatialIn?: SpatialTangent;
  spatialOut?: SpatialTangent;
  spatialInterpolation?: SpatialInterpolationType;
}

export interface SerializedProperty {
  type: PropertyTypeName;
  baseValue: unknown;
  keyframes: SerializedKeyframe[];
}

export interface SerializedLayer {
  id: string;
  name: string;
  startTime: Time;
  endTime: Time;
  properties: Record<string, SerializedProperty>;
}

export interface SerializedCompositionData {
  id: string;
  name: string;
  width: number;
  height: number;
  fps: number;
  duration: Time;
  layers?: SerializedLayer[];
}

export interface SerializedProject {
  schemaVersion: "0.1.0" | "0.2.0";
  composition: SerializedCompositionData;
  assets?: Asset[];
  elements?: Record<string, any>[];
}

/**
 * Serializa una propiedad animable a un objeto plano JSON.
 */
export function serializeProperty(property: Property<unknown>): SerializedProperty {
  const baseValue = property.getValue();
  const keyframes = property.getKeyframes();
  const type = detectValueType(baseValue);

  return {
    type,
    baseValue: cloneValue(baseValue),
    keyframes: keyframes.map((k) => ({
      time: k.time,
      value: cloneValue(k.value),
      ...(k.easing ? { easing: k.easing } : {}),
      ...(k.spatialIn ? { spatialIn: cloneValue(k.spatialIn) } : {}),
      ...(k.spatialOut ? { spatialOut: cloneValue(k.spatialOut) } : {}),
      ...(k.spatialInterpolation ? { spatialInterpolation: k.spatialInterpolation } : {}),
    })),
  };
}

/**
 * Serializa el sistema de Transformación.
 */
export function serializeTransform(transform: Transform): Record<string, SerializedProperty> {
  return {
    position: serializeProperty(transform.position as any),
    scale: serializeProperty(transform.scale as any),
    rotation: serializeProperty(transform.rotation as any),
    opacity: serializeProperty(transform.opacity as any),
    anchorPoint: serializeProperty(transform.anchorPoint as any),
  };
}

/**
 * Serializa un elemento individual de la jerarquía de Element Model.
 */
export function serializeElement(element: BaseElement): Record<string, any> {
  const baseData = {
    id: element.id,
    name: element.name,
    type: element.type,
    startTime: element.startTime,
    duration: element.duration,
    visible: element.visible,
    parentId: element.parentId,
    transform: serializeTransform(element.transform),
  };

  switch (element.type) {
    case "text": {
      const textElem = element as TextElement;
      return {
        ...baseData,
        text: textElem.text.getValue(),
        properties: {
          text: serializeProperty(textElem.text),
        },
        style: cloneValue(textElem.style),
      };
    }

    case "image": {
      const imgElem = element as ImageElement;
      return {
        ...baseData,
        assetId: imgElem.assetId,
      };
    }

    case "video": {
      const vidElem = element as VideoElement;
      return {
        ...baseData,
        assetId: vidElem.assetId,
        sourceStartTime: vidElem.sourceStartTime,
      };
    }

    case "audio": {
      const audElem = element as AudioElement;
      return {
        ...baseData,
        assetId: audElem.assetId,
        sourceStartTime: audElem.sourceStartTime,
        volume: audElem.volume.getValue(),
        properties: {
          volume: serializeProperty(audElem.volume),
        },
      };
    }

    case "shape": {
      const shapeElem = element as ShapeElement;
      return {
        ...baseData,
        shapeType: shapeElem.shapeType,
        shapeData: cloneValue(shapeElem.shapeData),
        style: cloneValue(shapeElem.style),
      };
    }

    case "group": {
      const groupElem = element as GroupElement;
      return {
        ...baseData,
        children: groupElem.getChildren().map((c: BaseElement) => serializeElement(c)),
      };
    }

    default:
      return baseData;
  }
}

/**
 * Serializa una capa individual a un objeto plano JSON (Fase 1).
 */
export function serializeLayer(layer: Layer): SerializedLayer {
  const properties: Record<string, SerializedProperty> = {};

  const sortedKeys = Array.from(layer.getProperties().keys()).sort();
  for (const key of sortedKeys) {
    const prop = layer.getProperties().get(key);
    if (prop) {
      properties[key] = serializeProperty(prop);
    }
  }

  return {
    id: layer.id,
    name: layer.name,
    startTime: layer.startTime,
    endTime: layer.endTime,
    properties,
  };
}

/**
 * Serializa una composición completa al formato oficial Motion Engine.
 */
export function serializeComposition(composition: Composition): SerializedProject {
  const elements = composition.getElements();
  const layers = composition.getLayers();
  const assets = composition.assets.list();

  // Si tiene elementos de Fase 2, se serializa como v0.2.0
  if (elements.length > 0 || assets.length > 0) {
    return {
      schemaVersion: "0.2.0",
      composition: {
        id: composition.id,
        name: composition.name,
        width: composition.width,
        height: composition.height,
        fps: composition.fps,
        duration: composition.duration,
      },
      assets,
      elements: elements.map((e) => serializeElement(e)),
    };
  }

  // Si solo tiene capas de Fase 1, se preserva compatibilidad v0.1.0
  return {
    schemaVersion: "0.1.0",
    composition: {
      id: composition.id,
      name: composition.name,
      width: composition.width,
      height: composition.height,
      fps: composition.fps,
      duration: composition.duration,
      layers: layers.map((l) => serializeLayer(l)),
    },
  };
}
