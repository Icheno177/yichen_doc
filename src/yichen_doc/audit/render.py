"""Optional real-reader rendering adapters; unsupported environments fail closed."""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys


def render_pptx(path: str | Path, out_dir: str | Path) -> dict:
    if os.name != "nt":
        return {"status": "BLOCKED", "reason": "PowerPoint COM renderer is Windows-only; supply rendered page images from a compatible renderer."}
    powershell = shutil.which("powershell") or shutil.which("pwsh")
    if not powershell:
        return {"status": "BLOCKED", "reason": "PowerShell not found."}
    script = Path(__file__).with_name("render_pptx.ps1")
    out = Path(out_dir).resolve(); out.mkdir(parents=True, exist_ok=True)
    try:
        # Bypass is scoped to this child process only; no machine or user
        # ExecutionPolicy setting is changed.
        run = subprocess.run([powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script), "-InputPptx", str(Path(path).resolve()), "-OutputDirectory", str(out)],
                             capture_output=True, text=True, timeout=180)
    except Exception as exc:
        return {"status": "BLOCKED", "reason": f"{type(exc).__name__}: {exc}"}
    images = sorted(out.glob("slide-*.png"))
    if run.returncode != 0 or not images:
        return {"status": "BLOCKED", "reason": run.stderr[-2000:] or "Renderer returned no slide images."}
    return {"status": "RENDERED", "page_count": len(images), "renderer": "Microsoft PowerPoint COM", "output_dir": str(out), "stdout": run.stdout.strip()}
