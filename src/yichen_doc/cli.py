from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from . import __version__
from .content import load_content
from .qa import inspect_output, write_qa_report
from .audit.project import run_project
from .renderers import docx, html, xlsx


def _safe_name(value: str) -> str:
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in value).strip("_") or "research_report"


def build(content_path: Path, output_dir: Path, formats: list[str]) -> list[Path]:
    content = load_content(content_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = _safe_name(content["metadata"]["title"])
    base_dir = content_path.resolve().parent
    outputs: list[Path] = []
    for fmt in formats:
        target = output_dir / f"{stem}.{fmt}"
        if fmt == "docx": docx.render(content, target, base_dir)
        elif fmt == "xlsx": xlsx.render(content, target)
        elif fmt == "html": html.render(content, target, base_dir)
        elif fmt == "pptx":
            node = shutil.which("node")
            if not node:
                raise RuntimeError("Node.js is required for the PptxGenJS renderer")
            script = Path(__file__).parent / "renderers" / "pptx.js"
            project_root = Path(__file__).resolve().parents[2]
            env = os.environ.copy()
            module_paths = [str(project_root / "node_modules"), str(Path.cwd() / "node_modules")]
            if env.get("NODE_PATH"):
                module_paths.append(env["NODE_PATH"])
            env["NODE_PATH"] = os.pathsep.join(dict.fromkeys(module_paths))
            subprocess.run([node, str(script), str(content_path.resolve()), str(target.resolve())], check=True, cwd=project_root, env=env)
        else: raise ValueError(f"Unsupported format: {fmt}")
        outputs.append(target)
    qa = [inspect_output(p) for p in outputs]
    write_qa_report(qa, output_dir / f"{stem}.qa.json")
    return outputs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="yichen_doc", description="Build editable research deliverables from a shared JSON content contract")
    parser.add_argument("--version", action="version", version=f"yichen_doc {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)
    build_parser = sub.add_parser("build", help="render selected formats")
    build_parser.add_argument("content", type=Path, help="research content JSON")
    build_parser.add_argument("--formats", default="docx,pptx,xlsx,html", help="comma-separated: docx,pptx,xlsx,html")
    build_parser.add_argument("--out", type=Path, default=Path("outputs"))
    validate_parser = sub.add_parser("validate", help="validate a shared content contract")
    validate_parser.add_argument("content", type=Path)
    audit_parser = sub.add_parser("audit", help="run an independent staged audit from a JSON manifest")
    audit_parser.add_argument("manifest", type=Path, help="local JSON manifest listing source, revision and presentation files")
    audit_parser.add_argument("--out", type=Path, default=Path("audit_outputs"))
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            load_content(args.content); print("PASS: content contract valid"); return 0
        if args.command == "audit":
            result = run_project(args.manifest, args.out)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result["overall_status"] in {"PASS", "PASS_WITH_WARNINGS"} else 3
        formats = [x.strip().lower() for x in args.formats.split(",") if x.strip()]
        allowed = {"docx", "pptx", "xlsx", "html"}
        if not formats or set(formats) - allowed: raise ValueError(f"formats must be selected from {sorted(allowed)}")
        paths = build(args.content, args.out, formats)
        print(json.dumps({"status":"PASS", "outputs":[str(p.resolve()) for p in paths]}, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr); return 2


if __name__ == "__main__":
    raise SystemExit(main())
