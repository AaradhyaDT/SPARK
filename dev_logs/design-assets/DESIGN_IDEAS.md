# SPARK — Design Ideas Log

Exploratory design concepts, external render outputs, and aesthetic direction notes.
**Not implementation-locked.** Cross-reference `SPARK_TRACKER.md` Action #8 (enclosure form factor) for the resolved engineering decision this log feeds into.

---

## DI-01 — Bracer-Silhouette Enclosure, Two-Zone Internal Layout

- **Status:** Exploratory concept. Not adopted into BOM/CAD.
- **Date logged:** 2026-08-06
- **Asset:** `dev_logs/design-assets/enclosure_concept_v1_two_zone_bracer.png`
- **Source:** AI image concept render (external tool, prompt-engineered manually; not generated in-repo).

**Concept summary:**
Single-piece open-back forearm enclosure, silhouette inspired by a bracer/vambrace (reference used for form only — explicitly not for leather/Viking/medieval material or ornamentation). Wraps ~70–75% of forearm circumference, 25–30% continuous open seam along the underside for flex/ventilation/weight. Matte charcoal TPU, soft-touch micro-texture. Single wide Velcro strap closure (senior-friendly, one-handed) bridging the seam near the wrist — no buckles/rivets/lacing. USB-C port with flexible TPU dust cover + hidden status LED.

**Internal layout — two-zone architecture** (supersedes an earlier single-cavity packaging draft in the same prompt-engineering session):
- **Zone 1 (wrist, slim):** MPU6050 IMU only (~15×20×3 mm), flat against inner shell wall, dorsal/top-of-wrist position — motion-sensing reference point.
- **Zone 2 (forearm/elbow, wide):** ESP32-S3-WROOM-1 dev board (~25×50×7 mm), 1000 mAh LiPo (~32×52×7 mm), TP4056 charge/protect PCB (~15×17×2 mm). Widest cross-section of the shell lives here; USB-C access at this end.
- **Connecting spine:** thin bridge between zones, wiring only, no rigid components.
- Rationale: keeps wrist joint low-profile for daily wear/hand movement; pushes mass up the forearm, away from the wrist.

**Renders produced (6 panels):** hero (worn, annotated), isolated product (3/4 view), Velcro detail, USB-C port detail, internal two-zone cutaway, profile/side silhouette.

**Verification notes against prompt spec:**
- All 4 required renders present, plus 2 additional (internal cutaway, profile) — not requested but consistent with the stated requirement that renders show the zone width differential.
- Zone labeling correctly split (IMU/wrist vs. ESP32+battery+charge/forearm) per spec, rather than one combined callout.
- Negative-prompt compliance clean: no rivets, lacing, medieval styling, exposed screws.
- Minor deviation: shell finish reads slightly glossier/more specular than the specified matte TPU soft-touch in panels 2 and 4 (profile/product views) — cosmetic only, no dimensional or structural conflict.

**Open questions carried forward:**
- This is an aesthetic/form direction only — no dimensional validation against Action #8's locked wrist-worn/dorsal placement, no fit-check against WP 3.0 enclosure work (Sankalpa).
- Single-cavity packaging variant (from the same prompt session, pre-two-zone) was explored but not rendered/adopted — two-zone is the carried-forward direction.
---

## DI-02 — Master Composite Design Sheet (Two-Zone Ergonomic Dorsal Bracer)

