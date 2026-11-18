# UAF-81.93: DYNAMIC ECONOMY, WEAPON AFFIXES & PROCEDURAL LOOT FABRIC (UE5 GAS & DATATABLES)

**Status:** Approved & Normative  
**Subsystem:** Universal Asset Framework (AOE/UAF) - Itemization, Combat Economy & GAS Interoperability  
**Target Engine:** Unreal Engine 5 (DataTables, Gameplay Ability System, Gameplay Effects, AttributeSets)  
**Execution Environment:** 100% Headless Orchestrator & Exporter  

---

## 1. MISSION & SCOPE

UAF-81.93 formalizes a mathematically sound, deterministic procedural itemization and economy fabric for the Universal Asset Framework. Complementing the level topology and pacing director (UAF-81.90), macro-landscape biomes (UAF-81.91), and multi-agent AI ecosystems (UAF-81.92), UAF-81.93 provides the core progression engine driving player rewards, combat dynamics, and transactional economies.

The subsystem operates entirely headlessly with zero external engine dependencies, synthesizing balanced weapon statistics, deterministic affix combinations, elemental affinities, weighted drop distributions with bad luck protection, and tension-coupled market pricing. All outputs are exportable to native **Unreal Engine 5 DataTables** (CSV and JSON) and mapped directly into the **Gameplay Ability System (GAS)** via `FWeaponItemDefinition` and `FGameplayEffectSpec` definitions.

---

## 2. MATHEMATICAL & ARCHITECTURAL SPECIFICATIONS

### 2.1 Power Budget Formulation & Conservation
Every weapon generated possesses an expected power budget determined strictly by item level ($L \ge 1$) and rarity tier ($R \in \{\text{Common, Uncommon, Rare, Epic, Legendary}\}$):

$$\text{PowerBudget}(L, R) = \text{BasePower} \cdot (1 + 0.12 \cdot L) \cdot \text{RarityMultiplier}(R)$$

Where:
- $\text{RarityMultiplier}(\text{Common}) = 1.00$
- $\text{RarityMultiplier}(\text{Uncommon}) = 1.35$
- $\text{RarityMultiplier}(\text{Rare}) = 1.85$
- $\text{RarityMultiplier}(\text{Epic}) = 2.60$
- $\text{RarityMultiplier}(\text{Legendary}) = 4.00$

The actual base DPS of the weapon strictly satisfies power budget conservation within $\pm 5\%$ tolerance:
$$\text{DPS} = \text{damage\_per\_shot} \cdot \text{rounds\_per\_second} \approx \text{PowerBudget}(L, R)$$

Weapon archetypes (Pistol, Shotgun, Assault Rifle, Sniper Rifle, Heavy Cannon, Energy SMG, Plasma Blaster, Melee Blade) distribute this budget across ballistic handling parameters including magazine capacity, reload duration, spread angle, recoil pitch, effective range, and mass.

### 2.2 Elemental Synergy & Armor Vulnerability Matrix
Combat damage resolves through an element-versus-armor multiplier matrix:

$$\text{FinalDamage} = \text{RawDamage} \cdot M(\text{Element}, \text{Armor})$$

| Damage Type | Flesh | Plated Armor | Energy Shield | Cybernetic | Tactical Role |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Kinetic** | $1.00\times$ | $0.65\times$ | $0.85\times$ | $0.90\times$ | Baseline ballistic projectile |
| **Incendiary** | $1.75\times$ | $0.75\times$ | $0.75\times$ | $1.25\times$ | Anti-infantry, thermal overheating |
| **Cryo** | $1.20\times$ | $1.10\times$ | $1.00\times$ | $1.35\times$ | Embrittlement & hydraulic freeze, slow CC |
| **Shock** | $1.00\times$ | $0.70\times$ | $2.20\times$ | $1.80\times$ | Extreme shield overload & electrical arcs |
| **Corrosive** | $1.25\times$ | $2.00\times$ | $0.50\times$ | $1.50\times$ | Armor melting & chassis structural degradation |
| **Void** | $1.30\times$ | $1.30\times$ | $1.30\times$ | $1.30\times$ | Quantum distortion, flat true damage bypassing all defenses |

