# dbts — validação de esteiras de dados a partir do código

CLI (e servidor MCP) para quem valida modelos e esteiras: aponte para um diretório com muitos repos Git
clonados e a ferramenta **mapeia** o fluxo dos dados (tabelas, colunas, junções, filtros, cálculos),
**propõe testes** a partir de uma biblioteca de hipóteses, **gera e executa** as queries (Athena ou DuckDB
local) e escreve um **relatório formal** por teste. Tudo fica registrado numa **trilha de auditoria**
encadeada por hash.

O mapa é guardado e reaproveitado: um repo só é relido quando há commit novo (ou quando a lógica de
extração muda), o que economiza tempo e chamadas de LLM.

## Instalação

Requer Python 3.12+, [uv](https://docs.astral.sh/uv/) e git.

```bash
uv sync
uv run dbts --help
```

Para usar o LLM local padrão, instale o [Ollama](https://ollama.com) e baixe o modelo:

```bash
ollama pull qwen3:4b
```

## Uso rápido

```bash
export DBTS_MAP_DIR=~/dbts-mapa          # onde ficam mapa, planos, queries, relatórios e auditoria

dbts scan ~/repos                        # mapeia todos os repos do diretório (incremental)
dbts map score_base --depth 2 --enrich   # guia Markdown + Mermaid + JSON (resumos por LLM)
dbts map --all                           # mapa completo

dbts propose score_base --plan meu-plano # propostas de teste a partir das hipóteses
dbts plan show meu-plano --sql           # revisar propostas e SQL
dbts plan accept meu-plano ID1 ID2       # aceitar / dbts plan reject ...
dbts plan set meu-plano ID ref_col=dt_ref event_col=dt_evento   # parâmetros faltantes
dbts plan add meu-plano --title "Meu teste" --sql-file teste.sql  # teste próprio
dbts generate meu-plano --lang python    # código com cabeçalho descritivo (sql ou python)

dbts run meu-plano --database db --workgroup wg --sandbox meu_schema   # executa no Athena
dbts report meu-plano ID                 # refaz o relatório da última execução
dbts audit verify                        # verifica a integridade da trilha
```

### Sem AWS (ensaio local)

`--local-db` executa as queries num arquivo DuckDB local; o SQL do Athena é traduzido via sqlglot.
Útil para testar a lógica com dados de amostra antes de gastar no Athena.

```bash
dbts run meu-plano --yes --local-db amostra.duckdb --sandbox sandbox
```

## O que é extraído do código

| Linguagem | O que vira mapa |
|---|---|
| SQL (Athena/Presto) | tabelas lidas/escritas, chaves de junção, lineage de coluna (atravessa CTEs e subqueries), filtros do `WHERE` |
| Python / PySpark | `spark.table`, `spark.read.*`, joins, `withColumn`/`select`/`agg`, `saveAsTable`, filtros em string, SQL embutido (`spark.sql`, awswrangler, boto3, strings soltas) |
| Terraform | tabelas Glue (colunas, partições, localização S3) e `aws_athena_named_query` |
| JavaScript / TypeScript | SQL embutido em strings |

Cada fato guarda arquivo, linha e commit de origem. Trechos que o parser não entende aparecem nos guias em
"Trechos não analisados". Conteúdo gerado por LLM é sempre marcado como **hipótese**.

## Biblioteca de hipóteses

Em `src/dbts/testing/catalog/*.toml` — adicionar uma hipótese é adicionar um arquivo:

| Hipótese | O que testa |
|---|---|
| `join-fanout` | junção que duplica linhas (chave não única) |
| `null-key-loss` | perda de linhas por chave nula ou sem correspondência |
| `duplicate-keys` | identificador repetido em tabela produzida pela esteira |
| `temporal-leakage` | evento posterior à data de referência |
| `definition-drift` | mesma coluna calculada de formas diferentes |
| `sample-filter-bias` | filtro que exclui parte relevante da amostra |

## Execução e relatórios

- **Guarda:** só `SELECT` ou `CREATE TABLE AS` no schema sandbox; reaplicada a cada correção.
- **Correção de erros:** em falha, escolha auto-corrigir com o LLM, editar no `$EDITOR` ou pular.
- **Biblioteca de queries:** só a versão que executou é salva, em `<hash>.sql` (hash do SQL normalizado, sem
  comentários), com cabeçalho detalhado; índice em `runs.jsonl`.
- **Resultados:** `--sink csv` (padrão), `parquet` e `table` (CTAS no sandbox; reexecuta a query).
- **Relatório:** template fixo com 7 seções (o que é, por que, o que se quis testar, desenho, resultados,
  análise, conclusões). O LLM só redige análise e conclusão, marcadas para revisão (`--no-analysis` desliga).

## Configuração

| Variável | Padrão | Uso |
|---|---|---|
| `DBTS_MAP_DIR` | `~/.dbts` | diretório do mapa e artefatos (ou `--map-dir`) |
| `DBTS_QUERIES_DIR` | `<map-dir>/queries` | biblioteca de queries executadas |
| `DBTS_STORE` | `sqlite` | `sqlite` ou `duckdb` para o mapa |
| `DBTS_LLM_PROVIDER` | `ollama` | `ollama`, `anthropic` ou `azure` |
| `DBTS_LLM_MODEL` | por provider | `qwen3:4b`, `claude-sonnet-5-5`; no Azure, o nome do deployment |
| `DBTS_ATHENA_DATABASE`, `DBTS_ATHENA_WORKGROUP`, `DBTS_SANDBOX` | — | padrões do `dbts run` |
| `AWS_PROFILE`, `AWS_REGION` | — | credenciais do AWS CLI |
| `DBTS_LOCAL_DB` | — | executa localmente em DuckDB |

Credenciais dos providers externos vêm das variáveis usuais (`ANTHROPIC_API_KEY`; `AZURE_OPENAI_API_KEY`,
`AZURE_OPENAI_ENDPOINT`, `OPENAI_API_VERSION`). **Atenção:** providers externos recebem código, metadados e
amostras de resultado; verifique a política de dados antes de usar com dados sensíveis.

## Servidor MCP

```bash
dbts mcp --map-dir ~/dbts-mapa
```

Exemplo de configuração num cliente MCP:

```json
{
  "mcpServers": {
    "dbts": {
      "command": "uv",
      "args": ["--directory", "/caminho/para/database_test_streamline", "run", "dbts", "mcp"],
      "env": { "DBTS_MAP_DIR": "/home/voce/dbts-mapa" }
    }
  }
}
```

As ferramentas são determinísticas (quem raciocina é o LLM do cliente). `run_test` exige `confirm=true` e,
em erro, devolve a mensagem para o cliente corrigir com `set_sql`.

## Desenvolvimento

```bash
uv run pytest          # 100% de cobertura de linhas e branches é obrigatório
uv run ruff check .    # inclui complexidade ciclomática máxima 8
uv run ruff format .
uv run mypy src tests  # modo strict
uv run pre-commit install
```

Arquitetura, decisões e regras do projeto estão em [`CLAUDE.md`](CLAUDE.md). O teste
`tests/test_e2e.py` cobre o fluxo completo offline (repos Git temporários + DuckDB + LLM falso).

## CI/CD e fluxo de branches

Workflow em `.github/workflows/ci.yml` (GitHub Actions):

| Job | Quando | O que faz |
|---|---|---|
| `lint` | todo push/PR para `dev` e `main` | ruff (inclui complexidade), formatação, mypy strict |
| `sast` | idem | bandit no código e pip-audit nas dependências |
| `unit` | idem | testes unitários, cobertura mínima de 95% (relatório `coverage.xml`) |
| `integration` | PRs para a `main` e push na `main` | teste ponta a ponta (`-m integration`) |
| `deploy-dev` | push na `dev`, após lint/sast/unit | gera o pacote (wheel) como artefato do ambiente `dev` |
| `deploy-prod` | push na `main`, após todos os checks | publica uma GitHub Release com o pacote |

Criar o repositório (uma vez):

```bash
gh auth login -s workflow
scripts/github_bootstrap.sh database_test_streamline private
```

O script faz o commit inicial (se não houver), cria o repo, sobe `main` e `dev`, cria os ambientes e
protege as branches: na `main` só entra PR com `lint`, `sast`, `unit` e `integration` verdes.
Proteção de branch em repo privado exige GitHub Pro/Team.

Dia a dia:

```bash
git switch dev && git pull
git switch -c feat/minha-mudanca
# ... código + testes ...
git commit -am "feat: minha mudança"
git push                                   # cria a branch remota
gh pr create --base dev --fill             # CI roda lint, sast e unit
gh pr merge --squash --delete-branch       # entra na dev -> deploy-dev

gh pr create --base main --head dev --title "release: dev -> main" --fill
gh pr checks --watch                       # inclui integration
gh pr merge --merge                        # entra na main -> deploy-prod (release)
```

Rodar localmente o mesmo que o CI:

```bash
uv run ruff check . && uv run ruff format --check . && uv run mypy src tests
uv run bandit -q -r src -c pyproject.toml
uv run pytest -m "not integration" --cov-fail-under=95
uv run pytest -m integration --no-cov
```

## Limitações conhecidas

- `join-fanout` pode dar falso positivo quando a junção é contra uma CTE agregada na chave.
- No PySpark, colunas definidas em outro repo ficam sem lineage depois de joins.
- Vereditos do LLM nos relatórios são rascunho e devem ser revisados.
- Execução no Athena ainda não validada em conta real; execução direto em infra AWS ainda não implementada.
