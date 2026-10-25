#!/usr/bin/env python3
"""
pdf_report.py

Clinical PDF incident report generator for SPARK's Gateway (Layer 2),
per proposal claim 5 ("Auto-generated clinical PDF reports") and WBS WP3.

Generates a structured, professional one-page medical incident summary
including kinematics, CNN confidence, SHAP attribution chart, and care staff
acknowledgement blocks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from gateway.receiver.wire_format import IMU_CHANNELS


@dataclass
class ReportData:
    """Flat view-model for the clinical PDF report."""

    event_id: str
    timestamp_iso: str
    severity_score: float  # 0.0 - 1.0
    cnn_confidence: float  # Layer 2 P(FALL), 0.0 - 1.0
    shap_top_feature: str
    shap_values: dict[str, float]  # channel_name -> attribution
    device_id: str = "SPARK-DEV-01"
    firmware_version: str = "v1.0.0"
    clinical_summary: str = ""
    temporal_attributions: dict[str, float] = field(default_factory=dict)


# Default dummy data for testing layout
DUMMY_EVENT = ReportData(
    event_id="EVT-20260820-001",
    timestamp_iso=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    severity_score=0.88,
    cnn_confidence=0.94,
    shap_top_feature="a_z",
    shap_values={
        "a_x": 0.08,
        "a_y": 0.12,
        "a_z": 0.52,
        "w_x": 0.06,
        "w_y": 0.14,
        "w_z": 0.08,
    },
    device_id="SPARK-NODE-01",
    firmware_version="v1.0.0-s3",
    clinical_summary="High-impact fall detected with dominant vertical acceleration spike (a_z) during impact phase.",
    temporal_attributions={"pre_impact": 0.15, "impact_spike": 0.70, "post_impact": 0.15},
)


# 60-30-10 Harmonized Palette
# 60% Canvas & Body Slate | 30% Structural Navy | 10% Gem-Toned Accents
COLOR_BODY_SLATE = colors.HexColor("#1e293b")  # Deep Charcoal Slate body text
COLOR_STRUCT_NAVY = colors.HexColor("#1b365d")  # Structural Navy (Headers, formal rules)
COLOR_MUTED_SLATE = colors.HexColor("#475569")  # Subtext, labels, captions
COLOR_TRACK_SLATE = colors.HexColor("#f1f5f9")  # Calibrated attribution track background
COLOR_BORDER_SLATE = colors.HexColor("#cbd5e1")  # Subtle divider lines
COLOR_CARD_BG = colors.HexColor("#f8fafc")  # Neutral card background

# Gem-toned accents & status tints (10%)
COLOR_ACCENT_TEAL = colors.HexColor("#0f766e")  # Base SHAP attribution bar
COLOR_PARITY_GREEN = colors.HexColor("#166534")  # Normal status badge
COLOR_ALERT_CRIMSON = colors.HexColor("#991b1b")  # Top trigger feature & Confirmed fall
COLOR_ALERT_CRIMSON_BG = colors.HexColor("#fdf2f2")  # Crimson card background
COLOR_ALERT_AMBER = colors.HexColor("#b45309")  # Warning / Diagnostic border
COLOR_ALERT_AMBER_BG = colors.HexColor("#fef9e7")  # Diagnostic disclaimer card background
COLOR_GUARD_INDIGO = colors.HexColor("#3730a3")  # System badge / telemetry
COLOR_GUARD_INDIGO_BG = colors.HexColor("#eef2ff")  # Indigo badge tint


PAGE_W, PAGE_H = A4
MARGIN = 18 * mm


def _draw_header(c: canvas.Canvas, data: ReportData) -> float:
    """Draws title banner and metadata header with 60-30-10 styling."""
    y = PAGE_H - MARGIN

    # Top brand bar (Structural Navy)
    c.setFillColor(COLOR_STRUCT_NAVY)
    c.rect(MARGIN, y - 10 * mm, PAGE_W - 2 * MARGIN, 12 * mm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(MARGIN + 5 * mm, y - 4 * mm, "SPARK Clinical Fall Incident Report")
    c.setFont("Helvetica", 8.5)
    c.drawRightString(
        PAGE_W - MARGIN - 5 * mm, y - 4 * mm, "Signal Pattern Analysis & Real-time Kinetics"
    )

    y -= 17 * mm

    # Metadata section header
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(COLOR_STRUCT_NAVY)
    c.drawString(MARGIN, y, "INCIDENT METADATA & TELEMETRY CONTRACT")
    c.setStrokeColor(COLOR_STRUCT_NAVY)
    c.setLineWidth(1.0)
    c.line(MARGIN, y - 2 * mm, PAGE_W - MARGIN, y - 2 * mm)
    y -= 6 * mm

    c.setFont("Helvetica", 8.5)
    c.setFillColor(COLOR_BODY_SLATE)
    col1_x = MARGIN
    col2_x = MARGIN + 60 * mm
    col3_x = MARGIN + 120 * mm

    c.drawString(col1_x, y, f"Event ID: {data.event_id}")
    c.drawString(col2_x, y, f"Timestamp: {data.timestamp_iso}")
    c.drawString(col3_x, y, f"Device ID: {data.device_id}")
    y -= 5 * mm

    c.drawString(col1_x, y, f"Firmware: {data.firmware_version}")
    c.drawString(col2_x, y, "Protocol: WIRE_FORMAT_v1 (BLE/Serial)")
    c.drawString(col3_x, y, "Location: Wrist Wearable Node")
    y -= 8 * mm

    return y


def _draw_detection_summary(c: canvas.Canvas, data: ReportData, y: float) -> float:
    """Draws 4-card detection summary and clinical narrative strip."""
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(COLOR_STRUCT_NAVY)
    c.drawString(MARGIN, y, "DETECTION CLASSIFICATION & OUTPUT METRICS")
    c.setStrokeColor(COLOR_STRUCT_NAVY)
    c.setLineWidth(1.0)
    c.line(MARGIN, y - 2 * mm, PAGE_W - MARGIN, y - 2 * mm)
    y -= 6.5 * mm

    # 4-Card Strip (Executive Summary structure)
    card_gap = 3 * mm
    total_w = PAGE_W - 2 * MARGIN
    box_w = (total_w - 3 * card_gap) / 4
    box_h = 16 * mm

    # Card 1: Event Status
    c.setFillColor(COLOR_ALERT_CRIMSON_BG)
    c.rect(MARGIN, y - box_h, box_w, box_h, fill=1, stroke=0)
    c.setFillColor(COLOR_ALERT_CRIMSON)
    c.rect(MARGIN, y - box_h, 2.5 * mm, box_h, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 7)
    c.drawString(MARGIN + 4 * mm, y - 4 * mm, "STATUS")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN + 4 * mm, y - 11 * mm, "CONFIRMED FALL")

    # Card 2: Layer-2 CNN Confidence
    x2 = MARGIN + box_w + card_gap
    c.setFillColor(COLOR_CARD_BG)
    c.rect(x2, y - box_h, box_w, box_h, fill=1, stroke=0)
    c.setFillColor(COLOR_STRUCT_NAVY)
    c.rect(x2, y - box_h, 2.5 * mm, box_h, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(COLOR_MUTED_SLATE)
    c.drawString(x2 + 4 * mm, y - 4 * mm, "L2 CONFIDENCE")
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(COLOR_STRUCT_NAVY)
    c.drawString(x2 + 4 * mm, y - 11 * mm, f"{data.cnn_confidence:.1%}")

    # Card 3: Impact Severity Score
    x3 = x2 + box_w + card_gap
    c.setFillColor(COLOR_CARD_BG)
    c.rect(x3, y - box_h, box_w, box_h, fill=1, stroke=0)
    c.setFillColor(COLOR_MUTED_SLATE)
    c.rect(x3, y - box_h, 2.5 * mm, box_h, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 7)
    c.drawString(x3 + 4 * mm, y - 4 * mm, "IMPACT SEVERITY")
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(COLOR_BODY_SLATE)
    c.drawString(x3 + 4 * mm, y - 11 * mm, f"{data.severity_score:.2f} / 1.00")

    # Card 4: Top Contributing Trigger
    x4 = x3 + box_w + card_gap
    c.setFillColor(COLOR_GUARD_INDIGO_BG)
    c.rect(x4, y - box_h, box_w, box_h, fill=1, stroke=0)
    c.setFillColor(COLOR_GUARD_INDIGO)
    c.rect(x4, y - box_h, 2.5 * mm, box_h, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 7)
    c.drawString(x4 + 4 * mm, y - 4 * mm, "TOP TRIGGER")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x4 + 4 * mm, y - 11 * mm, f"{data.shap_top_feature.upper()} AXIS")

    y -= box_h + 6 * mm

    # Narrative Summary Card
    if data.clinical_summary:
        card_h = 11 * mm
        c.setFillColor(COLOR_CARD_BG)
        c.setStrokeColor(COLOR_BORDER_SLATE)
        c.setLineWidth(0.5)
        c.rect(MARGIN, y - card_h, PAGE_W - 2 * MARGIN, card_h, fill=1, stroke=1)
        c.setFillColor(COLOR_BODY_SLATE)
        c.setFont("Helvetica-Oblique", 8.5)
        c.drawString(MARGIN + 3 * mm, y - 4 * mm, f"Clinical Analysis: {data.clinical_summary}")
        y -= card_h + 6 * mm

    return y


def _draw_shap_chart(c: canvas.Canvas, data: ReportData, y: float) -> float:
    """Draws horizontal SHAP feature attribution bar chart with calibrated track styling."""
    c.setFillColor(COLOR_STRUCT_NAVY)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(MARGIN, y, "SHAP EXPLAINABILITY ATTRIBUTION (IMU KINEMATICS)")
    c.setStrokeColor(COLOR_STRUCT_NAVY)
    c.setLineWidth(1.0)
    c.line(MARGIN, y - 2 * mm, PAGE_W - MARGIN, y - 2 * mm)
    y -= 5 * mm

    c.setFont("Helvetica-Oblique", 7.5)
    c.setFillColor(COLOR_MUTED_SLATE)
    c.drawString(
        MARGIN,
        y,
        "Additive feature attributions normalized across 6 IMU channels. Highlights dominant shock and rotation axes.",
    )
    y -= 5.5 * mm

    axis_labels = {
        "a_x": "Lateral Acceleration (a_x)",
        "a_y": "Longitudinal Acceleration (a_y)",
        "a_z": "Vertical Impact Acceleration (a_z)",
        "w_x": "Roll Angular Velocity (w_x)",
        "w_y": "Pitch Angular Velocity (w_y)",
        "w_z": "Yaw Angular Velocity (w_z)",
    }

    chart_left = MARGIN + 58 * mm
    chart_width = PAGE_W - MARGIN - chart_left - 24 * mm
    bar_height = 4.2 * mm
    bar_gap = 2.4 * mm
    max_val = max(data.shap_values.values(), default=1.0) or 1.0

    c.setFont("Helvetica", 7.5)
    for ch in IMU_CHANNELS:
        val = data.shap_values.get(ch, 0.0)
        label = axis_labels.get(ch, ch)
        frac = (abs(val) / max_val) if max_val > 0 else 0.0
        bar_w = frac * chart_width

        # Axis label (right-aligned in muted slate)
        c.setFillColor(COLOR_MUTED_SLATE)
        c.drawRightString(chart_left - 3 * mm, y + 0.8 * mm, label)

        # Background track rectangle (#f1f5f9 track styling)
        c.setFillColor(COLOR_TRACK_SLATE)
        c.rect(chart_left, y, chart_width, bar_height, fill=1, stroke=0)

        # Proportional attribution fill bar
        if ch == data.shap_top_feature:
            bar_color = COLOR_ALERT_CRIMSON  # Primary trigger in crimson
        else:
            bar_color = COLOR_ACCENT_TEAL  # Standard attribution in teal

        c.setFillColor(bar_color)
        c.rect(chart_left, y, max(bar_w, 0.8), bar_height, fill=1, stroke=0)

        # Formatted percentage & absolute score label
        c.setFillColor(COLOR_BODY_SLATE)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(chart_left + chart_width + 2 * mm, y + 0.8 * mm, f"{val * 100:.1f}%")
        c.setFont("Helvetica", 7.5)

        y -= bar_height + bar_gap

    y -= 3 * mm

    # Diagnostic Disclaimer Box
    disclaimer_h = 13 * mm
    c.setFillColor(COLOR_ALERT_AMBER_BG)
    c.rect(MARGIN, y - disclaimer_h, PAGE_W - 2 * MARGIN, disclaimer_h, fill=1, stroke=0)
    c.setFillColor(COLOR_ALERT_AMBER)
    c.rect(MARGIN, y - disclaimer_h, 2.5 * mm, disclaimer_h, fill=1, stroke=0)

    c.setFont("Helvetica-Bold", 7.5)
    c.setFillColor(COLOR_ALERT_AMBER)
    c.drawString(
        MARGIN + 4 * mm, y - 3.8 * mm, "Diagnostic Kinematic Saliency Notice (Local Attribution):"
    )

    c.setFont("Helvetica", 7)
    c.setFillColor(COLOR_BODY_SLATE)
    c.drawString(
        MARGIN + 4 * mm,
        y - 7.5 * mm,
        "Attributions quantify empirical kinematic contributions to Layer-2 CNN confidence. They identify dominant shock axes",
    )
    c.drawString(
        MARGIN + 4 * mm,
        y - 11.0 * mm,
        "rather than standalone causality. Must be evaluated alongside patient vitals and direct clinical observation.",
    )

    y -= disclaimer_h + 6 * mm
    return y


def _draw_signature_block(c: canvas.Canvas, y: float) -> None:
    """Draws care staff acknowledgement and signoff block."""
    c.setFillColor(COLOR_STRUCT_NAVY)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(MARGIN, y, "CLINICAL / CAREGIVER ACKNOWLEDGEMENT")
    c.setStrokeColor(COLOR_STRUCT_NAVY)
    c.setLineWidth(1.0)
    c.line(MARGIN, y - 2 * mm, PAGE_W - MARGIN, y - 2 * mm)
    y -= 9 * mm

    c.setFont("Helvetica", 8)
    c.setFillColor(COLOR_BODY_SLATE)
    c.drawString(
        MARGIN, y, "Reviewing Clinician / Caregiver Name: ________________________________"
    )
    c.drawString(MARGIN + 105 * mm, y, "Review Date: ___________________")
    y -= 7 * mm
    c.drawString(
        MARGIN,
        y,
        "Triage Action: [  ] Assistance Provided   [  ] False Alarm   [  ] Hospital Escalation",
    )
    y -= 7 * mm
    c.drawString(MARGIN, y, "Clinician Signature: _________________________________")


def generate_report(data: ReportData, output_path: str | Path) -> str:
    """
    Renders a clinical one-page PDF report to output_path.
    Returns the resolved output path as a string.
    """
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(out_file), pagesize=A4)
    y = _draw_header(c, data)
    y = _draw_detection_summary(c, data, y)
    y = _draw_shap_chart(c, data, y)
    _draw_signature_block(c, y)

    c.showPage()
    c.save()
    return str(out_file)


if __name__ == "__main__":
    out = generate_report(DUMMY_EVENT, "data/gateway_events/sample_report.pdf")
    print(f"Sample report generated at {out}")
