# 01 — As sete camadas

```text
L0  SOURCES
    ↓
L1  EVIDENCE
    ↓
L2  NORMATIVE RULES
    ↓
L3  BUSINESS FACTS
    ↓
L4  COMPUTATION
    ↓
L5  CLAIMS / ANALYSIS
    ↓
L6  ADVISORY DECISIONS
```

Camada transversal, presente em todos os objetos:

```text
TIME + AUTHORITY + PROVENANCE
```

## L0 — Sources

Tudo entra como fonte, nunca como verdade. Uma fonte é identificada, datada e assinada (hash, commit, handle).

```yaml
source:
  id: SRC-RFB-LC214
  type: legislation
  publisher: Presidência da República
  title: Lei Complementar 214/2025
  retrieved_at: 2026-09-15
  sha256: ...
```

Para software, o commit é obrigatório:

```text
mcp-fiscal hoje  ≠  mcp-fiscal daqui a 6 meses
```

Schema: [`schemas/source.schema.json`](../../schemas/source.schema.json).

## L1 — Evidence

Aqui nada é interpretado. Um trecho de lei, uma célula de dataset ou um registro de SPED viram evidência com locator, texto ou valor, e data de observação. Tudo continua recuperável até o original.

Schema: [`schemas/evidence.schema.json`](../../schemas/evidence.schema.json).

## L2 — Normative Rules

Texto jurídico vira **regra computável**. Gravar "CBS é 0,9%" é insuficiente. A verdade completa é:

```text
CBS = 0,9%
ONDE?
QUANDO?
PARA QUEM?
SOB QUAIS CONDIÇÕES?
COM QUAIS EXCEÇÕES?
SEGUNDO QUAL NORMA?
```

A chave canônica de uma regra é:

```text
tributo
+ hipótese de incidência
+ jurisdição
+ regime
+ CNAE/NCM/NBS
+ data
+ situação da empresa
```

Schema: [`schemas/rule.schema.json`](../../schemas/rule.schema.json).

## L3 — Business Facts

O gêmeo digital tributário da empresa: identidade fiscal, estabelecimentos, CNAEs, regimes, produtos/NCM, serviços/NBS, fornecedores, clientes, municípios/UFs, faturamento, compras, folha, créditos, benefícios, obrigações, processos, incentivos e histórico tributário.

Permite trocar a pergunta genérica ("qual regime é melhor para uma empresa de serviços?") pela pergunta que vale dinheiro:

> O que acontece com **esta empresa**, com **este mix de clientes**, **estas despesas**, **esta folha**, **estes créditos**, neste período?

Schemas: [`entity`](../../schemas/entity.schema.json), [`taxpayer`](../../schemas/taxpayer.schema.json), [`transaction`](../../schemas/transaction.schema.json), [`observation`](../../schemas/observation.schema.json).

## L4 — Computation

Motores de cálculo (MCIBr, motores PONTE, adaptadores do MCP Fiscal) recebem regras canônicas e fatos, e devolvem resultados reproduzíveis. Todo cálculo registra motor, versão, entradas, regras aplicadas e snapshot normativo.

Schemas: [`calculation`](../../schemas/calculation.schema.json), [`tax_treatment`](../../schemas/tax_treatment.schema.json).

## L5 — Claims / Analysis

Toda afirmação é um **candidato** até passar pelo motor de confrontação ([`05-motor-de-confrontacao.md`](05-motor-de-confrontacao.md)). Um `compare_tax_regimes()` do MCP Fiscal produz `SCENARIO_CANDIDATE`, nunca `DECISION`.

Schema: [`claims`](../../schemas/claim.schema.json).

## L6 — Advisory Decisions

A decisão aconselhável ao empresário, derivada de claims verificados, com premissas contadas, evidências faltantes listadas, sensibilidade e revisão humana.

Schema: [`decision`](../../schemas/decision.schema.json).

## Fluxo completo

```text
                 FONTES OFICIAIS
             RFB / Planalto / CGIBS
                      │
                      ▼
              NORMATIVE ENGINE
                      │
          ┌───────────┴───────────┐
          │                       │
          ▼                       ▼
      RULE STORE             EVENT STORE
                                   ▲
                                   │
                         SPED / NFe / NFSe
                         ERP / contabilidade
                                   │
                                   ▼
                        BUSINESS DIGITAL TWIN
                                   │
        ┌──────────────────────────┼───────────────┐
        │                          │               │
        ▼                          ▼               ▼
     MCIBr                    MCP Fiscal       PONTE engines
   calculation                adapters           analytics
        │                          │               │
        └───────────────┬──────────┴───────────────┘
                        ▼
                  SCENARIO ENGINE
                        │
                        ▼
                 CLAIM CANDIDATES
                        │
                  verification
                        │
                        ▼
                 ADVISORY LAYER
```
