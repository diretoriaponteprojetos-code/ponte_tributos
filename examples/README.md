# Exemplos de referência

Instâncias YAML do modelo canônico, uma por arquivo, nomeadas pelo próprio ID (`<ID>.yaml`). Cada pasta corresponde a um schema em `schemas/` (mapeamento em `tools/validate.py`).

Os exemplos contam uma única história, encadeada:

```text
AUT-*                           quem pode afirmar o quê
SRC-*                           fontes (lei, orientação RFB, dataset, pesquisa, software, documentos do cliente)
EV-*                            evidências recuperáveis até a fonte
TAX-CBS-2026-001, TAX-IBS-2026-001   alíquotas de teste 2026 (ACTIVE, com Review)
RULE-100 → RULE-101             cadeia supersedes (Simples Nacional, adequação CGSN ago/2026)
CU-2026-08-CGSN-001             detecção pelo watcher + impacto no portfólio
ENT-0034 / TP-0034              cliente fictício (gêmeo digital)
TX-*, OBS-*                     operações e métricas observadas
CALC-*                          motor canônico PONTE e motor candidato MCIBr comparados
TT-*                            tratamento tributário de uma operação
CLM-*                           claims (RULE_APPLICATION, SCENARIO, BENCHMARK) confrontados
RF-029                          achado de pesquisa, client_specific: false
ADV-0034-2026-09-001            decisão em rascunho com premissas 7 / 6 / 1
```

## Avisos

- **Todos os valores do cliente, do dataset e dos cenários são fixtures ilustrativos.** Não descrevem nenhuma empresa real.
- **Hashes `sha256` compostos só de zeros são placeholders.** Ao ingerir a fonte real, substitua pelo hash do arquivo recuperado.
- **A LC 214/2025 (`SRC-RFB-LC214`) foi recuperada do Planalto em 2026-10-29** com `tools/ingest_source.py`. `EV-000381` (art. 346, CBS 0,9%) e `EV-000383` (art. 343, IBS 0,1%) estão `VERIFIED_AGAINST_SOURCE` com transcrição literal do caput. `EV-000384` (art. 348, § 1º, dispensa condicionada) segue `PENDING`: o trecho exibido cortou antes do parágrafo. Para concluir, sem baixar de novo:

  ```bash
  python tools/ingest_source.py SRC-RFB-LC214 --file sources_cache/SRC-RFB-LC214.html --dry-run --grep "Art. 348" --context 60
  ```

- **As demais evidências normativas estão com `verification_status: PENDING`** porque ainda não foram conferidas contra o arquivo recuperado. [`DEC-001`](../docs/decisions/DEC-001-autoridade-da-conclusao.md) proíbe promover a `VERIFIED` sem a conferência. Por consequência, a decisão de exemplo está `DRAFT` e nenhum claim está `VERIFIED`.
- A fonte Ipea `11058/17421` está `retrieval_status: PENDING` (timeout na sessão de fundação). Nenhuma evidência foi extraída dela.
