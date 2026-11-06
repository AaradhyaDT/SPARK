# SPARK Enclosure Architecture Iterations — Fit and Comfort

**Status:** Preferred concept direction refined; still exploratory and not selected for CAD.
**Date:** 2026-11-06  
**Baseline:** DI-03, canonical 270° C-shell reference.  
**Priority:** Wearability, fit adjustment, low wrist profile, and stable dorsal IMU orientation.

> This is a concept brief, not a validated mechanical specification. No physical fit, component clearance, printability, comfort, attachment retention, or market performance has been demonstrated. Keep DI-03 canonical until a design is explicitly selected and reconciled with measured hardware.

## Preferred Product Direction — Shared Core, Placement-Specific Modules

## College Major Project Feasibility and Plan in Progress

**Status: Plan in progress (2026-11-06).** The shared core, wrist-to-forearm harness, waist reference node, serviceable enclosure, and belt/waistband adapters are considered feasible goals for an engineering-college prototype. This is a scope assessment, not a guarantee of completion or commercial readiness. Physical realization depends on measured parts, firmware bring-up, printing access, and team time.

The session produced architecture exploration, BOM grounding, a product-presentation iteration, and a hidden-issue iteration. Their images and decisions are recorded below. Those documentation and visual tasks are complete; fabrication and experimental validation remain pending. DI-03 remains canonical.

- [x] Record shared-core arm and waist concepts with separate local IMUs.
- [x] Produce product presentation and hidden-issue visual studies.
- [x] Record BOM inputs and open battery allocation/dimension questions.
- [ ] Reconcile received hardware and measure components before CAD packaging.
- [ ] Bring up two reliable, timestamped acquisition nodes; measure sampling quality and synchronization error.
- [ ] Build a serviceable enclosure family with stable arm and belt attachments.
- [ ] Evaluate waistband compatibility on a defined garment set; record retention, rotation, comfort, and fabric marking.
- [ ] Measure runtime and integrated detector performance; preserve evaluation provenance and uncertainty.
- [ ] Conduct data collection only after logger validation and required institutional approval.
- [ ] Compare wrist and waist performance, then evaluate one bounded adaptation/translation approach using separate development and evaluation data.

**Scope priorities:** The core deliverable is functioning acquisition/detection hardware and measured placement evaluation. A custom quick-release latch is a stretch feature; start with simple mechanically retained attachment prototypes. The refined appearance remains a design goal, while actual printed finish and size follow fabrication results. Garment compatibility means tested combinations, not every garment.

**Research boundary:** Recording both placements does not prove that wrist and waist signals or trained detectors transfer between them. Generalizable translation is a separate research experiment. Current `firmware/main/tflite/inference.cpp` contains stub inference bodies at the time of this assessment; embedded inference and integration remain substantive work. Repository verification checks validate their stated software/documentation checks, not physical fit or safety.

The intended project claim is: build two wearable nodes, measure their operation, and evaluate how sensor placement affects fall detection. A commercial sales claim or clinical validation claim requires additional evidence.

### Preferred architecture

Concepts 2 and 3 are the preferred direction for the next design iteration. Use one uniform electronics-core design, reproduced in each active node, with a common keyed mechanical dock. Keep the IMU local to its intended body placement: a dorsal wrist sensor pod for arm use and its own waist-mounted IMU for waist use. The arm node places the common electronics core in the forearm pod and links it to the wrist IMU with a protected flexible bridge. The waist node contains a copy of the same core beside its waist IMU. This supports paired wrist/waist collection; it does not imply the signals are interchangeable.

For the waist node, develop two removable adapters that engage the same core dock: (1) a belt loop/dock for the BOM's nylon belt and (2) a beltless waistband clip for common trousers or skirts. The clip must retain the module and preserve its orientation without pins, stitching, holes, or permanent garment changes. “Universal” here means the two specified everyday waist attachment modes; compatibility across all garment materials and thicknesses is not assumed. Set fit range after representative garment checks.

**Product-design intent:** a recognizable shared core, clean rounded exterior, low-profile wrist sensor pod, simple one-handed wrist closure, serviceable electronics lid, and swappable waist adapters. These are design goals for a polished market-facing product, not substantiated usability or sales claims.

## Product Presentation Iteration — 2026-11-06

The requested single product-appeal iteration is shown in [`enclosure_product_pitch_iteration_v1.png`](enclosure_product_pitch_iteration_v1.png). Its presentation line is **“A considered fit. A shared core.”** The same rounded graphite core appears in the arm, belt, and beltless waistband views, with a smaller matching wrist sensor pod. The earlier architecture board remains available for engineering context.

