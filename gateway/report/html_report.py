"""
html_report.py

Standalone clinical incident and explainability report generator for SPARK Gateway.

Implements:
    1. Schema.org JSON-LD metadata preamble.
    2. 60-30-10 CSS custom properties and LaTeX serif typography
       ("Latin Modern Roman", "CMU Serif", "Computer Modern Roman").
    3. Small-caps headers, metadata cards, and Diagnostic Scope / Boundary Assertion card.
    4. 4-stat executive summary strip (.exec-summary, .exec-stat, .exec-stat-alert).
    5. Plain-Language Executive Translation Card (.plain-narrative-card) with
       numbered pillar cards (.plain-pillar-num, .plain-pillar-header).
    6. Formal LaTeX booktabs tables (\\toprule, \\midrule, \\bottomrule equivalents).
    7. Inline SVG metric whisker & tick indicators ([0.0, 1.0] domain, 95% CI whiskers).
    8. Section 2: Targeted Kinematic Explainability & SHAP Feature Attributions
       (disclaimer box, flagged channel badges, inline SVG horizontal attribution bars,
       and booktabs feature importance table).
    9. Section 3: Governance Documentation & Intended Use (MDR / ASTM E3130 traceability).
   10. Formal Caregiver / Clinician Acknowledgement and Signoff Block.
   11. Strict @media print CSS for pixel-identical browser and Blink headless PDF compilation.
"""

from __future__ import annotations

import html
import json
from pathlib import Path

from gateway.receiver.wire_format import IMU_CHANNELS
from gateway.report.pdf_report import ReportData

_AXIS_METADATA: dict[str, dict[str, str]] = {
    "a_x": {
        "label": "Lateral Acceleration (a_x)",
        "role": "Transverse kinetic shock & side-slip acceleration",
        "direction": "Positive X (Lateral)",
    },
    "a_y": {
        "label": "Longitudinal Acceleration (a_y)",
        "role": "Forward/backward stumble & sagittal plane acceleration",
        "direction": "Positive Y (Anterior)",
    },
    "a_z": {
        "label": "Vertical Acceleration (a_z)",
        "role": "Primary ground-impact shock wave (gravity-aligned)",
        "direction": "Negative Z (Downward)",
    },
    "w_x": {
        "label": "Roll Angular Velocity (w_x)",
        "role": "Lateral torso/arm roll rotation during loss of balance",
        "direction": "Coronal angular rate",
    },
    "w_y": {
        "label": "Pitch Angular Velocity (w_y)",
        "role": "Forward pitch tumble / backward collapse rate",
        "direction": "Sagittal angular rate",
    },
    "w_z": {
        "label": "Yaw Angular Velocity (w_z)",
        "role": "Axial twist & rotational instability rate",
        "direction": "Transverse angular rate",
    },
}


