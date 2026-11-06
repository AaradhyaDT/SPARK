# SPARK Enclosure Architecture Iterations — Fit and Comfort

**Status:** Exploratory concept round; no architecture selected.  
**Date:** 2026-11-06  
**Baseline:** DI-03, canonical 270° C-shell reference.  
**Priority:** Wearability, fit adjustment, low wrist profile, and stable dorsal IMU orientation.

> This is a concept brief, not a validated mechanical specification. No physical fit, component clearance, printability, or comfort has been demonstrated. Keep DI-03 canonical until a design is explicitly selected and reconciled with the measured hardware.

## Concepts

### DI-03 — Continuous 270° C-shell (baseline)

One continuous open-back TPU shell carries the wrist IMU island, flexible wiring spine, and forearm electronics bay. Its single shell and strap closure are relatively simple to wear and assemble, but a fit adjustment at one region can affect pressure and rotation at another. The current design reference gives nominal geometry; it does not establish fit across users.

### ALT-A — Dual cuff with a low-profile flex bridge

Separate adjustable open cuffs position the IMU at the dorsal wrist and the electronics bay proximally on the forearm. A narrow, rounded TPU bridge protects the wire run and flexes between independently retained cuffs. Each cuff adjusts separately, so the sensor can remain snug while the forearm pod fit changes. Keep the bridge free of rigid electronics and provide strain relief at both ends.

**Fit hypothesis:** Independent adjustment may reduce wrist pressure and let the IMU cuff resist rotation without tightening the heavier forearm section.  
**Tradeoff to assess:** The bridge and two closures add parts and setup steps; bridge flex, snagging, and cable fatigue require evaluation.

### ALT-B — Dual cuff with broad conformal contact wings

Retain the independent wrist and forearm cuffs and flexible bridge from ALT-A. Broaden and round the shell contact wings, with removable segmented sleeve-facing pads to spread local pressure and accommodate small contour differences. The IMU remains fixed to the dorsal wrist cuff; the battery and electronics remain on the forearm cuff.

**Fit hypothesis:** Broader supported contact and replaceable pads may reduce edge pressure and improve fit over a compression sleeve.  
**Tradeoff to assess:** Added bulk, heat retention, moisture management, cleaning, and pad retention; the wider wings must not obstruct wrist motion.

### ALT-C — Dual-placement IMU platform with waist and wrist modules

Support both a dorsal wrist-worn IMU module and a waist-worn IMU module so the team can collect data at both body locations and investigate translating between wrist-collected and waist-collected signals. The waist configuration must include its own IMU mounted to the waist module; it is not a waist battery/MCU pod tethered to the wrist sensor. Keep the sensing modules mechanically location-specific, while exploring a common electronics core, battery arrangement, and serviceable attachment interface where practical. If data are collected simultaneously, define synchronization and device identity in the study protocol; if collected in separate sessions, preserve placement metadata and protocol comparability.

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

ALT-C is a dual-placement platform rather than a direct cuff-shape competitor. Compare it separately for arm load, belt stability, module attachment, placement-specific setup, synchronization, and the feasibility of wrist-to-waist signal translation.

These are qualitative design hypotheses, not measured results or rankings.

## Shared constraints and unresolved inputs

- Keep the IMU dorsal and mechanically stable; keep the heavier battery and MCU proximal on the forearm.
- Preserve off-body charging and distinct programming/charging access. Confirm the actual TP4056 connector and ESP32-S3 board port, buttons, antenna, camera-FPC keepout, and mounting geometry before fixing interfaces.
- Resolve the ESP32-S3 supply path before designing around battery and converter volumes. TP4056 cell output is not a regulated 5 V rail.
- For ALT-C, provide a waist-mounted IMU in addition to the wrist IMU. Make each sensor attachment keyed and positively retained so its orientation is repeatable. Keep charging access off-body.
- Record wrist and waist as distinct sensor placements in firmware/configuration and study metadata. For paired or simultaneous captures, define timestamp alignment, device identity, orientation convention, and placement-specific calibration; do not assume the signals are interchangeable.
- Measure the actual boards, battery, sleeve-covered wrist and forearm circumferences, and desired hand/wrist motion range. Existing reference dimensions are provisional packaging inputs.
- Treat TPU hardness, bridge wall geometry, closure method, and pad material as test variables. Do not carry forward conflicting boss/insert, wall-thickness, or slicer prescriptions from older task guides without checking them against the selected concept and current fabrication process.

## Suggested next iteration

1. Gather hardware caliper measurements and sleeve-on limb circumferences at wrist and forearm cuff locations.
2. Create a dimensioned fit mockup for DI-03 and ALT-A/ALT-B using the same component envelopes, IMU position, strap width, and sleeve; mock up ALT-C's wrist module and waist-belt module, each with an IMU.
3. Compare comfort and migration during donning, wrist flexion/extension, pronation/supination, ordinary arm movement, and belt movement. Record pressure, slippage, bridge/cable tension, module retention, and setup difficulty.
4. Define a paired data-collection protocol for wrist and waist placements, including simultaneous/separate capture choice, synchronization, orientation, and placement metadata; evaluate translation empirically.
5. Select a mechanical concept only after comparing fit and placement evidence; then update the canonical design reference and derive CAD dimensions.

## Visual concepts

The generated concept board is present in the conversation only; it is illustrative and should not be treated as a dimensioned design or fit evidence.

## BOM grounding (canonical order form, v64 tracker)

The concept board uses the current BOM's material and component families: TPU 95A shell, M2.5 machine screws with hex nuts, nylon waist belt with buckle, hook-and-loop wrist straps, and compression arm sleeves. Electronics shown are based on the ESP32-S3 dev board, MPU6050, 3.7 V 1100 mAh LiPo, TP4056 protected charging module, separate 5 V boost converter, slide switch, and flexible 30 AWG silicone signal wire. Use dedicated wrist and waist IMUs in the two-placement concept.

The tracker describes a planned two-active-node setup (wrist and waist) plus a spare chain; these are planned procurement quantities, not evidence of physical receipt. The order form lists 3 IMUs and 3 ESP32 boards but only 2 LiPo cells. Battery/module allocation for the spare is not established by those quantities. The BOM also says the LiPo dimensions and connector remain to be confirmed. Resolve these details against received hardware before CAD packaging. Do not infer exact internal geometry from the illustrative component render.
