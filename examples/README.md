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
ADV-0034-2026-09-001            decisão em rascunho com premissas 7 / 5 / 2
```

## Avisos

- **Todos os valores do cliente, do dataset e dos cenários são fixtures ilustrativos.** Não descrevem nenhuma empresa real.
- **Hashes `sha256` compostos só de zeros são placeholders.** Ao ingerir a fonte real, substitua pelo hash do arquivo recuperado.
- **Evidências normativas estão com `verification_status: PENDING`** porque o texto e o locator ainda não foram conferidos contra o arquivo recuperado. Isso é intencional: [`DEC-001`](../docs/decisions/DEC-001-autoridade-da-conclusao.md) proíbe promover a `VERIFIED` sem a conferência. Por consequência, a decisão de exemplo está `DRAFT` e nenhum claim está `VERIFIED`.
- **A LC 214/2025 (`SRC-RFB-LC214`) está `retrieval_status: PENDING`.** O ambiente de fundação bloqueava todos os repositórios oficiais de legislação. Por fontes secundárias convergentes, os locators foram fixados em art. 346 (CBS 0,9%, `EV-000381`), art. 343 (IBS 0,1%, `EV-000383`) e art. 348, § 1º (dispensa condicionada, `EV-000384`). Para concluir a recuperação e conferir a redação literal:

  ```bash
  python tools/ingest_source.py SRC-RFB-LC214 --grep "Art. 34[368]"
  ```
- A fonte Ipea `11058/17421` está `retrieval_status: PENDING` (timeout na sessão de fundação). Nenhuma evidência foi extraída dela.
