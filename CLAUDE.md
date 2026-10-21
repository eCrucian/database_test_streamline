# CLAUDE.md — database_test_streamline

CLI que mapeia um diretório com muitos repos Git já clonados (Python, PySpark, SQL AWS Presto/Athena,
Terraform, algum JavaScript), grava o mapeamento em formato legível por IA, e a partir dele propõe,
gera, executa e documenta testes de dados.

## Princípios inegociáveis

1. **Cobertura de testes unitários: 100% (linhas + branches).** Gate de CI. `# pragma: no cover` é proibido.
2. **Baixa complexidade ciclomatica:** `ruff` com `C901`, `max-complexity = 8`. Funções curtas, early return.
3. **Abstração só onde existe mais de uma implementação real hoje.** As únicas portas permitidas estão na seção "Portas". Qualquer porta nova exige justificativa escrita aqui.
4. **Código determinístico faz o trabalho pesado; o LLM só infere semântica e redige.** Parsing, lineage, grafos, hashing, templates e Mermaid são código. O LLM (inicialmente `qwen3:4b` via Ollama, modelo fraco de propósito) recebe contexto pequeno e responde com saída estruturada (Pydantic). Nada depende da qualidade do modelo para estar correto.
5. **Todo fato do mapa registra a origem** (repo, arquivo, linha, commit) e se veio de `parser` ou de `llm`.
6. **Execução é sempre explícita:** nada roda na AWS nem executa código gerado sem confirmação do usuário.

## Stack

Python 3.12, `uv`, Pydantic v2, Typer, sqlglot (dialeto `trino`/`athena`), python-hcl2 (Terraform),
tree-sitter (JS e fallback), `ast` (Python/PySpark), Jinja2, pyarrow, boto3, pytest + pytest-cov,
ruff, mypy `--strict`, pre-commit.

## Arquitetura

Pacote `src/dbts/`. Núcleo = biblioteca pura; CLI (e depois MCP) são adaptadores finos.

```
domain/      modelos Pydantic (Fact, Entity, Edge, TestProposal, QueryRun, Report) e funções puras
extract/     um Extractor por linguagem: python_ast, pyspark, sql, terraform, javascript
mapping/     orquestra scan → extract → enrich → grafo; cache por commit; geração de guias e Mermaid
enrich/      prompts e chamadas ao LLM (saída estruturada), sempre sobre camadas pequenas do mapa
testing/     propor, refinar, gerar código de teste (SQL / Python)
execution/   ciclo de vida da query: validar → executar → corrigir → salvar por hash
reporting/   modelo do relatório + template Jinja2 fixo
adapters/    implementações das portas (ollama, azure, anthropic, athena, sqlite, csv, parquet...)
cli/         Typer; só parsing de args, confirmações e chamadas ao núcleo
```

Regra: `domain/` não importa nada de fora dele. I/O só em `adapters/` e `cli/`.

### Portas (Protocols) permitidas

| Porta | Implementações | Motivo |
|---|---|---|
| `LLMProvider` | Ollama (1ª), Fake (testes), Azure OpenAI, Anthropic | troca de modelo prevista |
| `Extractor` | sql, pyspark (Python em geral), terraform, javascript | uma por linguagem; devolvem `Fact`s |
| `MapStore` | SQLite (padrão) e DuckDB (`DBTS_STORE=duckdb`), base comum `SqlMapStore` | pedido: ter mais opções de armazenamento |
| `QueryExecutor` | Athena via boto3 (1ª), infra AWS própria depois | execução vai migrar |
| `CodeRunner` | subprocess Python local | testes em Python/PySpark, rodam em processo isolado |
| `ResultSink` | csv, parquet, tabela em DB (Athena/Glue) | destinos de resultado |

## O mapa

- Diretório configurável (`--map-dir` / `DBTS_MAP_DIR` / config), **fora do git** desta ferramenta.
- **Cache por repo chaveado no SHA do HEAD.** Mesmo SHA = zero releitura. SHA novo = compara o inventário
  `git ls-tree -r HEAD` (caminho → blob) com o salvo e reprocessa só arquivos alterados/removidos.
  Sempre analisa o estado **commitado** (blobs), nunca a working tree.
  A impressão digital do código de `extract/` (`extractors_fingerprint`) fica na tabela `meta`; se mudar, o
  próximo scan reprocessa todos os arquivos uma vez.
