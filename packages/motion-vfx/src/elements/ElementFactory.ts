import { AssetRegistry } from "../assets/index.js";
import { SerializationError, ValidationError } from "../errors/index.js";
import { deserializeProperty } from "../serialization/deserializer.js";
import { AudioElement, AudioElementOptions } from "./AudioElement.js";
import { BaseElement } from "./BaseElement.js";
import { GroupElement, GroupElementOptions } from "./GroupElement.js";
import { ImageElement, ImageElementOptions } from "./ImageElement.js";
import { ShapeElement, ShapeElementOptions } from "./ShapeElement.js";
import { TextElement, TextElementOptions } from "./TextElement.js";
import { VideoElement, VideoElementOptions } from "./VideoElement.js";

/**
 * Fábrica polimórfica para la instanciación y reconstrucción de elementos audiovisuales.
 */
export class ElementFactory {
  public static createText(options: TextElementOptions = {}): TextElement {
    return new TextElement(options);
  }

  public static createImage(options: ImageElementOptions): ImageElement {
    return new ImageElement(options);
  }

  public static createVideo(options: VideoElementOptions): VideoElement {
    return new VideoElement(options);
  }

  public static createAudio(options: AudioElementOptions): AudioElement {
    return new AudioElement(options);
  }

  public static createShape(options: ShapeElementOptions): ShapeElement {
    return new ShapeElement(options);
  }

  public static createGroup(options: GroupElementOptions = {}): GroupElement {
    return new GroupElement(options);
  }

  /**
   * Reconstruye un elemento concreto a partir de una estructura serializada JSON.
   */
  public static fromJSON(raw: any, assetRegistry?: AssetRegistry): BaseElement {
    if (!raw || typeof raw !== "object") {
      throw new SerializationError("Element JSON must be an object.");
    }

    const { id, name, type, startTime, duration, visible, parentId, transform: rawTransform } = raw;

    if (!type || typeof type !== "string") {
      throw new SerializationError("Missing or invalid 'type' in element JSON.");
    }

    // Helper para aplicar transform deserializado
    const applyTransform = (elem: BaseElement) => {
      if (rawTransform) {
        if (rawTransform.position) elem.transform.position = deserializeProperty(rawTransform.position, "position") as any;
        if (rawTransform.scale) elem.transform.scale = deserializeProperty(rawTransform.scale, "scale") as any;
        if (rawTransform.rotation) elem.transform.rotation = deserializeProperty(rawTransform.rotation, "rotation") as any;
        if (rawTransform.opacity) elem.transform.opacity = deserializeProperty(rawTransform.opacity, "opacity") as any;
        if (rawTransform.anchorPoint) elem.transform.anchorPoint = deserializeProperty(rawTransform.anchorPoint, "anchorPoint") as any;
      }
      return elem;
    };

    // Helper para validar asset
    const validateAssetRef = (assetId: string) => {
      if (!assetId) {
        throw new ValidationError(`Element '${id}' is missing required assetId.`);
      }
      if (assetRegistry) {
        if (!assetRegistry.has(assetId)) {
          throw new ValidationError(`Element '${id}' references unknown asset '${assetId}'.`);
        }
      }
      return assetId;
    };

    switch (type) {
      case "text": {
        const elem = new TextElement({
          id,
          name,
          startTime,
          duration,
          visible,
          parentId,
          text: raw.text,
          style: raw.style,
        });
        if (raw.properties?.text) {
          elem.text = deserializeProperty(raw.properties.text, "text") as any;
        }
        return applyTransform(elem);
      }

      case "image": {
        const assetId = validateAssetRef(raw.assetId || raw.source?.assetId || raw.source?.id);
        const elem = new ImageElement({
          id,
          name,
          startTime,
          duration,
          visible,
          parentId,
          assetId,
        });
        return applyTransform(elem);
      }

      case "video": {
        const assetId = validateAssetRef(raw.assetId || raw.source?.assetId || raw.source?.id);
        const elem = new VideoElement({
          id,
          name,
          startTime,
          duration,
          visible,
          parentId,
          assetId,
          sourceStartTime: raw.sourceStartTime,
        });
        return applyTransform(elem);
      }

      case "audio": {
        const assetId = validateAssetRef(raw.assetId || raw.source?.assetId || raw.source?.id);
        const elem = new AudioElement({
          id,
          name,
          startTime,
          duration,
          visible,
          parentId,
          assetId,
          sourceStartTime: raw.sourceStartTime,
          volume: typeof raw.volume === "number" ? raw.volume : undefined,
        });
        if (raw.properties?.volume) {
          elem.volume = deserializeProperty(raw.properties.volume, "volume") as any;
        }
        return applyTransform(elem);
      }

      case "shape": {
        const elem = new ShapeElement({
          id,
          name,
          startTime,
          duration,
          visible,
          parentId,
          shapeType: raw.shapeType,
          shapeData: raw.shapeData,
          style: raw.style,
        });
        return applyTransform(elem);
      }

      case "group": {
        const elem = new GroupElement({
          id,
          name,
          startTime,
          duration,
          visible,
          parentId,
        });
        if (Array.isArray(raw.children)) {
          for (const childRaw of raw.children) {
            elem.addChild(ElementFactory.fromJSON(childRaw, assetRegistry));
          }
        }
        return applyTransform(elem);
      }

      default:
        throw new SerializationError(`Unsupported element type '${type}'.`);
    }
  }
}
