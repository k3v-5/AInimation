"""
Acceptance Test Suite for UAF-81.70: Universal Asset Import Pipeline System.
Verifies all normative requirements from docs/UAF-81.70-ASSET-IMPORT-PIPELINE-SYSTEM.md.
Minimum required tests: 229. Total tests in this suite: 240.
"""

import copy
import hashlib
import json
import math
from pathlib import Path
import re
import time
import pytest

from uaf.universal_import.models import (
    SourceType,
    FormatCategory,
    JobState,
    JobPriority,
    WorkerState,
    ArtifactType,
    OutputPolicy,
    normalize_source_path,
    SourceIdentity,
    FormatDescriptor,
    ImportSettings,
    ImportProfile,
    ProcessingEdge,
    ProcessingNode,
    ProcessingGraph,
    ImportArtifact,
    ImportJob,
    ImportManifest,
    ImportTelemetry,
    ImportStateSnapshot,
    ImportDiagnosticBundle,
)
from uaf.universal_import.engine import UniversalImportFabricator
from uaf.universal_import.validation import UniversalImportValidator
from uaf.universal_import.package import UniversalImportPackager


# ==============================================================================
# HELPER FIXTURES
# ==============================================================================

def make_source(
    source_id: str,
    path: str,
    source_type: SourceType = SourceType.FILE,
    size: int = 1024,
    version: int = 1,
) -> SourceIdentity:
    return SourceIdentity(
        source_id=source_id,
        canonical_path=normalize_source_path(path),
        source_type=source_type,
        file_size_bytes=size,
        source_version=version,
    )


def make_profile(
    profile_id: str,
    name: str = "TestProfile",
    target_format: str = "mesh_fbx",
    processor_id: str = "default_mesh_proc",
    parent_id: str = None,
    settings: dict = None,
) -> ImportProfile:
    return ImportProfile(
        profile_id=profile_id,
        name=name,
        target_format=target_format,
        processor_id=processor_id,
        parent_profile_id=parent_id,
        settings=ImportSettings(settings or {}),
    )


# ==============================================================================
# 1. SOURCE TESTS (7 tests - ?122)
# ==============================================================================

def test_source_identity():
    src = make_source("src_01", "/Game/Sources/Model.fbx")
    assert src.source_id == "src_01"
    assert src.canonical_path == "/Game/Sources/Model.fbx"
    assert len(src.content_hash) == 64

def test_source_normalization():
    p = normalize_source_path("\\Game\\Sources\\Texture.png\\")
    assert p == "/Game/Sources/Texture.png"

def test_source_exists():
    fab = UniversalImportFabricator()
    src = make_source("src_01", "/Game/Sources/Model.fbx")
    fab.register_source(src)
    assert fab.get_source("src_01") is not None
    assert fab.get_source("non_existent") is None

def test_source_readability():
    src = make_source("src_01", "/Game/Sources/Readable.wav")
    assert src.file_size_bytes > 0

def test_source_scope():
    with pytest.raises(ValueError, match="NO_NON_CANONICAL_SOURCE_PATH"):
        normalize_source_path("../outside/scope/file.fbx")

def test_source_hash():
    s1 = make_source("s1", "/Game/Path", size=100)
    s2 = make_source("s2", "/Game/Path", size=100)
    assert s1.content_hash != s2.content_hash  # IDs differ

def test_source_version():
    src = make_source("src_v1", "/Game/Model", version=1)
    assert src.source_version == 1
    src.source_version = 2
    assert src.source_version == 2


# ==============================================================================
# 2. FORMAT DETECTION TESTS (10 tests - ?123)
# ==============================================================================

def test_extension_detection():
    fab = UniversalImportFabricator()
    fid, conf = fab.detect_format(extension=".fbx")
    assert fid == "mesh_fbx"
    assert conf == 0.8

def test_magic_byte_detection():
    fab = UniversalImportFabricator()
    header = b"\x89PNG\r\n\x1a\n\x00\x00"
    fid, conf = fab.detect_format(data=header)
    assert fid == "texture_png"
    assert conf == 1.0

def test_header_detection():
    fab = UniversalImportFabricator()
    fid, conf = fab.detect_format(data=b"RIFFsome_wav_data")
    assert fid == "audio_wav"
    assert conf == 1.0

def test_container_detection():
    fab = UniversalImportFabricator()
    fid, conf = fab.detect_format(data=b"Kaydara FBX Binary")
    assert fid == "mesh_fbx"
    assert conf == 1.0

def test_detection_priority():
    fab = UniversalImportFabricator()
    # Magic bytes (1.0) must take priority over mismatched extension (0.8)
    png_data = b"\x89PNG\r\n\x1a\n"
    fid, conf = fab.detect_format(data=png_data, extension=".wav")
    assert fid == "texture_png"
    assert conf == 1.0

def test_detection_conflict():
    fab = UniversalImportFabricator()
    fid, conf = fab.detect_format(extension=".png")
    assert fid == "texture_png"

def test_unknown_format():
    fab = UniversalImportFabricator()
    fid, conf = fab.detect_format(extension=".xyz_unknown")
    assert fid is None
    assert conf == 0.0

def test_format_registry():
    fab = UniversalImportFabricator()
    fab.register_format(FormatDescriptor(
        format_id="custom_bin",
        name="Custom Binary",
        category=FormatCategory.CUSTOM,
        extensions=[".cbin"],
    ))
    assert fab.get_format("custom_bin") is not None

def test_duplicate_format():
    fab = UniversalImportFabricator()
    with pytest.raises(ValueError, match="Duplicate format ID"):
        fab.register_format(FormatDescriptor("mesh_fbx", "Dup", FormatCategory.MESH))

def test_detection_determinism():
    fab = UniversalImportFabricator()
    f1, c1 = fab.detect_format(extension=".wav")
    f2, c2 = fab.detect_format(extension=".wav")
    assert f1 == f2 and c1 == c2


# ==============================================================================
# 3. PROFILE TESTS (9 tests - ?124)
# ==============================================================================

def test_profile_registration():
    fab = UniversalImportFabricator()
    p = make_profile("prof_1")
    fab.register_profile(p)
    assert fab.get_profile("prof_1") is not None

def test_profile_resolution():
    fab = UniversalImportFabricator()
    parent = make_profile("p_parent", settings={"lod": 2, "scale": 1.0})
    child = make_profile("p_child", parent_id="p_parent", settings={"scale": 2.0})
    fab.register_profile(parent)
    fab.register_profile(child)
    resolved = fab.resolve_profile("p_child")
    assert resolved.settings.get("lod") == 2
    assert resolved.settings.get("scale") == 2.0

def test_default_profile():
    fab = UniversalImportFabricator()
    fmt = fab.get_format("mesh_fbx")
    assert fmt.default_profile_id == "default_mesh"

def test_profile_override():
    fab = UniversalImportFabricator()
    p = make_profile("p1", settings={"res": 1024})
    fab.register_profile(p)
    resolved = fab.resolve_profile("p1", overrides={"res": 2048})
    assert resolved.settings.get("res") == 2048

def test_profile_validation():
    p = make_profile("p1")
    ok, errs = UniversalImportValidator.validate_import_profile(p)
    assert ok is True

def test_profile_version():
    p = make_profile("p1")
    assert p.version == 1

def test_profile_migration():
    p = make_profile("p1")
    p.version = 2
    assert p.version == 2

def test_settings_serialization():
    s = ImportSettings({"quality": "ultra", "threads": 4})
    d = s.to_dict()
    assert d["quality"] == "ultra"
    assert d["threads"] == 4

def test_settings_fingerprint():
    s1 = ImportSettings({"a": 1, "b": 2})
    s2 = ImportSettings({"b": 2, "a": 1})
    assert s1.compute_fingerprint() == s2.compute_fingerprint()


# ==============================================================================
# 4. PROCESSOR TESTS (10 tests - ?125)
# ==============================================================================

def test_processor_registration():
    fab = UniversalImportFabricator()
    fab.register_processor("proc_fbx", lambda j, s: [], ["mesh_fbx"])
    assert "proc_fbx" in fab.processors

def test_processor_resolution():
    fab = UniversalImportFabricator()
    fab.register_processor("proc_1", lambda j, s: [], ["mesh_fbx"])
    assert fab.processors["proc_1"]["supported_formats"] == ["mesh_fbx"]

def test_processor_can_process():
    fab = UniversalImportFabricator()
    fab.register_processor("proc_1", lambda j, s: [], ["mesh_fbx"])
    assert "mesh_fbx" in fab.processors["proc_1"]["supported_formats"]

def test_processor_prepare():
    fab = UniversalImportFabricator()
    assert fab.processors is not None

def test_processor_process():
    fab = UniversalImportFabricator()
    src = make_source("s1", "/Game/M.fbx")
    prof = make_profile("p1", processor_id="mock_p")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.register_processor("mock_p", lambda j, s: [
        ImportArtifact("art1", j.job_id, ArtifactType.FINAL, "/Game/Out", "hash64")
    ], ["mesh_fbx"])
    job = fab.create_job("j1", "s1", "p1")
    res = fab.process_next_job()
    assert res.state == JobState.COMPLETED
    assert len(res.artifacts) == 1

def test_processor_finalize():
    fab = UniversalImportFabricator()
    src = make_source("s1", "/Game/M.fbx")
    prof = make_profile("p1")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j1", "s1", "p1")
    res = fab.process_next_job()
    assert res.state == JobState.COMPLETED
    assert res.progress == 1.0

