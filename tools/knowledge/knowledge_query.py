"""Query absorber-manufacturing knowledge in a human-readable way."""

from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Any
import yaml

def find_repo_root(start: Path | None = None) -> Path:
    start = (start or Path.cwd()).resolve()
    for candidate in (start, *start.parents):
        if (candidate / "engineering_navigator").is_dir():
            return candidate
    raise FileNotFoundError("Could not locate repository root containing engineering_navigator/.")

def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path}: expected one top-level mapping")
    return data

def norm(v: Any) -> str:
    return str(v).lower()

def matches(fields: list[Any], q: str) -> bool:
    return any(q in norm(v) for v in fields)

def query_knowledge(k: dict[str, Any], query: str) -> dict[str, Any]:
    q = query.strip().lower()

    relationships = [
        r for r in k.get("relationships", [])
        if isinstance(r, dict) and matches(
            [r.get("id"), r.get("from"), r.get("to"), r.get("status"),
             r.get("statement"), r.get("effect"), r.get("sources")], q
        )
    ]

    decisions = [
        d for d in k.get("engineering_decisions", {}).get("supported_now", [])
        if isinstance(d, dict) and matches([d.get("decision"), d.get("sources")], q)
    ]

    open_specs = [
        s for s in k.get("engineering_decisions", {}).get("open_specifications", [])
        if isinstance(s, dict) and matches(
            [s.get("id"), s.get("specification"), s.get("reason"), s.get("sources")], q
        )
    ]

    aliases = {
        "thickness": ["bismuth_thickness_um"],
        "current": ["current_density_mA_per_cm2"],
        "temperature": ["bath_temperature", "bath_temperature_C"],
        "grain": ["grain_size_nm"],
        "rate": ["plating_rate_nm_per_min"],
        "voltage": ["bias_voltage_V"],
    }

    process_points = []
    for p in k.get("reported_process_points", []):
        if not isinstance(p, dict):
            continue
        hit = q in norm(p)
        if not hit:
            for alias, keys in aliases.items():
                if q in alias and any(key in p for key in keys):
                    hit = True
                    break
        if hit:
            process_points.append(p)

    return {
        "query": query,
        "relationships": relationships,
        "supported_decisions": decisions,
        "open_specifications": open_specs,
        "reported_process_points": process_points,
    }

def srcs(v: Any) -> str:
    return ", ".join(v) if isinstance(v, list) else str(v or "")

def print_result(r: dict[str, Any]) -> None:
    q = r["query"]
    print(f"\n{q.upper()}\n{'=' * len(q)}")

    if r["relationships"]:
        print("\nSUPPORTED RELATIONSHIPS")
        for rel in r["relationships"]:
            print(f"\n{rel.get('from')} -> {rel.get('to')}")
            print(f"  status: {rel.get('status')}")
            print(f"  {rel.get('statement')}")
            if rel.get("effect"):
                print(f"  effect: {rel.get('effect')}")
            print(f"  evidence: {srcs(rel.get('sources'))}")

    if r["supported_decisions"]:
        print("\nSUPPORTED ENGINEERING DECISIONS")
        for d in r["supported_decisions"]:
            print(f"\n- {d.get('decision')}")
            print(f"  evidence: {srcs(d.get('sources'))}")

    if r["open_specifications"]:
        print("\nOPEN SPECIFICATIONS")
        for s in r["open_specifications"]:
            print(f"\n- {s.get('specification')}")
            print(f"  why open: {s.get('reason')}")
            print(f"  evidence: {srcs(s.get('sources'))}")

    if r["reported_process_points"]:
        print("\nREPORTED PROCESS POINTS")
        for p in r["reported_process_points"]:
            print()
            for key, value in p.items():
                print(f"  {key}: {value}")

    if not any(r[k] for k in (
        "relationships","supported_decisions","open_specifications","reported_process_points"
    )):
        print("\nNo matching knowledge entries.")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--knowledge", type=Path)
    ap.add_argument("--repo-root", type=Path)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    root = args.repo_root.resolve() if args.repo_root else find_repo_root()
    path = args.knowledge.resolve() if args.knowledge else (
        root / "engineering_navigator" / "absorber_manufacturing" / "knowledge" / "absorber_manufacturing.yaml"
    )
    result = query_knowledge(load_yaml(path), args.query)
    print(json.dumps(result, indent=2, ensure_ascii=False) if args.json else "", end="")
    if not args.json:
        print_result(result)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
