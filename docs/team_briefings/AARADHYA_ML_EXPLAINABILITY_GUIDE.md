# SPARK — Aaradhya's Machine Learning, Explainability & Systems Guide

**Author:** Aaradhya Dev Tamrakar (Project Lead & Systems Architect / BEI)  
**Created:** October 25, 2026  
**Document Version:** 1.0  
**Associated GitHub Issues:** [Issue #10](https://github.com/Aaradhya-Dev-Tamrakar/SPARK/issues/10), [Issue #12](https://github.com/Aaradhya-Dev-Tamrakar/SPARK/issues/12), [Issue #13](https://github.com/Aaradhya-Dev-Tamrakar/SPARK/issues/13)

---

## 1. Subsystem Architecture & Philosophy

The intelligence architecture of SPARK rests on three non-negotiable principles:
1. **Asymmetric Cognitive Allocation:** The edge wearable node (`firmware/`) performs strict, deterministically budgeted forward inference ($18.5\text{ KB}$ INT8 ConvNet). The host laptop gateway (`gateway/`) handles computationally heavy, floating-point feature attributions (SHAP) and clinical dossier compilation.
2. **Zero-Cloud Autonomy:** All model inference, BLE telemetry acquisition, feature attribution, and PDF compilation execute locally on air-gapped hardware.
3. **Clinical Transparency:** Machine learning predictions are accompanied by empirical sensor attributions across all 6 kinematic degrees of freedom ($a_x, a_y, a_z, \omega_x, \omega_y, \omega_z$), calibrated confidence intervals, and dynamic plain-language narrative synthesis.

---

## 2. Work Breakdown & Task Checklist

### Phase 1: Machine Learning & TinyML Edge Forge (Status: 100% Verified)
- [x] **SisFall Dataset Processing (`training/prepare_sisfall.py`):**
  - Ingested 4,500 raw trial files across 38 subjects (15 elderly, 23 young adults).
  - Implemented 200 Hz → 100 Hz decimation and $200 \times 6$ temporal window extraction (2.0s duration).
  - Partitioned dataset into subject-grouped splits (zero data leakage across training, validation, and test splits).
- [x] **1D ConvNet Architecture & Training (`training/train_cnn.py`):**
  - Architecture: Conv1D ($k=5, 32$ filters) $\to$ BatchNorm $\to$ ReLU $\to$ Conv1D ($k=3, 64$ filters) $\to$ GlobalAveragePooling1D $\to$ Dense(32) $\to$ Dense(1, sigmoid).
  - Achieved $87.81\%$ tuned sensitivity and $0.9185$ AUC-ROC.
  - Calibrated safety-critical decision threshold using Youden's $J$ statistic.
- [x] **Full INT8 Quantization (`training/quantize_model.py`):**
  - TensorFlow Lite full integer quantization using representative calibration dataset.
  - Quantized FlatBuffer size: **18.5 KB** (satisfies $<120\text{ KB}$ flash limit with $84.6\%$ headroom).
  - Automated 16-byte aligned C header export (`firmware/main/models/spark_cnn_int8.h`).
- [x] **Transfer Learning Scaffold (`training/train_transfer.py`):**
  - Implemented Partial-Freeze Fine-Tuning pipeline for upcoming KEC Nepal cohort adaptation.

---

### Phase 2: Gateway Daemon & Clinical Reporting (Status: 100% Verified)
- [x] **Asynchronous Ingestion Daemon (`gateway/receiver/receiver.py`):**
  - Implemented `BleReceiver` using `bleak` for BLE GATT notifications.
  - Added `SerialReceiver` for USB-Serial bench testing and `ReplayReceiver` for deterministic simulation.
- [x] **FastAPI REST Server (`gateway/server.py`):**
  - Zero-heavy-dependency endpoints: `/api/health`, `/api/events`, `/api/events/{id}`, `/api/reports/{id}`, `/api/reports/{id}.html`.
- [x] **Clinical Report Generator (`gateway/report/html_report.py`):**
  - 60-30-10 palette (`#1e293b`, `#1b365d`, `#0f766e`, `#991b1b`, `#b45309`, `#f1f5f9`).
  - LaTeX Computer Modern / Latin Modern Roman serif typography.
  - 4-card executive output strip with dynamic 4-pillar narrative synthesis.
  - Inline SVG confidence whiskers and full-track horizontal SHAP attribution bars.
  - Diagnostic Kinematic Saliency notice and clinician sign-off block.
- [x] **Headless Blink PDF Exporter (`gateway/report/pdf_exporter.py`):**
  - Native Edge/Chrome discovery with `--headless=new --print-to-pdf` compilation.
  - Re-routed `gateway/report/pdf_report.py` to compile crisp vector PDFs directly from HTML.
  - Batch generated all 22 event dossiers in `data/gateway_events/`.

---

### Phase 3: Quantitative SHAP Evaluation & Defense Figures ([Issue #12](https://github.com/Aaradhya-Dev-Tamrakar/SPARK/issues/12)) — *ACTIVE TASK*
- [ ] **Develop `training/evaluate_shap.py`:**
  - Build evaluation script loading trained model weights (`training/models/spark_cnn.keras`) and test impact windows.
  - Compute gradient-weighted feature attribution ($X \times \nabla_X Y$) and KernelExplainer attributions across all 6 IMU channels.
- [ ] **Comparative Biomechanical Analysis:**
  - Compare true falls (lateral slip, forward trip, vertical collapse) against challenging false-alarm ADLs (stumbling, brisk sitting, bed flop).
  - Quantify sensor channel relative dominance: Accelerometer ($a_x, a_y, a_z$) vs. Gyroscope ($\omega_x, \omega_y, \omega_z$).
- [ ] **Export Publication-Grade Defense Figures:**
  - Save publication figures into [`docs/SPARK_Final_Defense/Figures/`](../SPARK_Final_Defense/Figures/).
  - Ensure figures are styled for LaTeX inclusion (`\includegraphics`).

---

### Phase 4: Academic Thesis & Faculty Defense Alignment ([Issue #10](https://github.com/Aaradhya-Dev-Tamrakar/SPARK/issues/10), [#13](https://github.com/Aaradhya-Dev-Tamrakar/SPARK/issues/13))
- [ ] **Update Evaluation Section (`docs/SPARK_Final_Defense/Chapters/chapter5_results.tex`):**
  - Incorporate empirical test set confusion matrix ($87.81\%$ sensitivity).
  - Document INT8 quantization accuracy delta vs. FP32 baseline ($<1.5\%$ degradation).
- [ ] **Thesis Roadmap & Defense Slide Preparation:**
  - Align LaTeX defense roadmap with next-semester procurement and hardware bring-up schedule.
  - Maintain reproducible CPM DAG build pipeline (`.\sync.ps1 -Build`).

---

## 3. Verification Commands Reference

```bash
# Run full test suite (73 automated unit tests)
uv run pytest

# Check and fix code linting
uv run ruff check --fix

# Verify code formatting
uv run ruff format --check

# Run deterministic verification script
python scripts/verify.py

# Re-generate all clinical incident dossiers
uv run python scripts/regenerate_reports.py

# Synchronize repository across remotes
.\sync.bat -m "feat(scope): concise description (#issue)"
```
