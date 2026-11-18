"""
UAF-81.70: Universal Asset Import Pipeline Fabricator Engine.
Authoritative core implementation for Source Normalization, Format Detection,
Profile Resolution, Processing Graphs, Priority Job Queues, Worker Pools,
Incremental Cache, Error Retries, and UE5 Export Manifests.
"""

from __future__ import annotations

import copy
import hashlib
import json
import time
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from uaf.universal_import.models.definition import (
    ArtifactType,
    FormatCategory,
    FormatDescriptor,
    ImportArtifact,
    ImportDiagnosticBundle,
    ImportJob,
    ImportJobPriority,
    ImportJobState,
    ImportManifest,
    ImportProfile,
    ImportSettings,
    ImportStateSnapshot,
    ImportTelemetry,
    JobPriority,
    JobState,
    OutputPolicy,
    ProcessingEdge,
    ProcessingGraph,
    ProcessingNode,
    SourceIdentity,
    SourceType,
    WorkerState,
    normalize_source_path,
)


class UniversalImportFabricator:
    """
    Authoritative asset import pipeline engine.
    Fully decoupled and independent of external graphical engines.
    """

    def __init__(self, max_workers: int = 4):
        self.sources: Dict[str, SourceIdentity] = {}
        self.formats: Dict[str, FormatDescriptor] = {}
        self.profiles: Dict[str, ImportProfile] = {}
        self.processors: Dict[str, Dict[str, Any]] = {}
        self.jobs: Dict[str, ImportJob] = {}
        self.job_queue: List[str] = []  # List of job_ids ordered by priority
        self.cache: Dict[str, List[ImportArtifact]] = {}  # cache_key -> artifacts
        self.dependencies: Dict[str, Set[str]] = {}  # upstream_id -> set of downstream_ids
        self.worker_count: int = max_workers
        self.workers: Dict[int, WorkerState] = {i: WorkerState.IDLE for i in range(max_workers)}
        self.telemetry = ImportTelemetry(worker_count=max_workers)

        # Register default builtin formats
        self._register_default_formats()

    # --------------------------------------------------------------------------
    # 1. DEFAULT FORMAT REGISTRATION
    # --------------------------------------------------------------------------

    def _register_default_formats(self) -> None:
        self.register_format(FormatDescriptor(
            format_id="mesh_fbx",
            name="Autodesk FBX",
            category=FormatCategory.MESH,
            extensions=[".fbx"],
            magic_bytes=[b"Kaydara FBX Binary"],
            mime_types=["application/octet-stream"],
            default_profile_id="default_mesh",
        ))
        self.register_format(FormatDescriptor(
            format_id="mesh_obj",
            name="Wavefront OBJ",
            category=FormatCategory.MESH,
            extensions=[".obj"],
            mime_types=["text/plain"],
            default_profile_id="default_mesh",
        ))
        self.register_format(FormatDescriptor(
            format_id="texture_png",
            name="PNG Image",
            category=FormatCategory.TEXTURE,
            extensions=[".png"],
            magic_bytes=[b"\x89PNG\r\n\x1a\n"],
            mime_types=["image/png"],
            default_profile_id="default_texture",
        ))
        self.register_format(FormatDescriptor(
            format_id="audio_wav",
            name="WAV Audio",
            category=FormatCategory.AUDIO,
            extensions=[".wav"],
            magic_bytes=[b"RIFF"],
            mime_types=["audio/wav"],
            default_profile_id="default_audio",
        ))

    # --------------------------------------------------------------------------
    # 2. SOURCE MANAGEMENT
    # --------------------------------------------------------------------------

    def register_source(self, source: SourceIdentity) -> None:
        if source.source_id in self.sources:
            raise ValueError(f"NO_DUPLICATE_SOURCE_IDENTITY: Source '{source.source_id}' already registered.")
        for existing in self.sources.values():
            if existing.canonical_path == source.canonical_path:
                raise ValueError(f"NO_DUPLICATE_SOURCE_IDENTITY: Path '{source.canonical_path}' already exists.")

        self.sources[source.source_id] = source

    def get_source(self, source_id: str) -> Optional[SourceIdentity]:
        return self.sources.get(source_id)

    def remove_source(self, source_id: str) -> None:
        if source_id in self.sources:
            del self.sources[source_id]
            # Invalidate dependent jobs/cache
            self.invalidate_source_dependents(source_id)

    # --------------------------------------------------------------------------
    # 3. FORMAT DETECTION & REGISTRY
    # --------------------------------------------------------------------------

    def register_format(self, descriptor: FormatDescriptor) -> None:
        if descriptor.format_id in self.formats:
            raise ValueError(f"Duplicate format ID '{descriptor.format_id}'.")
        self.formats[descriptor.format_id] = descriptor

    def get_format(self, format_id: str) -> Optional[FormatDescriptor]:
        return self.formats.get(format_id)

    def detect_format(
        self,
        data: Optional[bytes] = None,
        extension: Optional[str] = None
    ) -> Tuple[Optional[str], float]:
        """
        Determines format with strict priority:
        1. Magic bytes match (confidence 1.0)
        2. File extension match (confidence 0.8)
        Returns (format_id, confidence) or (None, 0.0) if unsupported.
        """
        if data:
            for fid, desc in self.formats.items():
                for magic in desc.magic_bytes:
                    if data.startswith(magic):
                        return fid, 1.0

        if extension:
            ext_clean = ("." + extension.lstrip(".")).lower()
            for fid, desc in self.formats.items():
                if ext_clean in [e.lower() for e in desc.extensions]:
                    return fid, 0.8

        return None, 0.0

    # --------------------------------------------------------------------------
    # 4. PROFILE MANAGEMENT & RESOLUTION
    # --------------------------------------------------------------------------

    def register_profile(self, profile: ImportProfile) -> None:
        if profile.profile_id in self.profiles:
            raise ValueError(f"Duplicate profile ID '{profile.profile_id}'.")
        self.profiles[profile.profile_id] = profile

    def get_profile(self, profile_id: str) -> Optional[ImportProfile]:
        return self.profiles.get(profile_id)

    def resolve_profile(
        self,
        profile_id: str,
        overrides: Optional[Dict[str, Any]] = None
    ) -> ImportProfile:
        if profile_id not in self.profiles:
            raise KeyError(f"Profile '{profile_id}' not found.")

        # Chain inheritance
        chain = []
        curr = self.profiles[profile_id]
        visited = set()

        while curr:
            if curr.profile_id in visited:
                raise ValueError(f"NO_GRAPH_CYCLES: Profile inheritance cycle detected in '{curr.profile_id}'.")
            visited.add(curr.profile_id)
            chain.append(curr)
            curr = self.profiles.get(curr.parent_profile_id) if curr.parent_profile_id else None

        # Merge base-to-derived
        merged_settings = {}
        for p in reversed(chain):
            merged_settings.update(p.settings.to_dict())

        if overrides:
            merged_settings.update(overrides)

        resolved = copy.deepcopy(chain[0])
        resolved.settings = ImportSettings(merged_settings)
        return resolved

    # --------------------------------------------------------------------------
    # 5. PROCESSOR REGISTRY
    # --------------------------------------------------------------------------

    def register_processor(
        self,
        processor_id: str,
        handler: Callable[[ImportJob, ImportSettings], List[ImportArtifact]],
        supported_formats: List[str]
    ) -> None:
        self.processors[processor_id] = {
            "handler": handler,
            "supported_formats": list(supported_formats),
        }

    # --------------------------------------------------------------------------
    # 6. JOB QUEUE & SCHEDULING
    # --------------------------------------------------------------------------

    def create_job(
        self,
        job_id: str,
        source_id: str,
        profile_id: str,
        priority: JobPriority = JobPriority.NORMAL
    ) -> ImportJob:
        if job_id in self.jobs:
            raise ValueError(f"Duplicate job ID '{job_id}'.")
        if source_id not in self.sources:
            raise KeyError(f"Source '{source_id}' does not exist.")
        if profile_id not in self.profiles:
            raise KeyError(f"Profile '{profile_id}' does not exist.")

        job = ImportJob(
            job_id=job_id,
            source_id=source_id,
            profile_id=profile_id,
            priority=priority,
            state=JobState.QUEUED,
        )
        self.jobs[job_id] = job
        self.enqueue_job(job_id)
        return job

    def enqueue_job(self, job_id: str) -> None:
        if job_id not in self.job_queue:
            self.job_queue.append(job_id)
        self._sort_queue()
        self.telemetry.queued_jobs = len([j for j in self.jobs.values() if j.state == JobState.QUEUED])

    def _sort_queue(self) -> None:
        def sort_key(jid: str):
            job = self.jobs[jid]
            # Highest priority first, then earliest created_time, then alphabetical jid
            return (-int(job.priority.value), job.created_time, jid)

        self.job_queue.sort(key=sort_key)

    def dequeue_job(self) -> Optional[ImportJob]:
        if not self.job_queue:
            return None
        jid = self.job_queue.pop(0)
        job = self.jobs.get(jid)
        self.telemetry.queued_jobs = len([j for j in self.jobs.values() if j.state == JobState.QUEUED])
        return job

    def cancel_job(self, job_id: str) -> bool:
        if job_id not in self.jobs:
            return False
        job = self.jobs[job_id]
        if job.state in (JobState.COMPLETED, JobState.FAILED, JobState.CANCELLED):
            return False

        job.state = JobState.CANCELLED
        if job_id in self.job_queue:
            self.job_queue.remove(job_id)
        self.telemetry.cancelled_jobs += 1
        return True

    def reprioritize_job(self, job_id: str, new_priority: JobPriority) -> bool:
        if job_id not in self.jobs:
            return False
        self.jobs[job_id].priority = new_priority
        self._sort_queue()
        return True

    # --------------------------------------------------------------------------
    # 7. CACHING & INCREMENTAL PROCESSING
    # --------------------------------------------------------------------------

    def compute_cache_key(self, source_id: str, profile_id: str) -> str:
        source = self.sources.get(source_id)
        profile = self.profiles.get(profile_id)
        if not source or not profile:
            return ""

        settings_fp = profile.settings.compute_fingerprint()
        payload = f"{source.content_hash}:{profile.profile_id}:{profile.version}:{settings_fp}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def get_cached_artifacts(self, cache_key: str) -> Optional[List[ImportArtifact]]:
        return self.cache.get(cache_key)

    def register_dependency(self, upstream_id: str, downstream_id: str) -> None:
        if upstream_id not in self.dependencies:
            self.dependencies[upstream_id] = set()
        self.dependencies[upstream_id].add(downstream_id)

    def invalidate_source_dependents(self, source_id: str) -> List[str]:
        invalidated = []
        to_visit = [source_id]
        while to_visit:
            curr = to_visit.pop(0)
            if curr in self.dependencies:
                for dep in self.dependencies[curr]:
                    invalidated.append(dep)
                    to_visit.append(dep)
        # Purge cache entries
        for key in list(self.cache.keys()):
            for inv in invalidated:
                if inv in key:
                    del self.cache[key]
        return invalidated

    # --------------------------------------------------------------------------
    # 8. EXECUTION & WORKER PROCESSING
    # --------------------------------------------------------------------------

    def process_next_job(self, worker_id: int = 0) -> Optional[ImportJob]:
        job = self.dequeue_job()
        if not job or job.state == JobState.CANCELLED:
            return None

        self.workers[worker_id] = WorkerState.RUNNING
        self.telemetry.running_jobs += 1
        job.state = JobState.RUNNING
        job.started_time = time.time()

        # Check Cache
        cache_key = self.compute_cache_key(job.source_id, job.profile_id)
        cached = self.get_cached_artifacts(cache_key)
        if cached:
            job.artifacts = copy.deepcopy(cached)
            job.state = JobState.COMPLETED
            job.progress = 1.0
            job.completed_time = time.time()
            self.telemetry.cache_hits += 1
            self.telemetry.completed_jobs += 1
            self.telemetry.running_jobs -= 1
            self.workers[worker_id] = WorkerState.IDLE
            return job

        self.telemetry.cache_misses += 1
        profile = self.resolve_profile(job.profile_id)
        proc_info = self.processors.get(profile.processor_id)

        try:
            if proc_info and proc_info.get("handler"):
                artifacts = proc_info["handler"](job, profile.settings)
            else:
                # Default mock generator
                src = self.sources[job.source_id]
                art_id = f"art_{job.job_id}_0"
                art_path = f"/Game/Imported/{src.canonical_path.split('/')[-1]}"
                artifacts = [
                    ImportArtifact(
                        artifact_id=art_id,
                        job_id=job.job_id,
                        artifact_type=ArtifactType.FINAL,
                        output_path=art_path,
                        content_hash=hashlib.sha256(art_path.encode("utf-8")).hexdigest(),
                        size_bytes=src.file_size_bytes or 1024,
                    )
                ]

            job.artifacts = artifacts
            job.state = JobState.COMPLETED
            job.progress = 1.0
            job.completed_time = time.time()
            self.cache[cache_key] = copy.deepcopy(artifacts)
            self.telemetry.completed_jobs += 1

        except Exception as ex:
            job.error_message = str(ex)
            if job.retry_count < job.max_retries:
                job.retry_count += 1
                job.state = JobState.RETRYING
                self.telemetry.retries += 1
                self.enqueue_job(job.job_id)
            else:
                job.state = JobState.FAILED
                self.telemetry.failed_jobs += 1

        finally:
            self.telemetry.running_jobs = max(0, self.telemetry.running_jobs - 1)
            self.workers[worker_id] = WorkerState.IDLE

        return job

    def generate_manifest(self, job_id: str) -> ImportManifest:
        if job_id not in self.jobs:
            raise KeyError(f"Job '{job_id}' not found.")
        job = self.jobs[job_id]
        manifest_id = f"manifest_{job.job_id}_{int(time.time() * 1000)}"
        return ImportManifest(
            manifest_id=manifest_id,
            job_id=job.job_id,
            artifacts=copy.deepcopy(job.artifacts),
        )

    # --------------------------------------------------------------------------
    # 9. SNAPSHOTS & TELEMETRY
    # --------------------------------------------------------------------------

    def take_snapshot(self) -> ImportStateSnapshot:
        snap_id = f"snap_import_{int(time.time() * 1000)}"
        src_data = {sid: s.to_dict() for sid, s in self.sources.items()}
        job_data = {jid: j.to_dict() for jid, j in self.jobs.items()}
        prof_data = {pid: p.to_dict() for pid, p in self.profiles.items()}

        return ImportStateSnapshot(
            snapshot_id=snap_id,
            timestamp=time.time(),
            sources=src_data,
            jobs=job_data,
            profiles=prof_data,
        )

    def generate_diagnostic_bundle(self) -> ImportDiagnosticBundle:
        bundle_id = f"bundle_import_{int(time.time() * 1000)}"
        snap = self.take_snapshot()
        return ImportDiagnosticBundle(
            bundle_id=bundle_id,
            timestamp=time.time(),
            snapshot=snap,
            telemetry=copy.deepcopy(self.telemetry),
        )
