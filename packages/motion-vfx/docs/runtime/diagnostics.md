# Diagnósticos y Salud del Runtime (Fase 18)

## Health Report
```typescript
interface HealthReport {
  status: "healthy" | "warning" | "degraded" | "invalid" | "corrupted";
  projectId: string;
  revisionId: string;
  errors: Diagnostic[];
  warnings: Diagnostic[];
  determinism: { verified: boolean; hash?: string };
  persistence: { readable: boolean; writable: boolean; checksumValid: boolean };
}
```

## Métricas Operacionales
`RuntimeMetrics` recopila latencias de `load`, `save`, `validation`, `diff`, `restore` y `hash` calculando p50, p95 y p99.