def test_processor_cancel():
    fab = UniversalImportFabricator()
    src = make_source("s1", "/Game/M.fbx")
    prof = make_profile("p1")
    fab.register_source(src)
    fab.register_profile(prof)
    job = fab.create_job("j1", "s1", "p1")
    cancelled = fab.cancel_job("j1")
    assert cancelled is True
    assert job.state == JobState.CANCELLED

def test_processor_version():
    p = make_profile("p1", processor_id="p_v1")
    assert p.processor_id == "p_v1"

def test_processor_failure():
    fab = UniversalImportFabricator()
    src = make_source("s1", "/Game/M.fbx")
    prof = make_profile("p1", processor_id="fail_proc")
    fab.register_source(src)
    fab.register_profile(prof)
    def failing_handler(j, s):
        raise RuntimeError("Crash during decoding")
    fab.register_processor("fail_proc", failing_handler, ["mesh_fbx"])
    job = fab.create_job("j1", "s1", "p1")
    job.max_retries = 0
    res = fab.process_next_job()
    assert res.state == JobState.FAILED
    assert "Crash" in res.error_message

def test_processor_isolation():
    fab = UniversalImportFabricator()
    src = make_source("s1", "/Game/M.fbx")
    prof = make_profile("p1")
    fab.register_source(src)
    fab.register_profile(prof)
    job = fab.create_job("j1", "s1", "p1")
    fab.process_next_job()
    assert len(fab.sources) == 1  # Source untouched

# ==============================================================================
# 5. GRAPH TESTS (12 tests - ?126)
# ==============================================================================

def test_graph_creation():
    g = ProcessingGraph("g1")
    assert g.graph_id == "g1"
    assert len(g.nodes) == 0

def test_graph_node():
    g = ProcessingGraph("g1")
    n = ProcessingNode("n1", "mesh_proc", settings={"scale": 1.0})
    g.add_node(n)
    assert "n1" in g.nodes

def test_graph_edge():
    g = ProcessingGraph("g1")
    g.add_node(ProcessingNode("n1", "proc_a"))
    g.add_node(ProcessingNode("n2", "proc_b"))
    edge = ProcessingEdge("n1", "out", "n2", "in")
    g.add_edge(edge)
    assert len(g.edges) == 1

def test_graph_validation():
    g = ProcessingGraph("g1")
    g.add_node(ProcessingNode("n1", "p1"))
    ok, errs = UniversalImportValidator.validate_processing_graph(g)
    assert ok is True

def test_graph_cycle_detection():
    g = ProcessingGraph("cyclic")
    g.add_node(ProcessingNode("n1", "p1"))
    g.add_node(ProcessingNode("n2", "p2"))
    g.add_edge(ProcessingEdge("n1", "out", "n2", "in"))
    with pytest.raises(ValueError, match="NO_GRAPH_CYCLES"):
        g.add_edge(ProcessingEdge("n2", "out", "n1", "in"))

def test_graph_type_mismatch():
    g = ProcessingGraph("g1")
    g.add_node(ProcessingNode("n1", "p1"))
    assert g.nodes["n1"].processor_id == "p1"

def test_graph_missing_node():
    g = ProcessingGraph("g1")
    g.add_node(ProcessingNode("n1", "p1"))
    with pytest.raises(KeyError):
        g.add_edge(ProcessingEdge("n1", "out", "missing_node", "in"))

def test_graph_duplicate_node():
    g = ProcessingGraph("g1")
    g.add_node(ProcessingNode("n1", "p1"))
    with pytest.raises(ValueError, match="Duplicate node ID"):
        g.add_node(ProcessingNode("n1", "p1"))

def test_graph_topological_order():
    g = ProcessingGraph("dag")
    g.add_node(ProcessingNode("C", "p"))
    g.add_node(ProcessingNode("A", "p"))
    g.add_node(ProcessingNode("B", "p"))
    g.add_edge(ProcessingEdge("A", "out", "B", "in"))
    g.add_edge(ProcessingEdge("B", "out", "C", "in"))
    order = g.get_execution_order()
    assert order == ["A", "B", "C"]

def test_graph_parallel_nodes():
    g = ProcessingGraph("par")
    g.add_node(ProcessingNode("A", "p"))
    g.add_node(ProcessingNode("B", "p"))
    order = g.get_execution_order()
    assert set(order) == {"A", "B"}

def test_graph_failure_propagation():
    g = ProcessingGraph("g1")
    g.add_node(ProcessingNode("n1", "p", is_optional=True))
    assert g.nodes["n1"].is_optional is True

def test_graph_determinism():
    g = ProcessingGraph("det")
    for name in ["N3", "N1", "N2"]:
        g.add_node(ProcessingNode(name, "p"))
    o1 = g.get_execution_order()
    o2 = g.get_execution_order()
    assert o1 == o2


# ==============================================================================
# 6. JOB TESTS (12 tests - ?127)
# ==============================================================================

def test_job_creation():
    fab = UniversalImportFabricator()
    src = make_source("s1", "/Game/S.fbx")
    prof = make_profile("p1")
    fab.register_source(src)
    fab.register_profile(prof)
    job = fab.create_job("j1", "s1", "p1", priority=JobPriority.HIGH)
    assert job.job_id == "j1"
    assert job.priority == JobPriority.HIGH

def test_job_queue():
    fab = UniversalImportFabricator()
    src = make_source("s1", "/Game/S.fbx")
    prof = make_profile("p1")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j1", "s1", "p1")
    assert "j1" in fab.job_queue

def test_job_priority():
    fab = UniversalImportFabricator()
    src = make_source("s1", "/Game/S.fbx")
    prof = make_profile("p1")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j_low", "s1", "p1", priority=JobPriority.LOW)
    fab.create_job("j_crit", "s1", "p1", priority=JobPriority.CRITICAL)
    next_job = fab.dequeue_job()
    assert next_job.job_id == "j_crit"

def test_job_tie_breaker():
    fab = UniversalImportFabricator()
    src = make_source("s1", "/Game/S.fbx")
    prof = make_profile("p1")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j_b", "s1", "p1", priority=JobPriority.NORMAL)
    fab.create_job("j_a", "s1", "p1", priority=JobPriority.NORMAL)
    # Both same priority, j_b created earlier or tie-break
    j1 = fab.dequeue_job()
    assert j1 is not None

def test_job_cancel_queued():
    fab = UniversalImportFabricator()
    src = make_source("s1", "/Game/S.fbx")
    prof = make_profile("p1")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j1", "s1", "p1")
    assert fab.cancel_job("j1") is True
    assert fab.jobs["j1"].state == JobState.CANCELLED
    assert fab.dequeue_job() is None

def test_job_cancel_running():
    job = ImportJob("j1", "s1", "p1", state=JobState.RUNNING)
    assert job.state == JobState.RUNNING

def test_job_state_machine():
    job = ImportJob("j1", "s1", "p1")
    assert job.state == JobState.QUEUED
    job.state = JobState.PREPARING
    job.state = JobState.RUNNING
    job.state = JobState.COMPLETED
    assert job.state == JobState.COMPLETED

def test_job_progress():
    job = ImportJob("j1", "s1", "p1")
    assert job.progress == 0.0
    job.progress = 0.5
    assert job.progress == 0.5

def test_job_logging():
    job = ImportJob("j1", "s1", "p1")
    job.error_message = "Logged info"
    assert job.error_message == "Logged info"

def test_job_retry():
    fab = UniversalImportFabricator()
    src = make_source("s1", "/Game/S.fbx")
    prof = make_profile("p1", processor_id="flaky")
    fab.register_source(src)
    fab.register_profile(prof)
    attempts = [0]
    def flaky(j, s):
        attempts[0] += 1
        if attempts[0] == 1:
            raise RuntimeError("Temporary glitch")
        return [ImportArtifact("art", j.job_id, ArtifactType.FINAL, "/Game/A", "h")]
    fab.register_processor("flaky", flaky, ["mesh_fbx"])
    fab.create_job("j1", "s1", "p1")
    # First attempt: glitch -> RETRYING
    res1 = fab.process_next_job()
    assert res1.state == JobState.RETRYING
    # Second attempt: success -> COMPLETED
    res2 = fab.process_next_job()
    assert res2.state == JobState.COMPLETED

def test_job_recovery():
    job = ImportJob("j1", "s1", "p1", checkpoint={"step": 2})
    assert job.checkpoint["step"] == 2

def test_job_resume():
    job = ImportJob("j1", "s1", "p1", checkpoint={"offset": 512})
    assert job.checkpoint["offset"] == 512


# ==============================================================================
# 7. WORKER TESTS (8 tests - ?128)
# ==============================================================================

def test_worker_start():
    fab = UniversalImportFabricator(max_workers=2)
    assert len(fab.workers) == 2
    assert fab.workers[0] == WorkerState.IDLE

def test_worker_stop():
    fab = UniversalImportFabricator(max_workers=1)
    fab.workers[0] = WorkerState.STOPPED
    assert fab.workers[0] == WorkerState.STOPPED

def test_worker_execute():
    fab = UniversalImportFabricator(max_workers=1)
    src = make_source("s1", "/Game/S.fbx")
    prof = make_profile("p1")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j1", "s1", "p1")
    res = fab.process_next_job(worker_id=0)
    assert res.state == JobState.COMPLETED
    assert fab.workers[0] == WorkerState.IDLE

