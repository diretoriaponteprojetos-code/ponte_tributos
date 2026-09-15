"""Executa o validador sobre o repositório e sobre casos negativos."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from validate import validate_repo  # noqa: E402


def test_repository_examples_are_valid() -> None:
    errors = validate_repo(ROOT)
    assert errors == [], "\n".join(errors)


@pytest.fixture
def repo_copy(tmp_path: Path) -> Path:
    for folder in ("schemas", "examples"):
        shutil.copytree(ROOT / folder, tmp_path / folder)
    return tmp_path


def _rewrite(path: Path, mutate) -> None:
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    mutate(doc)
    path.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")


def test_dangling_reference_is_rejected(repo_copy: Path) -> None:
    _rewrite(
        repo_copy / "examples/claims/CLM-0034-CBS-2026-01.yaml",
        lambda d: d["supported_by"].append("EV-NAO-EXISTE"),
    )
    errors = validate_repo(repo_copy)
    assert any("EV-NAO-EXISTE" in e for e in errors)


def test_rule_cannot_cite_non_normative_source(repo_copy: Path) -> None:
    _rewrite(
        repo_copy / "examples/rules/TAX-CBS-2026-001.yaml",
        lambda d: d["authority"].__setitem__("source", "SRC-GITHUB-MCPFISCAL"),
    )
    errors = validate_repo(repo_copy)
    assert any("DEC-001" in e for e in errors)


def test_supersedes_chain_must_not_overlap(repo_copy: Path) -> None:
    _rewrite(
        repo_copy / "examples/rules/RULE-100.yaml",
        lambda d: d["validity"].__setitem__("valid_until", "2026-09-30"),
    )
    errors = validate_repo(repo_copy)
    assert any("vigência sobreposta" in e for e in errors)


def test_decision_premise_counts_must_match_claims(repo_copy: Path) -> None:
    _rewrite(
        repo_copy / "examples/decisions/ADV-0034-2026-09-001.yaml",
        lambda d: d.__setitem__("premises_verified", 7),
    )
    errors = validate_repo(repo_copy)
    assert any("contagem de premissas" in e for e in errors)


def test_decision_needs_review_to_be_delivered(repo_copy: Path) -> None:
    _rewrite(
        repo_copy / "examples/decisions/ADV-0034-2026-09-001.yaml",
        lambda d: d.__setitem__("status", "DELIVERED"),
    )
    errors = validate_repo(repo_copy)
    assert any("'review' is a required property" in e for e in errors)


def test_verified_premise_needs_verified_evidence(repo_copy: Path) -> None:
    _rewrite(
        repo_copy / "examples/claims/CLM-0034-CBS-2026-01.yaml",
        lambda d: (
            d["premises"][0].__setitem__("status", "VERIFIED"),
            d["premises"][0].__setitem__("supported_by", ["EV-000381"]),
        ),
    )
    errors = validate_repo(repo_copy)
    assert any("evidência não conferida EV-000381" in e for e in errors)


def test_research_finding_is_never_client_specific(repo_copy: Path) -> None:
    _rewrite(
        repo_copy / "examples/research/RF-029.yaml",
        lambda d: d["applicability"].__setitem__("client_specific", True),
    )
    errors = validate_repo(repo_copy)
    assert any("client_specific" in e for e in errors)
