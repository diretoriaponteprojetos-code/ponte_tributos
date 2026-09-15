# 04 — Temporalidade nativa

No tributário, tempo não é metadado: é parte da chave.

## Chave canônica de uma regra

Não é:

```text
tributo + regra
```

É:

```text
tributo
+ hipótese de incidência
+ jurisdição
+ regime
+ CNAE / NCM / NBS
+ data
+ situação da empresa
```

## Quatro datas distintas

Toda `Rule` e toda `Evidence` normativa distinguem:

| Campo | Significado |
| --- | --- |
| `publication_date` | quando o ato foi publicado |
| `legal_effect_from` / `valid_from` | a partir de quando produz efeitos |
| `legal_effect_until` / `valid_until` | até quando produz efeitos (`null` = vigente) |
| `retrieved_at` | quando o sistema recuperou o texto |

```yaml
validity:
  legal_effect_from: 2027-01-01
  legal_effect_until: null

publication_date: ...
retrieved_at: ...
supersedes: RULE-...
```

Assim uma mudança de 2028 não "corrige" retroativamente um cálculo de 2026.

## Correção nunca sobrescreve

Suponha que em janeiro o sistema possua `RULE-100` e em agosto saia nova regulamentação.

Não fazemos:

```text
UPDATE rule
```

Fazemos:

```text
RULE-100
  valid_until: 2026-08-31
  status: SUPERSEDED
  superseded_by: RULE-101

RULE-101
  valid_from: 2026-09-01
  supersedes: RULE-100
```

Então **o passado continua reproduzível**. Isso é indispensável para auditoria, planejamento, prestação de contas, contencioso, perícia e revisão tributária.

O validador verifica que, em toda cadeia `supersedes`, o `valid_until` da regra antiga é anterior ao `valid_from` da nova.

## Snapshot normativo

Um `normative_snapshot` (formato `CANON-YYYY-MM-DD`) identifica o conjunto de regras `ACTIVE` em uma data. Todo `Claim`, `Calculation` e `Decision` registra o snapshot com o qual foi produzido. Reexecutar com o mesmo snapshot e a mesma versão de motor deve reproduzir o mesmo resultado.

## Status de uma regra

```text
CANDIDATE    detectada pelo watcher, ainda não revisada
DRAFT        em modelagem
ACTIVE       vigente e revisada
SUPERSEDED   substituída por regra posterior (permanece consultável)
REVOKED      revogada sem sucessora
```

Uma `Rule` só passa de `DRAFT`/`CANDIDATE` para `ACTIVE` com uma `Review` aprovada.
