# 05 — Motor de confrontação

É o coração do sistema. Toda afirmação candidata (`Claim`) passa por uma bateria de verificações antes de poder sustentar uma `Decision`.

## Checklist obrigatório

```text
CLAIM
 │
 ├── existe fonte?
 ├── fonte tem autoridade suficiente?
 ├── estava vigente?
 ├── escopo coincide?
 ├── entidade coincide?
 ├── produto/CNAE coincide?
 ├── jurisdição coincide?
 ├── período coincide?
 ├── existem exceções?
 ├── existem evidências contraditórias?
 ├── o cálculo é reproduzível?
 └── o resultado depende de hipótese?
```

Cada item vira um campo em `claim.verification.checks` (schema [`claim`](../../schemas/claim.schema.json)), com valor `PASS`, `FAIL`, `NOT_APPLICABLE` ou `UNKNOWN`. `PASS` significa sempre resultado **favorável** ao claim; por isso o último item se chama `free_of_hypothesis` (PASS = não depende de hipótese).

| Pergunta | Check |
| --- | --- |
| existe fonte? | `source_exists` |
| fonte tem autoridade suficiente? | `authority_sufficient` |
| estava vigente? | `in_force` |
| escopo coincide? | `scope` |
| entidade coincide? | `entity` |
| produto/CNAE coincide? | `product_or_cnae` |
| jurisdição coincide? | `jurisdiction` |
| período coincide? | `period` |
| existem exceções? | `exceptions` (PASS = nenhuma exceção aplicável) |
| existem evidências contraditórias? | `contradictory_evidence` (PASS = nenhuma) |
| o cálculo é reproduzível? | `reproducible` |
| o resultado depende de hipótese? | `free_of_hypothesis` (PASS = não depende) |

## Resultado

O status é uma categoria, não um score:

| Status | Significado | Pode sustentar decisão? |
| --- | --- | --- |
| `VERIFIED` | todos os checks aplicáveis passaram | sim |
| `PARTIALLY_SUPPORTED` | parte das premissas verificada, parte não | sim, com premissas listadas |
| `SCENARIO_ONLY` | depende de hipótese sobre o futuro ou sobre fatos não observados | sim, como cenário |
| `CONTRADICTED` | existe evidência contrária de autoridade igual ou superior | não |
| `INCOMPARABLE` | escopo, entidade, período ou jurisdição não coincidem | não |
| `STALE` | a regra ou evidência de suporte não estava vigente no período | não |
| `INSUFFICIENT_EVIDENCE` | faltam evidências para decidir | não |

Isso é muito superior a um simples score de confiança: cada status diz **o que fazer** (buscar evidência, esperar norma, listar premissa, descartar).

## Mapeamento de checks para status

Ordem de avaliação, a primeira condição que bate define o status:

1. algum check `FAIL` em `contradictory_evidence` → `CONTRADICTED`
2. algum check `FAIL` em `scope`, `entity`, `product_or_cnae`, `jurisdiction`, `period` → `INCOMPARABLE`
3. check `FAIL` em `in_force` → `STALE`
4. check `FAIL` em `source_exists` ou `authority_sufficient` → `INSUFFICIENT_EVIDENCE`
5. check `FAIL` em `free_of_hypothesis` (isto é, depende de hipótese) → `SCENARIO_ONLY`
6. alguma premissa `UNVERIFIED` → `PARTIALLY_SUPPORTED`
7. caso contrário → `VERIFIED`

## Premissas

Toda `Claim` de natureza `SCENARIO` ou `COMPUTATION` declara premissas individualmente:

```yaml
premises:
  - id: P1
    statement: "Mix de vendas B2B/B2C mantido em 2027"
    status: UNVERIFIED
  - id: P2
    statement: "Alíquota de referência CBS 2027 conforme snapshot CANON-2026-09-15"
    status: VERIFIED
    supported_by: [EV-000381]
```

Uma `Decision` agrega contagens: `premises_total`, `premises_verified`, `premises_unverified`.

## Pergunta futura, resposta defensável

O empresário pergunta: "Vale a pena abrir uma filial em Pernambuco?"

O sistema:

```text
1.  identifica empresa atual
2.  identifica CNAEs
3.  identifica produtos
4.  identifica mix vendas
5.  identifica clientes PE
6.  recupera regras vigentes
7.  calcula cenário atual
8.  calcula cenário PE
9.  verifica incentivos possíveis
10. calcula custos adicionais
11. compara cenários
12. lista pressupostos
13. produz sensibilidade
```

E responde não "PE é melhor", mas:

```text
Cenário PB:            R$ X
Cenário PE:            R$ Y
Diferença:             R$ Z

63% da vantagem depende de:
  - hipótese A
  - enquadramento B
  - volume C

Ponto de equilíbrio:   R$ ...
Evidências faltantes:  ...
```
