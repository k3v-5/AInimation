import test from "node:test";
import assert from "node:assert/strict";
import fc from "fast-check";
import {
  EditorialProfileRegistry,
  EditorialGenre,
  EditorialProfileSchema,
  ProductionIntent,
} from "../../editorial/index.js";

test("Fase 4A — Editorial Profile Registry Suite", async (t) => {
  await t.test("provides valid schemas for all 10 canonical profiles", () => {
    const genres: EditorialGenre[] = [
      "VLOG",
      "DOCUMENTARY",
      "JOURNALISM",
      "EDUCATIONAL",
      "INTERVIEW",
      "NEWS",
      "CINEMATIC",
      "CORPORATE",
      "SHORT_FORM",
      "TECHNICAL",
    ];

    assert.equal(genres.length, 10);

    for (const genre of genres) {
      const profile = EditorialProfileRegistry.getProfile(genre);
      assert.equal(profile.genre, genre);
      assert.doesNotThrow(() => EditorialProfileSchema.parse(profile));

      // Invariant: B-Roll precedence over punch in must always be true
      assert.equal(profile.brollPolicy.precedenceOverPunchIn, true);
    }
  });

  await t.test("resolves profile explicitly and via AUTO heuristics based on intent", () => {
    // Explicit resolution
    const explicitIntent: ProductionIntent = {
      projectId: "proj_1",
      format: "DOCUMENTARY",
      primaryObjective: "DOCUMENT",
      audience: "GENERAL",
      platform: "YOUTUBE_16x9",
      language: "es-MX",
      tone: "SERIOUS",
      pacingPreference: "CONTEMPLATIVE",
      visualDensity: 0.4,
      narrationDensity: 0.7,
      brollDensity: 0.8,
    };
    const resolvedExplicit = EditorialProfileRegistry.resolveProfile(explicitIntent);
    assert.equal(resolvedExplicit.genre, "DOCUMENTARY");
    assert.equal(resolvedExplicit.silencePolicy.preserveDramaticPauses, true);

    // AUTO resolution -> VERTICAL_SOCIAL becomes SHORT_FORM
    const socialIntent: ProductionIntent = {
      ...explicitIntent,
      format: "AUTO",
      platform: "VERTICAL_SOCIAL",
    };
    const resolvedSocial = EditorialProfileRegistry.resolveProfile(socialIntent);
    assert.equal(resolvedSocial.genre, "SHORT_FORM");
    assert.equal(resolvedSocial.pacing.pacingCurve, "AGGRESSIVE");

    // AUTO resolution -> EDUCATE becomes EDUCATIONAL
    const eduIntent: ProductionIntent = {
      ...explicitIntent,
      format: "AUTO",
      primaryObjective: "EDUCATE",
    };
    const resolvedEdu = EditorialProfileRegistry.resolveProfile(eduIntent);
    assert.equal(resolvedEdu.genre, "EDUCATIONAL");
  });

  await t.test("PBT: any canonical profile satisfies baseline pacing and audio constraints", () => {
    fc.assert(
      fc.property(
        fc.constantFrom(
          "VLOG",
          "DOCUMENTARY",
          "JOURNALISM",
          "EDUCATIONAL",
          "INTERVIEW",
          "NEWS",
          "CINEMATIC",
          "CORPORATE",
          "SHORT_FORM",
          "TECHNICAL"
        ),
        (genre) => {
          const profile = EditorialProfileRegistry.getProfile(genre as EditorialGenre);
          return (
            profile.pacing.baseShotDurationSeconds > 0 &&
            profile.pacing.wordsPerMinuteTarget > 50 &&
            profile.silencePolicy.maxFillerSilenceSeconds > 0 &&
            profile.audioPolicy.targetDialogueLufs <= -10 &&
            profile.audioPolicy.targetDialogueLufs >= -30
          );
        }
      ),
      { numRuns: 50 }
    );
  });
});
