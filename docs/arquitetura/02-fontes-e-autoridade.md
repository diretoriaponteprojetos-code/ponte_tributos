# 02 — Fontes e autoridade

Essas fontes **não têm a mesma autoridade**. Esse é o ponto de partida de tudo.

| Fonte | O que ela pode dizer | O que ela não deveria decidir |
| --- | --- | --- |
| **Receita Federal / Planalto / CGIBS** | regra vigente, obrigação, cadastro, arrecadação, leiaute, prazo | se determinada estratégia é economicamente melhor para a empresa |
| **Ipea** | evidência econômica, incidência, distribuição, efeitos, pesquisas | obrigação fiscal individual |
| **ObservaBR** | estudos, evidências, interpretações e debate tributário | regra jurídica vigente |
| **MCIBr** | implementação computacional / cálculo | qual é a norma correta |
| **mcp-fiscal-brasil** | ferramentas, integrações, parsing, consultas, estimativas | fonte final de verdade tributária |
| **documentos do cliente** | o que efetivamente ocorreu na empresa | norma aplicável |
| **contador / advogado / especialista** | julgamento profissional contextualizado | alterar silenciosamente evidência ou legislação |

## Níveis de autoridade no modelo

O campo `authority_level` (definido em [`schemas/common.schema.json`](../../schemas/common.schema.json)) classifica toda fonte:

| Nível | Uso permitido | Exemplos |
| --- | --- | --- |
| `NORMATIVE` | fundamentar `Rule` | EC 132/2023, LC 214/2025, LC 227/2026, atos RFB/CGIBS/CGSN/Confaz/SEFAZ |
| `OFFICIAL_DATA` | fundamentar `Evidence` quantitativa e benchmarks | datasets de arrecadação, cadastro, carga tributária, comércio exterior da RFB |
| `RESEARCH` | fundamentar `ResearchFinding` (benchmark, contexto) | Ipea, ObservaBR |
| `SOFTWARE` | fundamentar `Calculation` como motor candidato | MCIBr, mcp-fiscal-brasil |
| `CLIENT_RECORD` | fundamentar `Observation`, `Transaction`, `Taxpayer` | SPED, NF-e, NFS-e, ERP |
| `PROFESSIONAL_JUDGMENT` | fundamentar `Review` | contador, advogado, especialista |

Uma `Rule` só pode citar fontes `NORMATIVE`. Uma `Decision` só pode derivar de `Claims`. Um `ResearchFinding` nunca é `client_specific`.

## O que cada fonte responde

```text
RFB:        quanto foi arrecadado
Cliente:    quanto ele pagou
Norma:      quanto deveria incidir
Ipea:       quais efeitos econômicos são observados
ObservaBR:  quais evidências existem sobre incidência/distribuição
PONTE:      qual é a consequência gerencial para este cliente
```

## Contexto normativo em setembro de 2026

Registro do estado observado na data de fundação deste repositório. Cada item abaixo deve entrar no sistema como `Source` + `Evidence`, com hash e data de recuperação, antes de virar `Rule`.

- A Receita Federal informa que 2026 é o ano de teste de IBS/CBS e que, cumpridas determinadas obrigações acessórias, há dispensa do recolhimento; há orientações próprias para emissão dos documentos fiscais.
- A legislação relevante inclui EC 132/2023, LC 214/2025, LC 227/2026, regulamentação e atos posteriores.
- A Receita registra para a transição a referência de **CBS 0,9% e IBS 0,1% em 2026**.
- Em agosto de 2026 o CGSN atualizou regras do Simples Nacional para adequação ao IBS/CBS.
- Em julho de 2026 RFB e CGIBS publicaram cronograma conjunto de implementação dos documentos fiscais eletrônicos.

Um PDF ou RAG congelado envelheceria imediatamente. Ver [`06-watcher-normativo.md`](06-watcher-normativo.md).

## Fontes ainda não recuperadas

- Ipea, handle `11058/17421`: o repositório respondeu com timeout na sessão de fundação. Nenhum conteúdo deve ser atribuído a esse item até que o PDF e os metadados sejam recuperados e registrados como `Source` com hash. O exemplo em [`examples/sources/SRC-IPEA-17421.yaml`](../../examples/sources/SRC-IPEA-17421.yaml) está marcado como `retrieval_status: PENDING`.
- LC 214/2025 (`SRC-RFB-LC214`): o ambiente de fundação bloqueava, por política de rede, os domínios oficiais de legislação. A recuperação foi concluída em 2026-10-29 a partir de uma estação Windows com `tools/ingest_source.py`, que gravou o hash do HTML do Planalto. A conferência contra o texto oficial confirmou: **art. 343** fixa o IBS estadual a 0,1% em 2026 (`EV-000383`), **art. 346** fixa a CBS a 0,9% em 2026 (`EV-000381`) e **art. 348** abre a Seção III, "Disposições Comuns ao IBS e à CBS em 2026" (`EV-000384`): compensação do montante recolhido com PIS/Cofins, aplicação das alíquotas de teste com redução nos regimes diferenciados e sobre as bases dos regimes específicos, **não aplicação aos optantes do Simples Nacional** (inciso III, "c"), dispensa de recolhimento para quem cumprir as obrigações acessórias (§ 1º) e, por inserção da LC 227/2026, prazo de 60 dias para suprir omissões autuadas (§§ 3º e 4º). Isso corrige a primeira versão do repositório, que atribuía as duas alíquotas ao art. 343, e a síntese secundária do art. 348, que omitia a exclusão do Simples. Fontes secundárias fixaram o locator; só o texto oficial promoveu as evidências a `VERIFIED_AGAINST_SOURCE`.
- Regras de 2027 a 2028 modeladas a partir do mesmo HTML, em `DRAFT` até revisão humana: `TAX-IBS-2027-UF-001` e `TAX-IBS-2027-MUN-001` (art. 344: 0,05% estadual e 0,05% municipal) e `TAX-CBS-2027-001` (art. 347: alíquota-padrão do art. 14 reduzida em 0,1 ponto percentual, modelada como `RATE_FORMULA` porque a lei não traz número). O valor da alíquota-padrão ou de referência da CBS para 2027 depende de lei específica da União ou da fixação da alíquota de referência (art. 18, ainda não transcrito), e é o item que o watcher normativo deve capturar.
- Página institucional "Entenda a Reforma Tributária do Consumo" (`SRC-RFB-ENTENDA-RTC`): recuperada e conferida em 2026-10-29 (`EV-000382`). É corroboração, não norma: usa "isenta a arrecadação da taxa de prova" onde a lei diz "dispensado o recolhimento".

## Como recuperar uma fonte

```bash
python tools/ingest_source.py SRC-RFB-LC214 --grep "Art. 346"
```

O script baixa o arquivo da `url` da fonte para `sources_cache/`, grava o `sha256`, atualiza `retrieved_at` e `retrieval_status` no YAML, e imprime as ocorrências do padrão com contexto para conferência humana. Ele nunca altera uma `Evidence`.