- **Fatos** (`Fact`: entidade ou aresta + `SourceLocation` + origem) no `MapStore`; arestas `reads`, `writes`,
  `joins_on`, `derives_from`, `deployed_by`, `stored_at`. IDs: `job:<repo>/<path>`, `table:<nome>`,
  `column:<tabela>.<coluna>`. Tabelas em minúsculas; caminhos `s3://` mantêm a caixa e perdem a barra final.
- Extratores:
  - `sql`: sqlglot (dialeto athena); lineage de coluna via `sqlglot.lineage` (atravessa CTEs/subqueries),
    com fallback de aliases. Templates `${x}`/`{{ x }}` viram `__param__`.
  - `pyspark`: `ast`, por arquivo, em ordem de linha; `Frame` rastreia tabelas e colunas (transitivo) por variável;
    SQL em `spark.sql`/awswrangler/boto3 e em qualquer string que pareça SQL.
  - `terraform`: python-hcl2; Glue tables (colunas, partições, S3) e `aws_athena_named_query`.
  - `javascript`: regex em strings/template literals que parecem SQL (sem tree-sitter, de propósito).
- Filtros: termos do `WHERE` (e `.filter("...")`/`.where("...")` no PySpark) sobre uma única tabela viram arestas
  `filters` com o predicado sem alias em `Edge.detail`; predicados com subquery ou `${param}` são ignorados.
- Avisos: statements SQL não analisados viram entidades `warning:<repo>/<path>:<linha>`; o scan conta na
  auditoria (`warnings=N`) e os guias listam em "Trechos não analisados".
- Guias (`dbts map TERMO|--all [--depth N] [--enrich]`): subgrafo por busca + N saltos; Markdown (Mermaid +
  cartão por tabela) e JSON em `<map-dir>/guides/`. Cartões são a camada pequena enviada ao LLM.
- Enriquecimento LLM (`--enrich`): `TableSummary` por tabela, cache por sha256(prompt+provider+modelo+versão)
  na tabela `annotations`; só chamadas reais vão para a auditoria. Ollama com `think: false`.
- Saídas legíveis por IA (Markdown, Mermaid, JSON) **são geradas do grafo**, nunca escritas à mão.

## Ciclo de vida da query

1. Gerar o código e **mostrar ao usuário** na linguagem pedida. Usuário refina a lista de testes antes de gerar.
2. Validar (`EXPLAIN` no Athena). Executar só após confirmação.
3. Em erro: coletar traceback; o usuário escolhe **auto-corrigir** (máx. N tentativas, configurável) ou **corrigir manualmente**.
4. **Só a versão que executou com sucesso é armazenada:** `<queries-dir>/<hash>.sql`, com cabeçalho comentado
   e descrição detalhada (o que faz, tabelas/colunas, joins, cálculos, por que existe).
5. `hash` = sha256 do corpo SQL normalizado (sqlglot) **sem o cabeçalho**.
6. Índice liga hash → execuções → resultados → relatório.
7. Guardas: apenas `SELECT` ou CTAS no schema sandbox do usuário; workgroup com limite de bytes escaneados;
   usar `boto3.Session(profile_name=...)` com o perfil do AWS CLI (sem subprocess do `aws`).
8. Código Python gerado roda via `CodeRunner` em subprocess, nunca `exec` no processo da ferramenta.

## Relatório

Template Jinja2 único em `reporting/templates/`. Seções fixas e na mesma ordem: O que é, Por que foi feito,
O que se quis testar, Desenho, Resultados, Análise, Conclusões. Dados vêm de um modelo Pydantic;
o LLM só preenche campos de texto. Sem seção opcional.

## Trilha de auditoria

Contexto de uso: validação independente de modelos e esteiras. Toda ação relevante gera um registro
**append-only** (JSON Lines em `<map-dir>/audit/`), escrito pelo núcleo e nunca pelo adaptador.

- Campos mínimos: `timestamp`, `usuario`, `acao`, `repo` + `commit_sha` analisado, `hash` da query (quando houver),
  `provider` e `modelo` de LLM usados, `origem` (`parser` | `llm` | `usuario`), `decisao` do usuário (confirmou, recusou, editou).
- Eventos obrigatórios: scan/reanálise de repo, enriquecimento por LLM, proposta de teste, aceite/edição pelo usuário,
  execução (sucesso e erro, com traceback), correção (auto ou manual), geração de relatório.
- Conteúdo inferido por LLM é sempre marcado como **hipótese**; só vira fato se um parser ou uma execução o confirmar.
- Registros não são editados nem apagados pela ferramenta. Cada registro inclui o hash do anterior (cadeia simples)
  para detectar adulteração.