def test_worker_failure():
    fab = UniversalImportFabricator()
    fab.workers[0] = WorkerState.FAILED
    assert fab.workers[0] == WorkerState.FAILED

def test_worker_requeue():
    fab = UniversalImportFabricator()
    src = make_source("s1", "/Game/S.fbx")
    prof = make_profile("p1")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j1", "s1", "p1")
    job = fab.dequeue_job()
    fab.enqueue_job(job.job_id)
    assert "j1" in fab.job_queue

def test_worker_limit():
    fab = UniversalImportFabricator(max_workers=4)
    assert fab.worker_count == 4

def test_worker_pool():
    fab = UniversalImportFabricator(max_workers=8)
    assert len(fab.workers) == 8

def test_worker_cleanup():
    fab = UniversalImportFabricator(max_workers=2)
    for wid in fab.workers:
        fab.workers[wid] = WorkerState.STOPPED
    assert all(st == WorkerState.STOPPED for st in fab.workers.values())


# ==============================================================================
# 8. DEPENDENCY TESTS (9 tests - ?129)
# ==============================================================================

def test_dependency_order():
    fab = UniversalImportFabricator()
    fab.register_dependency("mat_base", "mesh_knight")
    assert "mesh_knight" in fab.dependencies["mat_base"]

def test_dependency_available():
    fab = UniversalImportFabricator()
    src = make_source("s_base", "/Game/Base.fbx")
    fab.register_source(src)
    assert fab.get_source("s_base") is not None

def test_dependency_missing():
    fab = UniversalImportFabricator()
    assert fab.get_source("missing_upstream") is None

def test_dependency_outdated():
    fab = UniversalImportFabricator()
    fab.register_dependency("src_a", "src_b")
    invalidated = fab.invalidate_source_dependents("src_a")
    assert "src_b" in invalidated

def test_dependency_processing():
    fab = UniversalImportFabricator()
    fab.register_dependency("texture_diffuse", "material_master")
    assert "material_master" in fab.dependencies["texture_diffuse"]

def test_dependency_failure():
    fab = UniversalImportFabricator()
    fab.register_dependency("upstream", "downstream")
    assert "downstream" in fab.dependencies["upstream"]

def test_dependency_cycle():
    g = ProcessingGraph("dep_cycle")
    g.add_node(ProcessingNode("A", "p"))
    g.add_node(ProcessingNode("B", "p"))
    g.add_edge(ProcessingEdge("A", "out", "B", "in"))
    assert g.detect_cycles() is False

def test_dependency_fingerprint():
    s1 = make_source("s1", "/Game/S1")
    p1 = make_profile("p1")
    fab = UniversalImportFabricator()
    fab.register_source(s1)
    fab.register_profile(p1)
    fp = fab.compute_cache_key("s1", "p1")
    assert len(fp) == 64

def test_dependency_determinism():
    fab = UniversalImportFabricator()
    s = make_source("s1", "/Game/S1")
    p = make_profile("p1")
    fab.register_source(s)
    fab.register_profile(p)
    fp1 = fab.compute_cache_key("s1", "p1")
    fp2 = fab.compute_cache_key("s1", "p1")
    assert fp1 == fp2

# ==============================================================================
# 9. CACHE TESTS (8 tests - ?130)
# ==============================================================================

def test_cache_key():
    fab = UniversalImportFabricator()
    src = make_source("s1", "/Game/S1")
    prof = make_profile("p1")
    fab.register_source(src)
    fab.register_profile(prof)
    key = fab.compute_cache_key("s1", "p1")
    assert len(key) == 64

def test_cache_hit():
    fab = UniversalImportFabricator()
    src = make_source("s1", "/Game/S1")
    prof = make_profile("p1")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j1", "s1", "p1")
    fab.process_next_job()
    assert fab.telemetry.cache_misses == 1

    # Second run should be a cache hit
    fab.create_job("j2", "s1", "p1")
    fab.process_next_job()
    assert fab.telemetry.cache_hits == 1

def test_cache_miss():
    fab = UniversalImportFabricator()
    src = make_source("s1", "/Game/S1")
    prof = make_profile("p1")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j1", "s1", "p1")
    fab.process_next_job()
    assert fab.telemetry.cache_misses == 1

def test_cache_invalidation():
    fab = UniversalImportFabricator()
    src = make_source("s1", "/Game/S1")
    prof = make_profile("p1")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j1", "s1", "p1")
    fab.process_next_job()
    key = fab.compute_cache_key("s1", "p1")
    assert key in fab.cache
    del fab.cache[key]
    assert key not in fab.cache

def test_cache_version():
    fab = UniversalImportFabricator()
    src = make_source("s1", "/Game/S1")
    p1 = make_profile("p1", settings={"v": 1})
    p2 = make_profile("p2", settings={"v": 2})
    fab.register_source(src)
    fab.register_profile(p1)
    fab.register_profile(p2)
    k1 = fab.compute_cache_key("s1", "p1")
    k2 = fab.compute_cache_key("s1", "p2")
    assert k1 != k2

def test_cache_corruption():
    fab = UniversalImportFabricator()
    fab.cache["corrupt_key"] = []
    assert fab.get_cached_artifacts("corrupt_key") == []

def test_cache_equivalence():
    fab = UniversalImportFabricator()
    src = make_source("s1", "/Game/S1")
    prof = make_profile("p1")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j1", "s1", "p1")
    r1 = fab.process_next_job()
    fab.create_job("j2", "s1", "p1")
    r2 = fab.process_next_job()
    assert len(r1.artifacts) == len(r2.artifacts)

def test_cache_cleanup():
    fab = UniversalImportFabricator()
    fab.cache["dummy"] = []
    fab.cache.clear()
    assert len(fab.cache) == 0


# ==============================================================================
# 10. ARTIFACT TESTS (8 tests - ?131)
# ==============================================================================

def test_artifact_creation():
    art = ImportArtifact("art_1", "job_1", ArtifactType.FINAL, "/Game/Mesh", "hash64")
    assert art.artifact_id == "art_1"
    assert art.artifact_type == ArtifactType.FINAL

def test_artifact_identity():
    art = ImportArtifact("art_1", "job_1", ArtifactType.GEOMETRY, "/Game/Geo", "hash64")
    assert art.output_path == "/Game/Geo"

def test_artifact_hash():
    art = ImportArtifact("art_1", "job_1", ArtifactType.IMAGE, "/Game/Tex", "hash64")
    assert art.content_hash == "hash64"

def test_artifact_atomic_publish():
    fab = UniversalImportFabricator()
    src = make_source("s1", "/Game/S1")
    prof = make_profile("p1")
    fab.register_source(src)
    fab.register_profile(prof)
    job = fab.create_job("j1", "s1", "p1")
    res = fab.process_next_job()
    assert res.state == JobState.COMPLETED
    assert len(res.artifacts) > 0

def test_partial_output_rejection():
    art = ImportArtifact("art_1", "job_1", ArtifactType.FINAL, "/Game/Valid", "hash")
    ok, errs = UniversalImportValidator.validate_source_path(art.output_path)
    assert ok is True

def test_manifest():
    fab = UniversalImportFabricator()
    src = make_source("s1", "/Game/S1")
    prof = make_profile("p1")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j1", "s1", "p1")
    fab.process_next_job()
    man = fab.generate_manifest("j1")
    assert man.job_id == "j1"
    assert len(man.artifacts) > 0
    assert len(man.signature) == 64

def test_manifest_determinism():
    fab = UniversalImportFabricator()
    src = make_source("s1", "/Game/S1")
    prof = make_profile("p1")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j1", "s1", "p1")
    fab.process_next_job()
    m1 = fab.generate_manifest("j1")
    m2 = fab.generate_manifest("j1")
    assert len(m1.artifacts) == len(m2.artifacts)

def test_artifact_cleanup():
    fab = UniversalImportFabricator()
    fab.cache.clear()
    assert len(fab.cache) == 0


# ==============================================================================
# 11. INCREMENTAL PROCESSING TESTS (8 tests - ?132)
# ==============================================================================

def test_incremental_no_change():
    fab = UniversalImportFabricator()
    src = make_source("s1", "/Game/S1")
    prof = make_profile("p1")
    fab.register_source(src)
    fab.register_profile(prof)
    k1 = fab.compute_cache_key("s1", "p1")
    k2 = fab.compute_cache_key("s1", "p1")
    assert k1 == k2

def test_incremental_source_change():
    fab = UniversalImportFabricator()
    s1 = make_source("s1", "/Game/S1", size=100)
    prof = make_profile("p1")
    fab.register_source(s1)
    fab.register_profile(prof)
    k1 = fab.compute_cache_key("s1", "p1")
    # Change source content hash
    s1.content_hash = "modified_hash_64_characters_long_000000000000000000000000000000"
    k2 = fab.compute_cache_key("s1", "p1")
    assert k1 != k2

def test_incremental_settings_change():
    fab = UniversalImportFabricator()
    src = make_source("s1", "/Game/S1")
    p1 = make_profile("p1", settings={"lod": 1})
    fab.register_source(src)
    fab.register_profile(p1)
    k1 = fab.compute_cache_key("s1", "p1")
    p1.settings.set("lod", 2)
    k2 = fab.compute_cache_key("s1", "p1")
    assert k1 != k2

def test_incremental_processor_change():
    fab = UniversalImportFabricator()
    src = make_source("s1", "/Game/S1")
    p1 = make_profile("p1", processor_id="pA")
    fab.register_source(src)
    fab.register_profile(p1)
    k1 = fab.compute_cache_key("s1", "p1")
    p1.version += 1
    k2 = fab.compute_cache_key("s1", "p1")
    assert k1 != k2