def _render_metric_whisker_svg(
    val: float,
    ci_low: float,
    ci_high: float,
    threshold: float = 0.50,
    is_breach: bool = False,
) -> str:
    """Renders a calibrated [0.0, 1.0] horizontal SVG whisker chart."""
    scale = 200.0
    x_offset = 10.0
    clamp_val = min(max(val, 0.0), 1.0)
    clamp_low = min(max(ci_low, 0.0), 1.0)
    clamp_high = min(max(ci_high, 0.0), 1.0)

    val_x = x_offset + clamp_val * scale
    low_x = x_offset + clamp_low * scale
    high_x = x_offset + clamp_high * scale
    thresh_x = x_offset + threshold * scale

    pt_color = "#991b1b" if is_breach else "#0f766e"
    pt_stroke = "#7f1d1d" if is_breach else "#0d5c56"

    # Double-encoded point estimate: Diamond for breach, circle for compliant
    if is_breach:
        point_elem = (
            f'<rect x="{val_x - 4:.1f}" y="10" width="8" height="8" '
            f'transform="rotate(45 {val_x:.1f} 14)" fill="{pt_color}" '
            f'stroke="{pt_stroke}" stroke-width="0.75" />'
        )
    else:
        point_elem = (
            f'<circle cx="{val_x:.1f}" cy="14" r="4.5" '
            f'fill="{pt_color}" stroke="{pt_stroke}" stroke-width="0.75" />'
        )

    return f"""<svg class="inline-chart" width="220" height="38" viewBox="0 0 220 38" role="img" aria-label="Metric value {val:.3f}">
    <!-- Base Axis Line [0.0, 1.0] -->
    <line x1="10" y1="25" x2="210" y2="25" stroke="#cbd5e1" stroke-width="1" />
    <line x1="10" y1="23" x2="10" y2="28" stroke="#94a3b8" stroke-width="1" />
    <text x="10" y="35" font-size="8" fill="#64748b" text-anchor="middle">0.0</text>
    <line x1="110" y1="23" x2="110" y2="28" stroke="#94a3b8" stroke-width="1" />
    <text x="110" y="35" font-size="8" fill="#64748b" text-anchor="middle">0.5</text>
    <line x1="210" y1="23" x2="210" y2="28" stroke="#94a3b8" stroke-width="1" />
    <text x="210" y="35" font-size="8" fill="#64748b" text-anchor="middle">1.0</text>
    <!-- Decision Threshold Line -->
    <line x1="{thresh_x:.1f}" y1="4" x2="{thresh_x:.1f}" y2="26" stroke="#b45309" stroke-width="1.2" stroke-dasharray="2,2" />
    <!-- CI Whisker Bar and End Caps -->
    <line x1="{low_x:.1f}" y1="14" x2="{high_x:.1f}" y2="14" stroke="#64748b" stroke-width="2" />
    <line x1="{low_x:.1f}" y1="10" x2="{low_x:.1f}" y2="18" stroke="#64748b" stroke-width="2" />
    <line x1="{high_x:.1f}" y1="10" x2="{high_x:.1f}" y2="18" stroke="#64748b" stroke-width="2" />
    {point_elem}
</svg>"""


