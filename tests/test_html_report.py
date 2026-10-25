"""
test_html_report.py

Unit tests for standalone HTML clinical incident report generation in SPARK Gateway.
Verifies 60-30-10 visual hierarchy, inline SVG SHAP attribution, and print styling.
"""

from pathlib import Path

from gateway.report.html_report import generate_html_report
from gateway.report.pdf_report import DUMMY_EVENT, ReportData


class TestHtmlReport:
    def test_generate_html_string_in_memory(self):
        raw_html = generate_html_report(DUMMY_EVENT)
        assert "<!DOCTYPE html>" in raw_html
        assert "SPARK Clinical Fall Incident Report" in raw_html
        assert "CONFIRMED FALL" in raw_html
        assert "SHAP Explainability Attribution" in raw_html
        assert '<svg class="inline-chart"' in raw_html
        assert "#0f766e" in raw_html  # Accent teal attribution fill
        assert "#991b1b" in raw_html  # Top trigger alert crimson
        assert "#f1f5f9" in raw_html  # Attribution track background
        assert "Diagnostic Kinematic Saliency Notice" in raw_html

    def test_generate_html_file(self, tmp_path: Path):
        out_html = tmp_path / "test_report.html"
        res = generate_html_report(DUMMY_EVENT, out_html)

        assert Path(res).exists()
        content = out_html.read_text(encoding="utf-8")
        assert len(content) > 1500
        assert "a_z" in content
        assert "EVT-20260820-001" in content

    def test_custom_data_html_rendering(self, tmp_path: Path):
        custom_data = ReportData(
            event_id="EVT-TEST-CUSTOM-42",
            timestamp_iso="2026-10-25 12:00:00 UTC",
            severity_score=0.92,
            cnn_confidence=0.99,
            shap_top_feature="w_x",
            shap_values={
                "a_x": 0.1,
                "a_y": 0.1,
                "a_z": 0.1,
                "w_x": 0.5,
                "w_y": 0.1,
                "w_z": 0.1,
            },
            clinical_summary="Severe lateral tumble detected.",
        )
        out_html = tmp_path / "custom.html"
        generate_html_report(custom_data, out_html)

        content = out_html.read_text(encoding="utf-8")
        assert "EVT-TEST-CUSTOM-42" in content
        assert "W_X AXIS" in content
        assert "Severe lateral tumble detected." in content
        # Verify dynamic pillar synthesis
        assert "angular velocity" in content.lower()
        assert "tumbling motion" in content.lower()
        assert "high impact severity" in content.lower()
