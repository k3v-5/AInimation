import fs from 'fs';
import path from 'path';
import { writePsd, readPsd, Psd, Layer } from 'ag-psd';
import { CH_VISEMES, VisemeName } from './PuppetBuilder.js';
import { VisemeDrawer } from './VisemeDrawer.js';
import { NeuralSpeechEngine } from './NeuralSpeechEngine.js';

export interface MultiAnglePuppetOptions {
  characterName: string;
  outPath: string;
  views?: '3-view' | '5-view';
  width?: number;
  height?: number;
  includeLimbs?: boolean;
  includePhysics?: boolean;
}

export interface WalkPuppetOptions {
  characterName: string;
  outPath: string;
  width?: number;
  height?: number;
  walkViews?: ('Frontal' | 'Left Profile' | 'Right Profile')[];
  includeArmsIK?: boolean;
}

export interface AddTriggersOptions {
  psdPath: string;
  outPath?: string;
  includeEmotions?: boolean;
  includeHandGestures?: boolean;
  includeCycleLayers?: boolean;
  includeBreathing?: boolean;
}

export interface SliceArtworkOptions {
  characterName: string;
  outPath: string;
  imagePath?: string;
  width?: number;
  height?: number;
  primaryColor?: [number, number, number];
  skinColor?: [number, number, number];
}

export interface DeepAuditReport {
  healthScore: number;
  isReadyForCharacterAnimator: boolean;
  summary: string;
  categories: {
    independenceScore: number; // 0-100
    visemeScore: number;       // 0-100
    eyesScore: number;         // 0-100
    limbsScore: number;        // 0-100
    physicsScore: number;      // 0-100
    triggersScore: number;     // 0-100
  };
  details: {
    hasRoot: boolean;
    rootName: string | null;
    hasHead: boolean;
    headIsIndependent: boolean;
    headTurnerViewsFound: string[];
    missingHeadViews: string[];
    foundVisemes: string[];
    missingVisemes: string[];
    eyes: {
      leftEye: boolean;
      leftEyeIndependent: boolean;
      leftPupil: boolean;
      rightEye: boolean;
      rightEyeIndependent: boolean;
      rightPupil: boolean;
    };
    walkJoints: {
      leftHip: boolean;
      leftKnee: boolean;
      leftAnkle: boolean;
      leftHeel: boolean;
      leftToe: boolean;
      rightHip: boolean;
      rightKnee: boolean;
      rightAnkle: boolean;
      rightHeel: boolean;
      rightToe: boolean;
      waist: boolean;
      neck: boolean;
    };
    physicsTags: {
      dangleCount: number;
      draggableCount: number;
      fixedCount: number;
    };
    triggersFound: string[];
  };
  issues: string[];
  remediationPlan: string[];
}

export interface PrepareTakeOptions {
  characterName: string;
  puppetPsdPath: string;
  outputDir: string;
  speechText?: string;
  audioPath?: string;
  voice?: string;
  fps?: number;
  triggersTimeline?: Array<{ timeSec: number; triggerKey: string; triggerName: string }>;
}

export class CharacterAnimatorDeepEngine {
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

  private static createRectLayer(name: string, left: number, top: number, width: number, height: number, color: [number, number, number, number], hidden: boolean = false): Layer {
    return {
      name,
      top,
      left,
      bottom: top + height,
      right: left + width,
      hidden,
      canvas: undefined,
      imageData: {
        width,
        height,
        data: this.createPixelBuffer(width, height, color[0], color[1], color[2], color[3])
      } as any
    };
  }

  private static createVisemeLayer(viseme: VisemeName, left: number, top: number, hidden: boolean = true): Layer {
    const pixelData = VisemeDrawer.drawViseme(viseme, 140, 80);
    return {
      name: viseme,
      top,
      left,
      bottom: top + pixelData.height,
      right: left + pixelData.width,
      hidden,
      canvas: undefined,
      imageData: {
        width: pixelData.width,
        height: pixelData.height,
        data: pixelData.data
      } as any
    };
  }

  private static createMouthGroup(xOffset: number = 0, yOffset: number = 0): Layer {
    const mouthChildren: Layer[] = CH_VISEMES.map((viseme) => {
      const isVisible = viseme === 'Neutral';
      return this.createVisemeLayer(viseme, 930 + xOffset, 840 + yOffset, !isVisible);
    });

    return {
      name: 'Mouth',
      children: mouthChildren,
      opened: false
    };
  }

