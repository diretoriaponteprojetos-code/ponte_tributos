# DEC-001 — Autoridade de uma conclusão tributária

| Campo | Valor |
| --- | --- |
| Status | ACEITA |
| Data | 2026-09-15 |
| Escopo | Todo o sistema PONTE Tributos |
| Supersede | — |

## Decisão

> **Nenhuma conclusão tributária é verdadeira por ter sido produzida por código, LLM, estudo ou manual. Sua autoridade deriva da fonte normativa aplicável, da vigência temporal e dos fatos demonstrados da empresa.**

## Contexto

O sistema integra fontes com naturezas muito diferentes:

- legislação e atos normativos (Planalto, Receita Federal, CGIBS, CGSN, Confaz, SEFAZ, prefeituras);
- dados oficiais de arrecadação e cadastro (Receita Federal);
- pesquisa econômica (Ipea, ObservaBR);
- bibliotecas de cálculo e ferramentas (MCIBr, mcp-fiscal-brasil);
- documentos do cliente (SPED, NF-e, NFS-e, ERP, contabilidade);
- julgamento profissional (contador, advogado, especialista).

Cada uma dessas fontes é capaz de afirmar algo, mas nenhuma delas é capaz de decidir tudo. Ver [`02-fontes-e-autoridade.md`](../arquitetura/02-fontes-e-autoridade.md).

## Motivação concreta

Dois exemplos observados em setembro de 2026:

1. O simulador de regimes do `mcp-fiscal-brasil` declara usar cálculo simplificado, premissas médias e tabelas de 2025 (por exemplo, margem presumida de 15% no Lucro Real, PIS/Cofins a 9,25% sobre faturamento, ISS 5%, ICMS 12%). É um bom **simulador preliminar**, e seria um mau **motor canônico de planejamento**.
2. O manual do MCIBr traz exemplos como `SetAliquotaUF(17.5)` e `SetAliquotaMUN(2.0)` para IBS sob o rótulo genérico "Reforma Tributária 2026+", enquanto a Receita Federal registra para 2026 as alíquotas de teste de CBS 0,9% e IBS 0,1%. O código não está "errado": é um exemplo parametrizado. Mas **o sistema não pode confundir exemplo de biblioteca com regra vigente**.

## Consequências

1. Todo objeto que afirma algo (`Claim`, `Decision`, `Calculation`) carrega obrigatoriamente: fontes, evidências, regras aplicadas, período, snapshot normativo e versão do motor de cálculo.
2. Nenhuma saída de LLM, biblioteca ou estudo entra no modelo como `Rule` ou `Decision` sem passar pelas camadas L0 → L1 → L2 e pelo motor de confrontação ([`05-motor-de-confrontacao.md`](../arquitetura/05-motor-de-confrontacao.md)).
3. Bibliotecas de cálculo são **testadas contra o modelo canônico**, nunca o contrário.
4. Estudos e pesquisas entram com `applicability.client_specific: false` e só podem ser usados como benchmark ou contexto econômico.
5. Toda regra tem vigência explícita. Correções nunca sobrescrevem: criam nova versão com `supersedes` ([`04-temporalidade.md`](../arquitetura/04-temporalidade.md)).
6. O sistema nunca devolve um número isolado. Ver a regra inegociável em [`03-modelo-canonico.md`](../arquitetura/03-modelo-canonico.md#regra-inegociável-de-saída).
