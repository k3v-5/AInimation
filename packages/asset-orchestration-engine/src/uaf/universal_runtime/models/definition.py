"""
Universal Runtime Bootstrap, Application Lifecycle, Service Container,
Dependency Injection, Health Monitoring, Watchdog, Safe Mode, Recovery and Runtime Orchestration Models (UAF-81.64).
"""

from __future__ import annotations
import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union


# ==============================================================================
# ENUMS
# ==============================================================================

class RuntimeState(str, Enum):
    """Authoritative runtime lifecycle states (?5)."""
    CREATED = "CREATED"
    BOOTSTRAPPING = "BOOTSTRAPPING"
    DISCOVERING = "DISCOVERING"
    LOADING_CONFIGURATION = "LOADING_CONFIGURATION"
    REGISTERING_SERVICES = "REGISTERING_SERVICES"
    RESOLVING_DEPENDENCIES = "RESOLVING_DEPENDENCIES"
    INITIALIZING = "INITIALIZING"
    STARTING = "STARTING"
    VALIDATING = "VALIDATING"
    HEALTH_CHECK = "HEALTH_CHECK"
    READY = "READY"
    DEGRADED = "DEGRADED"
    SAFE_MODE = "SAFE_MODE"
    RECOVERY_MODE = "RECOVERY_MODE"
    SHUTTING_DOWN = "SHUTTING_DOWN"
    STOPPED = "STOPPED"
    FAILED = "FAILED"


class ServiceLifecycle(str, Enum):
    """Service instance states (?25)."""
    REGISTERED = "REGISTERED"
    RESOLVING = "RESOLVING"
    CREATED = "CREATED"
    INITIALIZING = "INITIALIZING"
    INITIALIZED = "INITIALIZED"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    FAILED = "FAILED"
    DISABLED = "DISABLED"


class ServiceScope(str, Enum):
    """Dependency injection resolution scopes (?28)."""
    APPLICATION = "APPLICATION"
    SESSION = "SESSION"
    REQUEST = "REQUEST"
    TRANSIENT = "TRANSIENT"
    SINGLETON = "SINGLETON"


class HealthState(str, Enum):
    """Service and runtime health states (?86)."""
    UNKNOWN = "UNKNOWN"
    STARTING = "STARTING"
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    FAILED = "FAILED"


class HealthCheckType(str, Enum):
    """Health check inspection categories (?88)."""
    LIVENESS = "LIVENESS"
    READINESS = "READINESS"
    DEPENDENCY = "DEPENDENCY"
    RESOURCE = "RESOURCE"
    FUNCTIONAL = "FUNCTIONAL"


class ShutdownReason(str, Enum):
    """Shutdown triggers and motivations (?108)."""
    USER_REQUEST = "USER_REQUEST"
    SYSTEM_REQUEST = "SYSTEM_REQUEST"
    UPDATE_REQUEST = "UPDATE_REQUEST"
    CRASH_RECOVERY = "CRASH_RECOVERY"
    FATAL_ERROR = "FATAL_ERROR"


class CrashType(str, Enum):
    """Crash classifications (?121, ?123)."""
    HARD_CRASH = "HARD_CRASH"
    UNHANDLED_EXCEPTION = "UNHANDLED_EXCEPTION"
    DEADLOCK = "DEADLOCK"
    TIMEOUT = "TIMEOUT"
    OUT_OF_MEMORY = "OUT_OF_MEMORY"
    ASSERTION_FAILURE = "ASSERTION_FAILURE"


class RestartPolicy(str, Enum):
    """Service restart policies (?127, ?148)."""
    NEVER = "NEVER"
    ON_FAILURE = "ON_FAILURE"
    ALWAYS = "ALWAYS"
    EXPONENTIAL_BACKOFF = "EXPONENTIAL_BACKOFF"


class WatchdogEscalation(str, Enum):
    """Watchdog fault escalation steps (?98)."""
    WARNING = "WARNING"
    RETRY = "RETRY"
    RESTART = "RESTART"
    DEGRADED = "DEGRADED"
    SAFE_MODE = "SAFE_MODE"
    ABORT = "ABORT"


class CapabilityStatus(str, Enum):
    """Runtime feature / capability statuses (?62, ?144)."""
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    LIMITED = "LIMITED"


