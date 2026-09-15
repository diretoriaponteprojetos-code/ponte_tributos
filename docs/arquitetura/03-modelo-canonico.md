# 03 — Modelo canônico mínimo

## Doze objetos de domínio

| Objeto | Camada | Prefixo de ID | Schema | O que representa |
| --- | --- | --- | --- | --- |
| `Source` | L0 | `SRC-` | [`source`](../../schemas/source.schema.json) | origem identificada, datada e assinada |
| `Evidence` | L1 | `EV-` | [`evidence`](../../schemas/evidence.schema.json) | trecho, valor ou registro sem interpretação |
| `Authority` | transversal | `AUT-` | [`authority`](../../schemas/authority.schema.json) | quem pode afirmar o quê |
| `Rule` | L2 | `RULE-` ou `TAX-` | [`rule`](../../schemas/rule.schema.json) | regra normativa computável com vigência |
| `Entity` | L3 | `ENT-` | [`entity`](../../schemas/entity.schema.json) | pessoa jurídica (cliente, fornecedor, contraparte) |
| `Taxpayer` | L3 | `TP-` | [`taxpayer`](../../schemas/taxpayer.schema.json) | gêmeo digital tributário de um cliente |
| `Transaction` | L3 | `TX-` | [`transaction`](../../schemas/transaction.schema.json) | operação econômica documentada |
| `TaxTreatment` | L4 | `TT-` | [`tax_treatment`](../../schemas/tax_treatment.schema.json) | tratamento tributário aplicado a uma operação |
| `Calculation` | L4 | `CALC-` | [`calculation`](../../schemas/calculation.schema.json) | execução reproduzível de um motor |
| `Observation` | L3 | `OBS-` | [`observation`](../../schemas/observation.schema.json) | métrica observada na empresa em um período |
| `Claim` | L5 | `CLM-` | [`claim`](../../schemas/claim.schema.json) | afirmação candidata submetida à confrontação |
| `Decision` | L6 | `ADV-` | [`decision`](../../schemas/decision.schema.json) | decisão aconselhável auditável |

Os registros de decisão **arquitetural** deste repositório usam o prefixo `DEC-` e vivem em `docs/decisions/`. Não são objetos do modelo.

## Três objetos de governança

| Objeto | Prefixo | Schema | Papel |
| --- | --- | --- | --- |
| `Version` | `VER-` | [`version`](../../schemas/version.schema.json) | versionamento de qualquer objeto, com `supersedes` |
| `Review` | `REV-` | [`review`](../../schemas/review.schema.json) | revisão humana com resultado explícito |
| `Provenance` | embutido | [`common#/$defs/provenance`](../../schemas/common.schema.json) | como, quando, por quem e com qual ferramenta o objeto foi produzido |

## Objetos auxiliares

| Objeto | Prefixo | Schema | Papel |
| --- | --- | --- | --- |
| `ResearchFinding` | `RF-` | [`research_finding`](../../schemas/research_finding.schema.json) | achado de pesquisa (Ipea, ObservaBR), sempre `client_specific: false` |
| `CandidateUpdate` | `CU-` | [`candidate_update`](../../schemas/candidate_update.schema.json) | mudança normativa detectada pelo watcher, com análise de impacto |

## Três relações obrigatórias

```text
Evidence  SUPPORTS      Claim         claim.supported_by[]     → evidence_id
Rule      GOVERNS       Calculation   calculation.governed_by[] → rule_id
Decision  DERIVES_FROM  Claims        decision.derives_from[]   → claim_id
```

O validador ([`tools/validate.py`](../../tools/validate.py)) rejeita qualquer referência a um ID inexistente.

## Regra inegociável de saída

O sistema jamais devolve apenas:

```text
economia potencial = R$ 317.442
```

Ele devolve:

```text
economia potencial:      R$ 317.442
nature:                  SCENARIO
premises:                7
verified premises:       5
unverified premises:     2
applicable period:       2027
normative snapshot:      CANON-2026-09-15
source set:              [...]
calculation version:     TAXENGINE-0.8.3
```

Um vende uma estimativa. O outro vende uma **decisão auditável**. O schema de `Decision` torna todos esses campos obrigatórios.

## Convenções

- IDs em maiúsculas, prefixo fixo, separados por hífen (`^PREFIXO-[A-Z0-9-]+$`).
- Datas em ISO 8601 (`YYYY-MM-DD`), timestamps com fuso.
- Valores monetários como objeto `{ amount, currency }`, nunca número solto.
- Alíquotas como objeto `{ value, unit: percent }`.
- Todo objeto de L2 em diante carrega `provenance`.
- Todo objeto de L5 e L6 carrega `normative_snapshot`.
