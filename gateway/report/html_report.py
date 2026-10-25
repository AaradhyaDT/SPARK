"""
html_report.py

Standalone, zero-dependency HTML companion incident report generator for SPARK Gateway,
implementing the BiasAperture / Compliance Report Harmonizer 60-30-10 visual hierarchy.

Outputs:
    1. Incident metadata and telemetry contract card.
    2. 4-card executive detection & output metrics strip.
    3. Standalone inline SVG SHAP feature attribution bar chart with calibrated tracks.
    4. Diagnostic Kinematic Saliency disclaimer card (non-causal / local attribution).
    5. Clinical / Caregiver signoff table.
    6. Strict @media print CSS for browser-to-PDF export fidelity.
"""

from __future__ import annotations

import html
from pathlib import Path

from gateway.receiver.wire_format import IMU_CHANNELS
from gateway.report.pdf_report import ReportData


def generate_html_report(data: ReportData, output_path: str | Path | None = None) -> str:
    """
    Renders a standalone, offline HTML incident report with inline SVGs.
    If output_path is provided, writes to disk and returns the resolved path.
    Otherwise, returns the raw HTML string.
    """
    axis_labels = {
        "a_x": "Lateral Acceleration (a_x)",
        "a_y": "Longitudinal Acceleration (a_y)",
        "a_z": "Vertical Impact Acceleration (a_z)",
        "w_x": "Roll Angular Velocity (w_x)",
        "w_y": "Pitch Angular Velocity (w_y)",
        "w_z": "Yaw Angular Velocity (w_z)",
    }

    max_val = max(data.shap_values.values(), default=1.0) or 1.0

    # Build inline SVG rows for SHAP chart
    bar_h = 16
    gap = 7
    label_w = 230
    track_w = 340
    val_w = 70
    total_w = label_w + track_w + val_w
    total_h = len(IMU_CHANNELS) * (bar_h + gap) + 10

    svg_rows: list[str] = []
    for i, ch in enumerate(IMU_CHANNELS):
        val = data.shap_values.get(ch, 0.0)
        label = html.escape(axis_labels.get(ch, ch))
        y = i * (bar_h + gap) + 5
        frac = (abs(val) / max_val) if max_val > 0 else 0.0
        bar_len = frac * track_w

        is_top = ch == data.shap_top_feature
        bar_color = "#991b1b" if is_top else "#0f766e"
        val_display = f"{val * 100:.1f}%"

        svg_rows.append(
            f'    <text x="{label_w - 10}" y="{y + bar_h - 4}" font-size="11" '
            f'font-family="-apple-system, Segoe UI, Roboto, sans-serif" fill="#475569" '
            f'text-anchor="end">{label}</text>\n'
            f'    <rect x="{label_w}" y="{y}" width="{track_w}" height="{bar_h}" '
            f'fill="#f1f5f9" rx="3"/>\n'
            f'    <rect x="{label_w}" y="{y}" width="{max(bar_len, 2.0):.1f}" height="{bar_h}" '
            f'fill="{bar_color}" rx="3"/>\n'
            f'    <text x="{label_w + track_w + 8}" y="{y + bar_h - 4}" font-size="11" '
            f'font-weight="600" font-family="-apple-system, Segoe UI, Roboto, sans-serif" '
            f'fill="#1e293b">{val_display}</text>'
        )

    svg_chart = (
        f'<svg class="inline-chart" width="{total_w}" height="{total_h}" '
        f'viewBox="0 0 {total_w} {total_h}" role="img" '
        f'aria-label="IMU kinematics SHAP attribution bars">\n' + "\n".join(svg_rows) + "\n</svg>"
    )

    narrative_html = ""
    if data.clinical_summary:
        narrative_html = f"""
        <div class="narrative-card">
            <span class="narrative-label">Clinical Analysis:</span>
            <span class="narrative-body">{html.escape(data.clinical_summary)}</span>
        </div>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SPARK Clinical Incident Report — {html.escape(data.event_id)}</title>
    <style>
        :root {{
            --body-slate: #1e293b;
            --body-bg: #f8fafc;
            --struct-navy: #1b365d;
            --muted-slate: #64748b;
            --track-slate: #f1f5f9;
            --border-slate: #cbd5e1;
            --card-bg: #ffffff;
            --accent-teal: #0f766e;
            --alert-crimson: #991b1b;
            --alert-crimson-bg: #fdf2f2;
            --alert-amber: #b45309;
            --alert-amber-bg: #fef9e7;
            --guard-indigo: #3730a3;
            --guard-indigo-bg: #eef2ff;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: var(--body-bg);
            color: var(--body-slate);
            line-height: 1.5;
            padding: 24px;
        }}

        .report-container {{
            max-width: 840px;
            margin: 0 auto;
            background: #ffffff;
            border: 1px solid var(--border-slate);
            border-radius: 6px;
            padding: 28px 32px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        }}

        /* Header Brand Banner */
        .brand-header {{
            background: var(--struct-navy);
            color: #ffffff;
            padding: 12px 18px;
            border-radius: 4px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 22px;
        }}

        .brand-title {{
            font-size: 1.15rem;
            font-weight: 700;
            letter-spacing: -0.01em;
        }}

        .brand-subtitle {{
            font-size: 0.78rem;
            opacity: 0.9;
        }}

        /* Section Headings */
        .section-header {{
            font-size: 0.82rem;
            font-weight: 700;
            color: var(--struct-navy);
            text-transform: uppercase;
            letter-spacing: 0.04em;
            padding-bottom: 4px;
            border-bottom: 1.5px solid var(--struct-navy);
            margin: 20px 0 12px 0;
        }}

        /* Metadata Grid */
        .meta-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 8px 16px;
            font-size: 0.82rem;
            margin-bottom: 16px;
        }}

        .meta-item strong {{
            color: var(--struct-navy);
            font-weight: 600;
        }}

        /* 4-Stat Strip (BiasAperture Executive Summary) */
        .stat-strip {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            margin-bottom: 14px;
        }}

        .stat-card {{
            padding: 10px 12px;
            border-radius: 4px;
            position: relative;
            background: var(--card-bg);
            border: 1px solid var(--border-slate);
        }}

        .stat-card::before {{
            content: "";
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 3.5px;
            border-radius: 4px 0 0 4px;
        }}

        .stat-card.card-status {{
            background: var(--alert-crimson-bg);
            border-color: #fecaca;
        }}
        .stat-card.card-status::before {{
            background: var(--alert-crimson);
        }}

        .stat-card.card-confidence::before {{
            background: var(--struct-navy);
        }}

        .stat-card.card-severity::before {{
            background: var(--muted-slate);
        }}

        .stat-card.card-trigger {{
            background: var(--guard-indigo-bg);
            border-color: #e0e7ff;
        }}
        .stat-card.card-trigger::before {{
            background: var(--guard-indigo);
        }}

        .stat-label {{
            font-size: 0.68rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: var(--muted-slate);
            margin-bottom: 4px;
        }}

        .stat-card.card-status .stat-label {{
            color: var(--alert-crimson);
        }}

        .stat-card.card-trigger .stat-label {{
            color: var(--guard-indigo);
        }}

        .stat-value {{
            font-size: 1.05rem;
            font-weight: 700;
            color: var(--body-slate);
        }}

        .stat-card.card-status .stat-value {{
            color: var(--alert-crimson);
        }}

        .stat-card.card-confidence .stat-value {{
            color: var(--struct-navy);
        }}

        /* Narrative Summary Card */
        .narrative-card {{
            background: #f8fafc;
            border: 1px solid var(--border-slate);
            border-radius: 4px;
            padding: 10px 14px;
            font-size: 0.82rem;
            margin-bottom: 18px;
        }}

        .narrative-label {{
            font-weight: 600;
            color: var(--struct-navy);
            margin-right: 6px;
        }}

        .narrative-body {{
            font-style: italic;
            color: var(--body-slate);
        }}

        /* SHAP Section */
        .shap-subtext {{
            font-size: 0.78rem;
            color: var(--muted-slate);
            margin-bottom: 12px;
            font-style: italic;
        }}

        .chart-wrapper {{
            overflow-x: auto;
            margin-bottom: 16px;
        }}

        /* Diagnostic Disclaimer Card */
        .disclaimer-card {{
            background: var(--alert-amber-bg);
            border: 1px solid #fed7aa;
            border-left: 3.5px solid var(--alert-amber);
            border-radius: 4px;
            padding: 10px 14px;
            font-size: 0.76rem;
            line-height: 1.45;
            margin-bottom: 22px;
        }}

        .disclaimer-title {{
            font-weight: 700;
            color: var(--alert-amber);
            margin-bottom: 3px;
        }}

        /* Acknowledgement Block */
        .signoff-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.78rem;
            margin-top: 6px;
        }}

        .signoff-table td {{
            padding: 6px 0;
            color: var(--body-slate);
        }}

        /* Print Media Styles */
        @media print {{
            @page {{
                size: A4 portrait;
                margin: 14mm;
            }}

            body {{
                background: #ffffff !important;
                padding: 0 !important;
            }}

            .report-container {{
                border: none !important;
                box-shadow: none !important;
                padding: 0 !important;
                max-width: 100% !important;
            }}

            .section-header, .stat-card, .disclaimer-card, .chart-wrapper {{
                break-inside: avoid !important;
                page-break-inside: avoid !important;
            }}
        }}
    </style>
</head>
<body>
    <div class="report-container">
        <!-- Brand Header -->
        <div class="brand-header">
            <div class="brand-title">SPARK Clinical Fall Incident Report</div>
            <div class="brand-subtitle">Signal Pattern Analysis &amp; Real-time Kinetics</div>
        </div>

        <!-- Metadata Section -->
        <div class="section-header">Incident Metadata &amp; Telemetry Contract</div>
        <div class="meta-grid">
            <div class="meta-item"><strong>Event ID:</strong> {html.escape(data.event_id)}</div>
            <div class="meta-item"><strong>Timestamp:</strong> {html.escape(data.timestamp_iso)}</div>
            <div class="meta-item"><strong>Device ID:</strong> {html.escape(data.device_id)}</div>
            <div class="meta-item"><strong>Firmware:</strong> {html.escape(data.firmware_version)}</div>
            <div class="meta-item"><strong>Protocol:</strong> WIRE_FORMAT_v1 (BLE/Serial)</div>
            <div class="meta-item"><strong>Location:</strong> Wrist Wearable Node</div>
        </div>

        <!-- Detection & Output Metrics -->
        <div class="section-header">Detection Classification &amp; Output Metrics</div>
        <div class="stat-strip">
            <div class="stat-card card-status">
                <div class="stat-label">Status</div>
                <div class="stat-value">CONFIRMED FALL</div>
            </div>
            <div class="stat-card card-confidence">
                <div class="stat-label">L2 Confidence</div>
                <div class="stat-value">{data.cnn_confidence:.1%}</div>
            </div>
            <div class="stat-card card-severity">
                <div class="stat-label">Impact Severity</div>
                <div class="stat-value">{data.severity_score:.2f} / 1.00</div>
            </div>
            <div class="stat-card card-trigger">
                <div class="stat-label">Top Trigger</div>
                <div class="stat-value">{html.escape(data.shap_top_feature.upper())} AXIS</div>
            </div>
        </div>

        {narrative_html}

        <!-- SHAP Explainability Attribution -->
        <div class="section-header">SHAP Explainability Attribution (IMU Kinematics)</div>
        <div class="shap-subtext">
            Additive feature attributions normalized across 6 IMU channels. Highlights dominant shock and rotation axes.
        </div>
        <div class="chart-wrapper">
            {svg_chart}
        </div>

        <!-- Diagnostic Disclaimer Notice -->
        <div class="disclaimer-card">
            <div class="disclaimer-title">Diagnostic Kinematic Saliency Notice (Local Attribution):</div>
            <div>
                Attributions quantify empirical kinematic contributions to Layer-2 CNN confidence. They identify dominant
                shock axes rather than standalone causality. Must be evaluated alongside patient vitals and direct clinical observation.
            </div>
        </div>

        <!-- Clinical Signoff Block -->
        <div class="section-header">Clinical / Caregiver Acknowledgement</div>
        <table class="signoff-table">
            <tr>
                <td style="width: 60%;">Reviewing Clinician / Caregiver Name: ________________________________</td>
                <td style="width: 40%;">Review Date: ___________________</td>
            </tr>
            <tr>
                <td colspan="2">Triage Action: [  ] Assistance Provided &nbsp;&nbsp; [  ] False Alarm &nbsp;&nbsp; [  ] Hospital Escalation</td>
            </tr>
            <tr>
                <td colspan="2">Clinician Signature: _________________________________</td>
            </tr>
        </table>
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