| Design element | Product iteration decision |
|---|---|
| Core form | Elongated rounded pebble with a shallow domed face, matte TPU finish, discreet SPARK marking, and a perimeter service seam. Retain volume for the existing development board and power modules; no smaller custom PCB is assumed. |
| Service access | Move M2.5 screw/captive-nut access to the reverse, leaving a clean front. Removal from the dock exposes service access; screws and nuts require clearance checks. |
| Arm fit | Small dorsal wrist IMU pod and larger forearm core on independent hook-and-loop straps, with a graspable wrist pull tab and compression sleeve underneath. |
| Cable handling | Route the silicone signal harness in a removable rounded TPU guide close to the sleeve, with end strain relief and a wrist service loop. Check freedom of movement and snagging on a physical mockup. |
| Waist adapters | Match the rounded core with a wide belt-loop carrier and broad waistband-clip carrier, both engaging the common keyed dock with a guarded release. Clip stiffness, release force, and retention remain prototype questions. |
| Visual identity | Subtle debossed branding and a small amber light aperture. The light is a presentation cue using the BOM LED option; its position, visibility, power, and firmware behavior remain to be specified. |

Use the same core shell and interior layout in both nodes, reserving a local IMU seat for waist use and a serviceable harness exit for the arm node. Explore a replaceable exit insert/cap to accommodate these two assemblies without changing the exterior core design. Maintain access to the actual charging/programming connectors and switch during packaging review; off-body charging remains required.

This iteration provides a product form and pitch visual. It does not establish manufacturability, validated dimensions, latch geometry, customer demand, or sales performance. Evaluate appeal with representative users alongside physical fit and attachment trials before describing the design as a finished commercial product.

## Hidden-Issue Iteration — 2026-11-06

[`enclosure_hidden_issues_iteration_v2.png`](enclosure_hidden_issues_iteration_v2.png) explores a protected service panel with separately identified programming and charging openings, strain relief at both harness ends, wide waist-adapter support, a guarded dock release, and a serviceable common core. These are proposed features, not evidence of fit, retention, thermal performance, or electrical safety. The wrist IMU receives power through the harness.

- **Packaging and power:** Measure the received board, connectors, cell, protection/charger, boost converter, switch, and harness before placing pockets or service ports. Preserve non-compressive battery retention and assess charger heat and access with the real parts. Charging remains off-body.
- **Radio:** Locate the actual ESP32-S3 antenna before arranging battery, hardware, and dock. Espressif recommends sufficient clearance within the finished housing and end-product range/throughput checks ([ESP32-S3 hardware design guidelines](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html)). The rendering's dashed antenna zone is illustrative and its position is not an engineering layout.
- **Retention and measurement:** Prototype the belt and waistband carriers on representative garments, testing retention, rotation, fabric marking, release, and sensor orientation through walking, sitting, and donning. Confirm independent wrist and waist IMU locations and record their axes and synchronization.
- **Assembly and service:** Check the flex guide and strain relief over wrist movement, prevent pinching at the lid, and prototype a guarded release and service fasteners. Validate connector clearances and distinct port identification using the actual modules.

The illustrated component layout, ports, clip, latch, and shell are conceptual; no dimensions, interfaces, electrical interlocks, or fit are verified by the render. Keep DI-03 canonical until the team selects a validated direction.

## Concepts

### DI-03 — Continuous 270° C-shell (baseline)

One continuous open-back TPU shell carries the wrist IMU island, flexible wiring spine, and forearm electronics bay. Its single shell and strap closure are relatively simple to wear and assemble, but a fit adjustment at one region can affect pressure and rotation at another. The current design reference gives nominal geometry; it does not establish fit across users.

### ALT-A — Preferred arm configuration: dual cuff with common core

An adjustable dorsal wrist cuff holds the local MPU6050 IMU; a separate forearm pod houses a copy of the common electronics core. A narrow, rounded flexible bridge protects the wire run and has strain relief at both ends. The wrist cuff and forearm pod are retained independently so the sensor position can be adjusted without tightening the heavier core pod.

**Fit hypothesis:** Independent adjustment may reduce wrist pressure and let the IMU cuff resist rotation without tightening the heavier forearm section.  
**Tradeoff to assess:** The bridge and two closures add parts and setup steps; bridge flex, snagging, and cable fatigue require evaluation.

### ALT-B — Arm fit variant: broad conformal contact wings

Retain the shared-core arm architecture from ALT-A. Broaden and round the shell contact wings, with removable segmented sleeve-facing pads to explore pressure distribution and accommodate contour differences. The IMU remains fixed to the dorsal wrist cuff; the core remains on the forearm.

**Fit hypothesis:** Broader supported contact and replaceable pads may reduce edge pressure and improve fit over a compression sleeve.  
**Tradeoff to assess:** Added bulk, heat retention, moisture management, cleaning, and pad retention; the wider wings must not obstruct wrist motion.

### ALT-C — Preferred waist configuration: common core with universal waist adapters

Use the same electronics-core enclosure design as the arm node, reproduced as a separate waist node with its own locally mounted MPU6050. A common keyed dock on the core accepts either the nylon-belt adapter or beltless waistband clip. Use positive retention and anti-rotation registration so normal movement is less likely to change module orientation; these properties require fit and motion testing. No garment modification is intended. If data are collected simultaneously, define synchronization and device identity in the study protocol; if collected in separate sessions, preserve placement metadata and protocol comparability.

