#!/usr/bin/env python3
"""
regenerate_reports.py

Batch report reconciler and generator for SPARK Gateway.
Re-renders all archived incident events in data/gateway_events using the
harmonized 60-30-10 palette, inline SVG attribution tracks,
and dual-format companion PDF and HTML dossiers.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from gateway.report.html_report import generate_html_report
from gateway.report.pdf_exporter import convert_html_to_pdf
from gateway.report.pdf_report import DUMMY_EVENT, ReportData


def regenerate_all_reports(store_dir: str | Path = "data/gateway_events") -> dict[str, int]:
    base_dir = Path(store_dir)
    if not base_dir.is_dir():
        raise FileNotFoundError(f"Gateway events directory not found: {base_dir}")

    event_files = sorted(base_dir.glob("*.json"))
    pdf_count = 0
    html_count = 0

    print(f"[*] Found {len(event_files)} event records in {base_dir}...")

    for event_file in event_files:
        try:
            record = json.loads(event_file.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"[!] Skipping unreadable JSON {event_file.name}: {exc}")
            continue

        if "payload" not in record or "shap" not in record:
            continue

        event_id = record.get("event_id", event_file.stem)
        payload = record["payload"]
        shap = record["shap"]

        ts_ms = payload.get("timestamp_ms", 0)
        if ts_ms:
            ts_str = datetime.fromtimestamp(ts_ms / 1000.0, tz=timezone.utc).strftime(
                "%Y-%m-%d %H:%M:%S UTC"
            )
        else:
            ts_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        confidence = float(payload.get("confidence", 0.0))
        report_data = ReportData(
            event_id=event_id,
            timestamp_iso=ts_str,
            severity_score=min(max(confidence, 0.0), 1.0),
            cnn_confidence=confidence,
            shap_top_feature=shap.get("top_feature", "a_z"),
            shap_values=shap.get("values", {}),
            device_id=payload.get("device_id", "SPARK-DEV-01"),
            firmware_version=payload.get("firmware_version", "v1.0.0-s3"),
            clinical_summary=shap.get("clinical_summary", ""),
            temporal_attributions=shap.get("temporal_attributions", {}),
        )

        pdf_path = base_dir / f"SPARK_Report_{event_id}.pdf"
        html_path = base_dir / f"SPARK_Report_{event_id}.html"

        # 1. Render standalone HTML dossier
        generate_html_report(report_data, html_path)
        html_count += 1

        # 2. Compile directly to publication-grade PDF via Blink headless engine
        convert_html_to_pdf(html_path, pdf_path)
        pdf_count += 1

        # Keep JSON pointer in sync
        record["report_path"] = str(pdf_path)
        record["html_report_path"] = str(html_path)
        event_file.write_text(json.dumps(record, indent=2), encoding="utf-8")

    # Also re-generate the standard sample dummy reports
    sample_pdf = base_dir / "sample_clinical_report.pdf"
    sample_html = base_dir / "sample_clinical_report.html"
    generate_html_report(DUMMY_EVENT, sample_html)
    convert_html_to_pdf(sample_html, sample_pdf)
    pdf_count += 1
    html_count += 1

    print(
        f"[OK] Re-generation complete: {pdf_count} PDFs and {html_count} HTML dossiers generated."
    )
    return {"pdf": pdf_count, "html": html_count}


if __name__ == "__main__":
    regenerate_all_reports()