class PreviousSessionStatus(str, Enum):
    """Previous session exit state (?18)."""
    CLEAN_EXIT = "CLEAN_EXIT"
    CRASH = "CRASH"
    FORCED_EXIT = "FORCED_EXIT"
    UNKNOWN = "UNKNOWN"


class StartupPolicy(str, Enum):
    """Service initialization triggering policy (?22, ?40)."""
    EAGER = "EAGER"
    LAZY = "LAZY"
    ON_DEMAND = "ON_DEMAND"


class ShutdownPolicy(str, Enum):
    """Service termination policy (?22, ?112)."""
    GRACEFUL = "GRACEFUL"
    FORCED = "FORCED"
    IMMEDIATE = "IMMEDIATE"


class RecoveryAction(str, Enum):
    """Recovery operations in recovery mode (?68)."""
    VERIFY_INSTALLATION = "VERIFY_INSTALLATION"
    REPAIR_INSTALLATION = "REPAIR_INSTALLATION"
    ROLLBACK_UPDATE = "ROLLBACK_UPDATE"
    REBUILD_REGISTRY = "REBUILD_REGISTRY"
    DISABLE_OPTIONAL_CONTENT = "DISABLE_OPTIONAL_CONTENT"
    COLLECT_DIAGNOSTICS = "COLLECT_DIAGNOSTICS"


# ==============================================================================
# DATA MODELS
# ==============================================================================

@dataclass
class RuntimeEnvironment:
    """Immutable platform & process execution descriptor (?14, ?15, ?16, ?17)."""
    application_id: str
    version: str
    build_id: str
    runtime_version: str = "1.0.0"
    platform: str = "windows"
    architecture: str = "x86_64"
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    boot_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    cpu_count: int = 8
    memory_mb: int = 16384
    gpu_info: str = "DirectX 12 / Vulkan Compatible"
    environment_variables: Dict[str, str] = field(default_factory=dict)
    start_time: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "application_id": self.application_id,
            "version": self.version,
            "build_id": self.build_id,
            "runtime_version": self.runtime_version,
            "platform": self.platform,
            "architecture": self.architecture,
            "session_id": self.session_id,
            "boot_id": self.boot_id,
            "cpu_count": self.cpu_count,
            "memory_mb": self.memory_mb,
            "gpu_info": self.gpu_info,
            "start_time": self.start_time,
        }


@dataclass
class ServiceDefinition:
    """Authoritative service contract declaration (?22)."""
    service_id: str
    version: str = "1.0.0"
    scope: ServiceScope = ServiceScope.SINGLETON
    dependencies: List[str] = field(default_factory=list)
    optional_dependencies: List[str] = field(default_factory=list)
    startup_policy: StartupPolicy = StartupPolicy.EAGER
    shutdown_policy: ShutdownPolicy = ShutdownPolicy.GRACEFUL
    restart_policy: RestartPolicy = RestartPolicy.ON_FAILURE
    startup_timeout: float = 10.0
    shutdown_timeout: float = 5.0
    heartbeat_interval: float = 1.0
    heartbeat_timeout: float = 3.0
    max_restart_attempts: int = 3
    is_critical: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "service_id": self.service_id,
            "version": self.version,
            "scope": self.scope.value,
            "dependencies": self.dependencies,
            "optional_dependencies": self.optional_dependencies,
            "startup_policy": self.startup_policy.value,
            "shutdown_policy": self.shutdown_policy.value,
            "restart_policy": self.restart_policy.value,
            "startup_timeout": self.startup_timeout,
            "shutdown_timeout": self.shutdown_timeout,
            "heartbeat_interval": self.heartbeat_interval,
            "heartbeat_timeout": self.heartbeat_timeout,
            "max_restart_attempts": self.max_restart_attempts,
            "is_critical": self.is_critical,
        }


@dataclass
class ServiceInstance:
    """Active runtime instance of a service (?26)."""
    definition: ServiceDefinition
    state: ServiceLifecycle = ServiceLifecycle.REGISTERED
    instance: Any = None
    factory: Optional[Callable[..., Any]] = None
    last_heartbeat: float = field(default_factory=time.time)
    missed_heartbeats: int = 0
    restart_count: int = 0
    error_history: List[Dict[str, Any]] = field(default_factory=list)
    start_time: Optional[float] = None
    stop_time: Optional[float] = None
    progress_token: int = 0

    @property
    def service_id(self) -> str:
        return self.definition.service_id


