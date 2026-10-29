#!/usr/bin/env python3
"""Recupera o arquivo de uma Source, grava o sha256 e marca a fonte como RETRIEVED.

Uso:
    python tools/ingest_source.py SRC-RFB-LC214
    python tools/ingest_source.py SRC-RFB-LC214 --grep "Art. 346" --context 6
    python tools/ingest_source.py SRC-RFB-LC214 --file lcp214.htm --grep "Art. 34[368]"

O arquivo baixado fica em `sources_cache/<ID>.<ext>` (ignorado pelo git). O YAML
da fonte em `examples/sources/<ID>.yaml` é atualizado in loco:
`sha256`, `retrieved_at` (hoje) e `retrieval_status: RETRIEVED`.

Se o site derrubar a conexão mesmo após as novas tentativas, salve a página pelo
navegador (Ctrl+S, "somente HTML") e passe o caminho com `--file`.

Com `--grep`, imprime as linhas do texto (HTML convertido em texto) que contêm
o padrão, com contexto, para conferir locator e redação de uma Evidence antes
de promovê-la a VERIFIED_AGAINST_SOURCE. O script não altera evidências: a
promoção é decisão humana (DEC-001).
"""
from __future__ import annotations

import argparse
import hashlib
import html
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "sources_cache"


class _Text(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip += 1
        elif tag in ("p", "br", "div", "li", "tr", "h1", "h2", "h3", "h4"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._skip = max(0, self._skip - 1)

    def handle_data(self, data):
        if not self._skip:
            self.parts.append(data)


def html_to_text(raw: bytes) -> str:
    for enc in ("utf-8", "windows-1252", "latin-1"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    parser = _Text()
    parser.feed(text)
    out = html.unescape("".join(parser.parts))
    return re.sub(r"[ \t\xa0]+", " ", out)


def fetch(url: str, attempts: int = 4) -> tuple[bytes, str]:
    """Baixa a URL identificando-se como navegador, com novas tentativas.

    O Planalto e outros sites oficiais derrubam a conexão de clientes que não
    parecem navegador (ConnectionResetError / WinError 10054).
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/pdf;q=0.9,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9",
        "Connection": "close",
    }
    last: Exception | None = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=120) as resp:
                return resp.read(), resp.headers.get("Content-Type", "")
        except (OSError, urllib.error.URLError) as exc:  # inclui ConnectionResetError
            last = exc
            wait = 2 ** i
            print(f"tentativa {i + 1}/{attempts} falhou ({exc}); nova tentativa em {wait}s", file=sys.stderr)
            time.sleep(wait)
    raise SystemExit(
        f"não foi possível baixar {url} após {attempts} tentativas: {last}\n"
        "Alternativa: abra a URL no navegador, salve a página (Ctrl+S, formato "
        "'Página da Web, somente HTML') e rode de novo com --file CAMINHO_DO_ARQUIVO."
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source_id")
    ap.add_argument("--grep", help="padrão (regex, sem distinção de maiúsculas) a procurar no texto")
    ap.add_argument("--context", type=int, default=4, help="linhas de contexto ao redor de cada ocorrência")
    ap.add_argument("--dry-run", action="store_true", help="não altera o YAML da fonte")
    ap.add_argument(
        "--file",
        type=Path,
        help="usar um arquivo já baixado (ex.: salvo pelo navegador) em vez de acessar a url da fonte",
    )
    args = ap.parse_args(argv)

    path = ROOT / "examples" / "sources" / f"{args.source_id}.yaml"
    if not path.exists():
        print(f"fonte não encontrada: {path}", file=sys.stderr)
        return 2
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    url = doc.get("url")
    if not url and not args.file:
        print("a fonte não tem `url`; use --file", file=sys.stderr)
        return 2

    if args.file:
        if not args.file.is_file():
            print(f"arquivo não encontrado: {args.file}", file=sys.stderr)
            return 2
        raw = args.file.read_bytes()
        ctype = "application/pdf" if args.file.suffix.lower() == ".pdf" else "text/html"
        origin = f"{args.file} (arquivo local; url da fonte: {url})"
    else:
        raw, ctype = fetch(url)
        origin = url
    ext = "pdf" if "pdf" in ctype or (url or "").lower().endswith(".pdf") else "html"
    CACHE.mkdir(exist_ok=True)
    cached = CACHE / f"{args.source_id}.{ext}"
    cached.write_bytes(raw)
    digest = hashlib.sha256(raw).hexdigest()
    print(f"origem  : {origin}")
    print(f"salvo   : {cached.relative_to(ROOT)} ({len(raw)} bytes)")
    print(f"sha256  : {digest}")

    if not args.dry_run:
        doc["sha256"] = digest
        doc["retrieved_at"] = date.today().isoformat()
        doc["retrieval_status"] = "RETRIEVED"
        if args.file:
            doc["notes"] = (doc.get("notes") or "").rstrip() + (
                f"\nRecuperado em {date.today().isoformat()} a partir de arquivo salvo manualmente "
                f"({args.file.name}); o hash é do arquivo salvo, não do stream HTTP."
            )
        path.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=100), encoding="utf-8")
        print(f"YAML    : {path.relative_to(ROOT)} atualizado (sha256, retrieved_at, retrieval_status)")

    if args.grep:
        if ext != "html":
            print("--grep só funciona para fontes HTML; abra o PDF manualmente", file=sys.stderr)
            return 0
        lines = [ln.strip() for ln in html_to_text(raw).splitlines()]
        lines = [ln for ln in lines if ln]
        pat = re.compile(args.grep, re.IGNORECASE)
        hits = [i for i, ln in enumerate(lines) if pat.search(ln)]
        print(f"\n{len(hits)} ocorrência(s) de /{args.grep}/:\n")
        for i in hits:
            lo, hi = max(0, i - args.context), min(len(lines), i + args.context + 1)
            for j in range(lo, hi):
                mark = ">>" if j == i else "  "
                print(f"{mark} {lines[j]}")
            print("-" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main())
