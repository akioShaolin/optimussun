import argparse
import json
from datetime import datetime
from pathlib import Path

from .config import mysql_config_from_env
from .mysql_target import _validate_plan, apply_schema, inspect_server, load_plan, verify_plan
from .reconciliation import empty_reconciliation, load_reconciliation
from .sqlite_source import create_snapshot, read_snapshot, sha256_file
from .transform import build_plan


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = ROOT / "src" / "optimus_sun.db"
DEFAULT_DDL = ROOT / "migrations" / "mysql" / "0001_initial.sql"


def _write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_report(path, plan):
    lines = [
        "# Relatório de simulação da migração v3", "",
        f"- Origem lógica: `{plan['source']['source_id']}`",
        f"- Hash do SQLite: `{plan['source']['source_sha256']}`",
        f"- Hash do snapshot: `{plan['source']['snapshot_sha256']}`", "",
        "## Contagens", "", "| Entidade | Quantidade |", "| --- | ---: |",
    ]
    lines.extend(f"| `{name}` | {value} |" for name, value in plan["counts"].items())
    lines.extend(["", "## Ocorrências", "",
                  "| Severidade | Entidade | Chave | Campo | Motivo |",
                  "| --- | --- | --- | --- | --- |"])
    for issue in plan["issues"]:
        lines.append(
            f"| {issue['severity']} | {issue['entity_type']} | {issue['source_key']} | "
            f"{issue.get('field') or '—'} | {issue['reason_code']} |"
        )
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def command_simulate(args):
    output = Path(args.output or ROOT / ".test_tmp" / "migration_v3" / datetime.now().strftime("%Y%m%d-%H%M%S"))
    output.mkdir(parents=True, exist_ok=True)
    source = Path(args.source).resolve()
    snapshot = output / "optimus_sun.snapshot.db"
    source_meta = create_snapshot(source, snapshot)
    source_data = read_snapshot(snapshot)
    decisions, decisions_hash, raw_decisions = load_reconciliation(args.reconciliation)
    plan = build_plan(source_data, source_meta, decisions, decisions_hash)
    _validate_plan(plan)
    _write_json(output / "import-plan.json", plan)
    _write_report(output / "report.md", plan)
    _write_json(output / "reconciliation-used.json", raw_decisions)
    if args.write_reconciliation_template:
        _write_json(output / "reconciliation-template.json", empty_reconciliation())
    summary = {"output": str(output), "source_hash_before": source_meta["source_sha256"],
               "source_hash_after": sha256_file(source), "snapshot_hash": source_meta["snapshot_sha256"],
               "integrity": source_data["integrity"], "foreign_key_issues": len(source_data["foreign_key_issues"]),
               "counts": plan["counts"]}
    _write_json(output / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 2 if plan["counts"]["errors"] else 0


def command_mysql(args):
    config = mysql_config_from_env()
    observed = inspect_server(config)
    print(json.dumps(observed, ensure_ascii=False, indent=2))
    if args.action == "inspect":
        return 0
    if args.action == "schema":
        print(json.dumps(apply_schema(config, DEFAULT_DDL), ensure_ascii=False, indent=2))
        return 0
    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    if args.action == "load":
        print(json.dumps(load_plan(config, plan), ensure_ascii=False, indent=2))
        return 0
    verification = verify_plan(config, plan)
    print(json.dumps(verification, ensure_ascii=False, indent=2))
    return 0 if verification["matches"] else 3


def parser():
    root = argparse.ArgumentParser(description="Migração controlada do Optimus Sun SQLite para MySQL v3")
    commands = root.add_subparsers(dest="command", required=True)
    simulate = commands.add_parser("simulate", help="Cria snapshot e plano local; não conecta ao MySQL")
    simulate.add_argument("--source", default=str(DEFAULT_SOURCE))
    simulate.add_argument("--output")
    simulate.add_argument("--reconciliation")
    simulate.add_argument("--write-reconciliation-template", action="store_true")
    simulate.set_defaults(handler=command_simulate)
    mysql = commands.add_parser("mysql", help="Operações explícitas no schema MySQL de ensaio")
    mysql.add_argument("action", choices=("inspect", "schema", "load", "verify"))
    mysql.add_argument("--plan")
    mysql.set_defaults(handler=command_mysql)
    return root


def main(argv=None):
    args = parser().parse_args(argv)
    if args.command == "mysql" and args.action in ("load", "verify") and not args.plan:
        raise SystemExit("--plan é obrigatório para load/verify")
    try:
        return args.handler(args)
    except (OSError, ValueError, RuntimeError) as error:
        print(f"ERRO: {error}")
        return 1
    except Exception:
        print("ERRO: falha inesperada; detalhes sensíveis foram omitidos.")
        return 1