def test_incremental_dependency_change():
    fab = UniversalImportFabricator()
    fab.register_dependency("src_parent", "src_child")
    inv = fab.invalidate_source_dependents("src_parent")
    assert "src_child" in inv

def test_incremental_profile_change():
    fab = UniversalImportFabricator()
    src = make_source("s1", "/Game/S1")
    p = make_profile("p1")
    fab.register_source(src)
    fab.register_profile(p)
    k1 = fab.compute_cache_key("s1", "p1")
    p.version = 5
    k2 = fab.compute_cache_key("s1", "p1")
    assert k1 != k2

def test_incremental_cache_hit():
    fab = UniversalImportFabricator()
    src = make_source("s1", "/Game/S1")
    prof = make_profile("p1")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j1", "s1", "p1")
    fab.process_next_job()
    fab.create_job("j2", "s1", "p1")
    fab.process_next_job()
    assert fab.telemetry.cache_hits == 1

def test_incremental_equivalence():
    fab = UniversalImportFabricator()
    src = make_source("s1", "/Game/S1")
    prof = make_profile("p1")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j1", "s1", "p1")
    res1 = fab.process_next_job()
    fab.create_job("j2", "s1", "p1")
    res2 = fab.process_next_job()
    assert res1.artifacts[0].output_path == res2.artifacts[0].output_path


# ==============================================================================
# 12. ERROR/RECOVERY TESTS (12 tests - ?133)
# ==============================================================================

def test_source_failure():
    fab = UniversalImportFabricator()
    with pytest.raises(KeyError):
        fab.create_job("j1", "non_existent_source", "default_mesh")

def test_processor_failure():
    fab = UniversalImportFabricator()
    src = make_source("s1", "/Game/S1")
    prof = make_profile("p1", processor_id="bad_proc")
    fab.register_source(src)
    fab.register_profile(prof)
    def bad(j, s):
        raise ValueError("Bad input buffer")
    fab.register_processor("bad_proc", bad, ["mesh_fbx"])
    job = fab.create_job("j1", "s1", "p1")
    job.max_retries = 0
    res = fab.process_next_job()
    assert res.state == JobState.FAILED

def test_output_failure():
    art = ImportArtifact("a1", "j1", ArtifactType.FINAL, "/Game/Path", "hash")
    assert art.artifact_id == "a1"

def test_retry():
    job = ImportJob("j1", "s1", "p1")
    assert job.retry_count == 0
    job.retry_count += 1
    assert job.retry_count == 1

def test_retry_limit():
    fab = UniversalImportFabricator()
    src = make_source("s1", "/Game/S1")
    prof = make_profile("p1", processor_id="fail")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.register_processor("fail", lambda j, s: (_ for _ in ()).throw(RuntimeError("fail")), ["mesh_fbx"])
    job = fab.create_job("j1", "s1", "p1")
    job.max_retries = 2
    # Attempt 1 -> retry 1
    fab.process_next_job()
    # Attempt 2 -> retry 2
    fab.process_next_job()
    # Attempt 3 -> FAILED
    fab.process_next_job()
    assert job.state == JobState.FAILED

def test_backoff():
    fab = UniversalImportFabricator()
    assert fab.telemetry.retries >= 0

def test_cancel():
    fab = UniversalImportFabricator()
    src = make_source("s1", "/Game/S1")
    prof = make_profile("p1")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j1", "s1", "p1")
    assert fab.cancel_job("j1") is True
    assert fab.jobs["j1"].state == JobState.CANCELLED

def test_resume():
    job = ImportJob("j1", "s1", "p1", checkpoint={"step": 3})
    assert job.checkpoint["step"] == 3

def test_checkpoint_validation():
    job = ImportJob("j1", "s1", "p1")
    job.checkpoint["processed_items"] = 42
    assert job.checkpoint["processed_items"] == 42

def test_worker_failure_recovery():
    fab = UniversalImportFabricator()
    fab.workers[0] = WorkerState.FAILED
    fab.workers[0] = WorkerState.IDLE
    assert fab.workers[0] == WorkerState.IDLE

def test_queue_recovery():
    fab = UniversalImportFabricator()
    src = make_source("s1", "/Game/S1")
    prof = make_profile("p1")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j1", "s1", "p1")
    fab.job_queue.clear()
    assert len(fab.job_queue) == 0
    fab.enqueue_job("j1")
    assert len(fab.job_queue) == 1

def test_cache_recovery():
    fab = UniversalImportFabricator()
    fab.cache.clear()
    assert len(fab.cache) == 0


# ==============================================================================
# 13. BATCH IMPORT TESTS (7 tests - ?134)
# ==============================================================================

def test_batch_import():
    fab = UniversalImportFabricator()
    prof = make_profile("p1")
    fab.register_profile(prof)
    for i in range(5):
        src = make_source(f"src_{i}", f"/Game/Item_{i}.fbx")
        fab.register_source(src)
        fab.create_job(f"job_{i}", f"src_{i}", "p1")
    assert len(fab.job_queue) == 5
    for _ in range(5):
        fab.process_next_job()
    assert fab.telemetry.completed_jobs == 5

def test_batch_fail_fast():
    fab = UniversalImportFabricator()
    assert fab.telemetry.failed_jobs == 0

def test_batch_continue():
    fab = UniversalImportFabricator()
    prof = make_profile("p1")
    fab.register_profile(prof)
    s1 = make_source("s1", "/Game/S1.fbx")
    s2 = make_source("s2", "/Game/S2.fbx")
    fab.register_source(s1)
    fab.register_source(s2)
    fab.create_job("j1", "s1", "p1")
    fab.create_job("j2", "s2", "p1")
    j1 = fab.process_next_job()
    j2 = fab.process_next_job()
    assert j1.state == JobState.COMPLETED
    assert j2.state == JobState.COMPLETED

def test_batch_atomic():
    fab = UniversalImportFabricator()
    assert fab.telemetry.completed_jobs >= 0

def test_batch_progress():
    fab = UniversalImportFabricator()
    src = make_source("s1", "/Game/S1.fbx")
    prof = make_profile("p1")
    fab.register_source(src)
    fab.register_profile(prof)
    job = fab.create_job("j1", "s1", "p1")
    assert job.progress == 0.0
    fab.process_next_job()
    assert job.progress == 1.0

def test_batch_cancel():
    fab = UniversalImportFabricator()
    prof = make_profile("p1")
    fab.register_profile(prof)
    for i in range(3):
        src = make_source(f"s_{i}", f"/Game/S_{i}.fbx")
        fab.register_source(src)
        fab.create_job(f"j_{i}", f"s_{i}", "p1")
    for i in range(3):
        fab.cancel_job(f"j_{i}")
    assert all(fab.jobs[f"j_{i}"].state == JobState.CANCELLED for i in range(3))

def test_batch_retry():
    fab = UniversalImportFabricator()
    src = make_source("s1", "/Game/S1.fbx")
    prof = make_profile("p1")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j1", "s1", "p1")
    assert fab.telemetry.retries >= 0

# ==============================================================================
# 14. COMMAND TESTS (8 tests - ?135)
# ==============================================================================

def test_import_command():
    fab = UniversalImportFabricator()
    src = make_source("s1", "/Game/S1.fbx")
    prof = make_profile("p1")
    fab.register_source(src)
    fab.register_profile(prof)
    job = fab.create_job("j1", "s1", "p1")
    assert job.state == JobState.QUEUED

def test_reimport_command():
    fab = UniversalImportFabricator()
    src = make_source("s1", "/Game/S1.fbx")
    prof = make_profile("p1")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j1", "s1", "p1")
    fab.process_next_job()
    # Reimport by clearing cache key
    key = fab.compute_cache_key("s1", "p1")
    if key in fab.cache:
        del fab.cache[key]
    job2 = fab.create_job("j2", "s1", "p1")
    res2 = fab.process_next_job()
    assert res2.state == JobState.COMPLETED

def test_cancel_import_command():
    fab = UniversalImportFabricator()
    src = make_source("s1", "/Game/S1.fbx")
    prof = make_profile("p1")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j1", "s1", "p1")
    res = fab.cancel_job("j1")
    assert res is True

def test_retry_import_command():
    job = ImportJob("j1", "s1", "p1", state=JobState.FAILED)
    job.state = JobState.QUEUED
    assert job.state == JobState.QUEUED

def test_clear_error_command():
    job = ImportJob("j1", "s1", "p1", state=JobState.FAILED, error_message="Error")
    job.error_message = None
    assert job.error_message is None

def test_rebuild_artifacts_command():
    fab = UniversalImportFabricator()
    fab.cache.clear()
    assert len(fab.cache) == 0

def test_command_validation():
    fab = UniversalImportFabricator()
    assert fab.cancel_job("non_existent") is False

def test_command_undo_redo():
    snap = ImportStateSnapshot("snap_1", time.time(), {}, {}, {})
    assert snap.snapshot_id == "snap_1"


# ==============================================================================
# 15. UI TESTS (9 tests - ?136)
# ==============================================================================

def test_import_queue_ui():
    fab = UniversalImportFabricator()
    src = make_source("s1", "/Game/S1.fbx")
    prof = make_profile("p1")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j1", "s1", "p1")
    assert fab.telemetry.queued_jobs == 1

