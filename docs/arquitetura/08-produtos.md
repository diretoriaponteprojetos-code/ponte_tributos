# 08 — Produtos PONTE sobre a mesma infraestrutura

Cinco produtos. Não cinco sistemas. Uma única base canônica gera todos.

| Produto | O que entrega | Camadas que consome |
| --- | --- | --- |
| **Radar Fiscal** | mudanças regulatórias que atingem aquela empresa | L2 + L3 + watcher ([`06`](06-watcher-normativo.md)) |
| **Diagnóstico Tributário** | o que paga, por quê, comparação e anomalias | L3 + L4 + L5 |
| **Simulador Estratégico** | regime, preços, fornecedores, localidades, investimentos | L2 + L3 + L4 + L5 |
| **Auditoria de Oportunidades** | créditos, incentivos, enquadramentos, desperdícios e inconsistências | L1 + L2 + L3 + L5 |
| **Conselheiro Fiscal Executivo** | tradução financeira e estratégica para o empresário | L6 |

## O produto não deve parecer jurídico

O empresário não quer "artigo 347 da LC X". Ele quer:

### Hoje

```text
Você faturou                  R$ 8.420.000
Tributos apurados             R$ 1.634.000
Carga observada                    19,41%
```

### Diagnóstico

```text
Carga estrutural esperada          18,70%
Carga observada                    19,41%

Diferença                           0,71 p.p.
```

### Por quê?

```text
1. créditos não apropriados
2. mix estadual
3. regime de determinados produtos
4. operação específica sem benefício
```

### O que pode ser feito?

```text
Ação                    impacto      evidência       risco
Revisar crédito X       R$...         alta            baixo
Rever cadastro NCM      R$...         média           médio
Simular regime Y        R$...         cenário         —
```

Isso é consultoria. A base jurídica continua inteira por baixo, em `Rule`, `Evidence` e `Claim`, disponível para o contador, o advogado e a auditoria.

## Posicionamento

Não competimos com contador, ERP, software fiscal ou biblioteca tributária. Criamos a camada que quase sempre falta entre eles:

```text
                     EMPRESÁRIO
                         ▲
                         │
                 DECISÃO ECONÔMICA
                         ▲
                         │
                    PONTE
               Decision Intelligence
                         ▲
          ┌──────────────┼──────────────┐
          │              │              │
      Fiscal          Contábil      Econômico
          │              │              │
        ERP/SPED       empresa      IPEA/estudos
          │
      legislação
```
