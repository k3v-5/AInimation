import fs from 'fs';
import path from 'path';
import { writePsd, readPsd, Psd, Layer } from 'ag-psd';
import { VisemeDrawer } from './VisemeDrawer.js';

export const CH_VISEMES = [
  'Neutral',
  'Ah',
  'D',
  'Ee',
  'F',
  'L',
  'M',
  'Oh',
  'R',
  'S',
  'Uh',
  'W-Oo',
  'Smile',
  'Surprised'
] as const;

export type VisemeName = typeof CH_VISEMES[number];

export interface PuppetScaffoldOptions {
  characterName: string;
  width?: number;
  height?: number;
  outPath: string;
  includeLimbs?: boolean;
  includeHandTriggers?: boolean;
  includePhysicsTags?: boolean;
  includeFaceParallax?: boolean;
}

export interface PuppetValidationReport {
  isValid: boolean;
  characterRoot: string | null;
  hasHead: boolean;
  headIsIndependent: boolean;
  hasMouth: boolean;
  foundVisemes: string[];
  missingVisemes: string[];
  hasEyes: {
    leftEye: boolean;
    leftPupil: boolean;
    rightEye: boolean;
    rightPupil: boolean;
  };
  hasLimbs: {
    leftArm: boolean;
    rightArm: boolean;
    torso: boolean;
    leftLeg: boolean;
    rightLeg: boolean;
  };
  physicsFeatures: {
    hasDangle: boolean;
    hasDraggable: boolean;
    hasFixed: boolean;
    dangleLayers: string[];
    draggableLayers: string[];
    fixedLayers: string[];
  };
  handTriggers: {
    hasSwapSets: boolean;
    triggerKeysFound: string[];
  };
  hasParallaxLayers: boolean;
  warnings: string[];
  recommendations: string[];
}

export class PuppetBuilder {
  private static createPixelBuffer(width: number, height: number, r: number, g: number, b: number, a: number = 255): Uint8Array {
    const data = new Uint8Array(width * height * 4);
    for (let i = 0; i < data.length; i += 4) {
      data[i] = r;
      data[i + 1] = g;
      data[i + 2] = b;
      data[i + 3] = a;
    }
    return data;
  }

  private static createRectLayer(name: string, left: number, top: number, width: number, height: number, color: [number, number, number, number]): Layer {
    return {
      name,
      top,
      left,
      bottom: top + height,
      right: left + width,
      canvas: undefined,
      imageData: {
        width,
        height,
        data: this.createPixelBuffer(width, height, color[0], color[1], color[2], color[3])
      } as any
    };
  }

  private static createVisemeLayer(viseme: VisemeName, left: number, top: number): Layer {
    const pixelData = VisemeDrawer.drawViseme(viseme, 140, 80);
    return {
      name: viseme,
      top,
      left,
      bottom: top + pixelData.height,
      right: left + pixelData.width,
      canvas: undefined,
      imageData: {
        width: pixelData.width,
        height: pixelData.height,
        data: pixelData.data
      } as any
    };
  }