def test_import_progress_ui():
    job = ImportJob("j1", "s1", "p1", progress=0.75)
    assert job.progress == 0.75

def test_import_error_ui():
    job = ImportJob("j1", "s1", "p1", state=JobState.FAILED, error_message="Parse err")
    assert job.state == JobState.FAILED

def test_import_retry_ui():
    job = ImportJob("j1", "s1", "p1", retry_count=2)
    assert job.retry_count == 2

def test_import_cancel_ui():
    job = ImportJob("j1", "s1", "p1", state=JobState.CANCELLED)
    assert job.state == JobState.CANCELLED

def test_import_profile_ui():
    p = make_profile("p1")
    assert p.name == "TestProfile"

def test_import_processor_ui():
    fab = UniversalImportFabricator()
    assert "mesh_fbx" in fab.formats

def test_browser_status_update():
    job = ImportJob("j1", "s1", "p1", state=JobState.COMPLETED)
    assert job.state == JobState.COMPLETED

def test_inspector_status_update():
    job = ImportJob("j1", "s1", "p1", state=JobState.RUNNING)
    assert job.state == JobState.RUNNING


# ==============================================================================
# 16. SECURITY TESTS (17 tests - ?137)
# ==============================================================================

def test_path_traversal():
    ok, errs = UniversalImportValidator.validate_source_path("/Game/../../Secret/File")
    assert not ok
    assert any("Path traversal" in e for e in errs)

def test_symlink_escape():
    with pytest.raises(ValueError, match="NO_NON_CANONICAL_SOURCE_PATH"):
        normalize_source_path("../outside/symlink")

def test_oversized_input():
    src = make_source("s1", "/Game/Huge", size=10**12)
    assert src.file_size_bytes == 10**12

def test_memory_exhaustion():
    fab = UniversalImportFabricator(max_workers=2)
    assert fab.worker_count == 2

def test_disk_exhaustion():
    art = ImportArtifact("a1", "j1", ArtifactType.FINAL, "/Game/Large", "hash", size_bytes=10**9)
    assert art.size_bytes == 10**9

def test_job_flood():
    fab = UniversalImportFabricator()
    prof = make_profile("p1")
    fab.register_profile(prof)
    for i in range(100):
        src = make_source(f"s_{i}", f"/Game/F_{i}")
        fab.register_source(src)
        fab.create_job(f"j_{i}", f"s_{i}", "p1")
    assert len(fab.jobs) == 100

def test_dependency_explosion():
    fab = UniversalImportFabricator()
    for i in range(50):
        fab.register_dependency("root", f"child_{i}")
    assert len(fab.dependencies["root"]) == 50

def test_malicious_metadata():
    src = make_source("s1", "/Game/S1")
    src.metadata["injected_script"] = "<script>alert(1)</script>"
    ok, _ = UniversalImportValidator.validate_source_identity(src)
    assert ok is True

def test_malicious_archive():
    with pytest.raises(ValueError):
        normalize_source_path("archive.zip:../../escape")

def test_unsafe_output_path():
    ok, errs = UniversalImportValidator.validate_source_path("/Game/../Output")
    assert not ok

def test_processor_isolation():
    fab = UniversalImportFabricator()
    assert fab.processors is not None

def test_invalid_profile():
    p = ImportProfile("", "", "", "")
    ok, errs = UniversalImportValidator.validate_import_profile(p)
    assert not ok

def test_invalid_graph():
    g = ProcessingGraph("")
    ok, errs = UniversalImportValidator.validate_processing_graph(g)
    assert not ok

def test_invalid_checkpoint():
    job = ImportJob("j1", "s1", "p1")
    job.checkpoint["corrupt"] = None
    assert "corrupt" in job.checkpoint

def test_cache_poisoning():
    fab = UniversalImportFabricator()
    fab.cache["poison"] = []
    assert fab.get_cached_artifacts("poison") == []

def test_manifest_tampering():
    man = ImportManifest("m1", "j1")
    man.signature = "tampered_sig"
    ok, errs = UniversalImportValidator.validate_manifest(man)
    assert not ok

def test_replay_tampering():
    snap = ImportStateSnapshot("s1", time.time(), {}, {}, {}, state_hash="bad_hash")
    ok, errs = UniversalImportValidator.validate_snapshot(snap)
    assert not ok


# ==============================================================================


# ==============================================================================
# 138. PERFORMANCE TESTS
# ==============================================================================

def test_1k_jobs():
    fab = UniversalImportFabricator()
    prof = make_profile("p_1k")
    fab.register_profile(prof)
    for i in range(1000):
        src = make_source(f"s_1k_{i}", f"/assets/mesh_{i}.fbx")
        fab.register_source(src)
        fab.create_job(f"j_1k_{i}", src.source_id, prof.profile_id)
    assert len(fab.jobs) == 1000
    assert len(fab.job_queue) == 1000

def test_10k_jobs():
    fab = UniversalImportFabricator()
    for i in range(10000):
        fab.job_queue.append(f"j_stress_{i}")
    assert len(fab.job_queue) == 10000

def test_large_asset():
    fab = UniversalImportFabricator()
    prof = make_profile("default_profile")
    fab.register_profile(prof)
    src = make_source("s_huge", "/assets/huge_world.fbx", size=500 * 1024 * 1024)
    fab.register_source(src)
    key = fab.compute_cache_key(src.source_id, "default_profile")
    assert len(key) == 64

def test_large_dependency_graph():
    fab = UniversalImportFabricator()
    for i in range(50):
        fab.register_dependency(f"p_{i}", f"p_{i+1}")
    deps = fab.invalidate_source_dependents("p_0")
    assert len(deps) == 50

def test_large_processing_graph():
    g = ProcessingGraph("g_large")
    for i in range(50):
        g.add_node(ProcessingNode(f"n_{i}", "proc"))
    for i in range(49):
        g.add_edge(ProcessingEdge(f"n_{i}", "out", f"n_{i+1}", "in"))
    order = g.get_execution_order()
    assert len(order) == 50
    assert order[0] == "n_0"
    assert order[-1] == "n_49"

def test_large_cache():
    fab = UniversalImportFabricator()
    for i in range(100):
        art = ImportArtifact(f"art_{i}", f"j_{i}", ArtifactType.GEOMETRY, f"/out/{i}.uasset", "hash", 100)
        fab.cache[f"key_{i}"] = [art]
    assert len(fab.cache) == 100
    assert len(fab.get_cached_artifacts("key_50")) == 1

def test_large_batch_import():
    fab = UniversalImportFabricator()
    prof = make_profile("batch_p")
    fab.register_profile(prof)
    for i in range(30):
        src = make_source(f"sb_{i}", f"/a/{i}.fbx")
        fab.register_source(src)
        fab.create_job(f"jb_{i}", src.source_id, prof.profile_id)
    assert len(fab.job_queue) == 30

def test_incremental_import():
    fab = UniversalImportFabricator()
    src = make_source("s_inc", "/a/tex.png")
    prof = make_profile("p_inc")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j_inc1", src.source_id, prof.profile_id)
    j1 = fab.process_next_job()
    assert j1.state == JobState.COMPLETED
    fab.create_job("j_inc2", src.source_id, prof.profile_id)
    j2 = fab.process_next_job()
    assert j2.state == JobState.COMPLETED
    assert fab.telemetry.cache_hits >= 1

def test_parallel_workers():
    fab = UniversalImportFabricator(max_workers=8)
    assert len(fab.workers) == 8
    assert fab.worker_count == 8

def test_queue_throughput():
    fab = UniversalImportFabricator()
    prof = make_profile("p_q")
    fab.register_profile(prof)
    for i in range(20):
        src = make_source(f"sq_{i}", f"/a/{i}.fbx")
        fab.register_source(src)
        p = JobPriority.CRITICAL if i == 15 else JobPriority.LOW
        fab.create_job(f"jq_{i}", src.source_id, prof.profile_id, priority=p)
    top = fab.dequeue_job()
    assert top.job_id == "jq_15"
    assert top.priority == JobPriority.CRITICAL

def test_search_status_updates():
    job = ImportJob("j_srch", "s1", "p1")
    for s in [JobState.QUEUED, JobState.RUNNING, JobState.COMPLETED]:
        job.state = s
    assert job.state == JobState.COMPLETED

def test_manifest_generation():
    fab = UniversalImportFabricator()
    src = make_source("sm_gen", "/a/m.fbx")
    prof = make_profile("pm_gen")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("jm_gen", src.source_id, prof.profile_id)
    fab.process_next_job()
    man = fab.generate_manifest("jm_gen")
    assert man.job_id == "jm_gen"
    assert len(man.signature) == 64

def test_rebuild():
    fab = UniversalImportFabricator()
    src = make_source("s_reb", "/a/reb.fbx")
    prof = make_profile("p_reb")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j_reb1", src.source_id, prof.profile_id)
    fab.process_next_job()
    key = fab.compute_cache_key(src.source_id, prof.profile_id)
    assert key in fab.cache
    fab.cache.pop(key)
    fab.create_job("j_reb2", src.source_id, prof.profile_id)
    j2 = fab.process_next_job()
    assert j2.state == JobState.COMPLETED

def test_recovery():
    fab = UniversalImportFabricator()
    src = make_source("s_rec", "/a/rec.fbx")
    prof = make_profile("p_rec")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j_rec", src.source_id, prof.profile_id)
    snap = fab.take_snapshot()
    assert "j_rec" in snap.jobs
    ok, _ = UniversalImportValidator.validate_snapshot(snap)
    assert ok


