# 06 — Watcher normativo e impacto de mudança

## Pipeline

```text
Receita Federal
Planalto
CGIBS
Confaz
SEFAZ-PB (e demais UFs conforme portfólio)
Prefeituras
CGSN
Diário Oficial
       ↓
change detector
       ↓
candidate_update            (schema candidate_update)
       ↓
diff normativo
       ↓
impact analysis             (consulta ao portfólio de Taxpayers)
       ↓
human review                (schema review)
       ↓
new canonical rule          (Rule com supersedes, ver 04-temporalidade)
```

Toda detecção gera um `CandidateUpdate` (`CU-`). Nenhuma `Rule` nasce `ACTIVE` a partir do watcher: nasce `CANDIDATE` e depende de `Review` aprovada.

## Não basta dizer "saiu regra nova"

O sistema pergunta: **quais clientes são afetados?**

```text
nova regra:
  CNAE X + operação Y + data Z

consulta ao portfólio:
  cliente A → AFFECTED
  cliente B → NOT_AFFECTED
  cliente C → POSSIBLE_IMPACT
  cliente D → INSUFFICIENT_DATA
```

## Alerta ao cliente

Saída do `impact_analysis`, por cliente:

```text
ALERTA CLIENTE 037

Mudança:
  ...

Afeta:
  18,4% das operações dos últimos 12 meses

Receita envolvida:
  R$ 1,8 milhão

Impacto projetado:
  cenário A
  cenário B
  cenário C

Evidência necessária:
  ...

Prazo operacional:
  ...
```

Aqui começa a monetização séria: o produto **Radar Fiscal** ([`08-produtos.md`](08-produtos.md)) é a face comercial deste pipeline.

## Fontes a monitorar (mínimo inicial)

| Fonte | O que observar |
| --- | --- |
| Planalto | leis complementares, decretos, medidas provisórias |
| Receita Federal | instruções normativas, atos declaratórios, orientações da reforma, cronogramas, leiautes |
| CGIBS | atos do Comitê Gestor do IBS, cronogramas conjuntos com RFB |
| CGSN | resoluções do Simples Nacional |
| Confaz | convênios e ajustes SINIEF |
| SEFAZ das UFs do portfólio | decretos, portarias, benefícios |
| Prefeituras dos municípios do portfólio | ISS e, na transição, IBS municipal |
| Diário Oficial da União | publicação primária |
