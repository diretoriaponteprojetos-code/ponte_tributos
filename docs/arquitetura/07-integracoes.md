# 07 — Integrações: papéis de cada componente

| Componente | Papel | Nível de autoridade |
| --- | --- | --- |
| MCIBr | candidato a **motor de cálculo** | `SOFTWARE` |
| mcp-fiscal-brasil | candidato a **camada de ferramentas / conectores** | `SOFTWARE` |
| Receita Federal / Planalto / CGIBS | **autoridade normativa + dados oficiais** | `NORMATIVE`, `OFFICIAL_DATA` |
| Ipea | **evidência econômica** | `RESEARCH` |
| ObservaBR | **pesquisa e debate especializado** | `RESEARCH` |
| dados do cliente | **verdade operacional individual** | `CLIENT_RECORD` |
| PONTE Canonical Model | **sistema de integração e decisão** | — |

## mcp-fiscal-brasil: adaptador, não cérebro

O projeto expõe ferramentas para CNPJ, Simples, NF-e, SPED, eSocial e análises de compliance, além de workflows agentic. Ele alimenta o modelo canônico **sempre** através de um adaptador:

```text
MCP Fiscal
     ↓
PONTE Adapter
     ↓
Canonical Schema
```

Nunca:

```text
MCP Fiscal
     ↓
cliente
```

Mapeamento de ferramentas para objetos canônicos:

| Ferramenta MCP | Adaptador | Objeto canônico produzido |
| --- | --- | --- |
| `consultar_cnpj()` | `normalize()` | `Entity` / `Taxpayer` (identidade, CNAEs, regime) |
| `summarize_sped()` | `extract_evidence()` | `Evidence[]` (`CLIENT_RECORD`) + `Observation[]` |
| parsing de NF-e / NFS-e | `extract_transactions()` | `Transaction[]` |
| `compare_tax_regimes()` | `to_scenario_candidate()` | `Claim` com `nature: SCENARIO`, status inicial `SCENARIO_ONLY` |

Nunca produz `Decision`.

Motivo registrado em [`DEC-001`](../decisions/DEC-001-autoridade-da-conclusao.md): o simulador de regimes declara premissas médias e tabelas de 2025. Todo `Claim` gerado a partir dele nasce com as premissas do simulador listadas como `UNVERIFIED`.

O `Source` correspondente registra o **commit** do repositório. O projeto está ativamente sendo atualizado (commits de setembro de 2026 em CNPJ, NF-e e auditoria de supply chain); o commit é o que torna a evidência reproduzível.

## MCIBr: motor de cálculo testado contra o canônico

O manual cobre ICMS, ST, IPI, PIS/Cofins, ISS, Simples, IBS, CBS etc. Ele entra como `COMPUTATION ENGINE CANDIDATE`, não como base de conhecimento.

```text
CANONICAL RULE
      ↓
TEST CASE
      ↓
MCIBr
      ↓
RESULT
      ↓
REFERENCE RESULT
      ↓
COMPARE
```

O MCIBr é **testado contra o modelo canônico**. Não o contrário. Exemplos de alíquota no manual (`SetAliquotaUF(17.5)`, `SetAliquotaMUN(2.0)`) são parâmetros de exemplo, não regras vigentes; o motor só é executado com os parâmetros que uma `Rule` `ACTIVE` fornece.

Cada execução produz um `Calculation` com `engine.name`, `engine.version`, `engine.commit`, `governed_by[]` e, quando houver, `reference_result` e `comparison`.

## Ipea e ObservaBR: contexto econômico, não cálculo

Eles não calculam o imposto da empresa. Eles ajudam a responder "o que isso significa economicamente?".

```yaml
research_finding:
  id: RF-029
  claim: ...
  population: empresas brasileiras
  period: ...
  method: ...
  source: SRC-IPEA-...
  applicability:
    client_specific: false
  use: benchmark
```

`client_specific: false` é obrigatório e fixo no schema. Um estudo sobre 100 mil empresas não prova nada sobre a Empresa X.

Exemplos de uso legítimo: benchmarks de carga efetiva por regime, evidência sobre regressividade, imposto seletivo, cashback, relação entre alíquotas estatutárias e efetivas.

## Receita Federal: dados abertos

A Receita disponibiliza datasets estruturados de arrecadação, cadastros, carga tributária, parcelamentos, compensações, comércio exterior etc., inclusive séries por CNAE, município, estado e natureza jurídica. Cada dataset entra como `Source` de tipo `official_dataset`; cada célula relevante vira `Evidence` com `dimensions`, `value` e `unit`.
