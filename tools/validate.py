#!/usr/bin/env python3
"""Valida os exemplos de `examples/` contra os schemas de `schemas/`.

Duas etapas:

1. Validação estrutural: cada arquivo YAML é validado contra o JSON Schema
   da sua pasta.
2. Integridade referencial e regras de governança (DEC-001):
   - todo ID referenciado existe;
   - IDs são únicos;
   - Rule só cita fontes NORMATIVE; ResearchFinding só cita fontes RESEARCH;
   - cadeias `supersedes` não se sobrepõem no tempo;
   - Rule ACTIVE exige Review APPROVED sobre ela;
   - Claim VERIFIED exige todas as premissas VERIFIED;
   - Decision: contagem de premissas bate com os Claims de origem e
     `source_set` cobre as fontes das evidências usadas.

Uso:
    python tools/validate.py            # valida o repositório
    python tools/validate.py --root DIR # outra raiz
Sai com código 1 se houver qualquer erro.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

SCHEMA_BASE = "https://ponte-projetos.dev/schemas/"

# pasta em examples/ -> (nome do schema, campo de ID)
FOLDERS: dict[str, tuple[str, str]] = {
    "sources": ("source", "id"),
    "evidence": ("evidence", "evidence_id"),
    "authorities": ("authority", "authority_id"),
    "rules": ("rule", "rule_id"),
    "entities": ("entity", "entity_id"),
    "taxpayers": ("taxpayer", "taxpayer_id"),
    "transactions": ("transaction", "transaction_id"),
    "tax_treatments": ("tax_treatment", "treatment_id"),
    "calculations": ("calculation", "calculation_id"),
    "observations": ("observation", "observation_id"),
    "claims": ("claim", "claim_id"),
    "decisions": ("decision", "decision_id"),
    "research": ("research_finding", "id"),
    "candidate_updates": ("candidate_update", "id"),
    "versions": ("version", "version_id"),
    "reviews": ("review", "review_id"),
}

ID_PREFIXES = (
    "SRC", "EV", "AUT", "RULE", "TAX", "ENT", "TP", "TX", "TT",
    "CALC", "OBS", "CLM", "ADV", "RF", "CU", "VER", "REV",
)
ID_RE = re.compile(r"^(?:%s)-[A-Z0-9-]+$" % "|".join(ID_PREFIXES))


@dataclass
class Repo:
    objects: dict[str, dict[str, Any]] = field(default_factory=dict)
    kinds: dict[str, str] = field(default_factory=dict)
    files: dict[str, Path] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    def err(self, where: str, msg: str) -> None:
        self.errors.append(f"{where}: {msg}")


def _load_schemas(schema_dir: Path) -> tuple[Registry, dict[str, dict]]:
    registry = Registry()
    schemas: dict[str, dict] = {}
    for path in sorted(schema_dir.glob("*.schema.json")):
        schema = json.loads(path.read_text(encoding="utf-8"))
        name = path.name.removesuffix(".schema.json")
        schemas[name] = schema
        registry = registry.with_resource(
            schema["$id"], Resource(contents=schema, specification=DRAFT202012)
        )
    return registry, schemas


def _iter_id_strings(node: Any):
    if isinstance(node, dict):
        for value in node.values():
            yield from _iter_id_strings(value)
    elif isinstance(node, list):
        for value in node:
            yield from _iter_id_strings(value)
    elif isinstance(node, str) and ID_RE.fullmatch(node):
        yield node


def _as_date(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def _stringify_dates(node: Any) -> Any:
    """PyYAML converte `2026-01-01` em date; o schema espera string."""
    if isinstance(node, dict):
        return {k: _stringify_dates(v) for k, v in node.items()}
    if isinstance(node, list):
        return [_stringify_dates(v) for v in node]
    if isinstance(node, date):
        return node.isoformat()
    return node


def load_examples(root: Path, repo: Repo, registry: Registry, schemas: dict[str, dict]) -> None:
    examples_dir = root / "examples"
    checker = FormatChecker()
    for folder, (schema_name, id_field) in FOLDERS.items():
        folder_path = examples_dir / folder
        if not folder_path.is_dir():
            continue
        validator = Draft202012Validator(
            schemas[schema_name], registry=registry, format_checker=checker
        )
        for path in sorted(folder_path.glob("*.yaml")):
            rel = str(path.relative_to(root))
            try:
                doc = _stringify_dates(yaml.safe_load(path.read_text(encoding="utf-8")))
            except yaml.YAMLError as exc:  # pragma: no cover - defensive
                repo.err(rel, f"YAML inválido: {exc}")
                continue
            if not isinstance(doc, dict):
                repo.err(rel, "o documento deve ser um mapeamento")
                continue
            for error in sorted(validator.iter_errors(doc), key=lambda e: list(e.path)):
                where = "/".join(str(p) for p in error.path) or "<raiz>"
                repo.err(rel, f"[{where}] {error.message}")
            obj_id = doc.get(id_field)
            if not isinstance(obj_id, str):
                repo.err(rel, f"campo de ID `{id_field}` ausente")
                continue
            if obj_id in repo.objects:
                repo.err(rel, f"ID duplicado {obj_id} (já em {repo.files[obj_id]})")
                continue
            expected_stem = obj_id
            if path.stem != expected_stem:
                repo.err(rel, f"nome do arquivo deve ser `{expected_stem}.yaml`")
            repo.objects[obj_id] = doc
            repo.kinds[obj_id] = schema_name
            repo.files[obj_id] = path.relative_to(root)


def _where(repo: Repo, obj_id: str) -> str:
    return str(repo.files.get(obj_id, obj_id))


def check_references(repo: Repo) -> None:
    for obj_id, doc in repo.objects.items():
        for ref in set(_iter_id_strings(doc)):
            if ref == obj_id:
                continue
            if ref not in repo.objects:
                repo.err(_where(repo, obj_id), f"referência a ID inexistente {ref}")


def check_authority_levels(repo: Repo) -> None:
    def level(source_id: str) -> str | None:
        src = repo.objects.get(source_id)
        return src.get("authority_level") if src else None

    for obj_id, doc in repo.objects.items():
        kind = repo.kinds[obj_id]
        where = _where(repo, obj_id)
        if kind == "rule":
            src = doc["authority"]["source"]
            if level(src) not in (None, "NORMATIVE"):
                repo.err(where, f"authority.source {src} não é NORMATIVE (DEC-001)")
            for ev_id in doc.get("evidence", []):
                ev = repo.objects.get(ev_id)
                if ev and level(ev["source"]) not in (None, "NORMATIVE"):
                    repo.err(where, f"evidência {ev_id} vem de fonte não NORMATIVE (DEC-001)")
        elif kind == "research_finding":
            if level(doc["source"]) not in (None, "RESEARCH"):
                repo.err(where, f"source {doc['source']} não é RESEARCH")
            for ev_id in doc.get("evidence", []):
                ev = repo.objects.get(ev_id)
                if ev and ev.get("client_specific"):
                    repo.err(where, f"evidência {ev_id} é client_specific; achado de pesquisa nunca é")
        elif kind == "evidence":
            src = repo.objects.get(doc["source"])
            if src and src.get("retrieval_status") == "PENDING" and doc["verification_status"] != "PENDING":
                repo.err(where, "fonte ainda PENDING: evidência não pode estar verificada")
            if src and src.get("type") == "client_document" and not doc.get("client_specific"):
                repo.err(where, "evidência de client_document deve ser client_specific: true")


def check_supersedes(repo: Repo) -> None:
    for obj_id, doc in repo.objects.items():
        if repo.kinds[obj_id] != "rule":
            continue
        where = _where(repo, obj_id)
        old_id = doc.get("supersedes")
        if not old_id:
            continue
        old = repo.objects.get(old_id)
        if not old or repo.kinds.get(old_id) != "rule":
            continue
        new_from = _as_date(doc["validity"]["valid_from"])
        old_until = _as_date(old["validity"]["valid_until"])
        if old_until is None:
            repo.err(where, f"supersede {old_id}, mas a regra antiga não tem valid_until")
        elif new_from is None or old_until >= new_from:
            repo.err(where, f"vigência sobreposta: {old_id} vale até {old_until}, nova vale desde {new_from}")
        if old.get("status") != "SUPERSEDED":
            repo.err(where, f"{old_id} deveria ter status SUPERSEDED")
        if old.get("superseded_by") != obj_id:
            repo.err(where, f"{old_id}.superseded_by deveria ser {obj_id}")


def check_reviews(repo: Repo) -> None:
    for obj_id, doc in repo.objects.items():
        kind = repo.kinds[obj_id]
        where = _where(repo, obj_id)
        needs_review = (
            (kind == "rule" and doc.get("status") == "ACTIVE")
            or (kind == "decision" and doc.get("status") in ("REVIEWED", "DELIVERED"))
            or (kind == "candidate_update" and doc.get("status") == "PROMOTED")
        )
        if not needs_review:
            continue
        review = repo.objects.get(doc.get("review", ""))
        if not review:
            continue  # referência inexistente já reportada
        if review.get("object_id") != obj_id:
            repo.err(where, f"review {doc['review']} refere-se a {review.get('object_id')}, não a {obj_id}")
        if review.get("outcome") != "APPROVED":
            repo.err(where, f"review {doc['review']} não está APPROVED")


def check_claims(repo: Repo) -> None:
    for obj_id, doc in repo.objects.items():
        if repo.kinds[obj_id] != "claim":
            continue
        where = _where(repo, obj_id)
        status = doc["verification"]["status"]
        premises = doc.get("premises", [])

        def evidence_verified(ev_id: str) -> bool:
            ev = repo.objects.get(ev_id)
            return bool(ev) and ev.get("verification_status") == "VERIFIED_AGAINST_SOURCE"

        if status == "VERIFIED" and any(p["status"] != "VERIFIED" for p in premises):
            repo.err(where, "claim VERIFIED com premissa não verificada")
        if status == "VERIFIED":
            for ev_id in doc.get("supported_by", []):
                if not evidence_verified(ev_id):
                    repo.err(where, f"claim VERIFIED apoiado em evidência não conferida {ev_id}")
        for premise in premises:
            if premise["status"] != "VERIFIED":
                continue
            for ev_id in premise.get("supported_by", []):
                if not evidence_verified(ev_id):
                    repo.err(where, f"premissa {premise['id']} VERIFIED apoiada em evidência não conferida {ev_id}")
        if status == "SCENARIO_ONLY" and doc["verification"]["checks"]["free_of_hypothesis"] != "FAIL":
            repo.err(where, "SCENARIO_ONLY exige checks.free_of_hypothesis = FAIL")
        for calc_id in doc.get("derived_from", []):
            calc = repo.objects.get(calc_id)
            if calc and calc.get("normative_snapshot") != doc["normative_snapshot"]:
                repo.err(where, f"snapshot do claim difere do snapshot de {calc_id}")


def check_decisions(repo: Repo) -> None:
    for obj_id, doc in repo.objects.items():
        if repo.kinds[obj_id] != "decision":
            continue
        where = _where(repo, obj_id)
        total = verified = 0
        sources_needed: set[str] = set()
        for claim_id in doc["derives_from"]:
            claim = repo.objects.get(claim_id)
            if not claim:
                continue
            if claim.get("normative_snapshot") != doc["normative_snapshot"]:
                repo.err(where, f"snapshot da decisão difere do snapshot de {claim_id}")
            if claim["verification"]["status"] in ("CONTRADICTED", "INCOMPARABLE", "STALE", "INSUFFICIENT_EVIDENCE"):
                repo.err(where, f"deriva de {claim_id} com status {claim['verification']['status']}")
            for premise in claim.get("premises", []):
                total += 1
                verified += premise["status"] == "VERIFIED"
            for ev_id in claim.get("supported_by", []):
                ev = repo.objects.get(ev_id)
                if ev:
                    sources_needed.add(ev["source"])
        if (doc["premises_total"], doc["premises_verified"], doc["premises_unverified"]) != (
            total, verified, total - verified
        ):
            repo.err(
                where,
                f"contagem de premissas declarada ({doc['premises_total']}/{doc['premises_verified']}/"
                f"{doc['premises_unverified']}) difere da observada nos claims ({total}/{verified}/{total - verified})",
            )
        missing = sources_needed - set(doc["source_set"])
        if missing:
            repo.err(where, f"source_set não cobre fontes usadas pelos claims: {sorted(missing)}")


def validate_repo(root: Path) -> list[str]:
    registry, schemas = _load_schemas(root / "schemas")
    for name, schema in schemas.items():
        Draft202012Validator.check_schema(schema)
    repo = Repo()
    load_examples(root, repo, registry, schemas)
    if repo.errors:
        return repo.errors  # sem estrutura válida não faz sentido cruzar referências
    check_references(repo)
    check_authority_levels(repo)
    check_supersedes(repo)
    check_reviews(repo)
    check_claims(repo)
    check_decisions(repo)
    return repo.errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args(argv)
    errors = validate_repo(args.root)
    counts: dict[str, int] = defaultdict(int)
    for folder in FOLDERS:
        counts[folder] = len(list((args.root / "examples" / folder).glob("*.yaml"))) if (args.root / "examples" / folder).is_dir() else 0
    for folder, n in counts.items():
        if n:
            print(f"  {folder:<20} {n}")
    if errors:
        print(f"\n{len(errors)} erro(s):", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print("\nOK: todos os exemplos válidos e consistentes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