- O relatório cita, para cada conclusão, os hashes de query e o commit de origem.
- Porta nova **não** é necessária: um módulo `audit/` concreto, injetado nos casos de uso.

## Biblioteca de hipóteses

Catálogo versionado de hipóteses de validação recorrentes, em `src/dbts/hypotheses/`. Cada hipótese é um
modelo Pydantic declarativo (dados, não lógica espalhada):

- `id`, `nome`, `descrição`, `categoria`, `severidade_padrão`
- `padrões_no_mapa`: o que procurar no grafo para saber que ela se aplica (ex.: `join` sem chave única, filtro por data
  posterior à data de referência, coluna derivada de campo pós-evento)
- `modelo_de_teste`: template de teste em SQL (e/ou Python) com parâmetros preenchidos com tabelas e colunas **reais** do mapa
- `critério`: como interpretar o resultado (limiar, comparação esperada)

Hipóteses iniciais:

| id | O que testa |
|---|---|
| `temporal-leakage` | variável construída com informação posterior à data de referência |
| `join-fanout` | junção que duplica linhas (chave não única de um dos lados) |
| `sample-filter-bias` | filtro que exclui um segmento relevante (ex.: inadimplentes, nulos) |
| `null-key-loss` | perda de linhas por chaves nulas em junções |
| `definition-drift` | mesma variável com cálculo diferente entre versões ou repos |
| `duplicate-keys` | chaves primárias esperadas com duplicidade |

Implementação: catálogo em `src/dbts/testing/catalog/*.toml` (campos `id, nome, descricao, categoria,
severidade, padrao, titulo, sql, criterio`; templates `${param}` via `string.Template`). Padrões disponíveis em
`testing/matchers.py`: `join`, `key_column`, `date_columns`, `divergent_definition`, `filter`. Parâmetros que o grafo não
sabe (ex.: `ref_col`) ficam como "faltando" e bloqueiam a geração até `dbts plan set`. Fluxo da CLI:
`dbts propose TERMO` → `dbts plan show|accept|reject|set|add` → `dbts generate PLANO --lang sql|python`.
Planos em `<map-dir>/plans/<plano>.json`; código gerado em `<map-dir>/plans/<plano>/<id>.<ext>`.

Regras:
- O motor é determinístico: percorre o grafo, compara com `padrões_no_mapa` e devolve candidatos com a evidência
  (arestas e arquivos). O LLM só ajuda a preencher parâmetros ambíguos e a redigir; a decisão de aplicabilidade não é dele.
- Cada hipótese tem testes unitários com um mini-grafo de fixture que a dispara e outro que não.
- Adicionar hipótese = adicionar um arquivo de dados + fixtures; sem alterar o motor.
- O usuário escolhe quais candidatos viram teste (fluxo de refinamento já descrito), e a escolha vai para a trilha de auditoria.

## MCP

Adaptador fino sobre o mesmo núcleo (`src/dbts/mcp_server.py`, SDK `mcp` 2.x / `MCPServer`), iniciado com
`dbts mcp` (stdio). Ferramentas **determinísticas** = métodos públicos de `DbtsTools` listados em `TOOL_NAMES`
(scan, guide, lineage_json, propose, show_plan, set_status, set_params, set_sql, add_test, generate, run_test,
list_runs, audit_verify). No MCP quem raciocina é o LLM do cliente: nada no servidor chama LLM; `run_test` exige
`confirm=true`, não auto-corrige (devolve erro + SQL; o cliente corrige com `set_sql`) e gera relatório sem análise.
Auditoria registra o usuário como `<usuário>@mcp`.

## Providers de LLM

`DBTS_LLM_PROVIDER=ollama|anthropic|azure` e `DBTS_LLM_MODEL` (padrões: `qwen3:4b`, `claude-sonnet-5-5`;
Azure exige o nome do deployment). Saída estruturada nativa: Ollama `format` (JSON schema, `think: false`),
Anthropic `messages.parse(output_format=...)`, Azure `chat.completions.parse(response_format=...)`.
Resposta sem saída estruturada → `LLMResponseError`. Providers externos recebem código/metadados e amostras de
resultado: considerar a política de dados antes de usar.

## Qualidade e testes

- `pytest --cov=dbts --cov-branch --cov-fail-under=100`, `ruff check`, `ruff format --check`, `mypy --strict` em pre-commit e CI.
- Testes unitários sem rede: `FakeLLMProvider` com respostas fixas, `botocore.stub.Stubber` para AWS, `tmp_path` para disco,
  repositórios Git de fixture criados em `tmp_path`.