@dataclass
class HealthCheckResult:
    """Result of an individual service health check (?87, ?88)."""
    check_type: HealthCheckType
    status: HealthState
    message: str = ""
    timestamp: float = field(default_factory=time.time)
    latency_ms: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthReport:
    """Aggregated health status of the runtime system (?85, ?86)."""
    overall_state: HealthState
    timestamp: float = field(default_factory=time.time)
    checks: Dict[str, List[HealthCheckResult]] = field(default_factory=dict)
    active_services: List[str] = field(default_factory=list)
    degraded_services: List[str] = field(default_factory=list)
    failed_services: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_state": self.overall_state.value,
            "timestamp": self.timestamp,
            "active_services": self.active_services,
            "degraded_services": self.degraded_services,
            "failed_services": self.failed_services,
            "check_count": sum(len(v) for v in self.checks.values()),
        }


@dataclass
class WatchdogEvent:
    """Watchdog fault detection and escalation event (?96, ?98)."""
    service_id: str
    event_type: str
    escalation_action: WatchdogEscalation
    timestamp: float = field(default_factory=time.time)
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CrashReport:
    """Authoritative crash capture document (?121, ?122)."""
    crash_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    crash_type: CrashType = CrashType.UNHANDLED_EXCEPTION
    timestamp: float = field(default_factory=time.time)
    session_id: str = ""
    boot_id: str = ""
    error_message: str = ""
    stack_trace: str = ""
    failed_service_id: Optional[str] = None
    active_services: List[str] = field(default_factory=list)
    diagnostic_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "crash_id": self.crash_id,
            "crash_type": self.crash_type.value,
            "timestamp": self.timestamp,
            "session_id": self.session_id,
            "boot_id": self.boot_id,
            "error_message": self.error_message,
            "stack_trace": self.stack_trace,
            "failed_service_id": self.failed_service_id,
            "active_services": self.active_services,
            "diagnostic_data": self.diagnostic_data,
        }


@dataclass
class RuntimeTelemetry:
    """Runtime performance, memory, and operational telemetry (?131, ?132)."""
    boot_time_ms: float = 0.0
    shutdown_time_ms: float = 0.0
    recovery_time_ms: float = 0.0
    cpu_utilization_percent: float = 0.0
    memory_rss_bytes: int = 0
    counters: Dict[str, int] = field(default_factory=dict)
    timings: Dict[str, float] = field(default_factory=dict)
    service_latencies: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "boot_time_ms": self.boot_time_ms,
            "shutdown_time_ms": self.shutdown_time_ms,
            "recovery_time_ms": self.recovery_time_ms,
            "cpu_utilization_percent": self.cpu_utilization_percent,
            "memory_rss_bytes": self.memory_rss_bytes,
            "counters": self.counters,
            "timings": self.timings,
            "service_latencies": self.service_latencies,
        }


@dataclass
class DiagnosticBundle:
    """Self-contained diagnostic export bundle (?138, ?139)."""
    bundle_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    environment: Optional[RuntimeEnvironment] = None
    runtime_state: RuntimeState = RuntimeState.READY
    crash_reports: List[CrashReport] = field(default_factory=list)
    telemetry: Optional[RuntimeTelemetry] = None
    service_logs: List[Dict[str, Any]] = field(default_factory=list)
    health_reports: List[HealthReport] = field(default_factory=list)
    sha256_digest: str = ""

    def compute_digest(self) -> str:
        data = {
            "bundle_id": self.bundle_id,
            "timestamp": self.timestamp,
            "runtime_state": self.runtime_state.value,
            "crashes": [c.to_dict() for c in self.crash_reports],
            "log_count": len(self.service_logs),
        }
        serialized = json.dumps(data, sort_keys=True)
        digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        self.sha256_digest = digest
        return digest


@dataclass
class RuntimeDiagnosticReport:
    """Validation report for runtime state and service configurations."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    info: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