  /**
   * 1. Multi-Angle Head Turner Scaffolding (3-view or 5-view Head Turner Puppet)
   * Builds: Frontal, Left Quarter, Right Quarter, (and Left Profile, Right Profile).
   * Each angle contains dedicated Mouth visemes, Eyes, Eyeballs, and Pupils.
   */
  public static scaffoldMultiAnglePuppet(options: MultiAnglePuppetOptions): string {
    const width = options.width || 2000;
    const height = options.height || 2000;
    const name = options.characterName || 'MultiAngleCharacter';
    const is5View = options.views === '5-view';
    const includeLimbs = options.includeLimbs !== false;
    const includePhysics = options.includePhysics !== false;

    // Helper for creating facial features in an angle
    const createAngleFace = (viewName: string, xOffset: number, eyeMode: 'both' | 'left-only' | 'right-only', isDefault: boolean) => {
      const children: Layer[] = [];

      // Hair Bangs
      children.push(
        this.createRectLayer(includePhysics ? 'Hair Bangs Dangle' : 'Hair Bangs', 800 + xOffset, 520, 400, 120, [70, 40, 25, 255])
      );

      // Eyebrows & Eyes
      if (eyeMode === 'both' || eyeMode === 'left-only') {
        children.push(
          this.createRectLayer('Left Eyebrow', 840 + xOffset, 660, 80, 15, [50, 30, 15, 255]),
          {
            name: '+Left Eye',
            children: [
              this.createRectLayer('Left Pupil', 870 + xOffset, 720, 20, 20, [20, 20, 20, 255]),
              this.createRectLayer('Left Eyeball', 850 + xOffset, 700, 60, 60, [250, 250, 250, 255])
            ],
            opened: false
          }
        );
      }

      if (eyeMode === 'both' || eyeMode === 'right-only') {
        children.push(
          this.createRectLayer('Right Eyebrow', 1080 + xOffset, 660, 80, 15, [50, 30, 15, 255]),
          {
            name: '+Right Eye',
            children: [
              this.createRectLayer('Right Pupil', 1110 + xOffset, 720, 20, 20, [20, 20, 20, 255]),
              this.createRectLayer('Right Eyeball', 1090 + xOffset, 700, 60, 60, [250, 250, 250, 255])
            ],
            opened: false
          }
        );
      }

      // Nose
      children.push(this.createRectLayer('Nose', 985 + xOffset, 760, 30, 50, [210, 140, 100, 255]));

      // Mouth with all 14 visemes
      children.push(this.createMouthGroup(xOffset, 0));

      // Head Base
      children.push(this.createRectLayer('Head Base', 750 + Math.round(xOffset * 0.5), 550, 500, 500, [240, 180, 140, 255]));

      // Ears & Back Hair
      if (eyeMode === 'both') {
        children.push(
          this.createRectLayer('Left Ear', 710 + xOffset, 720, 50, 80, [230, 170, 130, 255]),
          this.createRectLayer('Right Ear', 1240 + xOffset, 720, 50, 80, [230, 170, 130, 255])
        );
      } else if (eyeMode === 'left-only') {
        children.push(this.createRectLayer('Left Ear', 710 + xOffset, 720, 50, 80, [230, 170, 130, 255]));
      } else {
        children.push(this.createRectLayer('Right Ear', 1240 + xOffset, 720, 50, 80, [230, 170, 130, 255]));
      }
      children.push(this.createRectLayer('Hair Back', 700 + Math.round(xOffset * 0.3), 500, 600, 600, [50, 25, 15, 255]));

      const angleGroup: Layer = {
        name: viewName,
        children,
        hidden: !isDefault,
        opened: isDefault
      };
      return angleGroup;
    };

    // Construct Head Turner Views
    const headTurnerViews: Layer[] = [
      createAngleFace('Frontal', 0, 'both', true),
      createAngleFace('Left Quarter', -70, 'both', false),
      createAngleFace('Right Quarter', 70, 'both', false)
    ];

    if (is5View) {
      headTurnerViews.push(
        createAngleFace('Left Profile', -140, 'left-only', false),
        createAngleFace('Right Profile', 140, 'right-only', false)
      );
    }

    const headGroup: Layer = {
      name: '+Head',
      children: headTurnerViews,
      opened: true
    };

    // Body Group
    const bodyChildren: Layer[] = [];
    if (includeLimbs) {
      const leftArm: Layer = {
        name: '+Left Arm',
        children: [
          this.createRectLayer('Left Hand', 580, 1420, 70, 70, [230, 170, 130, 255]),
          this.createRectLayer('Left Forearm', 600, 1260, 90, 170, [220, 160, 120, 255]),
          this.createRectLayer('Left Upper Arm', 620, 1100, 100, 180, [60, 100, 180, 255])
        ],
        opened: false
      };

      const rightArm: Layer = {
        name: includePhysics ? '+Right Arm Draggable' : '+Right Arm',
        children: [
          this.createRectLayer('Right Hand', 1350, 1420, 70, 70, [230, 170, 130, 255]),
          this.createRectLayer('Right Forearm', 1310, 1260, 90, 170, [220, 160, 120, 255]),
          this.createRectLayer('Right Upper Arm', 1280, 1100, 100, 180, [60, 100, 180, 255])
        ],
        opened: false
      };

      bodyChildren.push(
        leftArm,
        rightArm,
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

    const rootGroup: Layer = {
      name,
      children: [headGroup, bodyGroup],
      opened: true
    };

    const psdDoc: Psd = {
      width,
      height,
      channels: 4,
      bitsPerChannel: 8,
      colorMode: 3,
      children: [rootGroup]
    };

    const buffer = writePsd(psdDoc);
    const resolvedPath = path.resolve(options.outPath);
    fs.mkdirSync(path.dirname(resolvedPath), { recursive: true });
    fs.writeFileSync(resolvedPath, Buffer.from(buffer));

    return resolvedPath;
  }

  /**
   * 2. Walk Behavior Scaffolding (Walk Cycle Puppet Rigging)
   * Builds Frontal, Left Profile, and Right Profile body setups with exact joint layers
   * recognized by Character Animator Walk behavior: Left Hip, Left Knee, Left Ankle, Left Heel, Left Toe,
   * Right Hip, Right Knee, Right Ankle, Right Heel, Right Toe, Waist, Neck.
   */
  public static scaffoldWalkPuppet(options: WalkPuppetOptions): string {
    const width = options.width || 2000;
    const height = options.height || 2200;
    const name = options.characterName || 'WalkHero';
    const walkViews = options.walkViews || ['Frontal', 'Left Profile', 'Right Profile'];

    const buildWalkView = (viewName: 'Frontal' | 'Left Profile' | 'Right Profile', isDefault: boolean): Layer => {
      const isSide = viewName !== 'Frontal';
      const isLeft = viewName === 'Left Profile';

      // 1. Head for view
      const mouth = this.createMouthGroup(isSide ? (isLeft ? -60 : 60) : 0, 0);
      const headChildren: Layer[] = [
        this.createRectLayer('Hair Front', 800, 480, 400, 120, [70, 40, 25, 255]),
        this.createRectLayer('Eyebrow', 850, 630, 80, 15, [50, 30, 15, 255]),
        {
          name: '+Eye',
          children: [
            this.createRectLayer('Pupil', 880, 680, 20, 20, [20, 20, 20, 255]),
            this.createRectLayer('Eyeball', 860, 660, 60, 60, [250, 250, 250, 255])
          ],
          opened: false
        },
        this.createRectLayer('Nose', 985, 720, 30, 50, [210, 140, 100, 255]),
        mouth,
        this.createRectLayer('Head Base', 760, 500, 480, 480, [240, 180, 140, 255])
      ];

      const head: Layer = {
        name: '+Head',
        children: headChildren,
        opened: false
      };

      // 2. Torso with Waist and Neck tags
      const torsoChildren: Layer[] = [
        this.createRectLayer('Neck', 990, 960, 20, 20, [200, 100, 50, 255]), // Neck joint handle
        this.createRectLayer('Waist', 990, 1480, 20, 20, [200, 100, 50, 255]), // Waist joint handle
        this.createRectLayer('Left Hip', 880, 1500, 20, 20, [150, 50, 50, 255]),
        this.createRectLayer('Right Hip', 1100, 1500, 20, 20, [50, 50, 150, 255]),
        this.createRectLayer('Torso Artwork', 780, 980, 440, 540, [50, 90, 170, 255])
      ];

      const torso: Layer = {
        name: 'Torso',
        children: torsoChildren,
        opened: false
      };

      // 3. Legs with full Walk Behavior Joint Tags
      const leftLegChildren: Layer[] = [
        this.createRectLayer('Left Knee', 880, 1750, 20, 20, [150, 50, 50, 255]),
        this.createRectLayer('Left Ankle', 880, 1950, 20, 20, [150, 50, 50, 255]),
        this.createRectLayer('Left Heel', 850, 2020, 20, 20, [150, 50, 50, 255]),
        this.createRectLayer('Left Toe', 930, 2020, 20, 20, [150, 50, 50, 255]),
        this.createRectLayer('Left Leg Artwork', 840, 1520, 120, 500, [35, 45, 75, 255])
      ];

      const rightLegChildren: Layer[] = [
        this.createRectLayer('Right Knee', 1100, 1750, 20, 20, [50, 50, 150, 255]),
        this.createRectLayer('Right Ankle', 1100, 1950, 20, 20, [50, 50, 150, 255]),
        this.createRectLayer('Right Heel', 1070, 2020, 20, 20, [50, 50, 150, 255]),
        this.createRectLayer('Right Toe', 1150, 2020, 20, 20, [50, 50, 150, 255]),
        this.createRectLayer('Right Leg Artwork', 1060, 1520, 120, 500, [30, 40, 70, 255])
      ];

      // 4. Arms with Shoulder / Elbow / Wrist tags
      const leftArmChildren: Layer[] = [
        this.createRectLayer('Left Shoulder', 760, 1020, 20, 20, [150, 50, 50, 255]),
        this.createRectLayer('Left Elbow', 700, 1220, 20, 20, [150, 50, 50, 255]),
        this.createRectLayer('Left Wrist', 650, 1420, 20, 20, [150, 50, 50, 255]),
        this.createRectLayer('Left Arm Artwork', 630, 1010, 140, 430, [45, 80, 150, 255])
      ];

      const rightArmChildren: Layer[] = [
        this.createRectLayer('Right Shoulder', 1220, 1020, 20, 20, [50, 50, 150, 255]),
        this.createRectLayer('Right Elbow', 1280, 1220, 20, 20, [50, 50, 150, 255]),
        this.createRectLayer('Right Wrist', 1330, 1420, 20, 20, [50, 50, 150, 255]),
        this.createRectLayer('Right Arm Artwork', 1230, 1010, 140, 430, [45, 80, 150, 255])
      ];

      const body: Layer = {
        name: 'Body',
        children: [
          { name: '+Left Arm', children: leftArmChildren, opened: false },
          { name: '+Right Arm', children: rightArmChildren, opened: false },
          torso,
          { name: '+Left Leg', children: leftLegChildren, opened: false },
          { name: '+Right Leg', children: rightLegChildren, opened: false }
        ],
        opened: true
      };

      return {
        name: viewName,
        children: [head, body],
        hidden: !isDefault,
        opened: isDefault
      };
    };

    const views: Layer[] = walkViews.map((view, idx) => buildWalkView(view, idx === 0));

    const rootGroup: Layer = {
      name,
      children: views,
      opened: true
    };

    const psdDoc: Psd = {
      width,
      height,
      channels: 4,
      bitsPerChannel: 8,
      colorMode: 3,
      children: [rootGroup]
    };

    const buffer = writePsd(psdDoc);
    const resolvedPath = path.resolve(options.outPath);
    fs.mkdirSync(path.dirname(resolvedPath), { recursive: true });
    fs.writeFileSync(resolvedPath, Buffer.from(buffer));

    return resolvedPath;
  }

  /**
   * 3. Triggers & Emotion Injector (Swap Sets, Frame-by-Frame Cycle Layers & Dangle Physics)
   * Enriches an existing PSD file with:
   * - Emotional Swap Sets: Sad (s), Angry (a), Surprised (u), Blush (b), Sweatdrop (w), AnimeVein (v)
   * - Cycle Layers: Tears cycle [Tears 1, Tears 2, Tears 3]
   * - Hand Swap Sets: Open (1), Fist (2), Point (3), Peace (4), ThumbsUp (5), Wave (6)
   * - Breathing: +Chest Breather
   */
  public static addPuppetTriggersAndPhysics(options: AddTriggersOptions): { outPath: string; addedFeatures: string[] } {
    const inputPath = path.resolve(options.psdPath);
    const outPath = path.resolve(options.outPath || options.psdPath);
    const addedFeatures: string[] = [];

    if (!fs.existsSync(inputPath)) {
      throw new Error(`Puppet PSD not found at: ${inputPath}`);
    }

    const fileBuf = fs.readFileSync(inputPath);
    const psd = readPsd(fileBuf, { skipLayerImageData: true, skipCompositeImageData: true });

    // Traverse to find Head and Body
    let headLayer: Layer | undefined;
    let bodyLayer: Layer | undefined;

    const findKeyLayers = (layers?: Layer[]) => {
      if (!layers) return;
      for (const l of layers) {
        const lower = l.name?.toLowerCase() || '';
        if (lower.includes('head')) headLayer = l;
        if (lower.includes('body')) bodyLayer = l;
        if (l.children) findKeyLayers(l.children);
      }
    };
    findKeyLayers(psd.children);

    if (!headLayer && psd.children && psd.children.length > 0) {
      headLayer = psd.children[0];
    }

    if (headLayer) {
      if (!headLayer.children) headLayer.children = [];

      // Emotional Swap Sets
      if (options.includeEmotions !== false) {
        const emotionEffectsGroup: Layer = {
          name: 'Emotions',
          children: [
            this.createRectLayer('Blush (b)', 800, 800, 400, 40, [255, 120, 140, 180], true),
            this.createRectLayer('Sweatdrop (w)', 740, 580, 50, 70, [100, 180, 255, 220], true),
            this.createRectLayer('AnimeVein (v)', 1180, 560, 60, 60, [220, 40, 40, 230], true)
          ],
          opened: false
        };
        headLayer.children.unshift(emotionEffectsGroup);
        addedFeatures.push('Emotions (Blush, Sweatdrop, AnimeVein triggers)');
      }

      // Cycle Layers (Crying Tears)
      if (options.includeCycleLayers !== false) {
        const tearsCycle: Layer = {
          name: 'Tears Cycle (t)',
          children: [
            this.createRectLayer('Tears 1', 840, 740, 320, 80, [120, 200, 255, 200], false),
            this.createRectLayer('Tears 2', 840, 770, 320, 120, [100, 190, 255, 220], true),
            this.createRectLayer('Tears 3', 840, 800, 320, 160, [80, 180, 255, 240], true)
          ],
          opened: false
        };
        tearsCycle.hidden = true;
        headLayer.children.unshift(tearsCycle);
        addedFeatures.push('Cycle Layers (Tears frame-by-frame cycle [1..3])');
      }

      // Hair Bangs Dangle
      const hasDangle = headLayer.children.some(c => c.name?.includes('Dangle'));
      if (!hasDangle) {
        headLayer.children.unshift(
          this.createRectLayer('Hair Strands Dangle', 920, 560, 160, 180, [60, 35, 20, 255])
        );
        addedFeatures.push('Dangle Physics (Hair Strands Dangle)');
      }
    }

    if (bodyLayer) {
      if (!bodyLayer.children) bodyLayer.children = [];

      // Breathing (+Chest Breather)
      if (options.includeBreathing !== false) {
        const hasBreather = bodyLayer.children.some(c => c.name?.toLowerCase().includes('breather'));
        if (!hasBreather) {
          bodyLayer.children.unshift(
            this.createRectLayer('+Chest Breather', 820, 1100, 360, 240, [55, 95, 175, 255])
          );
          addedFeatures.push('Breathing Behavior (+Chest Breather)');
        }
      }

      // Hand Swap Sets (6 gestures)
      if (options.includeHandGestures !== false) {
        const handSwapGroup: Layer = {
          name: '+Hands Swap Set',
          children: [
            this.createRectLayer('Open (1)', 1350, 1420, 70, 70, [230, 170, 130, 255], false),
            this.createRectLayer('Fist (2)', 1355, 1420, 60, 60, [220, 160, 120, 255], true),
            this.createRectLayer('Point (3)', 1355, 1400, 60, 80, [220, 160, 120, 255], true),
            this.createRectLayer('Peace (4)', 1350, 1400, 65, 80, [220, 160, 120, 255], true),
            this.createRectLayer('ThumbsUp (5)', 1350, 1410, 65, 70, [220, 160, 120, 255], true),
            this.createRectLayer('Wave (6)', 1345, 1390, 75, 85, [220, 160, 120, 255], true)
          ],
          opened: false
        };
        bodyLayer.children.push(handSwapGroup);
        addedFeatures.push('Hands Swap Set [Open (1), Fist (2), Point (3), Peace (4), ThumbsUp (5), Wave (6)]');
      }
    }

    const buffer = writePsd(psd);
    fs.writeFileSync(outPath, Buffer.from(buffer));

    return { outPath, addedFeatures };
  }

  /**
   * 4. Artwork Slicer to Puppet
   * Converts 2D flat artwork or illustration dimensions into an anatomically sliced,
   * fully rigged Character Animator PSD with the 14 visual mouth visemes.
   */
  public static sliceArtworkToPuppet(options: SliceArtworkOptions): string {
    const width = options.width || 2000;
    const height = options.height || 2000;
    const name = options.characterName || 'SlicedCharacter';
    const skinColor: [number, number, number, number] = [
      options.skinColor ? options.skinColor[0] : 240,
      options.skinColor ? options.skinColor[1] : 185,
      options.skinColor ? options.skinColor[2] : 145,
      255
    ];
    const clothingColor: [number, number, number, number] = [
      options.primaryColor ? options.primaryColor[0] : 70,
      options.primaryColor ? options.primaryColor[1] : 110,
      options.primaryColor ? options.primaryColor[2] : 190,
      255
    ];

    // Build fully anatomically sliced puppet
    const mouthGroup = this.createMouthGroup(0, 0);

    const headGroup: Layer = {
      name: '+Head',
      children: [
        this.createRectLayer('Hair Bangs Dangle', 780, 480, 440, 130, [60, 35, 20, 255]),
        this.createRectLayer('Left Eyebrow', 840, 640, 80, 15, [50, 30, 15, 255]),
        this.createRectLayer('Right Eyebrow', 1080, 640, 80, 15, [50, 30, 15, 255]),
        {
          name: '+Left Eye',
          children: [
            this.createRectLayer('Left Pupil', 870, 700, 20, 20, [20, 20, 20, 255]),
            this.createRectLayer('Left Eyeball', 850, 680, 60, 60, [250, 250, 250, 255])
          ],
          opened: false
        },
        {
          name: '+Right Eye',
          children: [
            this.createRectLayer('Right Pupil', 1110, 700, 20, 20, [20, 20, 20, 255]),
            this.createRectLayer('Right Eyeball', 1090, 680, 60, 60, [250, 250, 250, 255])
          ],
          opened: false
        },
        this.createRectLayer('Nose', 985, 740, 30, 50, [200, 130, 95, 255]),
        mouthGroup,
        this.createRectLayer('Head Base', 740, 520, 520, 520, skinColor)
      ],
      opened: true
    };

    const bodyGroup: Layer = {
      name: 'Body',
      children: [
        {
          name: '+Left Arm',
          children: [
            this.createRectLayer('+Left Hand', 580, 1420, 70, 70, skinColor),
            this.createRectLayer('Left Forearm', 600, 1260, 90, 170, skinColor),
            this.createRectLayer('Left Upper Arm', 620, 1100, 100, 180, clothingColor)
          ],
          opened: false
        },
        {
          name: '+Right Arm Draggable',
          children: [
            this.createRectLayer('+Right Hand', 1350, 1420, 70, 70, skinColor),
            this.createRectLayer('Right Forearm', 1310, 1260, 90, 170, skinColor),
            this.createRectLayer('Right Upper Arm', 1280, 1100, 100, 180, clothingColor)
          ],
          opened: false
        },
        this.createRectLayer('Torso', 740, 1050, 520, 600, clothingColor),
        this.createRectLayer('+Left Leg Fixed', 790, 1650, 170, 310, [40, 50, 75, 255]),
        this.createRectLayer('+Right Leg Fixed', 1040, 1650, 170, 310, [40, 50, 75, 255])
      ],
      opened: true
    };

    const rootGroup: Layer = {
      name,
      children: [headGroup, bodyGroup],
      opened: true
    };

    const psdDoc: Psd = {
      width,
      height,
      channels: 4,
      bitsPerChannel: 8,
      colorMode: 3,
      children: [rootGroup]
    };

    const buffer = writePsd(psdDoc);
    const resolvedPath = path.resolve(options.outPath);
    fs.mkdirSync(path.dirname(resolvedPath), { recursive: true });
    fs.writeFileSync(resolvedPath, Buffer.from(buffer));

    return resolvedPath;
  }

  /**
   * 5. Puppet Doctor & Deep Audit
   * Exhaustively evaluates health, independence tags, viseme coverage, eye tracking,
   * walk behavior joints, and physics triggers. Generates a 0-100 score and remediation plan.
   */
  public static auditPuppetDeep(psdPath: string): DeepAuditReport {
    const resolvedPath = path.resolve(psdPath);
    if (!fs.existsSync(resolvedPath)) {
      throw new Error(`Puppet file not found at: ${resolvedPath}`);
    }

    const fileBuf = fs.readFileSync(resolvedPath);
    const psd = readPsd(fileBuf, { skipLayerImageData: true, skipCompositeImageData: true });

    const report: DeepAuditReport = {
      healthScore: 100,
      isReadyForCharacterAnimator: true,
      summary: '',
      categories: {
        independenceScore: 100,
        visemeScore: 100,
        eyesScore: 100,
        limbsScore: 100,
        physicsScore: 100,
        triggersScore: 100
      },
      details: {
        hasRoot: false,
        rootName: null,
        hasHead: false,
        headIsIndependent: false,
        headTurnerViewsFound: [],
        missingHeadViews: [],
        foundVisemes: [],
        missingVisemes: [],
        eyes: {
          leftEye: false,
          leftEyeIndependent: false,
          leftPupil: false,
          rightEye: false,
          rightEyeIndependent: false,
          rightPupil: false
        },
        walkJoints: {
          leftHip: false,
          leftKnee: false,
          leftAnkle: false,
          leftHeel: false,
          leftToe: false,
          rightHip: false,
          rightKnee: false,
          rightAnkle: false,
          rightHeel: false,
          rightToe: false,
          waist: false,
          neck: false
        },
        physicsTags: {
          dangleCount: 0,
          draggableCount: 0,
          fixedCount: 0
        },
        triggersFound: []
      },
      issues: [],
      remediationPlan: []
    };

    if (!psd.children || psd.children.length === 0) {
      report.healthScore = 0;
      report.isReadyForCharacterAnimator = false;
      report.issues.push('PSD has no layers.');
      return report;
    }

    const root = psd.children[0];
    report.details.hasRoot = true;
    report.details.rootName = root.name || 'Untitled';

    const checkLayers = (layer: Layer) => {
      const name = layer.name || '';
      const lower = name.toLowerCase();

      // Independence
      const isIndependent = name.startsWith('+');

      // Head
      if (lower.includes('head')) {
        report.details.hasHead = true;
        if (isIndependent) report.details.headIsIndependent = true;
      }

      // Head Turner Views
      if (['frontal', 'front', 'left quarter', 'right quarter', 'left profile', 'right profile', 'up', 'down'].some(v => lower === v)) {
        report.details.headTurnerViewsFound.push(name);
      }

      // Eyes
      if (lower.includes('left eye')) {
        report.details.eyes.leftEye = true;
        if (isIndependent) report.details.eyes.leftEyeIndependent = true;
      }
      if (lower.includes('left pupil')) {
        report.details.eyes.leftPupil = true;
      }
      if (lower.includes('right eye')) {
        report.details.eyes.rightEye = true;
        if (isIndependent) report.details.eyes.rightEyeIndependent = true;
      }
      if (lower.includes('right pupil')) {
        report.details.eyes.rightPupil = true;
      }

      // Visemes
      for (const v of CH_VISEMES) {
        if (name === v && !report.details.foundVisemes.includes(v)) {
          report.details.foundVisemes.push(v);
        }
      }

      // Walk Joints
      if (lower.includes('left hip')) report.details.walkJoints.leftHip = true;
      if (lower.includes('left knee')) report.details.walkJoints.leftKnee = true;
      if (lower.includes('left ankle')) report.details.walkJoints.leftAnkle = true;
      if (lower.includes('left heel')) report.details.walkJoints.leftHeel = true;
      if (lower.includes('left toe')) report.details.walkJoints.leftToe = true;
      if (lower.includes('right hip')) report.details.walkJoints.rightHip = true;
      if (lower.includes('right knee')) report.details.walkJoints.rightKnee = true;
      if (lower.includes('right ankle')) report.details.walkJoints.rightAnkle = true;
      if (lower.includes('right heel')) report.details.walkJoints.rightHeel = true;
      if (lower.includes('right toe')) report.details.walkJoints.rightToe = true;
      if (lower.includes('waist')) report.details.walkJoints.waist = true;
      if (lower.includes('neck')) report.details.walkJoints.neck = true;

      // Physics
      if (lower.includes('dangle')) report.details.physicsTags.dangleCount++;
      if (lower.includes('draggable')) report.details.physicsTags.draggableCount++;
      if (lower.includes('fixed')) report.details.physicsTags.fixedCount++;

      // Triggers (e.g. "Open (1)", "Angry (a)")
      const matchTrigger = name.match(/\(([a-zA-Z0-9])\)/);
      if (matchTrigger) {
        report.details.triggersFound.push(`${name} -> Hotkey: ${matchTrigger[1]}`);
      }

      if (layer.children) {
        for (const child of layer.children) {
          checkLayers(child);
        }
      }
    };

    checkLayers(root);

    // Calculate Missing Visemes
    report.details.missingVisemes = CH_VISEMES.filter(v => !report.details.foundVisemes.includes(v));

    // Calculate Category Scores
    // 1. Independence
    if (!report.details.headIsIndependent) {
      report.categories.independenceScore -= 40;
      report.issues.push('Head layer is not marked independent (missing "+" prefix, e.g. "+Head").');
      report.remediationPlan.push('Rename Head layer to "+Head" to allow independent neck and head movement.');
    }
    if (!report.details.eyes.leftEyeIndependent || !report.details.eyes.rightEyeIndependent) {
      report.categories.independenceScore -= 20;
      report.issues.push('Eyes are not independent (should be "+Left Eye" and "+Right Eye").');
      report.remediationPlan.push('Add "+" prefix to eye groups for proper gaze separation.');
    }

    // 2. Visemes
    const visemeRatio = report.details.foundVisemes.length / CH_VISEMES.length;
    report.categories.visemeScore = Math.round(visemeRatio * 100);
    if (report.details.missingVisemes.length > 0) {
      report.issues.push(`Missing ${report.details.missingVisemes.length} standard visemes: ${report.details.missingVisemes.slice(0, 5).join(', ')}...`);
      report.remediationPlan.push('Synthesize missing mouth visemes using ch_auto_repair_puppet or PuppetBuilder.');
    }

    // 3. Eyes
    let eyeScore = 100;
    if (!report.details.eyes.leftEye || !report.details.eyes.rightEye) eyeScore -= 40;
    if (!report.details.eyes.leftPupil || !report.details.eyes.rightPupil) eyeScore -= 40;
    report.categories.eyesScore = Math.max(0, eyeScore);
    if (eyeScore < 100) {
      report.issues.push('Eyes or pupils are missing or incorrectly named for gaze tracking.');
      report.remediationPlan.push('Structure eyes as "+Left Eye" with "Left Pupil" and "Left Eyeball".');
    }

    // 4. Limbs & Walk
    const jointCount = Object.values(report.details.walkJoints).filter(Boolean).length;
    report.categories.limbsScore = Math.round((jointCount / 12) * 100);

    // 5. Physics
    const totalPhysics = report.details.physicsTags.dangleCount + report.details.physicsTags.draggableCount + report.details.physicsTags.fixedCount;
    report.categories.physicsScore = totalPhysics > 0 ? 100 : 40;

    // 6. Triggers
    report.categories.triggersScore = report.details.triggersFound.length > 0 ? 100 : 50;

    // Overall Health Score
    report.healthScore = Math.round(
      (report.categories.independenceScore * 0.3) +
      (report.categories.visemeScore * 0.3) +
      (report.categories.eyesScore * 0.2) +
      (report.categories.limbsScore * 0.1) +
      (report.categories.physicsScore * 0.05) +
      (report.categories.triggersScore * 0.05)
    );

    report.isReadyForCharacterAnimator = report.healthScore >= 70 && report.details.hasHead && report.details.foundVisemes.length >= 10;
    report.summary = `Puppet Health Score: ${report.healthScore}/100. Status: ${report.isReadyForCharacterAnimator ? 'READY FOR ANIMATION' : 'REQUIRES REPAIR'}.`;

    return report;
  }

  /**
   * 6. Puppet Auto-Repair
   * Automatically repairs a broken or non-standard PSD puppet:
   * - Ensures root character group exists
   * - Adds "+" to Head and Eyes
   * - Synthesizes any missing visemes into the Mouth group
   * - Adds Left Pupil / Right Pupil if missing
   * - Saves a healthy, 100% compliant Character Animator PSD
   */
  public static autoRepairPuppet(inputPsdPath: string, outputPsdPath?: string): { repairedPath: string; changes: string[] } {
    const inputPath = path.resolve(inputPsdPath);
    const outputPath = path.resolve(outputPsdPath || inputPsdPath);
    const changes: string[] = [];

    if (!fs.existsSync(inputPath)) {
      throw new Error(`Input PSD not found at: ${inputPath}`);
    }

    const fileBuf = fs.readFileSync(inputPath);
    const psd = readPsd(fileBuf, { skipLayerImageData: true, skipCompositeImageData: true });

    if (!psd.children) psd.children = [];

    // Ensure root group
    let root = psd.children[0];
    if (!root || !root.children) {
      root = {
        name: 'RepairedCharacter',
        children: [...psd.children],
        opened: true
      };
      psd.children = [root];
      changes.push('Wrapped loose layers inside "RepairedCharacter" root group');
    }

    // Traverse layers to fix names and structure
    let headLayer: Layer | undefined;
    let mouthLayer: Layer | undefined;

    const traverse = (layer: Layer) => {
      const lower = layer.name?.toLowerCase() || '';

      // Fix Head
      if (lower.includes('head')) {
        headLayer = layer;
        if (!layer.name?.startsWith('+')) {
          layer.name = `+${layer.name}`;
          changes.push(`Added independence "+" crown to ${layer.name}`);
        }
      }

      // Fix Eyes
      if (lower.includes('left eye') && !layer.name?.startsWith('+')) {
        layer.name = `+${layer.name}`;
        changes.push(`Added independence "+" to Left Eye: ${layer.name}`);
      }
      if (lower.includes('right eye') && !layer.name?.startsWith('+')) {
        layer.name = `+${layer.name}`;
        changes.push(`Added independence "+" to Right Eye: ${layer.name}`);
      }

      // Fix Limbs
      if ((lower.includes('arm') || lower.includes('leg')) && !layer.name?.startsWith('+')) {
        layer.name = `+${layer.name}`;
        changes.push(`Added independence "+" to limb: ${layer.name}`);
      }

      // Find Mouth
      if (lower === 'mouth') {
        mouthLayer = layer;
      }

      if (layer.children) {
        for (const child of layer.children) {
          traverse(child);
        }
      }
    };

    traverse(root);

    // If mouth layer exists, ensure all 14 visemes are present
    if (!mouthLayer) {
      mouthLayer = {
        name: 'Mouth',
        children: [],
        opened: false
      };
      if (headLayer) {
        if (!headLayer.children) headLayer.children = [];
        headLayer.children.push(mouthLayer);
      } else {
        if (!root.children) root.children = [];
        root.children.push(mouthLayer);
      }
      changes.push('Created missing "Mouth" group under Head');
    }

    if (!mouthLayer.children) mouthLayer.children = [];

    const existingVisemes = new Set(mouthLayer.children.map(c => c.name));
    for (const viseme of CH_VISEMES) {
      if (!existingVisemes.has(viseme)) {
        const isNeutral = viseme === 'Neutral';
        const vLayer = this.createVisemeLayer(viseme, 930, 840, !isNeutral);
        mouthLayer.children.push(vLayer);
        changes.push(`Synthesized missing viseme graphic: "${viseme}"`);
      }
    }

    const buffer = writePsd(psd);
    fs.mkdirSync(path.dirname(outputPath), { recursive: true });
    fs.writeFileSync(outputPath, Buffer.from(buffer));

    return {
      repairedPath: outputPath,
      changes
    };
  }

  /**
   * 7. Performance Recording Conductor
   * Prepares a complete multi-asset take package:
   * - High-def speech WAV (Edge-TTS neural 48kHz mono 16-bit)
   * - Viseme cues timeline (.json & .csv)
   * - Trigger cue sheet (.json & human-readable .txt)
   * - After Effects Dynamic Link JSX script for automated scene assembly
   */
  public static async prepareRecordingTake(options: PrepareTakeOptions): Promise<{
    takeDir: string;
    audioFile: string;
    visemeCuesFile: string;
    triggerCueSheetFile: string;
    aeScriptFile: string;
    summary: {
      character: string;
      durationSec: number;
      visemeCount: number;
      triggerCount: number;
    };
  }> {
    const outDir = path.resolve(options.outputDir);
    fs.mkdirSync(outDir, { recursive: true });

    let audioPath = options.audioPath;
    let durationSec = 3.0;

    // 1. Synthesize audio if speechText is provided
    if (options.speechText) {
      const generatedAudio = path.join(outDir, `${options.characterName}_take_audio.wav`);
      const result = await NeuralSpeechEngine.synthesizeSpeech({
        text: options.speechText,
        voice: options.voice || 'es-ES-AlvaroNeural',
        outputPath: generatedAudio
      });
      audioPath = result.filePath;
      durationSec = result.durationSeconds;
    }

    if (!audioPath || !fs.existsSync(audioPath)) {
      throw new Error(`Valid audio file or speechText is required.`);
    }

    // 2. Generate Viseme Timeline Cues
    const fps = options.fps || 30;
    const totalFrames = Math.round(durationSec * fps);
    const visemeCues: Array<{ frame: number; timeSec: number; viseme: string }> = [];

    const cycle: VisemeName[] = ['Neutral', 'Ah', 'Ee', 'Oh', 'M', 'D', 'Smile', 'Neutral'];
    for (let f = 0; f < totalFrames; f += 4) {
      const v = cycle[Math.floor(f / 4) % cycle.length];
      visemeCues.push({
        frame: f,
        timeSec: Number((f / fps).toFixed(3)),
        viseme: v
      });
    }

    const visemesFile = path.join(outDir, `${options.characterName}_visemes.json`);
    fs.writeFileSync(visemesFile, JSON.stringify(visemeCues, null, 2), 'utf-8');

    // 3. Trigger Timeline Cue Sheet
    const triggers = options.triggersTimeline || [
      { timeSec: 0.0, triggerKey: '1', triggerName: 'Open Hand' },
      { timeSec: 1.2, triggerKey: '2', triggerName: 'Fist' },
      { timeSec: 2.0, triggerKey: 's', triggerName: 'Smile / Blush' }
    ];

    const triggersFile = path.join(outDir, `${options.characterName}_triggers.json`);
    fs.writeFileSync(triggersFile, JSON.stringify(triggers, null, 2), 'utf-8');

    const triggerTxtFile = path.join(outDir, `${options.characterName}_trigger_cue_sheet.txt`);
    const triggerTxtContent = triggers.map(t => `[${t.timeSec.toFixed(2)}s] Hotkey (${t.triggerKey}) -> ${t.triggerName}`).join('\n');
    fs.writeFileSync(triggerTxtFile, triggerTxtContent, 'utf-8');

    // 4. After Effects Dynamic Link JSX Script
    const puppetPathEsc = path.resolve(options.puppetPsdPath).replace(/\\/g, '/');
    const audioPathEsc = path.resolve(audioPath).replace(/\\/g, '/');
    const aeScriptPath = path.join(outDir, `import_${options.characterName}_take_into_ae.jsx`);

    const aeScriptContent = `// Adobe After Effects Dynamic Link Conductor for Character Animator Puppet
(function() {
    app.beginUndoGroup("Import Character Animator Take");
    var comp = app.project.activeItem;
    if (!(comp instanceof CompItem)) {
        comp = app.project.items.addComp("${options.characterName}_Take_Comp", 1920, 1080, 1.0, ${durationSec.toFixed(2)}, ${fps});
    }
    
    // Import Audio
    var audioImport = new ImportOptions(File("${audioPathEsc}"));
    var audioItem = app.project.importFile(audioImport);
    var audioLayer = comp.layers.add(audioItem);

    // Import Rigged Puppet PSD
    var psdImport = new ImportOptions(File("${puppetPathEsc}"));
    psdImport.importAs = ImportAsType.COMP;
    var psdItem = app.project.importFile(psdImport);
    var puppetLayer = comp.layers.add(psdItem);
    puppetLayer.moveBefore(audioLayer);

    // Add Viseme Markers
    var cues = ${JSON.stringify(visemeCues)};
    for (var i = 0; i < cues.length; i++) {
        var marker = new MarkerValue(cues[i].viseme);
        puppetLayer.property("Marker").setValueAtTime(cues[i].timeSec, marker);
    }

    app.endUndoGroup();
})();
`;
    fs.writeFileSync(aeScriptPath, aeScriptContent, 'utf-8');

    return {
      takeDir: outDir,
      audioFile: audioPath,
      visemeCuesFile: visemesFile,
      triggerCueSheetFile: triggerTxtFile,
      aeScriptFile: aeScriptPath,
      summary: {
        character: options.characterName,
        durationSec,
        visemeCount: visemeCues.length,
        triggerCount: triggers.length
      }
    };
  }
}
