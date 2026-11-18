// Cross-Dimension Rescue — After Effects Master Composition Script
// Compiled automatically by after-effects-motion-engine for IANIMATION 5-Engine Monorepo
// Strictly adheres to Editorial Poster / TIME Style (USER_DESIGN_PREFERENCES.md)

(function buildCrossDimensionRescueComp() {
    app.beginUndoGroup("Build Cross-Dimension Rescue Master Comp");

    var COMP_NAME = "CrossDimensionRescue_Master_1280x720";
    var COMP_W = 1280;
    var COMP_H = 720;
    var COMP_FPS = 24;
    var COMP_DUR = 12.0;

    var APPROVED_FONTS = ["Impact", "Arial-Black", "Haettenschweiler", "Anton", "BebasNeue", "SegoeUI-Black", "Arial-BoldMT"];
    var COL_CRIMSON = [1.0, 0.08, 0.14];   // #FF1424
    var COL_WHITE   = [0.98, 0.98, 0.98];  // #FAFAFA
    var COL_SLATE   = [0.03, 0.03, 0.05];  // #08080D
    var BEAT_TIMESTAMPS = [0.0, 0.5226, 1.0453, 1.5679, 2.0906, 2.6132, 3.1359, 3.6585, 4.1812, 4.7038, 5.2265, 5.7491, 6.2718, 6.7944, 7.3171, 7.8397, 8.3624, 8.885, 9.4077, 9.9303, 10.453, 10.9756, 11.4983];
    var WORD_CUES = [
  {
    "word": "ALERTA",
    "start_sec": 5.85,
    "end_sec": 6.198,
    "start_frame": 141,
    "end_frame": 150
  },
  {
    "word": "EN",
    "start_sec": 6.198,
    "end_sec": 6.315,
    "start_frame": 150,
    "end_frame": 153
  },
  {
    "word": "SECTOR",
    "start_sec": 6.315,
    "end_sec": 6.605,
    "start_frame": 153,
    "end_frame": 160
  },
  {
    "word": "SIETE",
    "start_sec": 6.605,
    "end_sec": 6.895,
    "start_frame": 160,
    "end_frame": 166
  },
  {
    "word": "NÚCLEO",
    "start_sec": 6.895,
    "end_sec": 7.244,
    "start_frame": 166,
    "end_frame": 175
  },
  {
    "word": "TÉRMICO",
    "start_sec": 7.244,
    "end_sec": 7.592,
    "start_frame": 175,
    "end_frame": 183
  },
  {
    "word": "INESTABLE",
    "start_sec": 7.592,
    "end_sec": 8.115,
    "start_frame": 183,
    "end_frame": 196
  },
  {
    "word": "UNIDAD",
    "start_sec": 8.115,
    "end_sec": 8.464,
    "start_frame": 196,
    "end_frame": 204
  },
  {
    "word": "DE",
    "start_sec": 8.464,
    "end_sec": 8.58,
    "start_frame": 204,
    "end_frame": 207
  },
  {
    "word": "RESCATE",
    "start_sec": 8.58,
    "end_sec": 8.986,
    "start_frame": 207,
    "end_frame": 217
  },
  {
    "word": "DESPLEGADA",
    "start_sec": 8.986,
    "end_sec": 9.567,
    "start_frame": 217,
    "end_frame": 231
  }
];

    var proj = app.project || app.newProject();
    var comp = proj.items.addComp(COMP_NAME, COMP_W, COMP_H, 1.0, COMP_DUR, COMP_FPS);
    comp.bgColor = COL_SLATE;
    comp.motionBlur = true;
    comp.shutterAngle = 180;

    // 1. Background Slate Solid & Contrast Vignette Layer
    var bgLayer = comp.layers.addSolid(COL_SLATE, "Backdrop_DeepSlate", COMP_W, COMP_H, 1.0, COMP_DUR);
    bgLayer.motionBlur = true;

    // 2. Minimalist 24-Tick Rotating Vector Clock Dial (Editorial Poster Style)
    var dialLayer = comp.layers.addShape();
    dialLayer.name = "Editorial_ClockDial_24Ticks";
    dialLayer.motionBlur = true;
    dialLayer.property("Transform").property("Position").setValue([COMP_W / 2, COMP_H / 2]);
    dialLayer.property("Transform").property("Opacity").setValue(28);
    dialLayer.property("Transform").property("Rotation").expression = "time * 15;";
    var rootGroup = dialLayer.property("Contents").addProperty("ADBE Vector Group");
    var tickRect = rootGroup.property("Contents").addProperty("ADBE Vector Shape - Rect");
    tickRect.property("Size").setValue([3, 18]);
    tickRect.property("Position").setValue([0, -250]);
    var tickFill = rootGroup.property("Contents").addProperty("ADBE Vector Graphic - Fill");
    tickFill.property("Color").setValue(COL_WHITE);
    var repeater = rootGroup.property("Contents").addProperty("ADBE Vector Filter - Repeater");
    repeater.property("Copies").setValue(24);
    repeater.property("Transform").property("Rotation").setValue(15);

    // 3. 808 Beat-Reactive Snap Zoom Null Driver
    var beatNull = comp.layers.addNull(COMP_DUR);
    beatNull.name = "808_SnapZoom_Controller";
    beatNull.motionBlur = true;
    beatNull.property("Transform").property("Scale").expression = [
        "var beats = " + JSON.stringify(BEAT_TIMESTAMPS) + ";",
        "var boost = 0;",
        "for (var i = 0; i < beats.length; i++) {",
        "  var dt = time - beats[i];",
        "  if (dt >= 0 && dt < 0.35) boost = Math.max(boost, Math.exp(-10.5 * dt));",
        "}",
        "var s = 100 + 7.5 * boost;",
        "[s, s];"
    ].join("\n");

    function addEditorialTextLayer(name, content, fontSize, colorRGB, yPos, inPt, outPt, trackingVal, stretchY) {
        var tl = comp.layers.addText(content);
        tl.name = name;
        tl.startTime = 0;
        tl.inPoint = inPt;
        tl.outPoint = outPt;
        tl.motionBlur = true;

        var textProp = tl.property("Source Text");
        var textDoc = textProp.value;
        textDoc.font = APPROVED_FONTS[0];
        textDoc.fontSize = fontSize;
        textDoc.fillColor = colorRGB;
        textDoc.justification = ParagraphJustification.CENTER_JUSTIFY;
        textDoc.tracking = trackingVal;
        textProp.setValue(textDoc);

        var rect = tl.sourceRectAtTime(inPt + 0.05, false);
        tl.property("Transform").property("Anchor Point").setValue([rect.left + rect.width / 2, rect.top + rect.height / 2]);
        tl.property("Transform").property("Position").setValue([COMP_W / 2, yPos]);
        tl.property("Transform").property("Scale").setValue([100, stretchY]);
        tl.property("Transform").property("Scale").expression = [
            "var freq = 4.0; var decay = 7.0; var amp = 0.04;",
            "var t = Math.max(0, time - inPoint);",
            "var bounce = 1.0 + amp * Math.exp(-decay * t) * Math.sin(freq * t * 2 * Math.PI);",
            "[value[0] * bounce, value[1] * bounce];"
        ].join("\n");
        return tl;
    }

    // 4. Act 3 Kinetic Dialogue Word Cues (6.0s .. 9.5s)
    for (var w = 0; w < WORD_CUES.length; w++) {
        var cue = WORD_CUES[w];
        var isKeyWord = (cue.word === "SIETE." || cue.word === "NÚCLEO" || cue.word === "INESTABLE." || cue.word === "RESCATE");
        addEditorialTextLayer(
            "DialogueCue_" + w + "_" + cue.word,
            cue.word,
            isKeyWord ? 54 : 44,
            isKeyWord ? COL_CRIMSON : COL_WHITE,
            602,
            cue.start_sec,
            cue.end_sec + 0.12,
            -12,
            122
        );
    }

    // 5. Act 4 Hero TIME-Style Poster Titles (9.0s .. 12.0s)
    addEditorialTextLayer("Tag_Header", "✦ IANIMATION MONOREPO ✦", 26, COL_WHITE, 185, 10.65, 12.0, 32, 100);
    addEditorialTextLayer("Poster_Title_White", "CROSS-DIMENSION", 92, COL_WHITE, 295, 10.72, 12.0, -15, 135);
    addEditorialTextLayer("Poster_Title_Crimson", "RESCUE", 156, COL_CRIMSON, 438, 10.80, 12.0, -18, 138);
    addEditorialTextLayer("Poster_Badge_Footer", "[ 5 ENGINES // 144 MCP TOOLS // 2026 ]", 24, COL_WHITE, 558, 10.90, 12.0, 28, 100);

    app.endUndoGroup();
})();
