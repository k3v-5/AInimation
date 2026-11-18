import test from "node:test";
import assert from "node:assert/strict";
import { ProjectKnowledgeGraphEngine } from "../../editorial/index.js";

test("Fase 4A — Project Knowledge Graph Suite", async (t) => {
  await t.test("adds and indexes people, locations, claims, scenes, and shots", () => {
    const graph = new ProjectKnowledgeGraphEngine("project_alpha");

    graph.addPerson({
      id: "person_1",
      name: "Dr. Aris Thorne",
      role: "EXPERT",
      title: "Lead Geophysicist",
      affiliation: "Global Seismology Lab",
    });

    graph.addLocation({
      id: "loc_1",
      name: "Reykjavik Fault Zone",
      country: "Iceland",
      coordinates: { latitude: 64.1466, longitude: -21.9426 },
    });

    graph.addClaim({
      id: "claim_1",
      text: "The seismic anomaly escalated 300% over two weeks.",
      speakerId: "person_1",
      sourceCitation: "Report GEO-2026-X",
      confidence: 0.98,
      status: "VERIFIED",
      requiresOnScreenCitation: true,
    });

    graph.addScene({
      id: "scene_1",
      name: "Field Investigation",
      locationId: "loc_1",
      participantIds: ["person_1"],
      estimatedStartSeconds: 0,
      estimatedDurationSeconds: 120,
      narrativeImportance: 0.9,
    });

    graph.addShot({
      id: "shot_1",
      assetId: "raw_cam_a_01.mp4",
      sceneId: "scene_1",
      scale: "MEDIUM_CLOSE",
      startSeconds: 12.0,
      endSeconds: 18.5,
      durationSeconds: 6.5,
      technicalQuality: 0.95,
      subjectId: "person_1",
    });

    // Verification queries
    assert.equal(graph.getPerson("person_1")?.name, "Dr. Aris Thorne");
    assert.equal(graph.getLocation("loc_1")?.country, "Iceland");
    assert.equal(graph.getClaimsBySpeaker("person_1").length, 1);
    assert.equal(graph.getScenesByLocation("loc_1").length, 1);
    assert.equal(graph.getShotsForScene("scene_1").length, 1);

    const snapshot = graph.toSnapshot();
    assert.equal(snapshot.projectId, "project_alpha");
    assert.equal(snapshot.people.length, 1);
    assert.equal(snapshot.checksum.length, 64);
  });

  await t.test("guarantees 100% deterministic SHA-256 state checksum across instances", () => {
    const buildGraph = () => {
      const g = new ProjectKnowledgeGraphEngine("project_deterministic");
      g.addPerson({ id: "p1", name: "Alice", role: "INTERVIEWER" });
      g.addLocation({ id: "l1", name: "Tokyo" });
      g.addClaim({ id: "c1", text: "Population is 14 million", status: "VERIFIED" });
      return g.toSnapshot();
    };

    const snap1 = buildGraph();
    const snap2 = buildGraph();

    assert.equal(snap1.checksum, snap2.checksum);
  });
});
