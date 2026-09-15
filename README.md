# PONTE Tributos

Camada de **inteligência de decisão tributária** da Ponte Estruturação de Projetos.

O sistema não responde "qual imposto devo pagar?". Ele responde:

> **O que a estrutura tributária atual e futura significa para as decisões econômicas desta empresa?**

Para isso, ele integra fontes com autoridades distintas (legislação, dados oficiais, pesquisa econômica, bibliotecas de cálculo, documentos do cliente) em um **modelo canônico** com proveniência, vigência temporal e verificação explícita de cada afirmação.

## Regra fundadora

[`DEC-001`](docs/decisions/DEC-001-autoridade-da-conclusao.md):

> Nenhuma conclusão tributária é verdadeira por ter sido produzida por código, LLM, estudo ou manual. Sua autoridade deriva da fonte normativa aplicável, da vigência temporal e dos fatos demonstrados da empresa.

## Arquitetura em sete camadas

```text
L0  SOURCES              tudo entra como fonte, nunca como verdade
L1  EVIDENCE             trechos, valores e registros recuperáveis até o original
L2  NORMATIVE RULES      texto jurídico transformado em regra computável, com vigência
L3  BUSINESS FACTS       o gêmeo digital tributário de cada empresa
L4  COMPUTATION          motores de cálculo testados contra o modelo canônico
L5  CLAIMS / ANALYSIS    afirmações candidatas submetidas ao motor de confrontação
L6  ADVISORY DECISIONS   decisões auditáveis, com premissas, snapshot e versão

transversal: TIME + AUTHORITY + PROVENANCE
```

Detalhes em [`docs/arquitetura/01-camadas.md`](docs/arquitetura/01-camadas.md).

## Mapa do repositório

| Caminho | Conteúdo |
| --- | --- |
| `docs/decisions/` | Registros de decisão arquitetural (`DEC-nnn`) |
| `docs/arquitetura/` | Camadas, fontes e autoridade, modelo canônico, temporalidade, confrontação, watcher normativo, integrações, produtos |
| `schemas/` | JSON Schema (draft 2020-12) de cada objeto canônico |
| `examples/` | Instâncias YAML de referência, validadas em CI contra os schemas |
| `tools/validate.py` | Validador de schemas e de integridade referencial |
| `tests/` | Testes que executam o validador |

## Modelo canônico mínimo

Doze objetos de domínio:

```text
Source  Evidence  Authority  Rule  Entity  Taxpayer
Transaction  TaxTreatment  Calculation  Observation  Claim  Decision
```

Três objetos de governança:

```text
Version  Review  Provenance
```

Três relações obrigatórias:

```text
Evidence  SUPPORTS      Claim
Rule      GOVERNS       Calculation
Decision  DERIVES_FROM  Claims
```

Detalhes em [`docs/arquitetura/03-modelo-canonico.md`](docs/arquitetura/03-modelo-canonico.md).

## Validar localmente

```bash
pip install -r requirements-dev.txt
python tools/validate.py
pytest
```

O validador checa cada arquivo em `examples/` contra o schema da sua pasta e, em seguida, verifica as referências cruzadas (toda evidência aponta para uma fonte existente, toda regra para evidências existentes, toda decisão para claims existentes, cadeias de `supersedes` sem sobreposição de vigência).

## Estado atual

Este repositório contém a **especificação e o modelo canônico**. Motores de ingestão, watcher normativo, adaptadores (MCP Fiscal Brasil, MCIBr) e produtos serão construídos sobre estes schemas. Nada aqui é parecer tributário.

## Licença

MIT. Ver [`LICENSE`](LICENSE).