**Fit hypothesis:** A waist module can remove electronics and sensor mass from the arm in waist-mode trials, while the wrist module preserves the current placement for comparison data.  
**Tradeoff to assess:** The waist and wrist are distinct sensing locations with different motion signatures. Translation between them is a research objective to test, not an assumed equivalence; placement-specific data collection, calibration, synchronization, and evaluation will be needed.

## First comparison

| Criterion | DI-03 baseline | ALT-A | ALT-B |
|---|---|---|---|
| Independent wrist/forearm adjustment | Low | High | High |
| Potential for low wrist profile | Medium | High | Medium |
| Pressure distribution | Continuous shell contact | Narrow cuff contact | Broad padded contact |
| Parts and donning complexity | Lowest | Medium | Highest |
| Main fit risk | Local edge pressure or shell rotation | Bridge pull and cuff migration | Heat, moisture, pad movement, added bulk |

ALT-C is a waist placement using the same repeated core design; its belt-loop and waistband-clip adapters share the core dock. Compare it separately for attachment retention, orientation stability, setup, garment compatibility, synchronization, and the feasibility of wrist-to-waist signal translation.

These are qualitative design hypotheses, not measured results or rankings.

## Shared constraints and unresolved inputs

- Keep the IMU dorsal and mechanically stable; keep the heavier battery and MCU proximal on the forearm.
- Preserve off-body charging and distinct programming/charging access. Confirm the actual TP4056 connector and ESP32-S3 board port, buttons, antenna, camera-FPC keepout, and mounting geometry before fixing interfaces.
- Resolve the ESP32-S3 supply path before designing around battery and converter volumes. TP4056 cell output is not a regulated 5 V rail.
- Use one common keyed core dock for both waist adapters; keep the adapters mechanically separate from the electronics core so each can be evaluated or replaced independently. Provide a local waist IMU as well as the local wrist IMU. Keep charging access off-body.
- Check the beltless clip on representative beltless waistbands for secure retention, orientation, comfort, fabric marking, and release. Do not claim broad garment compatibility before those checks; do not assume a single clip geometry fits all garments.
- Record wrist and waist as distinct sensor placements in firmware/configuration and study metadata. For paired or simultaneous captures, define timestamp alignment, device identity, orientation convention, and placement-specific calibration; do not assume the signals are interchangeable.
- Measure the actual boards, battery, sleeve-covered wrist and forearm circumferences, and desired hand/wrist motion range. Existing reference dimensions are provisional packaging inputs.
- Treat TPU hardness, bridge wall geometry, closure method, and pad material as test variables. Do not carry forward conflicting boss/insert, wall-thickness, or slicer prescriptions from older task guides without checking them against the selected concept and current fabrication process.

## Suggested next iteration

1. Gather hardware caliper measurements and sleeve-on limb circumferences at wrist and forearm cuff locations.
2. Create dimensioned mockups for ALT-A and ALT-B around the repeated core envelope, local wrist IMU, bridge, and sleeve; mock up ALT-C with its local waist IMU, common dock, nylon-belt adapter, and beltless waistband clip.
3. Compare comfort and migration during donning, wrist flexion/extension, pronation/supination, ordinary arm movement, walking, sitting, and garment changes. Record pressure, slippage, bridge/cable tension, module retention/orientation, fabric marking, and setup difficulty.
4. Define a paired data-collection protocol for wrist and waist placements, including simultaneous/separate capture choice, synchronization, orientation, and placement metadata; evaluate translation empirically.
5. Select a mechanical concept only after comparing fit and placement evidence; then update the canonical design reference and derive CAD dimensions.

## Visual concepts

- **Current product presentation:** [`enclosure_product_pitch_iteration_v1.png`](enclosure_product_pitch_iteration_v1.png).
- **Earlier architecture board:** [`enclosure_shared_core_arm_waist_adapters.png`](enclosure_shared_core_arm_waist_adapters.png).

Both are illustrative and should not be treated as dimensioned designs or fit evidence.

## BOM grounding (canonical order form, v64 tracker)

The concept board uses the current BOM's material and component families: TPU 95A shell, M2.5 machine screws with hex nuts, nylon waist belt with buckle, hook-and-loop wrist straps, and compression arm sleeves. Electronics shown are based on the ESP32-S3 dev board, MPU6050, 3.7 V 1100 mAh LiPo, TP4056 protected charging module, separate 5 V boost converter, slide switch, and flexible 30 AWG silicone signal wire. Use dedicated wrist and waist IMUs in the two-placement concept.

The tracker describes a planned two-active-node setup (wrist and waist) plus a spare chain; these are planned procurement quantities, not evidence of physical receipt. The order form lists 3 IMUs and 3 ESP32 boards but only 2 LiPo cells. Battery/module allocation for the spare is not established by those quantities. The BOM also says the LiPo dimensions and connector remain to be confirmed. Resolve these details against received hardware before CAD packaging. Do not infer exact internal geometry from the illustrative component render.
