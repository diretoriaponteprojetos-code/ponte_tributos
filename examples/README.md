# Exemplos de referência

Instâncias YAML do modelo canônico, uma por arquivo, nomeadas pelo próprio ID (`<ID>.yaml`). Cada pasta corresponde a um schema em `schemas/` (mapeamento em `tools/validate.py`).

Os exemplos contam uma única história, encadeada:

```text
AUT-*                           quem pode afirmar o quê
SRC-*                           fontes (lei, orientação RFB, dataset, pesquisa, software, documentos do cliente)
EV-*                            evidências recuperáveis até a fonte
TAX-CBS-2026-001, TAX-IBS-2026-001   alíquotas de teste 2026 (ACTIVE, com Review)
TAX-CBS-2027-001, TAX-IBS-2027-*     alíquotas de 2027-2028 (DRAFT; CBS por fórmula, parâmetro ainda não fixado)
RULE-100 → RULE-101             cadeia supersedes (Simples Nacional, adequação CGSN ago/2026)
CU-2026-08-CGSN-001             detecção pelo watcher + impacto no portfólio
ENT-0034 / TP-0034              cliente fictício (gêmeo digital)
TX-*, OBS-*                     operações e métricas observadas
CALC-*                          motor canônico PONTE e motor candidato MCIBr comparados
TT-*                            tratamento tributário de uma operação
CLM-*                           claims (RULE_APPLICATION, SCENARIO, BENCHMARK) confrontados
RF-029                          achado de pesquisa, client_specific: false
ADV-0034-2026-09-001            decisão em rascunho com premissas 9 / 8 / 1
```

## Avisos

- **Todos os valores do cliente, do dataset e dos cenários são fixtures ilustrativos.** Não descrevem nenhuma empresa real.
- **Hashes `sha256` compostos só de zeros são placeholders.** Ao ingerir a fonte real, substitua pelo hash do arquivo recuperado.
- **A LC 214/2025 (`SRC-RFB-LC214`) e a página "Entenda" da RFB (`SRC-RFB-ENTENDA-RTC`) foram recuperadas em 2026-10-29** com `tools/ingest_source.py`. Estão `VERIFIED_AGAINST_SOURCE`, com transcrição literal: arts. 14, 343, 344, 346, 347 e 348 da LC 214 (`EV-000381`, `EV-000383` a `EV-000387`) e a seção "Transição" da página da RFB (`EV-000382`). Com isso, `CLM-0034-CBS-2026-01` é o primeiro claim `VERIFIED` do repositório.
- **As demais evidências normativas estão com `verification_status: PENDING`** porque ainda não foram conferidas contra o arquivo recuperado. [`DEC-001`](../docs/decisions/DEC-001-autoridade-da-conclusao.md) proíbe promover a `VERIFIED` sem a conferência.
- **A decisão de exemplo segue `DRAFT` por motivo real:** a LC 214/2025, art. 347, define a CBS de 2027-2028 como a alíquota-padrão do art. 14 reduzida em 0,1 ponto percentual, e a alíquota-padrão (ou de referência, art. 18) ainda não foi fixada por ato ingerido. A regra `TAX-CBS-2027-001` modela isso como `RATE_FORMULA`; a premissa P6 do cenário permanece hipótese até esse ato existir.
- A fonte Ipea `11058/17421` está `retrieval_status: PENDING` (timeout na sessão de fundação). Nenhuma evidência foi extraída dela.