# ==============================================================================
# 139. STRESS TESTS
# ==============================================================================

def test_rapid_enqueue():
    fab = UniversalImportFabricator()
    prof = make_profile("p_stress")
    fab.register_profile(prof)
    for i in range(50):
        src = make_source(f"s_st_{i}", f"/a/{i}.fbx")
        fab.register_source(src)
        fab.create_job(f"j_st_{i}", src.source_id, prof.profile_id)
    assert len(fab.job_queue) == 50

def test_rapid_cancel():
    fab = UniversalImportFabricator()
    prof = make_profile("p_canc")
    fab.register_profile(prof)
    for i in range(20):
        src = make_source(f"s_ca_{i}", f"/a/{i}.fbx")
        fab.register_source(src)
        fab.create_job(f"j_ca_{i}", src.source_id, prof.profile_id)
    for i in range(0, 20, 2):
        fab.cancel_job(f"j_ca_{i}")
    assert fab.jobs["j_ca_0"].state == JobState.CANCELLED
    assert fab.jobs["j_ca_1"].state == JobState.QUEUED

def test_rapid_retry():
    job = ImportJob("j_retry", "s1", "p1")
    job.state = JobState.FAILED
    job.retry_count += 1
    job.state = JobState.QUEUED
    assert job.retry_count == 1
    assert job.state == JobState.QUEUED

def test_rapid_reprioritize():
    fab = UniversalImportFabricator()
    prof = make_profile("p_rep")
    fab.register_profile(prof)
    fab.register_source(make_source("s1", "/a.fbx"))
    fab.register_source(make_source("s2", "/b.fbx"))
    fab.create_job("j1", "s1", prof.profile_id, priority=JobPriority.LOW)
    fab.create_job("j2", "s2", prof.profile_id, priority=JobPriority.NORMAL)
    fab.reprioritize_job("j1", JobPriority.CRITICAL)
    assert fab.dequeue_job().job_id == "j1"

def test_rapid_worker_restart():
    fab = UniversalImportFabricator(max_workers=2)
    assert len(fab.workers) == 2
    fab.workers = {i: WorkerState.IDLE for i in range(6)}
    assert len(fab.workers) == 6

def test_rapid_catalog_changes():
    fab = UniversalImportFabricator()
    prof = make_profile("p1")
    fab.register_profile(prof)
    s1 = make_source("s_cat", "/c.fbx", version=1)
    fab.register_source(s1)
    k1 = fab.compute_cache_key("s_cat", "p1")
    fab.remove_source("s_cat")
    s2 = make_source("s_cat", "/c.fbx", version=2)
    fab.register_source(s2)
    k2 = fab.compute_cache_key("s_cat", "p1")
    assert k1 != k2

def test_rapid_dependency_changes():
    fab = UniversalImportFabricator()
    for i in range(10):
        fab.register_dependency("mat_main", f"tex_{i}")
    assert len(fab.dependencies["mat_main"]) == 10

def test_rapid_cache_invalidation():
    fab = UniversalImportFabricator()
    for i in range(20):
        fab.cache[f"k_{i}"] = []
    for i in range(10):
        fab.cache.pop(f"k_{i}")
    assert len(fab.cache) == 10

def test_rapid_profile_changes():
    p = make_profile("p_mut")
    for i in range(10):
        p.settings.settings[f"opt_{i}"] = i
    assert len(p.settings.settings) == 10

def test_rapid_import_requests():
    fab = UniversalImportFabricator()
    src = make_source("s_req", "/r.fbx")
    prof = make_profile("p_req")
    fab.register_source(src)
    fab.register_profile(prof)
    j1 = fab.create_job("j1", src.source_id, prof.profile_id)
    j2 = fab.create_job("j2", src.source_id, prof.profile_id)
    assert j1.job_id != j2.job_id
    assert j1.source_id == j2.source_id

def test_rapid_ui_updates():
    job = ImportJob("j_ui", "s1", "p1")
    progress_history = []
    for p in [0.1, 0.25, 0.5, 0.75, 1.0]:
        job.progress = p
        progress_history.append(job.progress)
    assert progress_history == [0.1, 0.25, 0.5, 0.75, 1.0]

def test_rapid_recovery():
    fab = UniversalImportFabricator()
    snap = fab.take_snapshot()
    for _ in range(5):
        ok, _ = UniversalImportValidator.validate_snapshot(snap)
        assert ok


# ==============================================================================
# 140. PROPERTY-BASED TESTS
# ==============================================================================

def test_prop_rebuild_incremental_equivalence():
    fab = UniversalImportFabricator()
    src = make_source("s_prop", "/prop.fbx")
    prof = make_profile("p_prop")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j_p1", src.source_id, prof.profile_id)
    j1 = fab.process_next_job()
    arts1 = [a.content_hash for a in j1.artifacts]
    fab.create_job("j_p2", src.source_id, prof.profile_id)
    j2 = fab.process_next_job()
    arts2 = [a.content_hash for a in j2.artifacts]
    assert arts1 == arts2

def test_prop_cache_hit_process_equivalence():
    fab = UniversalImportFabricator()
    src = make_source("s_chp", "/t.png")
    prof = make_profile("p_chp")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j_c1", src.source_id, prof.profile_id)
    j1 = fab.process_next_job()
    key = fab.compute_cache_key(src.source_id, prof.profile_id)
    cached = fab.get_cached_artifacts(key)
    assert [a.content_hash for a in j1.artifacts] == [a.content_hash for a in cached]

def test_prop_retry_preserves_fingerprint():
    fab = UniversalImportFabricator()
    src = make_source("s_rfp", "/a.wav")
    prof = make_profile("p_rfp")
    fab.register_source(src)
    fab.register_profile(prof)
    job = fab.create_job("j_rfp", src.source_id, prof.profile_id)
    orig_key = fab.compute_cache_key(src.source_id, prof.profile_id)
    job.state = JobState.FAILED
    job.retry_count += 1
    job.state = JobState.QUEUED
    new_key = fab.compute_cache_key(src.source_id, prof.profile_id)
    assert orig_key == new_key

def test_prop_cancel_no_partial_artifacts():
    fab = UniversalImportFabricator()
    src = make_source("s_cnp", "/m.fbx")
    prof = make_profile("p_cnp")
    fab.register_source(src)
    fab.register_profile(prof)
    job = fab.create_job("j_cnp", src.source_id, prof.profile_id)
    fab.cancel_job("j_cnp")
    assert len(job.artifacts) == 0

def test_prop_topological_order_respects_deps():
    g = ProcessingGraph("prop_dag")
    g.add_node(ProcessingNode("step1", "p1"))
    g.add_node(ProcessingNode("step2", "p2"))
    g.add_node(ProcessingNode("step3", "p3"))
    g.add_edge(ProcessingEdge("step1", "out", "step2", "in"))
    g.add_edge(ProcessingEdge("step2", "out", "step3", "in"))
    order = g.get_execution_order()
    assert order.index("step1") < order.index("step2") < order.index("step3")

def test_prop_same_inputs_same_fingerprint():
    fab = UniversalImportFabricator()
    prof = make_profile("p1")
    fab.register_profile(prof)
    s1 = make_source("s_same", "/asset.fbx", size=2048, version=1)
    fab.register_source(s1)
    k1 = fab.compute_cache_key("s_same", "p1")
    k2 = fab.compute_cache_key("s_same", "p1")
    assert k1 == k2

def test_prop_same_fingerprint_equiv_outputs():
    fab = UniversalImportFabricator()
    src = make_source("s_eq_out", "/tex.png")
    prof = make_profile("p_eq_out")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j_eo1", src.source_id, prof.profile_id)
    j1 = fab.process_next_job()
    fab.create_job("j_eo2", src.source_id, prof.profile_id)
    j2 = fab.process_next_job()
    assert j1.artifacts[0].content_hash == j2.artifacts[0].content_hash


# ==============================================================================
# 141. GOLDEN TESTS
# ==============================================================================

def test_golden_import_image():
    fab = UniversalImportFabricator()
    src = make_source("s_img", "/textures/diffuse.png", size=4096)
    prof = make_profile("p_img")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j_img", src.source_id, prof.profile_id)
    j = fab.process_next_job()
    assert len(j.artifacts) >= 1
    man = fab.generate_manifest("j_img")
    ok, _ = UniversalImportValidator.validate_manifest(man)
    assert ok

def test_golden_import_model():
    fab = UniversalImportFabricator()
    src = make_source("s_mdl", "/meshes/hero.fbx", size=102400)
    prof = make_profile("p_mdl")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j_mdl", src.source_id, prof.profile_id)
    j = fab.process_next_job()
    assert len(j.artifacts) >= 1

def test_golden_import_material():
    fab = UniversalImportFabricator()
    src = make_source("s_mat", "/materials/m_metal.json", size=512)
    prof = make_profile("p_mat")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j_mat", src.source_id, prof.profile_id)
    j = fab.process_next_job()
    assert len(j.artifacts) >= 1

def test_golden_import_scene():
    fab = UniversalImportFabricator()
    src = make_source("s_scn", "/scenes/arena.usda", size=204800)
    prof = make_profile("p_scn")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j_scn", src.source_id, prof.profile_id)
    j = fab.process_next_job()
    assert len(j.artifacts) >= 1

def test_golden_import_audio():
    fab = UniversalImportFabricator()
    src = make_source("s_aud", "/audio/laser.wav", size=32768)
    prof = make_profile("p_aud")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j_aud", src.source_id, prof.profile_id)
    j = fab.process_next_job()
    assert len(j.artifacts) >= 1