  /**
   * Generates a fully compliant, production-ready Character Animator PSD file with
   * custom mouth visemes, optional physics tags (Dangle, Draggable, Fixed), hand swap sets, and parallax layers.
   */
  public static scaffoldPuppet(options: PuppetScaffoldOptions): string {
    const width = options.width || 2000;
    const height = options.height || 2000;
    const name = options.characterName || 'Character';
    const includePhysics = options.includePhysicsTags ?? true;
    const includeHands = options.includeHandTriggers ?? true;
    const includeParallax = options.includeFaceParallax ?? true;

    // 1. Mouth Visemes (Rendered with custom distinct graphics per viseme)
    const mouthChildren: Layer[] = CH_VISEMES.map((viseme) => {
      const isVisible = viseme === 'Neutral';
      const layer = this.createVisemeLayer(viseme, 930, 840);
      layer.hidden = !isVisible;
      return layer;
    });

    const mouthGroup: Layer = {
      name: 'Mouth',
      children: mouthChildren,
      opened: true
    };

    // 2. Eyes & Pupils
    const leftEyeGroup: Layer = {
      name: '+Left Eye',
      children: [
        this.createRectLayer('Left Pupil', 870, 720, 20, 20, [20, 20, 20, 255]),
        this.createRectLayer('Left Eyeball', 850, 700, 60, 60, [250, 250, 250, 255])
      ],
      opened: false
    };

    const rightEyeGroup: Layer = {
      name: '+Right Eye',
      children: [
        this.createRectLayer('Right Pupil', 1110, 720, 20, 20, [20, 20, 20, 255]),
        this.createRectLayer('Right Eyeball', 1090, 700, 60, 60, [250, 250, 250, 255])
      ],
      opened: false
    };

    // 3. Head Children with Optional 2.5D Parallax & Dangle Hair
    const headChildren: Layer[] = [];

    if (includeParallax) {
      // Front hair sways with Dangle physics
      headChildren.push(
        this.createRectLayer(includePhysics ? 'Hair Bangs Dangle' : 'Hair Front', 800, 520, 400, 120, [70, 40, 25, 255])
      );
    }

    headChildren.push(
      this.createRectLayer('Left Eyebrow', 840, 660, 80, 15, [50, 30, 15, 255]),
      this.createRectLayer('Right Eyebrow', 1080, 660, 80, 15, [50, 30, 15, 255]),
      leftEyeGroup,
      rightEyeGroup,
      this.createRectLayer('Nose', 985, 760, 30, 50, [210, 140, 100, 255]),
      mouthGroup,
      this.createRectLayer('Head Base', 750, 550, 500, 500, [240, 180, 140, 255])
    );

    if (includeParallax) {
      // Ears and back hair placed behind Head Base
      headChildren.push(
        this.createRectLayer('Left Ear', 710, 720, 50, 80, [230, 170, 130, 255]),
        this.createRectLayer('Right Ear', 1240, 720, 50, 80, [230, 170, 130, 255]),
        this.createRectLayer('Hair Back', 700, 500, 600, 600, [50, 25, 15, 255])
      );
    }

    const headGroup: Layer = {
      name: '+Head',
      children: headChildren,
      opened: true
    };

    // 4. Limbs & Hands (with optional Hand Swap Sets and Draggable tags)
    let leftArmLayer: Layer;
    let rightArmLayer: Layer;

    if (includeHands) {
      // Create hand swap groups with keyboard triggers (1, 2, 3, 4)
      const leftHandSwap: Layer = {
        name: '+Left Hand',
        children: [
          this.createRectLayer('Open (1)', 580, 1420, 70, 70, [230, 170, 130, 255]),
          (() => { const l = this.createRectLayer('Fist (2)', 585, 1420, 60, 60, [220, 160, 120, 255]); l.hidden = true; return l; })(),
          (() => { const l = this.createRectLayer('Point (3)', 585, 1400, 60, 80, [220, 160, 120, 255]); l.hidden = true; return l; })(),
          (() => { const l = this.createRectLayer('ThumbsUp (4)', 585, 1410, 65, 70, [220, 160, 120, 255]); l.hidden = true; return l; })()
        ],
        opened: false
      };

      const rightHandSwap: Layer = {
        name: includePhysics ? '+Right Hand Draggable' : '+Right Hand',
        children: [
          this.createRectLayer('Open (1)', 1350, 1420, 70, 70, [230, 170, 130, 255]),
          (() => { const l = this.createRectLayer('Fist (2)', 1355, 1420, 60, 60, [220, 160, 120, 255]); l.hidden = true; return l; })(),
          (() => { const l = this.createRectLayer('Point (3)', 1355, 1400, 60, 80, [220, 160, 120, 255]); l.hidden = true; return l; })(),
          (() => { const l = this.createRectLayer('ThumbsUp (4)', 1350, 1410, 65, 70, [220, 160, 120, 255]); l.hidden = true; return l; })()
        ],
        opened: false
      };

      leftArmLayer = {
        name: '+Left Arm',
        children: [
          leftHandSwap,
          this.createRectLayer('Left Forearm', 600, 1260, 90, 170, [220, 160, 120, 255]),
          this.createRectLayer('Left Upper Arm', 620, 1100, 100, 180, [60, 100, 180, 255])
        ],
        opened: false
      };

      rightArmLayer = {
        name: '+Right Arm',
        children: [
          rightHandSwap,
          this.createRectLayer('Right Forearm', 1310, 1260, 90, 170, [220, 160, 120, 255]),
          this.createRectLayer('Right Upper Arm', 1280, 1100, 100, 180, [60, 100, 180, 255])
        ],
        opened: false
      };
    } else {
      leftArmLayer = this.createRectLayer('+Left Arm', 600, 1100, 150, 400, [220, 160, 120, 255]);
      rightArmLayer = this.createRectLayer(includePhysics ? '+Right Arm Draggable' : '+Right Arm', 1250, 1100, 150, 400, [220, 160, 120, 255]);
    }

    const bodyChildren: Layer[] = [];
    if (options.includeLimbs !== false) {
      bodyChildren.push(
        leftArmLayer,
        rightArmLayer,
        this.createRectLayer('Torso', 750, 1050, 500, 600, [60, 100, 180, 255]),
        this.createRectLayer(includePhysics ? '+Left Leg Fixed' : '+Left Leg', 800, 1650, 160, 300, [40, 50, 80, 255]),
        this.createRectLayer(includePhysics ? '+Right Leg Fixed' : '+Right Leg', 1040, 1650, 160, 300, [40, 50, 80, 255])
      );
    } else {
      bodyChildren.push(this.createRectLayer('Torso', 750, 1050, 500, 600, [60, 100, 180, 255]));
    }

    const bodyGroup: Layer = {
      name: 'Body',
      children: bodyChildren,
      opened: true
    };

    // 5. Root Group
    const rootCharacter: Layer = {
      name,
      children: [headGroup, bodyGroup],
      opened: true
    };

    const psdDoc: Psd = {
      width,
      height,
      channels: 4,
      bitsPerChannel: 8,
      colorMode: 3, // RGB
      children: [rootCharacter]
    };

    const buffer = writePsd(psdDoc);
    const resolvedPath = path.resolve(options.outPath);
    fs.mkdirSync(path.dirname(resolvedPath), { recursive: true });
    fs.writeFileSync(resolvedPath, Buffer.from(buffer));

    return resolvedPath;
  }