- Funções puras no domínio; I/O nas bordas — é isso que torna 100% viável sem mocks em excesso.
- Um teste por comportamento; nomes `test_<unidade>_<cenario>_<resultado>`.
- Sem comentários que repetem o código; docstring só quando o "porquê" não é óbvio.

## CI/CD

`.github/workflows/ci.yml`: `lint`, `sast` (bandit + pip-audit), `unit` (`-m "not integration"`, CI exige
≥ 95%; localmente o padrão do projeto continua 100%), `integration` (só para a `main`), `deploy-dev` (wheel como
artefato) e `deploy-prod` (GitHub Release). Fluxo: feature → PR para `dev` → PR `dev` → `main` (protegida).
`scripts/github_bootstrap.sh` cria o repo, branches, ambientes e proteção. Supressões do bandit só com
`# nosec BXXX` e justificativa na linha de cima.

## Plano de implementação

Cada fase só termina com gates verdes (100% cobertura, complexidade, mypy).

0. ✅ **Fundação:** `uv`, estrutura, tooling e CI, modelos `domain/`, `LLMProvider` (Fake + Ollama), config e `--map-dir`,
   módulo `audit/` (cadeia de hashes), já usado por tudo que vem depois.
1. ✅ **Scan e cache:** descobrir repos, SHA, diff incremental, `MapStore` SQLite, esquema de fatos.
2. ✅ **Extratores determinísticos**, nesta ordem: `sql` (sqlglot/lineage de colunas) → `pyspark` + `python_ast` → `terraform` → `javascript`.
3. ✅ **Enriquecimento e guias:** LLM sobre cartões, geração de Markdown/Mermaid, comando "mapear X" e "mapa completo".
4. ✅ **Propostas de teste:** biblioteca de hipóteses e motor sobre o grafo, listar, refinar interativamente,
   gerar código (SQL/Python) na linguagem pedida.
5. ✅ **Execução:** `QueryExecutor` Athena, loop de correção com escolha do usuário, armazenamento por hash com cabeçalho.
   `dbts run PLANO [IDS] --database --workgroup --sandbox --profile --region [--yes]`; guarda reaplicada a cada
   correção; correção LLM (`SqlFixer`), manual (`$EDITOR`) ou pular; versão corrigida volta ao plano.
   Queries em `$DBTS_QUERIES_DIR` (padrão `<map-dir>/queries`), índice `runs.jsonl`. Ainda não validado em AWS real.
   `--local-db ARQUIVO.duckdb` (ou `DBTS_LOCAL_DB`) executa localmente: SQL Athena traduzido para DuckDB via
   sqlglot — para ensaios offline e para o teste e2e (`tests/test_e2e.py`).
6. ✅ **Resultados e relatório:** sinks csv/parquet/DB, template do relatório.
   `--sink csv|parquet|table` (table = CTAS no sandbox, reexecuta a query); falha de um destino vira
   `"erro: ..."` no registro sem perder a execução. Relatório em `reporting/templates/report.md.j2`, gravado em
   `<map-dir>/reports/<plano>/<id>-<execução>.md`; LLM só preenche status/análise/conclusão (`--no-analysis`
   deixa pendente). `dbts report PLANO ID` refaz a partir da última execução com CSV.
7. **Expansão:** ✅ servidor MCP, ✅ providers Azure OpenAI/Anthropic, ✅ `MapStore` DuckDB, execução em infra AWS (adiada).

## Limitações conhecidas (vistas no e2e)

- `join-fanout` olha a junção física: junção contra CTE agregada (`GROUP BY` na chave) gera falso positivo.
- PySpark resolve colunas só com evidência do próprio arquivo; colunas definidas em outro repo
  (ex.: `total_pago` de uma tabela produzida em SQL) ficam sem lineage após joins.
- Vereditos do LLM nos relatórios são rascunho: o qwen3:4b tende a "aprovado" quando o critério depende de regra
  de negócio que ele não conhece.
- Merge de plano preserva propostas que não reaparecem (inclusive falsos positivos já corrigidos): rejeitar à mão.

## Decisões em aberto

- Valor de N de tentativas do auto-corrigir e o limite de bytes do workgroup.
- Schema sandbox e DB de resultados do usuário (configuração por projeto).
- Segundo `MapStore` a implementar (DuckDB é o candidato).
