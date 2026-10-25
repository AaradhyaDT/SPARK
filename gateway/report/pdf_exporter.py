"""
pdf_exporter.py

Cross-platform Headless PDF Exporter for SPARK Clinical Dossiers.
Discovers the native Blink engine (Edge / Chrome / Chromium) across Windows,
Linux, and macOS to deterministically compile HTML dossiers into
vector-crisp, publication-grade paginated PDFs.
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
from pathlib import Path


def find_blink_browser() -> Path:
    """
    Discovers an available Blink-based browser binary across platforms.
    Prioritizes Windows installations (Edge / Chrome), followed by Linux and macOS.
    """
    # 1. Environment variable override
    if env_bin := os.environ.get("SPARK_BROWSER_BIN"):
        p = Path(env_bin)
        if p.exists():
            return p

    # 2. Executable name discovery in PATH (Windows prioritized)
    search_names = [
        "msedge.exe",
        "chrome.exe",
        "msedge",
        "chrome",
        "google-chrome-stable",
        "google-chrome",
        "chromium-browser",
        "chromium",
        "microsoft-edge-stable",
        "microsoft-edge",
    ]
    for name in search_names:
        if found := shutil.which(name):
            return Path(found)

    # 3. Known OS filesystem locations (Windows prioritized)
    system = platform.system()
    candidates: list[Path] = []

    if system == "Windows":
        candidates = [
            Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
            Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
            Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
            Path(os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe")),
            Path(os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")),
        ]
    elif system == "Linux":
        candidates = [
            Path("/usr/bin/google-chrome"),
            Path("/usr/bin/google-chrome-stable"),
            Path("/usr/bin/chromium"),
            Path("/usr/bin/chromium-browser"),
            Path("/usr/bin/microsoft-edge"),
            Path("/usr/bin/microsoft-edge-stable"),
            Path("/snap/bin/chromium"),
        ]
    elif system == "Darwin":
        candidates = [
            Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
            Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
            Path("/Applications/Chromium.app/Contents/MacOS/Chromium"),
        ]

    for p in candidates:
        if p.exists():
            return p

    raise FileNotFoundError(
        f"No Blink-based browser (Edge, Chrome, Chromium) discovered on {system}. "
        "Please install Edge/Chrome/Chromium or set SPARK_BROWSER_BIN."
    )


def convert_html_to_pdf(html_path: str | Path, pdf_path: str | Path | None = None) -> Path:
    """
    Converts a standalone HTML report into a publication-grade PDF file
    using the native Blink headless print-to-pdf pipeline.
    """
    html_file = Path(html_path).resolve()
    if not html_file.exists():
        raise FileNotFoundError(f"Source HTML report not found: {html_file}")

    if pdf_path is None:
        target_pdf = html_file.with_suffix(".pdf")
    else:
        target_pdf = Path(pdf_path).resolve()

    target_pdf.parent.mkdir(parents=True, exist_ok=True)
    browser_bin = find_blink_browser()

    base_args = [
        "--disable-gpu",
        "--run-all-compositor-stages-before-draw",
        "--no-pdf-header-footer",
        "--generate-pdf-document-outline",
        "--allow-file-access-from-files",
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        f"--print-to-pdf={target_pdf}",
        str(html_file),
    ]

    # Try modern headless first (--headless=new), with fallback to legacy --headless
    cmd = [str(browser_bin), "--headless=new", *base_args]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
    )

    needs_legacy_fallback = (
        result.returncode != 0 or not target_pdf.exists()
    ) and "unknown flag" in result.stderr.lower()

    if needs_legacy_fallback:
        cmd_legacy = [str(browser_bin), "--headless", *base_args]
        result = subprocess.run(
            cmd_legacy,
            capture_output=True,
            text=True,
            check=False,
        )

    if result.returncode != 0 and not target_pdf.exists():
        raise RuntimeError(
            f"PDF compilation failed (exit code {result.returncode}):\n{result.stderr}"
        )

    return target_pdf