- **Status:** Canonical Design Concept & CAD Blueprint Reference.
- **Date logged:** 2026-08-20
- **Asset:** [`dev_logs/design-assets/SPARK_Two_Zone_Bracer_Design_Concept_v2.jpg`](file:///D:/Aaradhya-Dev-Tamrakar/SPARK/dev_logs/design-assets/SPARK_Two_Zone_Bracer_Design_Concept_v2.jpg)
- **Visuals Included:**
  1. **Hero Render (Panel 1)**: Dorsal forearm wearable worn over compression sleeve, demonstrating $75\%$ wrap geometry, $25\text{–}30\%$ continuous open ventilation seam, matte soft-touch TPU 95A finish, and ergonomic wrist curvature.
  2. **Product Render (Panel 2)**: Single-piece ergonomic shell with seamless inner curvature and senior-friendly Velcro anchor slot.
  3. **Closure Detail (Panel 3)**: Wide hook-and-loop Velcro strap with recessed, flush anchors for skin safety.
  4. **Charging Port Detail (Panel 4)**: USB-C port with flexible hinged TPU dust/splash cover and hidden status LED indicator.
  5. **Internal Two-Zone Layout (Panel 5)**:
     - **Zone 1 (Slim Wrist Zone)**: Dedicated MPU6050 IMU bay ($\approx 15 \times 20 \times 3\text{ mm}$) anchored directly over the dorsal wrist reference.
     - **Connecting Spine**: Flexible wiring bridge routing 4-conductor I2C harness without rigid components.
     - **Zone 2 (Forearm Bay)**: Main electronics housing ESP32-S3 Dev Board ($\approx 25 \times 50 \times 7\text{ mm}$), $1000\text{–}1100\text{ mAh}$ LiPo battery ($\approx 32 \times 52 \times 7\text{ mm}$), and TP4056 charge/protect module ($\approx 15 \times 17 \times 2\text{ mm}$).
  6. **Side Profile View (Panel 6)**: Tapered elevation showing ultra-slim wrist clearance and elevated electronics chamber.

---

## DI-03 — Canonical 270° C-Shell Enclosure (Merged ChatGPT + Gemini)

- **Status:** **Canonical Engineering Reference** — supersedes DI-01 and DI-02.
- **Date logged:** 2026-08-22
- **Primary asset:** [`dev_logs/design-assets/SPARK_270deg_C_Shell_Design_DI03.md`](file:///D:/Aaradhya-Dev-Tamrakar/SPARK/dev_logs/design-assets/SPARK_270deg_C_Shell_Design_DI03.md)
- **Render assets:**
  - [`enclosure_concept_v2_gemini_270deg.jpg`](file:///D:/Aaradhya-Dev-Tamrakar/SPARK/dev_logs/design-assets/enclosure_concept_v2_gemini_270deg.jpg) — Gemini exploded/assembly render
  - [`enclosure_concept_v2_chatgpt_270deg.jpg`](file:///D:/Aaradhya-Dev-Tamrakar/SPARK/dev_logs/design-assets/enclosure_concept_v2_chatgpt_270deg.jpg) — ChatGPT orthographic design sheet
- **Source:** Parallel ChatGPT + Gemini design explorations from the same engineering prompt, best elements merged and validated against Track 10 DFM research.

**Concept summary:**
270° C-shaped cross-section (NOT full wraparound bracer). Three-quarter forearm coverage with 90° open ventral gap bridged by a single wide Velcro strap. Three-part mechanical architecture: main C-shell + removable Zone 2 dorsal lid + replaceable proximal USB port insert.

**Key design decisions resolved:**
- **Zone 1 IMU mounting:** Friction-fit pocket with 0.2–0.4 mm interference ribs — no screws (too thin for bosses per Track 10).
- **Zone 2 component layout:** Lateral distribution using 270° arc width, not vertical stacking, to minimize profile height.
- **Screw bosses:** 4–6× M2.5 in Zone 2 only. 9 mm OD, 6–7 mm blind standoff. Heat-set insert contingency designed in.
- **USB panel:** Replaceable modular insert (two versions: dual USB-C or USB-C + Micro-USB) resolving TP4056 connector TBD.
- **LED visibility:** Locally thinned TPU (3.5 → 0.8 mm) as diffuser — no separate light pipe.
- **Print orientation:** Vertical (Z-axis along forearm axis), support-free design with 45° chamfers.

**Updated cost estimate (3.5 mm walls):** ~70–75 cm³, ~85–91 g, NPR 360–400 (8–11 hr print). Previous 18.5 cm³ / NPR 90 estimate invalidated.

**Open blockers before Fusion 360:**
1.  ESP32-S3 power input path (TP4056 outputs raw 3.0–4.2V, not regulated 5V).
---

## DI-04 — Slotted Modular Enclosure Concept (Interlocking / Rail-Slotted Architecture)

- **Status:** Exploratory Design Idea / Architecture Variant.
- **Date logged:** 2026-08-22
- **Concept summary:**
  Explores a **slotted / rail-interlocking modular system** for the 270° C-shell assembly. Instead of relying solely on top-down screw fastening and static single-body chassis geometry:
  1. **Slotted Sub-Module Trays:** Individual sliding trays / snap-in sleds for Zone 1 (IMU carrier sled), Zone 2 (battery + MCU carrier sled), and proximal interface ports that slide into dovetailed or T-slotted longitudinal guide rails along the inner C-shell arc.
  2. **Benefits for Fabrication & Assembly:**
     - Modular maintenance: Replace or upgrade the sensor sled (e.g. testing alternative IMUs) or battery bay without reprinting the entire 145 mm forearm shell.
     - Screw elimination / reduction: Sliding interlocks reduce the count of M2.5 screw bosses required in flexible TPU 95A, bypassing thread-stripping risks.
     - Rapid iteration: Independent calibration of tolerance fits on smaller test coupons rather than large 8–11 hr full-body prints.
  3. **CAD & DFM Considerations:**
     - Requires careful clearance modeling in Fusion 360 ($\approx 0.3\text{–}0.5\text{ mm}$ sliding tolerance in TPU 95A / PETG hybrid).
     - Potential dual-material hybrid (rigid PETG sleds running in flexible TPU 95A C-shell channels).

---

## DI-05 — Wrist/Forearm Fit Variants and Waist IMU Reference Module

- **Status:** Preferred concept direction refined for next iteration; still exploratory, not selected for CAD, and not fit validated.
- **Date logged:** 2026-11-06
- **Detailed concept brief:** [`ENCLOSURE_ARCHITECTURE_ITERATIONS_FIT_COMFORT.md`](ENCLOSURE_ARCHITECTURE_ITERATIONS_FIT_COMFORT.md)
- **Visual concept board:** [`enclosure_shared_core_arm_waist_adapters.png`](enclosure_shared_core_arm_waist_adapters.png) — shared electronics core, local wrist/waist IMUs, arm bridge, and two waist adapter options.
- **Product presentation iteration:** [`enclosure_product_pitch_iteration_v1.png`](enclosure_product_pitch_iteration_v1.png) — one refinement toward a coherent consumer product: rounded graphite core, matching wrist pod, concealed reverse service fasteners, sleeve-following cable guide, and matching belt/waistband carriers.
- **Baseline:** DI-03 remains the canonical engineering reference.

**Concepts compared:**
- **DI-03 baseline:** Continuous 270° TPU C-shell with dorsal wrist sensor zone and forearm electronics bay.
- **ALT-A (preferred arm configuration):** Adjustable dorsal wrist cuff with local MPU6050 IMU; protected flexible bridge to a forearm pod containing a copy of the common electronics core.
- **ALT-B (arm fit variant):** Same shared-core arm architecture with broader rounded sleeve-contact wings and removable pads for fit exploration.
- **ALT-C (preferred waist configuration):** Separate waist node containing a copy of the same core and its own local MPU6050. A common keyed dock accepts either a nylon-belt adapter or a beltless waistband clip. The intended garment modes do not imply fit across every garment.

**Uniform core and product direction:** Use one electronics-core enclosure/interface design reproduced in the wrist/arm and waist nodes, with placement-specific IMUs and mechanically distinct attachments. Pairing supports wrist/waist data collection; it does not establish signal equivalence. Design intent is a coherent, rounded, serviceable product with a low-profile wrist sensor, simple arm closure, and interchangeable waist attachments. These are product-design goals, not validated usability or sales claims.

**Product iteration decisions:** Keep the existing BOM electronics and TPU 95A/M2.5 construction; use a clean pebble-shaped face and reverse-access fasteners, a removable cable guide with wrist service loop, and a guarded release on the common dock. Reserve core space for the waist IMU and a serviceable arm-harness exit/cap. The amber light in the pitch render is a visual cue whose LED placement and firmware behavior require specification. The presentation is intended to communicate product desirability; customer demand, garment retention, component fit, and manufacturability remain unverified.

**BOM grounding:** The concepts reflect the current order form's TPU 95A filament, M2.5 machine screws and hex nuts, nylon waist belt with buckle, hook-and-loop wrist straps, compression arm sleeves, ESP32-S3 development boards, MPU6050 modules, 3.7 V 1100 mAh LiPo cells, TP4056 protected charging modules, 5 V boost converters, slide switches, and flexible 30 AWG silicone signal wire. These are planned BOM quantities, not confirmation of receipt.

**Open packaging inputs:** The order form lists three ESP32-S3 boards and three MPU6050 modules but two LiPo cells, while the tracker describes two active nodes plus a spare chain. Spare-node battery allocation needs reconciliation. LiPo dimensions and connector are also unconfirmed. Measure received parts before freezing enclosure dimensions or ports.

**Waist adapter constraint:** Belt-loop/dock plus beltless waistband clip, both removable and engaging the same keyed core interface without permanent garment changes. Clip compatibility, retention, orientation, comfort, and fabric marking remain to be checked on representative garments; do not assert a universal thickness range before testing.

**Design boundary:** This entry records form-factor exploration only. It does not supersede DI-03, alter the BOM, validate comfort or attachment compatibility, establish wrist-to-waist signal translation, or claim CAD, printing, or physical testing.

---