  /**
   * Validates any PSD file against Adobe Character Animator rigging standards,
   * including physics tags (Dangle, Fixed, Draggable), hand swap sets, and parallax.
   */
  public static validatePuppet(psdPath: string): PuppetValidationReport {
    const resolvedPath = path.resolve(psdPath);
    if (!fs.existsSync(resolvedPath)) {
      throw new Error(`PSD file not found at: ${resolvedPath}`);
    }

    const buffer = fs.readFileSync(resolvedPath);
    const psd = readPsd(buffer, { skipLayerImageData: true, skipCompositeImageData: true });

    const warnings: string[] = [];
    const recommendations: string[] = [];

    // Find root character group
    let rootGroup = (psd.children || []).find(c => c.children && c.children.length > 0);
    const characterRoot = rootGroup ? (rootGroup.name || null) : null;

    if (!rootGroup) {
      warnings.push("No root group found. Character Animator expects artwork enclosed in a top-level character group.");
      rootGroup = { name: 'Root', children: psd.children || [] } as Layer;
    }

    const allDescendants: Layer[] = [];
    function collect(layers: Layer[]) {
      for (const l of layers) {
        allDescendants.push(l);
        if (l.children) collect(l.children);
      }
    }
    collect(rootGroup.children || []);

    // 1. Head checks
    const headLayer = allDescendants.find(l => l.name && (l.name.includes('Head') || l.name.includes('head')));
    const hasHead = !!headLayer;
    const headIsIndependent = headLayer?.name?.startsWith('+') ?? false;

    if (!hasHead) {
      warnings.push("Missing 'Head' group. The puppet will not track face or head rotation.");
    } else if (!headIsIndependent) {
      recommendations.push("The 'Head' group does not have a '+' prefix ('+Head'). Without '+', rotating the head will stretch the body mesh.");
    }

    // 2. Mouth & Visemes
    const mouthGroup = allDescendants.find(l => l.name && (l.name.toLowerCase() === 'mouth' || l.name.toLowerCase() === '+mouth'));
    const hasMouth = !!mouthGroup;
    const foundVisemes: string[] = [];
    const missingVisemes: string[] = [];

    if (hasMouth && mouthGroup?.children) {
      const mouthChildNames = mouthGroup.children.map(c => c.name || '');
      for (const v of CH_VISEMES) {
        if (mouthChildNames.some(name => name.toLowerCase() === v.toLowerCase())) {
          foundVisemes.push(v);
        } else {
          missingVisemes.push(v);
        }
      }
    } else {
      warnings.push("Missing 'Mouth' group. Lip-sync cannot be computed automatically.");
      missingVisemes.push(...CH_VISEMES);
    }

    // 3. Eyes & Pupils
    const leftEye = allDescendants.find(l => l.name && (l.name.includes('Left Eye') || l.name.includes('left eye')));
    const rightEye = allDescendants.find(l => l.name && (l.name.includes('Right Eye') || l.name.includes('right eye')));
    const leftPupil = allDescendants.find(l => l.name && l.name.toLowerCase().includes('left pupil'));
    const rightPupil = allDescendants.find(l => l.name && l.name.toLowerCase().includes('right pupil'));

    const hasEyes = {
      leftEye: !!leftEye,
      leftPupil: !!leftPupil,
      rightEye: !!rightEye,
      rightPupil: !!rightPupil
    };

    if (!leftPupil || !rightPupil) {
      recommendations.push("Pupils ('Left Pupil', 'Right Pupil') not detected. Eye gaze tracking will be disabled.");
    }

    // 4. Limbs
    const leftArm = allDescendants.find(l => l.name && l.name.toLowerCase().includes('left arm'));
    const rightArm = allDescendants.find(l => l.name && l.name.toLowerCase().includes('right arm'));
    const torso = allDescendants.find(l => l.name && (l.name.toLowerCase().includes('torso') || l.name.toLowerCase().includes('body')));
    const leftLeg = allDescendants.find(l => l.name && l.name.toLowerCase().includes('left leg'));
    const rightLeg = allDescendants.find(l => l.name && l.name.toLowerCase().includes('right leg'));

    const hasLimbs = {
      leftArm: !!leftArm,
      rightArm: !!rightArm,
      torso: !!torso,
      leftLeg: !!leftLeg,
      rightLeg: !!rightLeg
    };

    // 5. Physics Features Audit
    const dangleLayers: string[] = [];
    const draggableLayers: string[] = [];
    const fixedLayers: string[] = [];

    for (const l of allDescendants) {
      const lname = (l.name || '').toLowerCase();
      if (lname.includes('dangle')) dangleLayers.push(l.name || '');
      if (lname.includes('draggable')) draggableLayers.push(l.name || '');
      if (lname.includes('fixed')) fixedLayers.push(l.name || '');
    }

    const physicsFeatures = {
      hasDangle: dangleLayers.length > 0,
      hasDraggable: draggableLayers.length > 0,
      hasFixed: fixedLayers.length > 0,
      dangleLayers,
      draggableLayers,
      fixedLayers
    };

    // 6. Hand Triggers Audit
    const triggerKeysFound: string[] = [];
    for (const l of allDescendants) {
      const match = (l.name || '').match(/\(([0-9a-zA-Z])\)/);
      if (match) {
        triggerKeysFound.push(`${l.name}: Key '${match[1]}'`);
      }
    }

    const handTriggers = {
      hasSwapSets: triggerKeysFound.length > 0,
      triggerKeysFound
    };

    // 7. Parallax Audit
    const hasHairBack = allDescendants.some(l => (l.name || '').toLowerCase().includes('hair back'));
    const hasEars = allDescendants.some(l => (l.name || '').toLowerCase().includes('ear'));
    const hasParallaxLayers = hasHairBack || hasEars;

    const isValid = hasHead && hasMouth && foundVisemes.length >= 3;

    return {
      isValid,
      characterRoot,
      hasHead,
      headIsIndependent,
      hasMouth,
      foundVisemes,
      missingVisemes,
      hasEyes,
      hasLimbs,
      physicsFeatures,
      handTriggers,
      hasParallaxLayers,
      warnings,
      recommendations
    };
  }
}
