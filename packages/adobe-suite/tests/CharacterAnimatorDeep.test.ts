import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import fs from 'fs';
import path from 'path';
import { readPsd, writePsd } from 'ag-psd';
import { CharacterAnimatorDeepEngine } from '../src/core/CharacterAnimatorDeepEngine.js';
import { characterTools } from '../src/tools/characterTools.js';

describe('Character Animator Deep Specialization Suite', () => {
  const testOutputDir = path.resolve('./temp_test_ch_deep');

  beforeAll(() => {
    fs.mkdirSync(testOutputDir, { recursive: true });
  });

  afterAll(() => {
    if (fs.existsSync(testOutputDir)) {
      fs.rmSync(testOutputDir, { recursive: true, force: true });
    }
  });

  it('scaffolds a 5-view Multi-Angle Head Turner puppet with dedicated visemes', () => {
    const outPsd = path.join(testOutputDir, 'HeadTurnerHero.psd');
    const resultPath = CharacterAnimatorDeepEngine.scaffoldMultiAnglePuppet({
      characterName: 'HeadTurnerHero',
      outPath: outPsd,
      views: '5-view',
      includeLimbs: true,
      includePhysics: true
    });

    expect(fs.existsSync(resultPath)).toBe(true);
    const buffer = fs.readFileSync(resultPath);
    const psd = readPsd(buffer, { skipLayerImageData: true, skipCompositeImageData: true });

    expect(psd.children).toBeDefined();
    expect(psd.children![0].name).toBe('HeadTurnerHero');

    const root = psd.children![0];
    const head = root.children?.find(c => c.name === '+Head');
    expect(head).toBeDefined();

    // Verify all 5 Head Turner angles are present
    const angleNames = head!.children?.map(c => c.name);
    expect(angleNames).toContain('Frontal');
    expect(angleNames).toContain('Left Quarter');
    expect(angleNames).toContain('Right Quarter');
    expect(angleNames).toContain('Left Profile');
    expect(angleNames).toContain('Right Profile');

    // Verify Frontal view has Mouth with 14 visemes
    const frontal = head!.children?.find(c => c.name === 'Frontal');
    const mouth = frontal?.children?.find(c => c.name === 'Mouth');
    expect(mouth).toBeDefined();
    expect(mouth!.children?.length).toBe(14);

    // Frontal is visible, profiles are hidden by default
    expect(frontal?.hidden).toBe(false);
    const leftProfile = head!.children?.find(c => c.name === 'Left Profile');
    expect(leftProfile?.hidden).toBe(true);
  });

  it('scaffolds a Walk-Cycle rigged puppet with exact joint tags for Walk Behavior', () => {
    const outPsd = path.join(testOutputDir, 'WalkRunner.psd');
    const resultPath = CharacterAnimatorDeepEngine.scaffoldWalkPuppet({
      characterName: 'WalkRunner',
      outPath: outPsd,
      walkViews: ['Frontal', 'Left Profile', 'Right Profile']
    });

    expect(fs.existsSync(resultPath)).toBe(true);
    const buffer = fs.readFileSync(resultPath);
    const psd = readPsd(buffer, { skipLayerImageData: true, skipCompositeImageData: true });

    const root = psd.children![0];
    expect(root.name).toBe('WalkRunner');

    // Check Frontal view
    const frontal = root.children?.find(c => c.name === 'Frontal');
    expect(frontal).toBeDefined();
    const body = frontal?.children?.find(c => c.name === 'Body');
    expect(body).toBeDefined();

    // Check Torso has Waist and Neck joint tags
    const torso = body?.children?.find(c => c.name === 'Torso');
    const torsoTags = torso?.children?.map(c => c.name);
    expect(torsoTags).toContain('Waist');
    expect(torsoTags).toContain('Neck');
    expect(torsoTags).toContain('Left Hip');
    expect(torsoTags).toContain('Right Hip');

    // Check Left Leg has Hip/Knee/Ankle/Heel/Toe tags
    const leftLeg = body?.children?.find(c => c.name === '+Left Leg');
    expect(leftLeg).toBeDefined();
    const leftLegTags = leftLeg?.children?.map(c => c.name);
    expect(leftLegTags).toContain('Left Knee');
    expect(leftLegTags).toContain('Left Ankle');
    expect(leftLegTags).toContain('Left Heel');
    expect(leftLegTags).toContain('Left Toe');
  });

  it('injects emotional swap sets, cycle layers, hand gestures, and breathing physics into a PSD', () => {
    // Start with a basic scaffold
    const basePsd = path.join(testOutputDir, 'TriggerBase.psd');
    CharacterAnimatorDeepEngine.scaffoldMultiAnglePuppet({
      characterName: 'TriggerHero',
      outPath: basePsd,
      views: '3-view'
    });

    const enrichedPsd = path.join(testOutputDir, 'TriggerEnriched.psd');
    const res = CharacterAnimatorDeepEngine.addPuppetTriggersAndPhysics({
      psdPath: basePsd,
      outPath: enrichedPsd,
      includeEmotions: true,
      includeHandGestures: true,
      includeCycleLayers: true,
      includeBreathing: true
    });

    expect(fs.existsSync(res.outPath)).toBe(true);
    expect(res.addedFeatures.length).toBeGreaterThanOrEqual(4);

    const buffer = fs.readFileSync(res.outPath);
    const psd = readPsd(buffer, { skipLayerImageData: true, skipCompositeImageData: true });

    const audit = CharacterAnimatorDeepEngine.auditPuppetDeep(res.outPath);
    expect(audit.details.triggersFound.length).toBeGreaterThan(0);
  });

  it('slices artwork specifications into an anatomical 14-viseme rigged Character Animator PSD', () => {
    const outPsd = path.join(testOutputDir, 'ArtworkCharacter.psd');
    const resultPath = CharacterAnimatorDeepEngine.sliceArtworkToPuppet({
      characterName: 'ArtworkBot',
      outPath: outPsd,
      primaryColor: [40, 160, 220],
      skinColor: [245, 190, 150]
    });

    expect(fs.existsSync(resultPath)).toBe(true);
    const audit = CharacterAnimatorDeepEngine.auditPuppetDeep(resultPath);
    expect(audit.details.hasHead).toBe(true);
    expect(audit.details.headIsIndependent).toBe(true);
    expect(audit.details.foundVisemes.length).toBe(14);
    expect(audit.healthScore).toBeGreaterThanOrEqual(70);
    expect(audit.isReadyForCharacterAnimator).toBe(true);
  });

  it('Puppet Doctor: deeply audits a puppet and automatically repairs a broken PSD', () => {
    // 1. Create an intentionally broken PSD (loose layers, missing +, missing visemes, no root group)
    const brokenPsd = path.join(testOutputDir, 'BrokenPuppet.psd');
    const brokenDoc = {
      width: 1000,
      height: 1000,
      channels: 4,
      bitsPerChannel: 8,
      colorMode: 3,
      children: [
        {
          name: 'Head', // missing '+'
          children: [
            { name: 'Left Eye', children: [] }, // missing '+'
            { name: 'Right Eye', children: [] }, // missing '+'
            {
              name: 'Mouth',
              children: [
                { name: 'Neutral', hidden: false } // only 1 viseme! missing 13 visemes
              ]
            }
          ]
        },
        {
          name: 'Body',
          children: [
            { name: 'Left Arm', children: [] } // missing '+'
          ]
        }
      ]
    };
    fs.writeFileSync(brokenPsd, Buffer.from(writePsd(brokenDoc as any)));

    // 2. Audit the broken puppet
    const preAudit = CharacterAnimatorDeepEngine.auditPuppetDeep(brokenPsd);
    expect(preAudit.details.headIsIndependent).toBe(false);
    expect(preAudit.details.missingVisemes.length).toBe(13);
    expect(preAudit.healthScore).toBeLessThan(70);
    expect(preAudit.issues.length).toBeGreaterThan(0);

    // 3. Run auto-repair
    const repairedPsd = path.join(testOutputDir, 'RepairedPuppet.psd');
    const repairResult = CharacterAnimatorDeepEngine.autoRepairPuppet(brokenPsd, repairedPsd);
    expect(repairResult.changes.length).toBeGreaterThan(0);

    // 4. Audit repaired puppet
    const postAudit = CharacterAnimatorDeepEngine.auditPuppetDeep(repairedPsd);
    expect(postAudit.details.headIsIndependent).toBe(true);
    expect(postAudit.details.foundVisemes.length).toBe(14); // All 14 synthesized!
    expect(postAudit.healthScore).toBeGreaterThanOrEqual(70);
    expect(postAudit.isReadyForCharacterAnimator).toBe(true);
  });

  it('prepares a full recording take bundle with speech audio, viseme cues, trigger cue sheet, and After Effects JSX', async () => {
    const puppetPsd = path.join(testOutputDir, 'TakeHero.psd');
    CharacterAnimatorDeepEngine.scaffoldMultiAnglePuppet({
      characterName: 'TakeHero',
      outPath: puppetPsd
    });

    const takeDir = path.join(testOutputDir, 'Take_01');
    const result = await CharacterAnimatorDeepEngine.prepareRecordingTake({
      characterName: 'TakeHero',
      puppetPsdPath: puppetPsd,
      outputDir: takeDir,
      speechText: '¡Bienvenidos a la animación profesional con Character Animator!',
      voice: 'mexico_male',
      triggersTimeline: [
        { timeSec: 0.0, triggerKey: '1', triggerName: 'Open Hand' },
        { timeSec: 1.0, triggerKey: '2', triggerName: 'Fist' },
        { timeSec: 2.2, triggerKey: 'b', triggerName: 'Blush' }
      ]
    });

    expect(fs.existsSync(result.audioFile)).toBe(true);
    expect(fs.existsSync(result.visemeCuesFile)).toBe(true);
    expect(fs.existsSync(result.triggerCueSheetFile)).toBe(true);
    expect(fs.existsSync(result.aeScriptFile)).toBe(true);

    const visemesData = JSON.parse(fs.readFileSync(result.visemeCuesFile, 'utf-8'));
    expect(visemesData.length).toBeGreaterThan(0);

    const aeScript = fs.readFileSync(result.aeScriptFile, 'utf-8');
    expect(aeScript).toContain('app.beginUndoGroup("Import Character Animator Take");');
    expect(aeScript).toContain('ImportAsType.COMP');
  });

  it('MCP Character Tools handles tool invocations cleanly', async () => {
    // Test ch_scaffold_multi_angle_puppet handler
    const scaffoldAngleTool = characterTools.find(t => t.name === 'ch_scaffold_multi_angle_puppet');
    expect(scaffoldAngleTool).toBeDefined();

    const testMultiPath = path.join(testOutputDir, 'McpMultiAngle.psd');
    const response = await scaffoldAngleTool!.handler({
      character_name: 'McpMulti',
      output_path: testMultiPath,
      views: '3-view'
    });

    const parsed = JSON.parse(response.content[0].text);
    expect(parsed.status).toBe('SUCCESS');
    expect(parsed.ready_for_head_turner).toBe(true);

    // Test ch_audit_puppet_deep handler
    const auditTool = characterTools.find(t => t.name === 'ch_audit_puppet_deep');
    expect(auditTool).toBeDefined();

    const auditResponse = await auditTool!.handler({
      file_path: testMultiPath
    });

    const auditParsed = JSON.parse(auditResponse.content[0].text);
    expect(auditParsed.healthScore).toBeGreaterThanOrEqual(70);
    expect(auditParsed.details.hasHead).toBe(true);
  });
});