### 2.3 Affix Quotas & Procedural Synthesis
Affixes are partitioned into **Prefixes** (ballistic and handling modifiers), **Suffixes** (elemental affinities and status procs), and **Legendary Perks** (exclusive gameplay-altering behaviors):

- **Common**: 0 Prefixes, 0 Suffixes, 0 Perks.
- **Uncommon**: 1 Prefix, 0 Suffixes, 0 Perks.
- **Rare**: 1 Prefix, 1 Suffix, 0 Perks.
- **Epic**: 2 Prefixes, 1 Suffix, 0 Perks.
- **Legendary**: 2 Prefixes, 2 Suffixes, 1 Legendary Perk.

Stat modifiers conform to GAS standards:
- `ADD_FLAT`: $V' = V + \Delta$
- `MULTIPLY_PERCENT`: $V' = V \cdot (1 + \sum \Delta_i)$
- `OVERRIDE`: $V' = \Delta_{\text{override}}$

### 2.4 Weighted Loot Drops & Bad Luck Protection (PRD)
Loot drops roll across tiers (`TIER_1_STANDARD` through `TIER_5_VAULT`). Player Luck Score shifts probability mass towards higher rarities:

$$P'(R) = P_0(R) \cdot (1 + k_R \cdot \text{Luck})$$
where $k_{\text{Rare}} = 0.015$, $k_{\text{Epic}} = 0.030$, $k_{\text{Legendary}} = 0.050$, followed by unity normalization.

Deterministic Bad Luck Protection prevents reward drought:
- If rolls without Epic $\ge 15$: $+5\%$ per roll cumulative bonus to Epic chance.
- If rolls without Legendary $\ge 35$: $+8\%$ per roll cumulative bonus to Legendary chance.
- Counters reset immediately upon obtaining an item of that tier or higher.

### 2.5 Tension-Coupled Pacing Market & Circular Salvage
Market pricing dynamically responds to combat intensity phases evaluated by the `DynamicPacingDirector` (UAF-81.90):

$$\text{Price} = \text{BaseCost} \cdot (1 + 0.15 \cdot L)^{1.2} \cdot \text{RarityMultiplier} \cdot M_{\text{buy}}(\text{Phase})$$

- `CALM`: $1.00\times$ retail, merchant buyback $50\%$, abundant restock.
- `BUILDUP`: $1.25\times$ retail, merchant buyback $55\%$.
- `PEAK` / `SUSTAINED_PEAK`: $1.85\times - 2.10\times$ emergency wartime surcharge, merchant buyback elevated to $70\% - 80\%$.
- `COOLDOWN`: $0.80\times$ post-battle clearance discount, merchant buyback $45\%$.

**Salvage Workshop**:
Weapons deconstruct into 5 primary crafting materials: `SCRAP_METAL`, `REFINED_ALLOY`, `NANITE_CIRCUITS`, `ENERGY_CELL`, and `QUANTUM_CORE`. Materials can be spent in the workshop to reforge undesirable affixes deterministically while preserving base weapon identity.

### 2.6 Unreal Engine 5 GAS & DataTable Integration
Exports generate:
1. `DT_WeaponDefinitions.csv` & `DT_AffixCatalog.csv`: Compatible with Unreal Engine `UDataTable` import pipeline with `---` as primary row key.
2. Structured JSON manifest mapping each weapon to `FGameplayEffectSpec` with attribute modifier entries (`Attributes.Combat.WeaponDamage`, `Attributes.Combat.FireRate`, `Attributes.Combat.ReloadTime`) and hierarchical gameplay tags.
3. Autonomous editor Python script (`aoe_economy_loot_ingest.py`) for one-click ingestion into `/Game/Economy/DataTables/`.

---

## 3. ACCEPTANCE CRITERIA
- 100% deterministic weapon synthesis across all 8 archetypes.
- Strict mathematical conservation of power budgets ($\pm 5\%$).
- Complete verification of elemental damage multiplier matrix against all 4 armor types.
- Validated luck scaling and bad luck protection state machine transitions.
- Pacing market pricing fluctuations matching all 5 director phases.
- Flawless CSV and JSON DataTable formatting conforming to UE5 import rules.
- Zero regressions across the global test suite (> 8,684 tests passing at 100%).
