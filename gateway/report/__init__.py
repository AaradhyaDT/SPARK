"""
gateway.report

Clinical incident reporting package for SPARK Gateway (Layer 2).
Provides dual-mode (PDF via ReportLab and standalone HTML via inline SVG)
reporting implementing the 60-30-10 palette and SHAP visualization hierarchy.
"""

from gateway.report.html_report import generate_html_report
from gateway.report.pdf_report import DUMMY_EVENT, ReportData, generate_report

__all__ = [
    "DUMMY_EVENT",
    "ReportData",
    "generate_html_report",
    "generate_report",
]