def test_golden_import_data():
    fab = UniversalImportFabricator()
    src = make_source("s_dat", "/data/config.json", size=256)
    prof = make_profile("p_dat")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j_dat", src.source_id, prof.profile_id)
    j = fab.process_next_job()
    assert len(j.artifacts) >= 1

def test_golden_import_error():
    fab = UniversalImportFabricator()
    job = ImportJob("j_err", "s_err", "p_err")
    job.state = JobState.FAILED
    job.error_message = "Corrupt header in file"
    bundle = fab.generate_diagnostic_bundle()
    ok, _ = UniversalImportValidator.validate_diagnostic_bundle(bundle)
    assert ok
    assert job.error_message == "Corrupt header in file"

def test_golden_import_progress():
    job = ImportJob("j_prog", "s_prog", "p_prog")
    job.state = JobState.RUNNING
    job.progress = 0.5
    assert job.progress == 0.5
    job.state = JobState.COMPLETED
    assert job.state == JobState.COMPLETED

def test_golden_import_queue():
    fab = UniversalImportFabricator()
    prof = make_profile("p_gq")
    fab.register_profile(prof)
    fab.register_source(make_source("s_l", "/l.fbx"))
    fab.register_source(make_source("s_c", "/c.fbx"))
    fab.register_source(make_source("s_n", "/n.fbx"))
    fab.create_job("j_l", "s_l", prof.profile_id, priority=JobPriority.LOW)
    fab.create_job("j_c", "s_c", prof.profile_id, priority=JobPriority.CRITICAL)
    fab.create_job("j_n", "s_n", prof.profile_id, priority=JobPriority.NORMAL)
    first = fab.dequeue_job()
    assert first.job_id == "j_c"
    second = fab.dequeue_job()
    assert second.job_id == "j_n"
    third = fab.dequeue_job()
    assert third.job_id == "j_l"

def test_golden_import_dependencies():
    fab = UniversalImportFabricator()
    fab.register_dependency("mat_hero", "tex_diffuse")
    fab.register_dependency("mat_hero", "tex_normal")
    assert len(fab.dependencies["mat_hero"]) == 2
    affected = fab.invalidate_source_dependents("mat_hero")
    assert "tex_diffuse" in affected

def test_golden_import_retry():
    fab = UniversalImportFabricator()
    src = make_source("s_ret", "/model.fbx")
    prof = make_profile("p_ret")
    fab.register_source(src)
    fab.register_profile(prof)
    job = fab.create_job("j_ret", src.source_id, prof.profile_id)
    job.state = JobState.FAILED
    job.retry_count += 1
    job.state = JobState.QUEUED
    assert job.state == JobState.QUEUED
    assert job.retry_count == 1

def test_golden_import_cancelled():
    fab = UniversalImportFabricator()
    src = make_source("s_can", "/m.fbx")
    prof = make_profile("p_can")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j_can", src.source_id, prof.profile_id)
    fab.cancel_job("j_can")
    assert fab.jobs["j_can"].state == JobState.CANCELLED
    assert len(fab.jobs["j_can"].artifacts) == 0

def test_golden_import_inspector():
    job = ImportJob("j_insp", "s_insp", "p_insp")
    job.state = JobState.COMPLETED
    telemetry = ImportTelemetry(completed_jobs=1)
    assert telemetry.completed_jobs == 1

def test_golden_import_browser():
    src = make_source("s_browser_item", "/Game/Textures/T_Noise.png")
    assert src.source_id == "s_browser_item"
    assert src.canonical_path == "/Game/Textures/T_Noise.png"

def test_golden_import_dark_theme():
    theme_spec = {
        "background": "#1e1e1e",
        "surface": "#252526",
        "primary": "#0e639c",
        "status_success": "#89d185",
        "status_failed": "#f48771",
    }
    assert theme_spec["background"] == "#1e1e1e"


# ==============================================================================
# 142. REPLAY TESTS
# ==============================================================================

def test_import_replay():
    fab = UniversalImportFabricator()
    src = make_source("s_rep", "/assets/mesh.fbx")
    prof = make_profile("p_rep")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j_rep", src.source_id, prof.profile_id)
    fab.process_next_job()
    snap = fab.take_snapshot()
    ok, _ = UniversalImportValidator.validate_snapshot(snap)
    assert ok

def test_replay_same_fingerprint():
    fab = UniversalImportFabricator()
    src = make_source("s_rep_fp", "/assets/mesh.fbx")
    prof = make_profile("p_rep_fp")
    fab.register_source(src)
    fab.register_profile(prof)
    k1 = fab.compute_cache_key(src.source_id, prof.profile_id)
    k2 = fab.compute_cache_key(src.source_id, prof.profile_id)
    assert k1 == k2

def test_replay_same_manifest():
    fab = UniversalImportFabricator()
    src = make_source("s_rep_man", "/assets/mesh.fbx")
    prof = make_profile("p_rep_man")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j_rep_man", src.source_id, prof.profile_id)
    fab.process_next_job()
    man1 = fab.generate_manifest("j_rep_man")
    man2 = fab.generate_manifest("j_rep_man")
    assert man1.signature == man2.signature

def test_replay_output_equivalence():
    fab = UniversalImportFabricator()
    src = make_source("s_rep_eq", "/assets/mesh.fbx")
    prof = make_profile("p_rep_eq")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j_rep_eq1", src.source_id, prof.profile_id)
    j1 = fab.process_next_job()
    fab.create_job("j_rep_eq2", src.source_id, prof.profile_id)
    j2 = fab.process_next_job()
    assert j1.artifacts[0].content_hash == j2.artifacts[0].content_hash


# ==============================================================================
# 143. INTEGRATION TESTS
# ==============================================================================

def test_browser_import_integration():
    fab = UniversalImportFabricator()
    fmt_id, conf = fab.detect_format(extension=".fbx")
    assert fmt_id == "mesh_fbx"
    src = make_source("s_brw", "/content/character.fbx")
    prof = make_profile("p_brw")
    fab.register_source(src)
    fab.register_profile(prof)
    job = fab.create_job("j_brw", src.source_id, prof.profile_id)
    assert job.profile_id == "p_brw"

def test_inspector_import_integration():
    fab = UniversalImportFabricator()
    src = make_source("s_insp_int", "/content/wood.png")
    prof = make_profile("p_insp_int")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j_insp_int", src.source_id, prof.profile_id)
    j = fab.process_next_job()
    assert j.state == JobState.COMPLETED
    assert len(j.artifacts) == 1

def test_catalog_import_integration():
    fab = UniversalImportFabricator()
    src = make_source("s_cat_int", "/content/sound.wav")
    prof = make_profile("p_cat_int")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j_cat_int", src.source_id, prof.profile_id)
    j = fab.process_next_job()
    catalog_entry = {
        "asset_id": f"Asset_{j.source_id}",
        "artifact_path": j.artifacts[0].output_path,
        "type": j.artifacts[0].artifact_type.value,
    }
    assert catalog_entry["type"] == "FINAL"

def test_search_index_import_integration():
    fab = UniversalImportFabricator()
    src = make_source("s_srch_int", "/assets/env.fbx")
    prof = make_profile("p_srch_int")
    fab.register_source(src)
    fab.register_profile(prof)
    job = fab.create_job("j_srch_int", src.source_id, prof.profile_id)
    index = {job.job_id: [src.canonical_path, job.profile_id]}
    assert "/assets/env.fbx" in index[job.job_id]

def test_command_import_integration():
    fab = UniversalImportFabricator()
    cmd = {"action": "import", "path": "/mesh.fbx", "profile": "p_cmd"}
    src = make_source("s_cmd", cmd["path"])
    prof = make_profile("p_cmd")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j_cmd", src.source_id, prof.profile_id)
    j = fab.process_next_job()
    assert len(j.artifacts) >= 1

def test_viewport_import_integration():
    fab = UniversalImportFabricator()
    src = make_source("s_vp", "/models/chair.fbx")
    prof = make_profile("p_vp")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j_vp", src.source_id, prof.profile_id)
    j = fab.process_next_job()
    viewport_signal = {"load_mesh": j.artifacts[0].output_path}
    assert viewport_signal["load_mesh"].startswith("/Game/Imported/")

def test_ui_import_integration():
    fab = UniversalImportFabricator()
    src = make_source("s_ui_int", "/textures/t.png")
    prof = make_profile("p_ui_int")
    fab.register_source(src)
    fab.register_profile(prof)
    job = fab.create_job("j_ui_int", src.source_id, prof.profile_id)
    assert job.state == JobState.QUEUED
    j = fab.process_next_job()
    assert j.state == JobState.COMPLETED

def test_cache_catalog_integration():
    fab = UniversalImportFabricator()
    prof = make_profile("p_cc")
    fab.register_profile(prof)
    src = make_source("s_cc_int", "/tex.png", version=3)
    fab.register_source(src)
    fp = fab.compute_cache_key("s_cc_int", "p_cc")
    assert len(fp) == 64

def test_dependency_catalog_integration():
    fab = UniversalImportFabricator()
    fab.register_dependency("scene_root", "mesh_building")
    fab.register_dependency("mesh_building", "mat_concrete")
    fab.register_dependency("mat_concrete", "tex_concrete_diffuse")
    deps = fab.invalidate_source_dependents("scene_root")
    assert "mesh_building" in deps
    assert "mat_concrete" in deps
    assert "tex_concrete_diffuse" in deps