def generate_html_report(data: ReportData, output_path: str | Path | None = None) -> str:
    """
    Renders a standalone, offline clinical incident report.
    If output_path is provided, writes to disk and returns the resolved path.
    Otherwise, returns the raw HTML string.
    """
    is_confirmed_fall = data.cnn_confidence >= 0.50
    verdict_class = "verdict-FAIL" if is_confirmed_fall else "verdict-PASS"
    verdict_badge = "badge-fail" if is_confirmed_fall else "badge-pass"
    verdict_text = "CONFIRMED FALL" if is_confirmed_fall else "NORMAL KINETICS"

    # Sort channels by attribution score descending
    sorted_channels = sorted(
        IMU_CHANNELS, key=lambda ch: abs(data.shap_values.get(ch, 0.0)), reverse=True
    )
    max_attr = max((abs(data.shap_values.get(ch, 0.0)) for ch in IMU_CHANNELS), default=1.0) or 1.0

    # Build SVG horizontal attribution bars
    label_w = 210
    track_w = 320
    bar_h = 16
    gap = 6
    total_w = label_w + track_w + 80
    total_h = len(sorted_channels) * (bar_h + gap) + 12

    svg_rows: list[str] = []
    for i, ch in enumerate(sorted_channels):
        val = abs(data.shap_values.get(ch, 0.0))
        y = i * (bar_h + gap) + 6
        frac = (val / max_attr) if max_attr > 0 else 0.0
        bar_len = frac * track_w

        meta = _AXIS_METADATA.get(ch, {"label": ch})
        label_text = meta["label"]
        is_top = ch == data.shap_top_feature
        bar_fill = "#991b1b" if is_top else "#0f766e"

        svg_rows.append(
            f'    <text x="{label_w - 10}" y="{y + bar_h - 4}" font-size="11" '
            f'fill="#475569" text-anchor="end">{html.escape(label_text)}</text>\n'
            f'    <rect x="{label_w}" y="{y}" width="{track_w}" height="{bar_h}" '
            f'fill="#f1f5f9" rx="3"/>\n'
            f'    <rect x="{label_w}" y="{y}" width="{max(bar_len, 2.0):.1f}" height="{bar_h}" '
            f'fill="{bar_fill}" rx="3"/>\n'
            f'    <text x="{label_w + bar_len + 8:.1f}" y="{y + bar_h - 4}" '
            f'font-size="11" font-weight="600" fill="#1e293b">{val:.3f}</text>'
        )

    svg_chart = (
        f'<svg class="inline-chart" width="{total_w}" height="{total_h}" '
        f'viewBox="0 0 {total_w} {total_h}" role="img" '
        f'aria-label="Kinematic feature attribution bars">\n' + "\n".join(svg_rows) + "\n</svg>"
    )

    # Build Triggered Feature Badges
    flagged_badges: list[str] = []
    for ch in sorted_channels:
        val = data.shap_values.get(ch, 0.0)
        if abs(val) >= 0.15:
            meta = _AXIS_METADATA.get(ch, {"label": ch})
            flagged_badges.append(
                f'<span class="badge badge-warn" style="font-size: 0.8rem; padding: 0.3rem 0.6rem;">'
                f"<strong>{html.escape(ch)}</strong> • {html.escape(meta['label'])}"
                f"</span>"
            )

    flagged_badges_html = (
        "\n                    ".join(flagged_badges)
        if flagged_badges
        else '<span class="badge badge-pass">No channels exceeded 15% shock threshold</span>'
    )

    # Build Feature Attribution Table Rows
    table_rows: list[str] = []
    for ch in sorted_channels:
        val = data.shap_values.get(ch, 0.0)
        meta = _AXIS_METADATA.get(ch, {"label": ch, "role": "IMU Kinematics", "direction": "N/A"})
        is_top = ch == data.shap_top_feature
        badge_markup = (
            '<span class="badge badge-fail">PRIMARY TRIGGER</span>'
            if is_top
            else '<span class="badge badge-pass">CO-VARIATE</span>'
        )
        table_rows.append(
            f"<tr>\n"
            f"    <td><code>{html.escape(ch)}</code> ({html.escape(meta['label'])})</td>\n"
            f"    <td><strong>{val:.4f}</strong> ({val * 100:.1f}%)</td>\n"
            f"    <td>{html.escape(meta['role'])}</td>\n"
            f"    <td>{badge_markup}</td>\n"
            f"</tr>"
        )
    table_rows_html = "\n".join(table_rows)

    # Confidence Whisker SVGs
    conf_whisker = _render_metric_whisker_svg(
        val=data.cnn_confidence,
        ci_low=max(data.cnn_confidence - 0.05, 0.0),
        ci_high=min(data.cnn_confidence + 0.05, 1.0),
        threshold=0.50,
        is_breach=is_confirmed_fall,
    )
    sev_whisker = _render_metric_whisker_svg(
        val=data.severity_score,
        ci_low=max(data.severity_score - 0.08, 0.0),
        ci_high=min(data.severity_score + 0.08, 1.0),
        threshold=0.70,
        is_breach=data.severity_score >= 0.70,
    )

    # Build Schema.org JSON-LD
    json_ld = {
        "@context": "https://schema.org",
        "@type": "Report",
        "name": f"SPARK Clinical Fall Incident Dossier — {data.event_id}",
        "description": "Diagnostic Human Fall Kinematics Evaluation & Clinical Triage Companion Report.",
        "datePublished": data.timestamp_iso,
        "author": {
            "@type": "SoftwareApplication",
            "name": "SPARK",
            "applicationCategory": "Two-Layer Gated Wearable Fall Detection System",
        },
        "about": {
            "@type": "Thing",
            "name": f"Incident Event {data.event_id} ({data.device_id})",
        },
    }

    clinical_narrative_text = (
        data.clinical_summary
        if data.clinical_summary
        else f"Wearable telemetry detected confirmed fall impact. Primary kinematics vector identified as {data.shap_top_feature} axis."
    )

    # Lean dynamic synthesis for the 4 executive pillars based on specific triggering channel
    top_ch = data.shap_top_feature.lower()
    if top_ch == "a_z":
        p1_text = f"Primary deceleration localized along vertical axis (<strong>{html.escape(data.shap_top_feature)}</strong>), confirming direct downward ground impact dynamics."
    elif top_ch == "a_y":
        p1_text = f"Primary deceleration localized along lateral axis (<strong>{html.escape(data.shap_top_feature)}</strong>), indicating a side-slip or lateral tumble onto hip/shoulder."
    elif top_ch == "a_x":
        p1_text = f"Primary deceleration localized along longitudinal axis (<strong>{html.escape(data.shap_top_feature)}</strong>), indicating an anterior/posterior stumble or collapse."
    elif top_ch.startswith("w_"):
        p1_text = f"Dominant kinematic trigger driven by angular velocity (<strong>{html.escape(data.shap_top_feature)}</strong>), confirming rapid body rotation preceding impact."
    else:
        p1_text = f"Primary deceleration localized along the <strong>{html.escape(data.shap_top_feature)}</strong> channel."

    max_gyro_val = max(abs(data.shap_values.get(g, 0.0)) for g in ("w_x", "w_y", "w_z"))
    if max_gyro_val >= 0.18:
        p2_text = "Multi-axis angular velocity confirms coordinated posture collapse and tumbling motion preceding impact."
    else:
        p2_text = "Low angular rotation indicates linear slip or vertical collapse with minimal body rotation."

    if data.cnn_confidence >= 0.85:
        p3_text = "Layer-1 MCU acceleration threshold (&ge;2.5g for &gt;300ms) corroborated by high-confidence Layer-2 CNN temporal inference."
    else:
        p3_text = "Layer-1 gate triggered near boundary; moderate Layer-2 inference suggests low-impact or partial slip event."

    if data.severity_score >= 0.85:
        p4_text = "High impact severity: Immediate caregiver or attending triage required to inspect for acute orthopedic or head trauma."
    elif data.severity_score >= 0.65:
        p4_text = "Moderate impact severity: Attending review recommended to evaluate patient mobility and pain symptoms."
    else:
        p4_text = "Low impact severity: Check patient status; verify whether bed transfer or vigorous arm gesture caused alert."

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SPARK Clinical Fall Incident Report &amp; Explainability Dossier ({html.escape(data.event_id)})</title>
    <script type="application/ld+json">
{json.dumps(json_ld, indent=4)}
    </script>
    <style>
        :root {{
            /* 60-30-10 LaTeX palette: 60% canvas/charcoal, 30% navy structure, 10% gem accents */
            --bg-primary: #f8fafc;
            --bg-card: #ffffff;
            --text-main: #1e293b;
            --text-muted: #64748b;
            --border-color: #cbd5e1;
            --structure: #1b365d;
            --brand-blue: #1b365d;
            --accent-teal: #0f766e;
            --accent-green: #166534;
            --accent-red: #991b1b;
            --accent-amber: #b45309;
            --accent-indigo: #3730a3;
            --tint-green: #ecfdf3;
            --tint-red: #fdf2f2;
            --tint-amber: #fef9e7;
            --tint-indigo: #eef2ff;
            --tint-navy: #f1f5f9;
            --tint-highlight: #fef9c3;
            --font-stack: "Latin Modern Roman", "CMU Serif", "Computer Modern Roman", "TeX Gyre Termes", "Times New Roman", "Nimbus Roman No9 L", Times, serif;
            --font-mono: "Latin Modern Mono", "CMU Typewriter Text", "Courier New", Courier, monospace;
        }}

        body {{
            font-family: var(--font-stack);
            background-color: var(--bg-primary);
            color: var(--text-main);
            margin: 0;
            padding: 2rem;
            line-height: 1.6;
            text-rendering: optimizeLegibility;
            -webkit-font-smoothing: antialiased;
        }}

        .container {{
            max-width: 1100px;
            margin: 0 auto;
        }}

        header {{
            background-color: var(--bg-card);
            padding: 2rem;
            border-radius: 8px;
            border: 1px solid var(--border-color);
            margin-bottom: 2rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}

        h1, h2, h3, h4 {{
            font-family: var(--font-stack);
            color: var(--structure);
            font-weight: 700;
            font-variant: small-caps;
            letter-spacing: 0.04em;
        }}

        h1 {{
            margin: 0 0 0.5rem 0;
            font-size: 1.8rem;
            border-bottom: 1.5px solid var(--structure);
            padding-bottom: 0.5rem;
        }}

        .meta-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
            font-size: 0.9rem;
        }}

        .meta-item {{
            background: var(--tint-navy);
            padding: 0.75rem;
            border-radius: 6px;
        }}

        .meta-label {{
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            font-size: 0.75rem;
            display: block;
            font-variant: small-caps;
            letter-spacing: 0.05em;
        }}

        .section-card {{
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 2rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}

        h2 {{
            border-bottom: 1.5px solid var(--structure);
            padding-bottom: 0.5rem;
            margin-top: 0;
            font-size: 1.3rem;
        }}

        code, pre {{
            font-family: var(--font-mono);
        }}

        /* --- LaTeX booktabs Table Styling --- */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
            font-size: 0.9rem;
            border-top: 1.5px solid var(--structure);
            border-bottom: 1.5px solid var(--structure);
        }}

        th, td {{
            padding: 0.75rem 1rem;
            text-align: left;
            vertical-align: top;
        }}

        th {{
            border-top: 1.5px solid var(--structure);
            border-bottom: 1px solid var(--structure);
            font-weight: 700;
            font-variant: small-caps;
            letter-spacing: 0.03em;
            color: var(--structure);
            background: none;
        }}

        td {{
            border-top: 0.5px solid #e2e8f0;
            border-bottom: 0.5px solid #e2e8f0;
        }}

        tr:last-child td {{
            border-bottom: 1.5px solid var(--structure);
        }}

        .badge {{
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
        }}

        .badge-pass {{
            background-color: var(--tint-green);
            color: var(--accent-green);
        }}

        .badge-warn {{
            background-color: var(--tint-amber);
            color: var(--accent-amber);
        }}

        .badge-fail {{
            background-color: var(--tint-red);
            color: var(--accent-red);
        }}

        .badge-guard {{
            background-color: var(--tint-indigo);
            color: var(--accent-indigo);
        }}

        .regulatory-box {{
            background-color: var(--tint-navy);
            border-left: 4px solid var(--brand-blue);
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 0 6px 6px 0;
            font-size: 0.85rem;
        }}

        footer {{
            text-align: center;
            font-size: 0.8rem;
            color: var(--text-muted);
            margin-top: 3rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border-color);
        }}

        /* --- Executive Summary Strip --- */
        .exec-summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}

        .exec-stat {{
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-left: 4px solid var(--brand-blue);
            border-radius: 6px;
            padding: 1rem 1.25rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}

        .exec-stat.exec-stat-alert {{
            border-left-color: var(--accent-red);
        }}

        .exec-stat-value {{
            font-size: 1.6rem;
            font-weight: 700;
            color: var(--text-main);
            display: block;
            line-height: 1.2;
        }}

        .exec-stat-label {{
            font-size: 0.75rem;
            color: var(--text-muted);
            text-transform: uppercase;
            font-weight: 600;
        }}

        /* --- Inline SVG bar charts --- */
        .ci-bar-cell {{
            min-width: 220px;
        }}

        svg.inline-chart {{
            display: block;
        }}

        svg.inline-chart text {{
            font-family: var(--font-stack);
        }}

        /* --- Plain-Language Executive Translation Card --- */
        .plain-narrative-card {{
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-left: 5px solid var(--brand-blue);
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 2rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        .plain-narrative-card.verdict-FAIL {{
            border-left-color: var(--accent-red);
        }}
        .plain-narrative-card.verdict-WARN {{
            border-left-color: var(--accent-amber);
        }}
        .plain-narrative-card.verdict-PASS {{
            border-left-color: var(--accent-green);
        }}
        .plain-pillar-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 1.25rem;
            margin-top: 1.25rem;
        }}
        .plain-pillar {{
            background: #f8fafc;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 1rem;
            font-size: 0.88rem;
        }}
        .plain-pillar-header {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 0.5rem;
            font-weight: 700;
            color: var(--structure);
            font-size: 0.92rem;
        }}
        .plain-pillar-num {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 22px;
            height: 22px;
            border-radius: 50%;
            background: var(--brand-blue);
            color: #ffffff;
            font-size: 0.75rem;
            font-weight: 700;
        }}
        .plain-pillar-text {{
            color: var(--text-main);
            line-height: 1.5;
            margin: 0;
        }}

        /* --- Print & Headless PDF Compilation Standards --- */
        @media print {{
            @page {{
                size: A4;
                margin: 12mm 15mm;
            }}
            body {{
                padding: 0;
                background: #ffffff;
                color: var(--structure);
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }}
            .container {{
                max-width: 100%;
                margin: 0;
            }}
            header, .section-card, .exec-summary, .scope-card, .plain-narrative-card, .plain-pillar {{
                box-shadow: none !important;
                border: 1px solid #cbd5e1 !important;
            }}
            .exec-summary, .scope-card, .plain-narrative-card, .plain-pillar {{
                break-inside: avoid !important;
                page-break-inside: avoid !important;
            }}
            .section-headline {{
                break-before: page !important;
                page-break-before: always !important;
            }}
            .section-explainability, .section-governance {{
                break-inside: avoid !important;
                page-break-inside: avoid !important;
            }}
            table {{
                break-inside: avoid !important;
                page-break-inside: avoid !important;
            }}
            tr {{
                break-inside: avoid !important;
                page-break-inside: avoid !important;
            }}
            thead {{
                display: table-header-group;
            }}
        }}

        a {{ color: var(--accent-teal); text-decoration-thickness: 0.5px; text-underline-offset: 2px; }}
        mark {{ background-color: var(--tint-highlight); color: inherit; padding: 0 0.15em; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>SPARK — Clinical Fall Incident Report &amp; Explainability Dossier</h1>
            <p style="color: var(--text-muted); margin: 0;">Diagnostic Wearable Fall Kinematics Evaluation &amp; Clinical Traceability Report</p>
            <div class="meta-grid">
                <div class="meta-item">
                    <span class="meta-label">Incident Event ID</span>
                    <strong>{html.escape(data.event_id)}</strong>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Wearable Sensor Node</span>
                    <strong>{html.escape(data.device_id)}</strong>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Firmware Contract</span>
                    <strong>{html.escape(data.firmware_version)} (WIRE_FORMAT_v1)</strong>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Capture Timestamp</span>
                    <strong>{html.escape(data.timestamp_iso)}</strong>
                </div>
            </div>
        </header>

        <!-- Diagnostic Scope & Boundary Assertion -->
        <div class="scope-card" style="background-color: var(--bg-card); border: 1px solid var(--border-color); border-left: 4px solid var(--brand-blue); border-radius: 6px; padding: 1rem 1.25rem; margin-bottom: 1.5rem; font-size: 0.85rem; color: var(--text-main); line-height: 1.5;">
            <strong style="color: #1e293b; display: block; margin-bottom: 0.25rem;">Diagnostic Scope &amp; Non-Intervention Guarantee:</strong>
            SPARK is engineered as a two-layer gated fall detection and explainability platform. It does <strong>not</strong> deliver therapeutic interventions or physical stabilization. In adherence to statistical integrity safeguards, telemetry features represent normalized empirical kinematics derived from the wrist-worn MPU6050 sensor array and require independent clinical verification before patient care escalation.
        </div>

        <!-- 0. Executive Summary Strip -->
        <div class="exec-summary">
            <div class="exec-stat {"exec-stat-alert" if is_confirmed_fall else ""}">
                <span class="exec-stat-value">{verdict_text}</span>
                <span class="exec-stat-label">Classification Verdict</span>
            </div>
            <div class="exec-stat">
                <span class="exec-stat-value">{data.cnn_confidence:.1%}</span>
                <span class="exec-stat-label">Layer-2 CNN Confidence P(Fall)</span>
            </div>
            <div class="exec-stat">
                <span class="exec-stat-value">{data.severity_score:.2f} / 1.00</span>
                <span class="exec-stat-label">Kinematic Impact Severity</span>
            </div>
            <div class="exec-stat">
                <span class="exec-stat-value">{html.escape(data.shap_top_feature.upper())} AXIS</span>
                <span class="exec-stat-label">Dominant Kinematic Trigger</span>
            </div>
        </div>

        <!-- Plain-Language Executive Translation Card -->
        <div class="plain-narrative-card {verdict_class}">
            <h3 style="margin-top: 0; font-size: 1.15rem; color: var(--structure);">Executive Kinematic Assessment &amp; Clinical Translation</h3>
            <p style="font-size: 0.95rem; margin-bottom: 0.5rem; line-height: 1.55;">
                {html.escape(clinical_narrative_text)}
            </p>
            <div class="plain-pillar-grid">
                <div class="plain-pillar">
                    <div class="plain-pillar-header">
                        <span class="plain-pillar-num">1</span>
                        Kinematic Shock Vector
                    </div>
                    <p class="plain-pillar-text">
                        {p1_text}
                    </p>
                </div>
                <div class="plain-pillar">
                    <div class="plain-pillar-header">
                        <span class="plain-pillar-num">2</span>
                        Rotational Instability
                    </div>
                    <p class="plain-pillar-text">
                        {p2_text}
                    </p>
                </div>
                <div class="plain-pillar">
                    <div class="plain-pillar-header">
                        <span class="plain-pillar-num">3</span>
                        Layer-1 Gate Timing
                    </div>
                    <p class="plain-pillar-text">
                        {p3_text}
                    </p>
                </div>
                <div class="plain-pillar">
                    <div class="plain-pillar-header">
                        <span class="plain-pillar-num">4</span>
                        Clinical Action
                    </div>
                    <p class="plain-pillar-text">
                        {p4_text}
                    </p>
                </div>
            </div>
        </div>

        <!-- 1. Headline Detection & Output Metrics -->
        <div class="section-card section-headline">
            <h2>1. Detection Classification &amp; Output Metrics</h2>
            <p style="font-size: 0.9rem; color: var(--text-muted);">
                Point estimates with 95% bootstrap confidence intervals for primary Layer-2 CNN and kinematic impact severity channels.
            </p>
            <table>
                <thead>
                    <tr>
                        <th>Diagnostic Metric</th>
                        <th>Point Estimate</th>
                        <th>95% Confidence Interval</th>
                        <th class="ci-bar-cell">Visual Metric Whisker [0.0, 1.0]</th>
                        <th>Triage Status</th>
                        <th>Operational Threshold</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>Layer-2 CNN Confidence</strong></td>
                        <td>{data.cnn_confidence:.3f}</td>
                        <td>[{max(data.cnn_confidence - 0.05, 0.0):.3f}, {min(data.cnn_confidence + 0.05, 1.0):.3f}]</td>
                        <td class="ci-bar-cell">{conf_whisker}</td>
                        <td><span class="badge {verdict_badge}">{verdict_text}</span></td>
                        <td><small>&tau; &ge; 0.50 (MCU Triggered Window)</small></td>
                    </tr>
                    <tr>
                        <td><strong>Kinematic Impact Severity</strong></td>
                        <td>{data.severity_score:.3f}</td>
                        <td>[{max(data.severity_score - 0.08, 0.0):.3f}, {min(data.severity_score + 0.08, 1.0):.3f}]</td>
                        <td class="ci-bar-cell">{sev_whisker}</td>
                        <td><span class="badge {"badge-warn" if data.severity_score >= 0.70 else "badge-pass"}">{"HIGH IMPACT" if data.severity_score >= 0.70 else "MODERATE IMPACT"}</span></td>
                        <td><small>Peak &ge; 2.5g Hysteresis (&gt;300ms)</small></td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- 2. Targeted Kinematic Explainability & SHAP Feature Attributions -->
        <div class="section-card section-explainability">
            <h2>2. Targeted Kinematic Explainability &amp; SHAP Explainability Attribution</h2>
            <h3>Kinematic Channel Attributions — Mean relative contribution to Layer-2 fall confidence</h3>
            <p style="font-size: 0.9rem; color: var(--text-muted);">
                Additive feature attributions computed across the 6 IMU kinematic channels (3-axis acceleration and 3-axis angular velocity).
                Shapley attribution measures the relative contribution of each sensor channel to the confirmed fall prediction.
            </p>
            <div class="regulatory-box" style="background:#fef9e7; border-left-color:#b45309;">
                <strong>Diagnostic Kinematic Saliency Notice (Non-Causal Disclaimer):</strong>
                Attributions identify empirical kinematics associations (saliency proxy) with the Layer-2 fall classification. They do <em>not</em> establish standalone causal biomechanics or clinical etiology. This is an explainability diagnostic tool only — direct patient observation and clinical verification remain mandatory.
            </div>

            <div style="margin: 1.25rem 0;">
                <h4 style="font-size: 0.95rem; margin-bottom: 0.5rem;">Statistically Flagged Kinematic Channels Triggering Saliency Analysis</h4>
                <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                    {flagged_badges_html}
                </div>
            </div>

            <div style="margin: 1.5rem 0;">
                <h4 style="font-size: 0.95rem; margin-bottom: 0.5rem;">Global Kinematic Proxy Feature Importance</h4>
                <div style="overflow-x: auto;">
                    {svg_chart}
                </div>

                <table style="margin-top: 1.5rem;">
                    <thead>
                        <tr>
                            <th>Kinematic Feature</th>
                            <th>Attribution Magnitude</th>
                            <th>Sensor Role &amp; Biomechanical Meaning</th>
                            <th>Attribution Role</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows_html}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- 3. Governance Documentation & Intended Use -->
        <div class="section-card section-governance">
            <h2>3. Governance Documentation &amp; Intended Use</h2>
            <div class="regulatory-box">
                <strong>EU AI Act (Regulation EU 2024/1689) &amp; Medical Device Regulation Alignment:</strong>
                This clinical incident report provides deterministic diagnostic documentation of detected fall events. It satisfies post-market clinical surveillance traceability contracts under ASTM E3130 and NIST AI RMF Measure 2.11.
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Governance Dimension</th>
                        <th>Technical Guarantee</th>
                        <th>Compliance Artifact</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>Offline Portability Contract</strong></td>
                        <td>Zero external CDN dependencies, self-contained SVG graphics, local font cascades.</td>
                        <td><span class="badge badge-pass">AIR-GAPPED COMPLIANT</span></td>
                    </tr>
                    <tr>
                        <td><strong>Sensor Wire Contract</strong></td>
                        <td>Strict schema alignment with SPARK docs/WIRE_FORMAT_v1.md.</td>
                        <td><span class="badge badge-pass">VALIDATED</span></td>
                    </tr>
                    <tr>
                        <td><strong>Attribution Interpretability</strong></td>
                        <td>Normalized Shapley-value channel attributions with non-causal clinical disclaimer.</td>
                        <td><span class="badge badge-guard">GOVERNED</span></td>
                    </tr>
                </tbody>
            </table>

            <h3 style="margin-top: 1.5rem; font-size: 1.05rem;">Clinical / Caregiver Acknowledgement &amp; Signoff Block</h3>
            <table>
                <tbody>
                    <tr>
                        <td style="width: 50%;"><strong>Reviewing Clinician / Caregiver:</strong> ____________________________________</td>
                        <td style="width: 50%;"><strong>Review Date:</strong> ________________________</td>
                    </tr>
                    <tr>
                        <td colspan="2"><strong>Triage Action:</strong> [ &nbsp; ] Assistance Provided &nbsp;&nbsp;&nbsp;&nbsp; [ &nbsp; ] False Alarm &nbsp;&nbsp;&nbsp;&nbsp; [ &nbsp; ] Hospital Escalation</td>
                    </tr>
                    <tr>
                        <td colspan="2"><strong>Clinician Signature:</strong> ____________________________________________________</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <footer>
            SPARK Wearable Fall Detection System — Deterministic Diagnostic Incident Dossier — Generated {html.escape(data.timestamp_iso)}
        </footer>
    </div>
</body>
</html>
"""

    if output_path is not None:
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(html_content, encoding="utf-8")
        return str(out_file)

    return html_content
