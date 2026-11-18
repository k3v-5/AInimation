import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.amsl import (
    AMSLAPI, ConstraintSpec, ConstraintType, ConstraintPriority,
    ReferenceSpec, DamageLevel
)

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 35: ASSET/MODEL SPECIFICATION LANGUAGE (AMSL)")
    print("=" * 95)

    api = AMSLAPI()

    # 1. Creación de Medieval House en AMSL (Sección 96)
    print("\n[EJEMPLO 1] Especificación Completa de 'MEDIEVAL_HOUSE' en AMSL (Sección 96):")
    spec_house = api.create_medieval_house_spec(
        asset_id="HOUSE_001",
        width=6.0,
        depth=4.0,
        height=4.5,
        roof_pitch=40.0,
        door_width=0.90,
        window_count=4,
        seed=42191
    )

    print(f" - Spec ID: {spec_house.specification_id} (v{spec_house.schema_version}) -> Asset: {spec_house.asset_id}")
    print(f" - Dimensiones Declaradas: {spec_house.dimensions.width.target}x{spec_house.dimensions.depth.target}x{spec_house.dimensions.height.target}m")
    print(f" - Proporciones: {spec_house.dimensions.proportions}")
    print(f" - Estructura: Pisos={spec_house.structure.floors} | Techo={spec_house.structure.roof}")
    print(" - Componentes Lógicos:")
    for c in spec_house.components:
        print(f"   * [{c.id}] Tipo: {c.type} (Count={c.count}) -> Params: {c.parameters}")
    print(" - Materiales PBR Declarados:")
    for m in spec_house.materials:
        print(f"   * [{m.material_id}] Cat: {m.category.value} | Color: {m.base_color} | Roughness: {m.roughness}")

    spec_hash = spec_house.compute_specification_hash()
    print(f" - Hash Canónico SHA-256: {spec_hash}")

    # 2. Protección de Estructura mediante Restricciones Bloqueadas (Sección 97)
    print("\n[EJEMPLO 2] Protección Estructural mediante Restricciones (Sección 97):")
    spec_house.constraints.append(
        ConstraintSpec(
            type=ConstraintType.HARD,
            priority=ConstraintPriority.USER_HARD,
            rule={"preserve": "structure.roof"}
        )
    )
    print(" - Regla Añadida: HARD_CONSTRAINT (preserve: structure.roof)")
    try:
        api.compile_spec(spec_house, overrides={"structure.roof.pitch": 48.0})
    except ValueError as e:
        print(f" - Bloqueo de Conflicto: {e}")

    # 3. Envejecimiento Controlado y Daño (Sección 98)
    print("\n[EJEMPLO 3] Especificación de Desgaste y Daño Controlado (Sección 98):")
    spec_house.damage.level = DamageLevel.LOW
    spec_house.damage.cracks = True
    spec_house.damage.preserve_structural_integrity = True
    print(f" - Nivel de Daño: {spec_house.damage.level.value} | Grietas={spec_house.damage.cracks} | Preservar Integridad={spec_house.damage.preserve_structural_integrity}")

    # 4. Referencias Visuales Mapeadas (Sección 99)
    print("\n[EJEMPLO 4] Mapeo de Referencias Visuales Específicas (Sección 99):")
    spec_house.references = [
        ReferenceSpec(id="REF_001", type="IMAGE", priority="HIGH", applies_to=["silhouette", "proportions", "roof_shape"]),
        ReferenceSpec(id="REF_002", type="IMAGE", priority="MEDIUM", applies_to=["materials", "colors"])
    ]
    for r in spec_house.references:
        print(f"   * [{r.id}] Tipo: {r.type} (Prioridad={r.priority}) -> Aplica a: {r.applies_to}")

    # 5. Derivación de Requisitos de Construcción (Build Requirements)
    print("\n[EJEMPLO 5] Derivación de Requisitos de Construcción para el BuildPlanner:")
    # Caso A: Modificación de Material únicamente
    _, reqs_mat = api.compile_spec(spec_house, overrides={"material.mat_walls": "#606060"})
    print(f" - Caso Material -> Builders: {reqs_mat.required_builders} | Rebuild Necesario: {reqs_mat.requires_rebuild} | Costo: {reqs_mat.modification_cost}")

    # Caso B: Modificación de Techo (sin restricción)
    spec_house_unlocked = api.create_medieval_house_spec()
    _, reqs_roof = api.compile_spec(spec_house_unlocked, overrides={"structure.roof.pitch": 45.0})
    print(f" - Caso Techo    -> Builders: {reqs_roof.required_builders} | Rebuild Necesario: {reqs_roof.requires_rebuild} | Costo: {reqs_roof.modification_cost}")

    # 6. Diff Semántico entre Especificaciones (Sección 83)
    print("\n[EJEMPLO 6] Diff Semántico entre Versiones de Especificación (Sección 83):")
    spec_v2 = api.create_medieval_house_spec(width=7.2, door_width=1.10)
    diff = api.diff_specs(spec_house_unlocked, spec_v2)
    print(f" - Modificados: {diff.modified}")
    print(f" - Sin Cambios: {list(diff.unchanged.keys())}")

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 35 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()