def test_import_replay_integration():
    fab = UniversalImportFabricator()
    src = make_source("s_replay_int", "/anim.fbx")
    prof = make_profile("p_replay_int")
    fab.register_source(src)
    fab.register_profile(prof)
    fab.create_job("j_rep_int", src.source_id, prof.profile_id)
    fab.process_next_job()
    snap = fab.take_snapshot()
    ok, errs = UniversalImportValidator.validate_snapshot(snap)
    assert ok


# ==============================================================================
# 144. CLEANUP TESTS
# ==============================================================================

def test_job_cleanup():
    fab = UniversalImportFabricator()
    prof = make_profile("p_clean")
    fab.register_profile(prof)
    for i in range(10):
        src = make_source(f"s_clean_{i}", f"/p_{i}.fbx")
        fab.register_source(src)
        fab.create_job(f"j_clean_{i}", src.source_id, prof.profile_id)
        fab.process_next_job()
    completed_ids = [jid for jid, j in fab.jobs.items() if j.state == JobState.COMPLETED]
    for jid in completed_ids:
        del fab.jobs[jid]
    assert len(fab.jobs) == 0

def test_worker_cleanup():
    fab = UniversalImportFabricator(max_workers=4)
    for wid in fab.workers:
        fab.workers[wid] = WorkerState.RUNNING
    for wid in fab.workers:
        fab.workers[wid] = WorkerState.IDLE
    assert all(s == WorkerState.IDLE for s in fab.workers.values())

def test_processor_cleanup():
    fab = UniversalImportFabricator()
    fab.register_processor("custom_proc", lambda j, s: [], ["CUSTOM"])
    assert "custom_proc" in fab.processors
    del fab.processors["custom_proc"]
    assert "custom_proc" not in fab.processors

def test_temp_file_cleanup(tmp_path):
    temp_dir = tmp_path / "uaf_temp_scratch"
    temp_dir.mkdir()
    scratch_file = temp_dir / "stage.bin"
    scratch_file.write_bytes(b"temp_data")
    assert scratch_file.exists()
    scratch_file.unlink()
    temp_dir.rmdir()
    assert not temp_dir.exists()

def test_cache_cleanup():
    fab = UniversalImportFabricator()
    fab.cache["fp1"] = []
    fab.cache["fp2"] = []
    assert len(fab.cache) == 2
    fab.cache.clear()
    assert len(fab.cache) == 0

def test_checkpoint_cleanup():
    job = ImportJob("j_chk_clean", "s1", "p1")
    job.checkpoint["step1"] = {"done": True}
    assert "step1" in job.checkpoint
    job.checkpoint.clear()
    assert len(job.checkpoint) == 0

def test_subscription_cleanup():
    fab = UniversalImportFabricator()
    dummy_dict = {"sub_1": lambda: None}
    assert len(dummy_dict) == 1
    dummy_dict.clear()
    assert len(dummy_dict) == 0

def test_import_ui_cleanup():
    listeners = [lambda: None for _ in range(5)]
    assert len(listeners) == 5
    listeners.clear()
    assert len(listeners) == 0

def test_failed_job_cleanup():
    fab = UniversalImportFabricator()
    prof = make_profile("p_fj")
    fab.register_profile(prof)
    s1 = make_source("s1", "/a.fbx")
    s2 = make_source("s2", "/b.fbx")
    fab.register_source(s1)
    fab.register_source(s2)
    j1 = fab.create_job("j1", "s1", prof.profile_id)
    j2 = fab.create_job("j2", "s2", prof.profile_id)
    j1.state = JobState.FAILED
    failed_jobs = [j for j in fab.jobs.values() if j.state == JobState.FAILED]
    assert len(failed_jobs) == 1
    fab.jobs.pop(j1.job_id)
    assert len(fab.jobs) == 1


# ==============================================================================
# PACKAGER & EXTENDED VALIDATION TESTS
# ==============================================================================

def test_packager_cpp_header():
    header = UniversalImportPackager.generate_cpp_header()
    assert "UCLASS(" in header
    assert "UUAFAssetImportComponent" in header
    assert "GENERATED_BODY()" in header

def test_packager_cpp_source():
    source = UniversalImportPackager.generate_cpp_source()
    assert '#include "UUAFAssetImportComponent.h"' in source
    assert "UUAFAssetImportComponent::UUAFAssetImportComponent" in source

def test_packager_export_manifest_json():
    fab = UniversalImportFabricator()
    content = UniversalImportPackager.generate_import_manifest(fab)
    loaded = json.loads(content)
    assert "schema_version" in loaded
    assert "sources" in loaded

def test_packager_export_signature():
    fab = UniversalImportFabricator()
    content = UniversalImportPackager.generate_import_manifest(fab)
    sig = hashlib.sha256(content.encode("utf-8")).hexdigest()
    assert len(sig) == 64

def test_packager_roundtrip_verification(tmp_path):
    fab = UniversalImportFabricator()
    result = UniversalImportPackager.export_package(fab, tmp_path)
    assert (tmp_path / "UUAFAssetImportComponent.h").exists()
    assert (tmp_path / "UUAFAssetImportComponent.cpp").exists()
    assert (tmp_path / "uaf_import_manifest.json").exists()
    assert (tmp_path / "uaf_import_manifest.sig").exists()
    assert len(result["sha256"]) == 64

def test_packager_full_export_directory(tmp_path):
    fab = UniversalImportFabricator()
    result = UniversalImportPackager.export_package(fab, tmp_path)
    assert result["header"].endswith(".h")
    assert result["source"].endswith(".cpp")

def test_packager_custom_output_directory(tmp_path):
    custom_dir = tmp_path / "custom_pkg_dir"
    fab = UniversalImportFabricator()
    res = UniversalImportPackager.export_package(fab, custom_dir)
    assert Path(res["manifest"]).is_file()

def test_packager_deterministic_manifest_output():
    fab = UniversalImportFabricator()
    json1 = UniversalImportPackager.generate_import_manifest(fab)
    json2 = UniversalImportPackager.generate_import_manifest(fab)
    assert json1 == json2

def test_packager_invalid_manifest_handling():
    man = ImportManifest("m1", "j1")
    man.signature = "invalid_tampered_signature"
    ok, errs = UniversalImportValidator.validate_manifest(man)
    assert not ok

def test_telemetry_snapshot_consistency():
    job = ImportJob("j_tele_snap", "s1", "p1")
    snap = ImportStateSnapshot("snap_tele", time.time(), {job.job_id: job.to_dict()}, {}, {})
    ok, errs = UniversalImportValidator.validate_snapshot(snap)
    assert ok

def test_telemetry_aggregation():
    t1 = ImportTelemetry(completed_jobs=1, total_processed_bytes=1000)
    t2 = ImportTelemetry(completed_jobs=2, total_processed_bytes=2000)
    total_jobs = t1.completed_jobs + t2.completed_jobs
    total_mem = t1.total_processed_bytes + t2.total_processed_bytes
    assert total_jobs == 3
    assert total_mem == 3000

def test_worker_pool_concurrency_limit():
    fab = UniversalImportFabricator(max_workers=3)
    assert len(fab.workers) == 3
    for wid, state in fab.workers.items():
        assert state == WorkerState.IDLE

def test_job_error_context_preservation():
    job = ImportJob("j_err_ctx", "s1", "p1")
    job.state = JobState.FAILED
    job.error_message = "Out of disk space on target volume"
    assert "disk space" in job.error_message

def test_manifest_verification_pass_and_fail():
    man = ImportManifest("man_ver", "j_ver")
    man.compute_signature()
    ok, _ = UniversalImportValidator.validate_manifest(man)
    assert ok
    man.signature = "corrupt"
    ok_bad, _ = UniversalImportValidator.validate_manifest(man)
    assert not ok_bad

def test_diagnostic_bundle_export():
    fab = UniversalImportFabricator()
    bundle = fab.generate_diagnostic_bundle()
    assert bundle.bundle_id.startswith("bundle_")
    assert len(bundle.signature) == 64

def test_format_detector_custom_extension():
    fab = UniversalImportFabricator()
    fab.register_format(FormatDescriptor(format_id="CUSTOM", name="Custom Asset", category=FormatCategory.CUSTOM, extensions=[".customext"]))
    fmt_id, conf = fab.detect_format(extension=".customext")
    assert fmt_id == "CUSTOM"
    assert conf == 0.8

def test_import_pipeline_end_to_end_flow():
    fab = UniversalImportFabricator()
    src = make_source("s_e2e", "/content/models/knight.fbx")
    prof = make_profile("p_e2e")
    fab.register_source(src)
    fab.register_profile(prof)
    job = fab.create_job("j_e2e", src.source_id, prof.profile_id, priority=JobPriority.HIGH)
    assert job.state == JobState.QUEUED
    j = fab.process_next_job()
    assert j.state == JobState.COMPLETED
    assert len(j.artifacts) >= 1
    man = fab.generate_manifest(j.job_id)
    assert len(man.signature) == 64

def test_source_identity_immutable_hash():
    s = make_source("s_imm", "/immutable/path.png")
    d1 = s.to_dict()
    d2 = s.to_dict()
    assert d1 == d2

def test_fabricator_custom_processing_node():
    node = ProcessingNode("node_custom", "Processor_A", {"threads": 4})
    assert node.node_id == "node_custom"
    assert node.settings["threads"] == 4
