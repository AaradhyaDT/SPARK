# AGENTS.md — Universal Guidelines

See [`AGENT.md`](AGENT.md) for master architecture rules, non-negotiable hardware/firmware constraints, and module ownership.

## Evidence and Experiment Discipline

Apply this lightweight evidence standard to project decisions, reports, issue updates, and completion claims. The master architecture and ownership remain in `AGENT.md`.

- **Label claims by evidence:** proposed (idea or render), specified (documented design), implemented (inspectable implementation), locally checked (named software check), or physically measured (identified hardware and procedure). Record dataset-based results as benchmark observations with the dataset, split, model, and run identity. Evidence status belongs to each claim, not the whole project.
- **Match checks to claims:** syntax, tests, simulations, and CI support only what they exercise. A render does not demonstrate fit; model embedding does not demonstrate target inference; offline accuracy does not demonstrate wearable or clinical performance. Independent reproducibility alone does not establish production readiness.
- **Keep concise experiment records:** before hardware or ML experiments, record the question/hypothesis, setup and versions, baseline, procedure, planned acceptance criteria, and evaluation split where applicable. Afterwards retain raw evidence or its durable path/hash, results, uncertainty, failures, and limitations. Link records to the owning issue and project tracker; use the existing documentation structure rather than introducing a parallel tracking system.
- **Preserve measurement context:** hardware logs identify board/sensor variants, firmware, placement/axes, units, timestamps, sampling quality, power measurement point, and synchronization method as relevant. Enclosure checks record component measurements, print/material settings, tested garment/attachment combinations, retention, and observed movement.
- **Protect evaluation:** tune preprocessing, thresholds, and adaptation using development data only. Keep evaluation subjects separate, record sample sizes and relevant uncertainty, and report misses and false alarms. Wrist-to-waist transfer is a hypothesis until the defined comparison supports it. Volunteer recording requires validated acquisition and required institutional approval.
- **Close work with direct evidence:** link the artifact or run that meets each acceptance criterion. Keep unresolved blockers and untested assumptions open. Reconcile contradictory status descriptions against owning source and measured evidence before repeating a completion claim.

Current priorities are measured component packaging, reliable dual-node acquisition and synchronization, real embedded inference, and integrated evaluation. Custom attachment mechanisms and product styling should support these milestones. Use brainstorm's evidence policy as methodological reference; SPARK records must stand on their own evidence and contain no private tooling context.

### Quick Command Reference
```bash
# Python tests and linting
uv run pytest
uv run ruff check --fix
uv run ruff format

# Repository synchronization
.\sync.ps1 -m "feat(scope): message"
.\sync.ps1 -Build           # compile thesis PDF first, then sync
```
