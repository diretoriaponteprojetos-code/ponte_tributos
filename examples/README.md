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
ADV-0034-2026-09-001            decisão em rascunho com premissas 8 / 7 / 1
```

## Avisos

- **Todos os valores do cliente, do dataset e dos cenários são fixtures ilustrativos.** Não descrevem nenhuma empresa real.
- **Hashes `sha256` compostos só de zeros são placeholders.** Ao ingerir a fonte real, substitua pelo hash do arquivo recuperado.
- **A LC 214/2025 (`SRC-RFB-LC214`) foi recuperada do Planalto em 2026-10-29** com `tools/ingest_source.py`. `EV-000381` (art. 346, CBS 0,9%), `EV-000383` (art. 343, IBS 0,1%) e `EV-000384` (art. 348, disposições comuns de 2026, incluindo a exclusão do Simples Nacional e a dispensa de recolhimento) estão `VERIFIED_AGAINST_SOURCE` com transcrição literal. Com isso, `CLM-0034-CBS-2026-01` é o primeiro claim `VERIFIED` do repositório.
- **As demais evidências normativas estão com `verification_status: PENDING`** porque ainda não foram conferidas contra o arquivo recuperado. [`DEC-001`](../docs/decisions/DEC-001-autoridade-da-conclusao.md) proíbe promover a `VERIFIED` sem a conferência. A decisão de exemplo segue `DRAFT` porque a premissa sobre as alíquotas de 2027 continua hipótese.
- A fonte Ipea `11058/17421` está `retrieval_status: PENDING` (timeout na sessão de fundação). Nenhuma evidência foi extraída dela.
