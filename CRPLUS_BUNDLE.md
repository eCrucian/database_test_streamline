# crplus — pacote completo do código-fonte

Este arquivo contém os 92 arquivos do projeto (exceto `uv.lock`, que é regenerado).
Cada arquivo começa com uma linha `<!-- FILE: caminho -->`, seguida de um bloco de código
cujo conteúdo é **exatamente** o conteúdo do arquivo. Siga `RECREATE_INSTRUCTIONS.md`.

## Índice

- `.gitattributes`
- `.github/workflows/ci.yml`
- `.gitignore`
- `.pre-commit-config.yaml`
- `.python-version`
- `.secrets.baseline`
- `CHANGELOG.md`
- `CLAUDE.md`
- `Makefile`
- `README.md`
- `crplus.example.toml`
- `docs/adr/0001-fft-motor-principal.md`
- `docs/adr/0002-banding-ceil.md`
- `docs/adr/0003-variancia-setorial.md`
- `docs/adr/0004-devedor-operacao.md`
- `docs/adr/0005-chaves-de-configuracao-adicionais.md`
- `docs/adr/0006-threads-e-memoria.md`
- `docs/adr/0007-robustez-numerica.md`
- `docs/adr/index.md`
- `docs/configuracao.md`
- `docs/guia-de-uso.md`
- `docs/index.md`
- `docs/javascripts/mathjax.js`
- `docs/metodologia.md`
- `docs/performance.md`
- `docs/referencia-api.md`
- `docs/seguranca.md`
- `docs/validacao.md`
- `mkdocs.yml`
- `pyproject.toml`
- `src/crplus/__init__.py`
- `src/crplus/_checks.py`
- `src/crplus/_threads.py`
- `src/crplus/_version.py`
- `src/crplus/aggregation.py`
- `src/crplus/api.py`
- `src/crplus/banding.py`
- `src/crplus/config.py`
- `src/crplus/contributions.py`
- `src/crplus/distribution/__init__.py`
- `src/crplus/distribution/fft.py`
- `src/crplus/distribution/grid.py`
- `src/crplus/distribution/model.py`
- `src/crplus/distribution/panjer.py`
- `src/crplus/exceptions.py`
- `src/crplus/memory.py`
- `src/crplus/moments.py`
- `src/crplus/montecarlo.py`
- `src/crplus/obligor.py`
- `src/crplus/paths.py`
- `src/crplus/py.typed`
- `src/crplus/results.py`
- `src/crplus/risk_measures.py`
- `src/crplus/schema.py`
- `src/crplus/sectors.py`
- `src/crplus/sources.py`
- `src/crplus/tempstore.py`
- `src/crplus/validation.py`
- `tests/__init__.py`
- `tests/benchmarks/__init__.py`
- `tests/benchmarks/scale_runner.py`
- `tests/benchmarks/test_scale.py`
- `tests/conftest.py`
- `tests/integration/__init__.py`
- `tests/integration/golden/end_to_end.json`
- `tests/integration/reference/__init__.py`
- `tests/integration/reference/cases.py`
- `tests/integration/reference/test_reference.py`
- `tests/integration/test_end_to_end.py`
- `tests/pipeline.py`
- `tests/synthetic.py`
- `tests/unit/__init__.py`
- `tests/unit/test_aggregation.py`
- `tests/unit/test_api.py`
- `tests/unit/test_banding.py`
- `tests/unit/test_checks.py`
- `tests/unit/test_config.py`
- `tests/unit/test_contributions.py`
- `tests/unit/test_distribution.py`
- `tests/unit/test_exceptions.py`
- `tests/unit/test_memory.py`
- `tests/unit/test_moments.py`
- `tests/unit/test_montecarlo.py`
- `tests/unit/test_obligor.py`
- `tests/unit/test_paths.py`
- `tests/unit/test_results.py`
- `tests/unit/test_risk_measures.py`
- `tests/unit/test_sectors.py`
- `tests/unit/test_security.py`
- `tests/unit/test_sources.py`
- `tests/unit/test_tempstore.py`
- `tests/unit/test_validation.py`

<!-- FILE: .gitattributes -->
`````
* text=auto eol=lf
*.parquet binary
`````

<!-- FILE: .github/workflows/ci.yml -->
`````yaml
name: ci

on:
  push:
  pull_request:

permissions:
  contents: read

jobs:
  check:
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest]
        python: ["3.11", "3.12"]
    runs-on: ${{ matrix.os }}
    defaults:
      run:
        shell: bash
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6
        with:
          python-version: ${{ matrix.python }}
      - run: uv sync --all-extras --locked
      - run: make check
`````

<!-- FILE: .gitignore -->
`````
__pycache__/
*.py[cod]
.venv/
.mypy_cache/
.ruff_cache/
.pytest_cache/
.hypothesis/
.benchmarks/
.coverage
coverage.xml
htmlcov/
site/
dist/
build/
*.egg-info/
saida_crplus/
mutants/
`````

<!-- FILE: .pre-commit-config.yaml -->
`````yaml
# Hooks locais: usam as versões fixadas no uv.lock (uma única fonte de verdade).
repos:
  - repo: local
    hooks:
      - id: ruff-check
        name: ruff check
        entry: uv run python -m ruff check --force-exclude
        language: system
        types: [python]
      - id: ruff-format
        name: ruff format
        entry: uv run python -m ruff format --check --force-exclude
        language: system
        types: [python]
      - id: mypy
        name: mypy --strict
        entry: uv run python -m mypy --strict src
        language: system
        pass_filenames: false
        types: [python]
      - id: bandit
        name: bandit
        entry: uv run python -m bandit -r src -c pyproject.toml -ll -q
        language: system
        pass_filenames: false
        types: [python]
      - id: xenon
        name: xenon (complexidade A)
        entry: uv run python -m xenon --max-absolute A --max-modules A --max-average A src
        language: system
        pass_filenames: false
        types: [python]
      - id: detect-secrets
        name: detect-secrets
        entry: uv run python -m detect_secrets.pre_commit_hook --baseline .secrets.baseline
        language: system
        exclude: ^uv\.lock$
`````

<!-- FILE: .python-version -->
`````
3.12
`````

<!-- FILE: .secrets.baseline -->
`````
{
  "version": "1.5.0",
  "plugins_used": [
    {
      "name": "ArtifactoryDetector"
    },
    {
      "name": "AWSKeyDetector"
    },
    {
      "name": "AzureStorageKeyDetector"
    },
    {
      "name": "Base64HighEntropyString",
      "limit": 4.5
    },
    {
      "name": "BasicAuthDetector"
    },
    {
      "name": "CloudantDetector"
    },
    {
      "name": "DiscordBotTokenDetector"
    },
    {
      "name": "GitHubTokenDetector"
    },
    {
      "name": "GitLabTokenDetector"
    },
    {
      "name": "HexHighEntropyString",
      "limit": 3.0
    },
    {
      "name": "IbmCloudIamDetector"
    },
    {
      "name": "IbmCosHmacDetector"
    },
    {
      "name": "IPPublicDetector"
    },
    {
      "name": "JwtTokenDetector"
    },
    {
      "name": "KeywordDetector",
      "keyword_exclude": ""
    },
    {
      "name": "MailchimpDetector"
    },
    {
      "name": "NpmDetector"
    },
    {
      "name": "OpenAIDetector"
    },
    {
      "name": "PrivateKeyDetector"
    },
    {
      "name": "PypiTokenDetector"
    },
    {
      "name": "SendGridDetector"
    },
    {
      "name": "SlackDetector"
    },
    {
      "name": "SoftlayerDetector"
    },
    {
      "name": "SquareOAuthDetector"
    },
    {
      "name": "StripeDetector"
    },
    {
      "name": "TelegramBotTokenDetector"
    },
    {
      "name": "TwilioKeyDetector"
    }
  ],
  "filters_used": [
    {
      "path": "detect_secrets.filters.allowlist.is_line_allowlisted"
    },
    {
      "path": "detect_secrets.filters.common.is_ignored_due_to_verification_policies",
      "min_level": 2
    },
    {
      "path": "detect_secrets.filters.heuristic.is_indirect_reference"
    },
    {
      "path": "detect_secrets.filters.heuristic.is_likely_id_string"
    },
    {
      "path": "detect_secrets.filters.heuristic.is_lock_file"
    },
    {
      "path": "detect_secrets.filters.heuristic.is_not_alphanumeric_string"
    },
    {
      "path": "detect_secrets.filters.heuristic.is_potential_uuid"
    },
    {
      "path": "detect_secrets.filters.heuristic.is_prefixed_with_dollar_sign"
    },
    {
      "path": "detect_secrets.filters.heuristic.is_sequential_string"
    },
    {
      "path": "detect_secrets.filters.heuristic.is_swagger_file"
    },
    {
      "path": "detect_secrets.filters.heuristic.is_templated_secret"
    },
    {
      "path": "detect_secrets.filters.regex.should_exclude_file",
      "pattern": [
        "(\\.venv|uv\\.lock|\\.git)/?"
      ]
    }
  ],
  "results": {},
  "generated_at": "2026-11-12T20:26:06Z"
}
`````

<!-- FILE: CHANGELOG.md -->
`````markdown
# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/); versionamento
[SemVer](https://semver.org/lang/pt-BR/).

## [Não lançado]

### Adicionado

- **Fase 0**: `pyproject.toml` com uv, `Makefile`, pre-commit, CI, mkdocs; `exceptions`,
  `config` (TOML validado, caminhos confinados, SHA-256), `memory`, `tempstore`, `paths`.
- **Fase 1**: `sources` (LazyFrame/DataFrame/pandas → plano canônico, partição por hash),
  `validation` (regras vetorizadas, relatório sem valores nem ids), `obligor` (passo A).
- **Fase 2**: `banding` (ceil/round, $L_0$ automático), `aggregation` (passo B somável),
  `sectors` (métodos `pd_vol` e `external`), `moments`.
- **Fase 3**: motores `fft` (principal) e `panjer` (referência estável, numba), checagens de
  grade com dobra automática.
- **Fase 4**: `risk_measures` (VaR, ES de Acerbi–Tasche, EC; caudas por soma reversa).
- **Fase 5**: `contributions` (σ analítico, VaR/ES de Haaf–Tasche, passo D em parquet).
- **Fase 6**: partições automáticas pelo orçamento, benchmarks de escala com pico de RSS em
  subprocesso, otimizações de memória (ADR 0006).
- **Fase 7**: `run_creditrisk_plus`, `results` (`summary.json`, distribuição em parquet),
  `montecarlo` (validação), teste de integração ponta a ponta, golden file e leitor de casos de
  referência externos.
- **Fase 8**: documentação completa (metodologia, guia, configuração, performance, validação,
  segurança, referência da API, ADRs 0001–0007).

### Alterado

- `resources.polars_threads` e o padrão de `POLARS_MAX_THREADS`: 16 → 8 (ADR 0006).
`````

<!-- FILE: CLAUDE.md -->
`````markdown
# CLAUDE.md — CreditRisk+ (CR+) em Python, escala de centenas de milhões de operações

> Este arquivo orienta o Claude Code na implementação de uma **réplica completa do CreditRisk+**
> (CSFB, 1997, com as extensões numericamente estáveis da literatura). Leia tudo antes de escrever código.
> Em caso de conflito entre este arquivo e qualquer outra fonte, **este arquivo vence**. Se algo aqui
> estiver ambíguo, **pergunte antes de implementar** (veja a seção 14, "Premissas em aberto").

---

## 1. Objetivo

Construir o pacote Python `crplus` que:

1. Recebe **sempre um DataFrame polars** (`pl.LazyFrame` para a base completa, `pl.DataFrame` para bases
   menores; pandas aceito apenas via conversão) com uma linha por operação, contendo id do devedor, PD,
   volatilidade absoluta da PD, LGD, EAD e pesos setoriais.
2. Calcula a **distribuição de perdas completa** do portfólio pelo CreditRisk+.
3. Entrega as medidas de risco: EL, UL (desvio-padrão), VaR, Expected Shortfall (ES), Capital Econômico (EC).
4. Entrega as **contribuições de risco** (desvio-padrão, VaR e ES) **por operação** e os
   parâmetros/diagnósticos por setor. Agregações de contribuição são responsabilidade do usuário (se quiser
   resultado agregado, ele passa a base já agregada).
5. Roda em **centenas de milhões de linhas** dentro de um **orçamento de memória de ~9 GB** (30% de 32 GB) em
   um notebook Ryzen 7 7735HS (8 núcleos / 16 threads, GPU integrada — **não usar GPU**), com tempo previsível.
6. Lê todos os parâmetros de execução de um **arquivo de configuração TOML** (níveis de confiança, unidade de
   perda, método de variância setorial, limites de memória etc.).
7. Tem **teste unitário intencional para tudo**, **baixa complexidade ciclomática**, **controles básicos de SAST**,
   **teste de integração final** e **documentação completa**.

Fora de escopo (a menos que solicitado): LGD estocástica, correlação entre setores, horizonte multiperíodo,
interface gráfica. Deixar pontos de extensão, mas não implementar.

---

## 2. Stack e comandos

- Python **>= 3.11** (alvo 3.12). Gerenciador: **uv** (`pyproject.toml` + `uv.lock` versionado).
- Dependências de runtime: `polars` (motor de dados principal), `numpy`, `scipy`, `pyarrow`, `numba`.
  Extra opcional: `pandas` (extra `pandas`, só para conversão de entrada). Config TOML via `tomllib` (stdlib).
- Dev: `pytest`, `pytest-cov`, `hypothesis`, `pytest-benchmark`, `mypy`, `ruff`, `bandit`, `pip-audit`,
  `xenon` (radon), `detect-secrets`, `pre-commit`, `mkdocs-material`, `mkdocstrings[python]`, `mutmut` (opcional).
- Layout `src/`.

Comandos (expor também via `Makefile`):

```bash
uv sync --all-extras
```

```bash
uv run pytest -m "not slow" --cov=crplus --cov-branch --cov-fail-under=95
```

```bash
uv run pytest -m integration
```

```bash
uv run ruff check . && uv run ruff format --check .
```

```bash
uv run mypy --strict src
```

```bash
uv run bandit -r src -c pyproject.toml -ll && uv run pip-audit
```

```bash
uv run xenon --max-absolute A --max-modules A --max-average A src
```

```bash
uv run mkdocs build --strict
```

`make check` deve rodar **todos** os itens acima (exceto `slow`). Nenhuma tarefa está concluída sem `make check` verde.

---

## 3. Convenções

- Identificadores de código em **inglês**; docstrings, documentação e mensagens de erro ao usuário em **português**.
- Docstrings no estilo **NumPy**, com seção `Notes` contendo a fórmula implementada (LaTeX) e referência.
- Tipagem completa (`mypy --strict`). Arrays com `numpy.typing.NDArray[np.float64]` etc.
- Configuração e resultados em `@dataclass(frozen=True, slots=True)`. Nada de estado global mutável.
- Funções puras sempre que possível; I/O e logging somente nas bordas (`api.py`, `sources.py`, `results.py`, `tempstore.py`).
- **Proibido** loop Python por operação. Tudo por operação é expressão polars (preferido), numpy vetorizado ou kernel numba.
- Float64 para probabilidades, exposições e acumuladores. Float32 apenas para armazenar pesos, se configurado.
- Unidade monetária: a mesma do EAD de entrada. Perdas internas em **unidades de perda** (inteiros); conversão
  para moeda só na saída.

---

## 4. Contrato de entrada

### 4.1 Colunas (nomes configuráveis via `[columns]` no TOML)

| Coluna         | Tipo     | Domínio  | Significado                                                        |
|----------------|----------|----------|--------------------------------------------------------------------|
| `operation_id` | int/str  | único    | Chave da operação; repassada na saída de contribuições             |
| `obligor_id`   | int/str  | —        | **Obrigatória.** Devedor; o default acontece no devedor (§5.0)     |
| `pd`           | float    | `[0, 1]` | Probabilidade de default no horizonte (1 ano)                      |
| `pd_vol`       | float    | `>= 0`   | Desvio-padrão **absoluto** da PD (mesma unidade da PD) — confirmado |
| `lgd`          | float    | `[0, 1]` | Loss Given Default                                                 |
| `ead`          | float    | `>= 0`   | Exposure at Default (moeda)                                        |
| `w_<setor>`    | float    | `[0, 1]` | Peso no setor; **uma coluna por setor (wide)** — confirmado        |

- Pesos: se `Σ_k w_ik < 1`, o resíduo `w_i0 = 1 − Σ_k w_ik` vai para o **setor idiossincrático** (setor 0) —
  confirmado. Se `Σ_k w_ik > 1 + tol` → erro de validação.
- Setores = colunas que casam com `columns.weight_prefix` (padrão `"w_"`), em ordem estável (alfabética).
- Entrada: **`polars.LazyFrame`** (ex.: `pl.scan_parquet(...)`) é o caminho de produção; `polars.DataFrame`
  também aceito. `pandas.DataFrame` é convertido com `pl.from_pandas` (extra `pandas`).
- **Restrição de memória:** a base completa (centenas de milhões de linhas × (6 + K) colunas) **não cabe** no
  orçamento de ~9 GB como DataFrame eager. Toda a engine deve funcionar sobre `LazyFrame`, percorrendo a base
  em **lotes** (`collect_batches`/`iter_slices` ou leitura por row group do parquet) e podendo **reler** a
  fonte em vários passes. Nunca chamar `.collect()` na base inteira.
- Selecionar (`select`) apenas as colunas necessárias e fazer cast para os tipos mínimos já no plano lazy
  (`Float64` para pd/pd_vol/lgd/ead; pesos podem ser `Float32` conforme config; ids como estão).

### 4.2 Validação (`validation.py`)

Vetorizada (expressões polars), por lote, retornando um `ValidationReport` (contagem de violações por regra e
posições das primeiras N linhas violadoras — **nunca valores nem IDs nos logs**). Regras:

- colunas obrigatórias presentes e com tipo correto; sem `null`/`NaN`/`inf`;
- domínios da tabela acima; `operation_id` único (checado no passo A, §6.1);
- `pd > pd_warn_threshold` (padrão 0,3) gera **aviso** (aproximação de Poisson piora);
- `Σ w > 1 + 1e-9` → erro;
- inconsistência intra-devedor (PD, `pd_vol` ou pesos diferentes entre operações do mesmo devedor) → **aviso**
  com contagem de devedores afetados; o modelo usa a combinação ponderada por perda esperada (§5.0);
- operações com `lgd·ead == 0` recebem contribuição zero e são contadas no relatório.

Modo `strict=True` (padrão) levanta `InputValidationError`; `strict=False` devolve relatório e exclui linhas
inválidas. **Nunca usar `assert` para validação de runtime.**

---

## 5. Especificação matemática (implementar exatamente isto)

Notação: operação `i`, devedor `j`, `i ∈ j` = operações do devedor `j`; setores `k = 1..K`;
setor idiossincrático `k = 0`. `E_i = LGD_i · EAD_i`.

### 5.0 Devedor × operação (obrigatório)
O CR+ modela o default por **devedor**: todas as operações de um devedor entram em default juntas.

- Exposição do devedor: `E_j = Σ_{i∈j} E_i`; a banda é do devedor: `ν_j` (§5.1).
- Formulação **linear por operação** (não materializar tabela de PD/pesos por devedor): cada operação
  contribui para os agregados na banda do seu devedor com
  `λ_{k,ν_j} += w_ik · p_i · E_i / (ν_j · L0)` e `s_k += w_ik · σ_i · E_i / (ν_j · L0)`.
  Isso equivale a um devedor com PD, `σ` e pesos iguais à média ponderada por `p_i E_i` das suas operações;
  se forem iguais entre as operações (caso esperado), coincide exatamente com o CR+ por devedor.
- Só é preciso materializar a tabela `obligor_id → E_j` (passo A, §6.1).
- Contribuições: calculadas por operação com a banda do devedor (§5.8); a soma das operações de um devedor é a
  contribuição do devedor.

### 5.1 Banding
- Unidade de perda `L0 > 0` (fixa no TOML ou automática, §6.3).
- Banda do devedor: `ν_j = max(1, ceil(E_j / L0))` (configurável: `ceil` | `round`, sempre `>= 1`).
- Fator de ajuste preservando perda esperada: `f_j = E_j / (ν_j·L0)`; intensidade ajustada do devedor no setor
  `k`: `p̃_{jk} = Σ_{i∈j} w_ik p_i E_i / (ν_j L0)`.
- Garantia: `L0 · Σ_j Σ_k p̃_{jk} ν_j = Σ_i p_i E_i` (testar).
- Limite de segurança: `ν_max <= max_bands` (proteção contra `L0` minúsculo / estouro de memória).

### 5.2 Parâmetros setoriais (dois métodos, escolhidos no TOML — `sector_variance.method`)
- Intensidade por setor e banda: `λ_{k,ν} = Σ_{j: ν_j=ν} p̃_{jk}` (k = 0..K). Média: `μ_k = Σ_ν λ_{k,ν}`.
- **Método `pd_vol` (padrão, CSFB):** `s_k = Σ_i w_ik σ_i E_i / (ν_j L0)` (volatilidade com o mesmo ajuste de
  banding das PDs) e `v_k = (s_k / μ_k)²`. Sub-opção `adjust_for_banding = false` usa
  `s_k = Σ_i w_ik σ_i`, `μ_k^{raw} = Σ_i w_ik p_i` e `v_k = (s_k / μ_k^{raw})²`.
- **Método `external`:** o usuário informa `v_k` (variância do fator de média 1) ou `cv_k = sqrt(v_k)` por setor
  no TOML (`[sector_variance.values]`) ou em arquivo CSV/parquet indicado no TOML. Validar: todos os setores da
  base presentes, valores finitos `>= 0`, sem setores extras (erro) — `pd_vol` é então ignorada no cálculo
  (mas ainda validada).
- Ambos os métodos sempre reportam, em `result.sectors`, o `v_k` implícito pela `pd_vol` **e** o usado, para
  comparação.
- Setor 0: `v_0 = 0`. Setores com `μ_k = 0` são ignorados; com `v_k = 0` são tratados como Poisson.
- Fator `S_k ~ Gamma(α_k = 1/v_k, β_k = v_k)`, setores independentes.

> Estas agregações são **reduções** (map-reduce): computáveis por lote e somáveis. São os únicos passos que
> tocam as centenas de milhões de linhas (além das contribuições); o resto opera em arrays de tamanho `ν_max`
> ou `M`.

### 5.3 Função geradora de probabilidades (PGF)
Com `t_k(z) = Σ_ν λ_{k,ν} (z^ν − 1)`:

```
G(z) = exp( Σ_{k: v_k=0} t_k(z) ) · Π_{k: v_k>0} (1 − v_k · t_k(z))^(−1/v_k)
```

### 5.4 Motor principal: FFT (`distribution/fft.py`)
1. Grade de tamanho `M` (`scipy.fft.next_fast_len`), §6.3.
2. Para cada setor: `λ_k` como vetor de comprimento `M` (índice = banda), `T_k = rfft(λ_k)`,
   `t_k = T_k − μ_k`.
3. Acumular `log φ = Σ_{Poisson} t_k + Σ_{Gamma} −(1/v_k)·log(1 − v_k t_k)`.
   (Ramo principal do log é contínuo: `Re(1 − v_k t_k) >= 1`. Testar.)
   Setores Poisson: somar os `λ` **antes** e fazer uma única FFT.
4. `g = irfft(exp(log φ), n=M)`; zerar negativos com `|g_x| < tol_clip`; **erro** se houver negativo maior.
5. Processar setores **sequencialmente** acumulando `log φ` (memória O(M), não O(K·M)).
6. Otimização opcional (fase 6): janela deslocada `[s, s+M)` com `s = floor(EL_u − z_low·σ_u)`,
   multiplicando `φ` por `z^{−s}`; teste de equivalência obrigatório.

### 5.5 Motor de referência: Panjer estável (Haaf–Reiß–Schoenmakers, 2004) (`distribution/panjer.py`)
Cada setor Gamma é Binomial Negativa composta; setor Poisson é Poisson composta; ambas classe (a,b,0) com
todos os termos positivos (estável):

- Gamma: `q_k = v_k μ_k / (1 + v_k μ_k)`, `a = q_k`, `b = (1/v_k − 1)·q_k`, `g_0 = (1 − q_k)^{1/v_k}`.
- Poisson: `a = 0`, `b = μ_k`, `g_0 = exp(−μ_k)`.
- Severidade `h_ν = λ_{k,ν}/μ_k` (ν >= 1, `h_0 = 0`).
- Recursão: `g_x = Σ_{j=1}^{min(x,ν_max)} (a + b·j/x)·h_j·g_{x−j}`.
- Convolução entre setores via FFT. Kernel em numba (`@njit(cache=True)`), fallback numpy.
- Uso: portfólios pequenos/médios e **validação cruzada do motor FFT**. Detectar underflow de `g_0`
  (`μ_k` grande) e levantar `NumericalRangeError` sugerindo o motor FFT.

### 5.6 Momentos analíticos (`moments.py`) — oráculo de validação
Em unidades de perda:
- `EL_u = Σ_k Σ_ν ν·λ_{k,ν}`; `EL_k = Σ_ν ν·λ_{k,ν}`.
- `Var_u = Σ_k Σ_ν ν²·λ_{k,ν} + Σ_{k>=1} v_k · EL_k²`.
- `σ_u = sqrt(Var_u)`. Em moeda: multiplicar por `L0` (e `L0²`).

### 5.7 Medidas de risco (`risk_measures.py`), para cada `α` em `config.alphas`
- `F(x) = Σ_{y<=x} g_y`. `VaR_α = q·L0`, `q = min{x : F(x) >= α}`.
- ES (Acerbi–Tasche, coerente em distribuição discreta):
  `ES_α = L0/(1−α) · [ Σ_{x>q} x·g_x + q·(F(q) − α) ]`.
- `EC_α = VaR_α − EL`. Também `ES_α − EL`.
- Caudas calculadas por **soma acumulada reversa** (não `1 − cdf`, por precisão).

### 5.8 Contribuições de risco por operação (`contributions.py`) — alocação de Euler
Todas as fórmulas são **por operação `i`**, usando a banda `ν_j` do seu devedor; resultados em moeda.
`σ_u`, `EL_k` em unidades de perda (§5.6).

**Desvio-padrão (analítico):**
`RC^σ_i = (p_i E_i / σ_u) · (ν_j + Σ_{k>=1} v_k · w_ik · EL_k)`. Soma sobre todas as operações = `σ_u · L0`.

**VaR/ES (Haaf & Tasche, 2002):**
`E[L_i 1{L=x}] = (p_i E_i / L0) Σ_{k=0}^K w_ik · g^{(k)}_{x−ν_j}`, onde
`G^{(k)}(z) = G(z) / (1 − v_k t_k(z))` para `k>=1` com `v_k>0`, e `g^{(k)} = g` para setores Poisson/idiossincrático.

Implementação O(n·K) com pré-computação por setor sobre `ν ∈ [1, ν_max]`:
- `β = (F(q) − α) / g_q`.
- `A_k^{ES}(ν) = [ T^{(k)}(q−ν) + β·g^{(k)}_{q−ν} ] / (1−α)`, com `T^{(k)}(x) = Σ_{y>x} g^{(k)}_y`
  (para `x < 0`: `T = 1`, `g = 0`).
- `A_k^{VaR}(ν) = g^{(k)}_{q−ν} / g_q`.
- Por operação: `RC^{ES}_i = p_i E_i Σ_k w_ik A_k^{ES}(ν_j)` e `RC^{VaR}_i = p_i E_i Σ_k w_ik A_k^{VaR}(ν_j)`.
- Calcular cada `g^{(k)}` um por vez, reduzir imediatamente a `A_k` (comprimento `ν_max`) e descartar.
  Tabela final `A` tem forma `(n_alphas, K+1, ν_max+1)` — pequena, cabe em cache.
- Garantias (testar): `Σ_i RC^{ES}_i = ES_α`, `Σ_i RC^{VaR}_i = VaR_α`, `Σ_i RC^σ_i = σ`.
- Contribuições de VaR em distribuição discreta são ruidosas: documentar; opção `var_smoothing_window`
  (média de `A^{VaR}` numa janela de unidades em torno de `q`, renormalizada para fechar em `VaR_α`).
- Saída por operação: `operation_id`, `obligor_id`, `el`, `rc_sigma`, `rc_var_<α>`, `rc_es_<α>` (Float64),
  **escrita em parquet por lote** (§6.4). Nunca acumular as centenas de milhões de linhas em memória.

### 5.9 Monte Carlo (`montecarlo.py`) — somente validação
Simula `S_k ~ Gamma`, número de defaults por (setor, banda) `~ Poisson(λ_{k,ν} · S_k)` (equivalente em
distribuição à simulação por devedor, muito mais barato). `np.random.Generator(PCG64(seed))`.
Usado nos testes de integração. Variante por devedor (lenta) só em testes pequenos, para validar a equivalência.

---

## 6. Performance e escala

### 6.0 Ambiente-alvo e orçamento
- Máquina de referência: Ryzen 7 7735HS (8 núcleos / 16 threads), 32 GB RAM, **sem GPU utilizável** (Radeon
  integrada; não adicionar dependências CUDA/ROCm).
- **Orçamento de memória: `memory_budget_gb = 9.0`** (30% de 32 GB) para o processo inteiro, incluindo polars.
  Toda decisão de tamanho (lotes, partições, grade FFT) é derivada desse valor, que fica no TOML.
- Threads: polars usa o pool próprio (`POLARS_MAX_THREADS`, definido **antes** do import, padrão 16);
  `scipy.fft` com `workers = 8`; kernels numba com `numba.set_num_threads(8)`.

### 6.1 Pipeline em passes (todos em polars lazy/streaming, nunca `.collect()` na base inteira)
O trabalho é dividido em `P` **partições por hash de `obligor_id`** (`obligor_partitions`, `"auto"` = menor `P`
cuja tabela de devedores cabe em ~40% do orçamento). Todas as operações de um devedor caem na mesma partição,
então cada partição é independente e os agregados somam.

- **Passo A — tabela de devedores** (por partição): `group_by(obligor_id).agg(E_j = sum(lgd·ead),
  S1 = sum(E·pd), S2 = sum(E·pd²))` em modo streaming. Checagem de consistência de PD:
  `E_j·S2 − S1² > tol·E_j²` → conta devedores inconsistentes (aviso). Grava `(obligor_id, E_j)` em parquet num
  diretório temporário seguro (§9). Custo de memória ≈ 32 B/devedor (ids inteiros); **recomendar ids
  inteiros** (string multiplica o custo). Coleta também estatísticas para `L0` (máximo de `E_j`, `Σ p_i E_i`).
- **Escolha de `L0` e `M`** (§6.3), com as estatísticas do passo A.
- **Passo B — agregação setorial** (por partição): `join` com a tabela de devedores, `ν_j` como expressão, e
  `group_by(ν).agg(Σ w_ik p_i E_i/(ν L0), Σ w_ik σ_i E_i/(ν L0))` para todos os `k` → matriz
  `(K+1) × (ν_max+1)`. O `group_by` tem no máximo `ν_max` grupos (minúsculo). Resultado: `SectorBandAggregate`
  pequeno e **somável** (`__add__`, testado).
- **Passo C — distribuição**: O(K · M log M), independente de `n`.
- **Passo D — contribuições por operação** (por partição): `join` com a tabela de devedores e com a tabela
  pequena `A` indexada por `ν` (§5.8), expressões polars para `rc_*`, e `sink_parquet` direto no destino
  (`output.contributions_path`). Nunca materializa a saída.

### 6.2 Regras de performance
- Sem `apply`, `map_elements`, `iterrows` ou loops Python por linha; preferir expressões polars nativas.
  `map_batches` com numpy só quando não houver expressão nativa, e com teste de equivalência.
- `select` só das colunas necessárias e casts no plano lazy, antes de qualquer outra operação.
- Fonte releitura: a entrada `LazyFrame` é reexecutada em cada passo/partição; documentar que a fonte ideal é
  parquet com row groups de ~1M linhas (`pl.scan_parquet`).
- Engine de streaming do polars (`collect(engine="streaming")` / `sink_parquet`), versão de polars fixada no lock.
- FFT com `scipy.fft` (`rfft`/`irfft`, metade da memória), setores processados sequencialmente.
- Benchmarks (`pytest-benchmark`, marcados `slow`): throughput de cada passo (linhas/s), tempo do passo C por
  `M` e `K`, **pico de RSS** medido em subprocesso. Registrar em `docs/performance.md`. Meta inicial a validar:
  base de 300 M de linhas processada com pico de RSS <= `memory_budget_gb`.

### 6.3 Escolha de `L0` e da grade `M`
- `L0` automático: menor valor tal que `ν_max <= max_bands` **e** `M_estimado <= max_grid`; documentar o
  trade-off precisão de banding × custo. `L0` fixo no TOML sobrepõe.
- `M` inicial = `next_fast_len(ceil(EL_u + z_tail·σ_u) + ν_max)` com `z_tail` padrão 15.
- `max_grid` padrão `2**26` (≈ 2 GB de arrays de trabalho no pico); validar contra o orçamento.
- Pós-checagem: massa nos últimos 1% da grade `< tol_tail` (1e-12), `|E[L]−EL_u|/EL_u < tol_moment`
  e idem para variância. Se falhar, dobrar `M` até `max_grid`; senão `GridTooSmallError`.
- Todos os diagnósticos vão para `result.diagnostics`.

### 6.4 Saídas
- Contribuições por operação: parquet particionado (`part-<p>.parquet`), compressão zstd, colunas de §5.8.
- Resumo (`summary.json`): EL, UL, VaR, ES, EC por α, `L0`, `M`, tabela de setores, diagnósticos, versão do
  pacote e hash SHA-256 do TOML usado (reprodutibilidade).
- Distribuição de perdas: parquet `(loss, prob, cdf)`, truncada onde a cauda for `< tol_tail`.

---

## 7. Arquitetura

```
src/crplus/
  __init__.py            # exporta run_creditrisk_plus, load_config, CRPlusConfig, CRPlusResult
  api.py                 # orquestração dos passos (borda)
  config.py              # load_config(toml) -> CRPlusConfig (frozen, validado); ColumnMap
  exceptions.py          # CRPlusError, InputValidationError, ConfigError, GridTooSmallError,
                         # NumericalRangeError, MemoryBudgetError
  sources.py             # normaliza LazyFrame/DataFrame/pandas; select + casts; partição por hash
  validation.py          # regras vetorizadas (expressões polars) + ValidationReport
  obligor.py             # passo A: tabela de devedores, consistência, estatísticas
  banding.py             # escolha de L0, expressão de nu_j, fator de ajuste
  aggregation.py         # passo B: SectorBandAggregate (+ soma entre partições)
  sectors.py             # mu_k, s_k, v_k (métodos pd_vol e external), tabela de setores
  moments.py             # momentos analíticos
  memory.py              # orçamento: derivação de partições, max_grid, checagens
  distribution/
    __init__.py          # interface LossDistributionEngine (Protocol) + registro de motores
    fft.py               # motor principal
    panjer.py            # motor de referência estável (numba)
  risk_measures.py       # VaR, ES, EC, cdf/tail
  contributions.py       # tabela A e passo D (sink_parquet)
  montecarlo.py          # validação
  results.py             # CRPlusResult, SectorTable, Diagnostics, escrita de summary.json
  tempstore.py           # diretório temporário seguro e limpeza garantida
tests/
  unit/                  # espelha src/ (test_<modulo>.py)
  integration/
  benchmarks/
  conftest.py            # fixtures e geradores sintéticos com seed
docs/                    # mkdocs
crplus.example.toml      # exemplo de configuração comentado
```

API pública mínima:

```python
import polars as pl
from crplus import load_config, run_creditrisk_plus

config = load_config("crplus.toml")
result = run_creditrisk_plus(pl.scan_parquet("carteira/*.parquet"), config)
result.el, result.ul, result.var[0.999], result.es[0.999], result.ec[0.999]
result.loss_distribution        # LossDistribution(probs, loss_unit, offset)
result.sectors                  # pl.DataFrame: mu_k, s_k, v_k_pd_vol, v_k_usado, EL_k, contribuição do setor
result.contributions_path       # Path do parquet de contribuições por operação
result.diagnostics              # grade, massa de cauda, erros de momentos, erro de banding, memória, tempos
```

### 7.1 Arquivo de configuração (`crplus.toml`)
Carregado com `tomllib` (seguro), validado campo a campo; chaves desconhecidas → `ConfigError`.
Exemplo completo e comentado em `crplus.example.toml`:

```toml
[model]
alphas = [0.99, 0.999]
engine = "fft"                    # "fft" | "panjer"
loss_unit = "auto"                # ou número na moeda do EAD
banding = "ceil"                  # "ceil" | "round"

[sector_variance]
method = "pd_vol"                 # "pd_vol" | "external"
adjust_for_banding = true         # só para method = "pd_vol"
# values_file = "variancias_setoriais.csv"   # para method = "external" (colunas: sector, variance)
# [sector_variance.values]                   # alternativa inline
# w_agro = 0.85

[columns]
operation_id = "operation_id"
obligor_id = "obligor_id"
pd = "pd"
pd_vol = "pd_vol"
lgd = "lgd"
ead = "ead"
weight_prefix = "w_"

[validation]
strict = true
pd_warn_threshold = 0.3
weights_tolerance = 1e-9
check_operation_id_unique = true  # custo de memória alto em bases enormes; ver docs

[numerics]
z_tail = 15
tol_tail = 1e-12
tol_moment = 1e-8
max_bands = 100_000
max_grid = 67_108_864             # 2**26
var_smoothing_window = 0

[resources]
memory_budget_gb = 9.0
obligor_partitions = "auto"
polars_threads = 16
fft_workers = 8

[output]
directory = "saida_crplus"
overwrite = false
write_contributions = true
```

---

## 8. Baixa complexidade ciclomática (regra dura)

- `ruff` regra `C901` com `max-complexity = 5`; `xenon` exige grau **A** em tudo.
- Funções com no máximo ~30 linhas e no máximo 5 parâmetros (agrupar em dataclasses).
- Ramificações por tipo/estratégia via **dicionário de despacho** ou `Protocol`, não cadeias de `if/elif`.
- Validação como **lista de regras** (`Rule` = nome + função vetorizada), iterada uniformemente.
- Nunca "baixar" o limite ou adicionar `# noqa: C901`. Se estourar, refatorar.

Trecho obrigatório no `pyproject.toml`:

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E","F","W","I","B","C90","S","N","UP","SIM","RUF","PL","NPY","PD","PT","D","ANN","ERA"]
ignore = ["D203","D213"]

[tool.ruff.lint.mccabe]
max-complexity = 5

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101","PLR2004","D","ANN"]

[tool.bandit]
exclude_dirs = ["tests"]

[tool.pytest.ini_options]
markers = ["slow: testes de escala/benchmark", "integration: teste de integração ponta a ponta"]
addopts = "--strict-markers -ra"

[tool.coverage.report]
fail_under = 95
show_missing = true
```

---

## 9. Segurança (SAST básico) — obrigatório

1. **Ferramentas em CI e pre-commit**: `ruff` (regras `S` / flake8-bandit), `bandit -ll`, `pip-audit`,
   `detect-secrets`. Opcional: `semgrep --config p/python`.
2. **Proibido**: `eval`, `exec`, `pickle`/`joblib.load`/`np.load(allow_pickle=True)` de fontes não confiáveis,
   `yaml.load` sem `SafeLoader`, `subprocess` com `shell=True`, `assert` para checagens de runtime,
   `tempfile.mktemp`, segredos no código.
3. **Validação de entrada** completa (§4.2) antes de qualquer cálculo. Config TOML lida só com `tomllib`,
   validada no `__post_init__`, chaves desconhecidas rejeitadas, tipos e faixas checados.
4. **Limites de recursos** contra DoS por entrada maliciosa/errada: `max_bands`, `max_grid`, `max_sectors`,
   `memory_budget_gb`; estimar memória **antes** de alocar e levantar `MemoryBudgetError` com mensagem clara.
5. **Logging sem dados sensíveis**: apenas agregados e contagens; nunca IDs, valores de EAD individuais ou
   linhas do DataFrame. Usar `logging` (sem `print`).
6. **Caminhos de arquivo** (config, variâncias externas, saídas): `pathlib`, `resolve()`, rejeitar caminhos
   fora do diretório base configurado (path traversal) e links simbólicos inesperados; não sobrescrever sem
   `overwrite = true`.
   Temporários (`tempstore.py`): `tempfile.mkdtemp` com permissão `0o700`, limpeza garantida em
   `finally`/context manager, inclusive em erro.
7. **Numérico**: `np.errstate(over="raise", invalid="raise")` nos trechos críticos; checar finitude dos resultados.
8. **Supply chain**: `uv.lock` versionado, versões mínimas fixadas, `pip-audit` sem vulnerabilidades altas.
9. **Determinismo**: aleatoriedade só via `np.random.Generator` com seed explícita.
10. Testes de segurança explícitos em `tests/unit/test_security.py` (ex.: `max_bands` estourado levanta erro;
    NaN injetado é rejeitado; mensagens de erro não contêm valores de linha).

---

## 10. Testes

### 10.1 O que é "teste unitário intencional" neste projeto
- Cada teste protege **uma regra de negócio, propriedade matemática ou contrato** — não detalhes de implementação.
- Nome: `test_<unidade>_<comportamento_esperado>_<condição>`.
- Docstring obrigatória começando com **`Intenção:`** explicando o que quebra se o teste falhar.
- Estrutura Arrange / Act / Assert; um comportamento por teste; sem lógica condicional no teste.
- Oráculos independentes: fórmula fechada, `scipy.stats`, momentos analíticos, Monte Carlo ou outro motor.
- Propriedades com `hypothesis` onde houver invariantes.
- Cobertura >= 95% linhas **e** branches. Para `banding`, `distribution`, `risk_measures`, `contributions`:
  rodar `mutmut` periodicamente; mutantes sobreviventes viram novos testes.

Exemplo do padrão:

```python
def test_banding_preserves_expected_loss_for_any_loss_unit() -> None:
    """Intenção: o ajuste de PD no banding deve preservar exatamente a perda esperada do portfólio.
    Se falhar, EL e todas as medidas derivadas ficam viesadas pelo arredondamento de exposições."""
```

### 10.2 Testes unitários mínimos por módulo
- **config**: TOML de exemplo carrega; cada campo inválido (tipo, faixa, chave desconhecida) gera
  `ConfigError` com o nome do campo; `method = "external"` sem valores/arquivo é rejeitado.
- **validation**: cada regra rejeita o caso inválido e aceita o limite válido (PD=0, PD=1, LGD=1,
  peso residual = 0); `strict=False` remove apenas linhas inválidas; mensagens sem valores nem IDs.
- **sources**: `DataFrame`, `LazyFrame` e pandas produzem o mesmo plano/resultado; colunas renomeadas via
  `[columns]`; partição por hash coloca todas as operações de um devedor na mesma partição e cobre todas as
  linhas sem duplicar.
- **obligor**: `E_j` correto; inconsistência de PD intra-devedor detectada e contada; 1 partição == P partições.
- **banding**: EL preservada (hypothesis); `ν >= 1`; `E_j == k·L0` cai na banda `k`; `max_bands` respeitado;
  devedor com várias operações vai para a banda da exposição **somada**.
- **aggregation**: soma de agregados de partições == agregado do todo (hypothesis, ordem de linhas
  irrelevante); formulação linear por operação == cálculo explícito por devedor quando PD/pesos são iguais.
- **sectors**: `v_k` correto em caso de mão para `pd_vol` (com e sem `adjust_for_banding`) e `external`;
  setor faltando/sobrando em `external` → erro; setor com `μ_k=0` ignorado; `v_k=0` vira Poisson; pesos
  residuais vão ao setor 0; tabela reporta `v_k` implícito e usado.
- **memory**: estimativas monotônicas no tamanho; orçamento estourado → `MemoryBudgetError` antes de alocar.
- **moments**: casos com resultado conhecido (um devedor; um setor).
- **distribution (FFT e Panjer)**:
  - só idiossincrático, `ν=1` → `scipy.stats.poisson`;
  - um setor, `ν=1` → `scipy.stats.nbinom(n=1/v, p=1/(1+vμ))`;
  - Poisson composta com bandas mistas: FFT == Panjer;
  - soma das probabilidades = 1; sem negativos; média e variância == §5.6;
  - FFT == Panjer em portfólio aleatório pequeno (`max|Δ| < 1e-10`);
  - grade pequena dispara aumento automático ou `GridTooSmallError`;
  - janela deslocada == janela completa.
- **risk_measures**: VaR/ES em distribuição discreta construída à mão; ES >= VaR; monotonicidade em α.
- **contributions**: somas de Euler (σ, VaR, ES) fecham com tolerância 1e-8; operação com peso só no setor 0
  recebe contribuição sem termo sistêmico; dividir uma operação em duas metades do mesmo devedor divide a
  contribuição e não muda o portfólio; parquet escrito tem uma linha por operação válida, com `operation_id`.
- **montecarlo**: reprodutível com a mesma seed.
- **security**: ver §9 item 10.

### 10.3 Teste de integração final (`tests/integration/test_end_to_end.py`, marcador `integration`)
Portfólio sintético com seed (~500 mil operações, 8 setores + idiossincrático, PD log-normal, EAD de cauda
pesada, `obligor_id` com múltiplas operações), executando a API pública ponta a ponta:

0. Executa a partir de um `crplus.toml` e de `pl.scan_parquet` sobre arquivos gerados no `tmp_path`.
1. Entrada `LazyFrame`, `DataFrame` e pandas produzem resultados idênticos.
2. Processamento com 1 partição e com N partições produz resultados idênticos.
3. Distribuição soma 1; média e variância == momentos analíticos (rel. 1e-8).
4. VaR e ES a 99,9% dentro do intervalo de confiança de Monte Carlo (>= 2 milhões de cenários).
5. Motor FFT == motor Panjer.
6. Somas de Euler fecham para σ, VaR e ES.
7. **Golden file** (`tests/integration/golden/*.json`) para regressão; atualizar só com flag explícita
   `--update-golden` e justificativa no commit.
8. Métodos `pd_vol` e `external` (com as variâncias implícitas da `pd_vol` passadas como externas) produzem
   o mesmo resultado.
9. Parquet de contribuições: soma por coluna == medidas do portfólio; `summary.json` consistente.
10. Diagnósticos sem alertas; diretório temporário removido ao final, inclusive quando o run falha.

Teste de escala (`slow`, `tests/benchmarks/`): 50–300 milhões de linhas sintéticas gravadas em parquet por
lote, executado em **subprocesso** medindo pico de RSS <= `memory_budget_gb`, e registrando throughput.

Benchmark de referência externa: **ainda não há valores de referência** de outro CR+. Deixar
`tests/integration/reference/` com um teste `skip` e um leitor de casos (entrada + resultados esperados) para o
usuário incluir quando tiver.

---

## 11. Documentação (`docs/`, mkdocs-material + mkdocstrings)

- `index.md` — visão geral, instalação, exemplo mínimo.
- `metodologia.md` — toda a matemática da §5 com derivações curtas e referências.
- `guia-de-uso.md` — contrato de entrada, preparo da base em parquet, interpretação dos resultados.
- `configuracao.md` — cada chave do TOML: significado, padrão, faixa válida, impacto em precisão/memória.
- `performance.md` — arquitetura de passes, tuning de partições/`L0`/`M`, orçamento de memória, benchmarks.
- `validacao.md` — estratégia de testes, oráculos, resultados do teste de integração.
- `seguranca.md` — controles da §9.
- `referencia-api.md` — gerado por mkdocstrings.
- `adr/` — Architecture Decision Records (FFT como motor principal, banding `ceil`, método de variância
  setorial, tratamento devedor × operação, etc.).
- `CHANGELOG.md` (Keep a Changelog) e `README.md`.

`mkdocs build --strict` deve passar sem warnings.

---

## 12. Plano de implementação (seguir na ordem, TDD em cada fase)

Para cada fase: escrever os testes intencionais primeiro → implementar → `make check` verde → atualizar docs.

0. **Esqueleto**: `pyproject`, `Makefile`, pre-commit, CI, mkdocs, exceções, `config` + `crplus.example.toml`,
   `tempstore`, `memory`.
1. **Entrada**: `sources`, `validation`, `obligor` (passo A).
2. **Banding e agregação**: `banding`, `aggregation` (passo B), `sectors` (dois métodos), `moments`.
3. **Distribuição**: `panjer` (referência) e depois `fft`, com checagens de grade.
4. **Medidas de risco**: `risk_measures`.
5. **Contribuições**: σ analítico, VaR/ES Haaf–Tasche, passo D com `sink_parquet`.
6. **Escala**: partições automáticas pelo orçamento, janela deslocada, benchmarks com pico de RSS.
7. **Integração**: `api.py`, Monte Carlo, teste de integração final, golden files.
8. **Documentação final** e revisão de segurança (`/security-review`).

---

## 13. Regras de conduta para o Claude Code

- Não pular etapas de verificação nem reduzir limites (cobertura, complexidade, tolerâncias) para "fazer passar".
- Não alterar fórmulas da §5 sem registrar ADR e avisar o usuário.
- Se um teste revelar divergência numérica, investigar a causa; não afrouxar a tolerância sem justificativa.
- Commits pequenos, um tema por commit, mensagens no imperativo.
- Ao concluir cada fase, resumir: o que foi feito, saídas de `make check`, pendências.

---

## 14. Premissas (confirmadas pelo usuário)

1. `pd_vol` é **absoluta** (desvio-padrão na mesma unidade da PD).
2. Existe **`obligor_id`**; o default é por devedor (§5.0).
3. Pesos em formato **wide** (`w_<setor>`); resíduo `1 − Σw` vai para o setor idiossincrático.
4. Variância setorial: implementar **os dois** métodos (`pd_vol` e `external`), escolhidos no TOML.
5. Motor de dados: **polars** (mais rápido); pandas só via conversão.
6. Contribuições **por operação**; agregação é feita pelo usuário passando a base já agregada.
7. Níveis de confiança e demais parâmetros vêm do **arquivo de configuração** (padrão 0,99 e 0,999).
8. Hardware: Ryzen 7 7735HS, 32 GB; **orçamento de 9 GB** de memória; sem GPU.
9. Fora de escopo: LGD estocástica, correlação entre setores, multiperíodo.
10. Sem valores de referência externos por enquanto (§10.3).

Ainda em aberto (perguntar se afetar a implementação; até lá usar o padrão):
- Tipo de `obligor_id`/`operation_id` (padrão: aceitar qualquer; recomendar inteiro por memória).
- Quantidade aproximada de devedores (padrão: `obligor_partitions = "auto"`).
- PD/pesos são sempre iguais entre operações do mesmo devedor? (padrão: aviso e combinação ponderada por EL).

---

## 15. Referências

- Credit Suisse First Boston (1997). *CreditRisk+: A Credit Risk Management Framework*.
- Gundlach, M.; Lehrbass, F. (orgs.) (2004). *CreditRisk+ in the Banking Industry*. Springer.
- Haaf, H.; Reiß, O.; Schoenmakers, J. (2004). *Numerically stable computation of CreditRisk+*.
- Haaf, H.; Tasche, D. (2002). *Credit portfolio measurements*. GARP Risk Review.
- Acerbi, C.; Tasche, D. (2002). *On the coherence of Expected Shortfall*.
- Tasche, D. (2004). *Capital allocation for credit portfolios with kernel estimators* (contribuições de VaR).
- Panjer, H. (1981). *Recursive evaluation of a family of compound distributions*.
`````

<!-- FILE: Makefile -->
`````
# Ferramentas chamadas como `python -m <ferramenta>`: funciona mesmo onde políticas de controle
# de aplicativos do Windows bloqueiam os executáveis gerados em .venv/Scripts.
RUN := uv run python -m

.PHONY: install test integration lint format typecheck security complexity docs check slow

install:
	uv sync --all-extras

test:
	$(RUN) pytest -m "not slow" --cov=crplus --cov-branch --cov-fail-under=95

integration:
	$(RUN) pytest -m integration

lint:
	$(RUN) ruff check . && $(RUN) ruff format --check .

format:
	$(RUN) ruff check --fix . && $(RUN) ruff format .

typecheck:
	$(RUN) mypy --strict src

security:
	$(RUN) bandit -r src -c pyproject.toml -ll && $(RUN) pip_audit
	git ls-files -z | xargs -0 $(RUN) detect_secrets.pre_commit_hook --baseline .secrets.baseline

complexity:
	$(RUN) xenon --max-absolute A --max-modules A --max-average A src

# Só valida a documentação (links, referências da API): o HTML vai para um diretório temporário
# fora do projeto e é apagado em seguida. A documentação é lida direto dos Markdown em docs/.
docs:
	@out=$$(mktemp -d) && $(RUN) mkdocs build --strict --quiet --site-dir "$$out"; \
	status=$$?; rm -rf "$$out"; exit $$status

slow:
	$(RUN) pytest -m slow

check: lint typecheck test integration security complexity docs
`````

<!-- FILE: README.md -->
`````markdown
# crplus — CreditRisk+ em Python

Réplica completa do **CreditRisk+** (CSFB, 1997), com as extensões numericamente estáveis da
literatura (Panjer estável de Haaf–Reiß–Schoenmakers, contribuições de Haaf–Tasche), projetada
para carteiras de **centenas de milhões de operações** dentro de um orçamento de memória fixo
(padrão 9 GB), usando `polars` em modo *lazy/streaming*.

- Distribuição de perdas completa (FFT; Panjer estável como referência).
- EL, UL, VaR, Expected Shortfall e capital econômico por nível de confiança.
- Contribuições de risco (σ, VaR, ES) **por operação**, gravadas em parquet.
- Parâmetros e diagnósticos por setor; configuração em TOML.

## Instalação

```bash
uv sync --all-extras
```

## Uso

```python
import polars as pl
from crplus import load_config, run_creditrisk_plus

config = load_config("crplus.toml")          # veja crplus.example.toml
result = run_creditrisk_plus(pl.scan_parquet("carteira/*.parquet"), config)

result.el, result.ul, result.var[0.999], result.es[0.999], result.ec[0.999]
result.sectors                # parâmetros por setor (polars)
result.contributions_path     # parquet de contribuições por operação
result.diagnostics.alerts     # vazio quando tudo está nas tolerâncias
```

## Verificação

```bash
make check        # lint, tipos, testes (cobertura >= 95%), integração, SAST, complexidade, docs
make slow         # benchmarks de escala (pico de RSS em subprocesso)
```

No Windows sem `make`, rode os comandos do `Makefile` diretamente (`uv run python -m ...`).

## Documentação

Markdown em `docs/`: metodologia, guia de uso, configuração, performance, validação,
segurança, referência da API e ADRs. `make docs` apenas valida a documentação (links e
referências), sem gravar HTML no projeto.
`````

<!-- FILE: crplus.example.toml -->
`````toml
# Configuração de exemplo do crplus (CreditRisk+).
# Todos os valores abaixo são os PADRÕES do pacote. Chaves desconhecidas geram ConfigError.
# Caminhos relativos são resolvidos a partir do diretório deste arquivo e não podem sair dele.
# Documentação completa de cada chave: docs/configuracao.md

[model]
alphas = [0.99, 0.999]            # níveis de confiança de VaR/ES, em (0, 1)
engine = "fft"                    # "fft" (principal) | "panjer" (referência estável)
loss_unit = "auto"                # "auto" ou número positivo na moeda do EAD (L0)
banding = "ceil"                  # "ceil" | "round" (banda sempre >= 1)

[sector_variance]
method = "pd_vol"                 # "pd_vol" (CSFB, a partir da volatilidade das PDs) | "external"
adjust_for_banding = true         # só para method = "pd_vol"
value_type = "variance"           # só para "external": "variance" (v_k) | "cv" (sqrt(v_k))
# Para method = "external", informe exatamente UM dos dois abaixo:
# values_file = "variancias_setoriais.csv"   # colunas: sector, variance (ou cv)
# [sector_variance.values]                   # alternativa inline: setor = valor
# w_agro = 0.85

[columns]
operation_id = "operation_id"
obligor_id = "obligor_id"
pd = "pd"
pd_vol = "pd_vol"                 # desvio-padrão ABSOLUTO da PD
lgd = "lgd"
ead = "ead"
weight_prefix = "w_"              # colunas de peso setorial: w_<setor>

[validation]
strict = true                     # true: erro em violação; false: exclui linhas inválidas
pd_warn_threshold = 0.3           # PD acima disso gera aviso (Poisson piora)
weights_tolerance = 1e-9          # tolerância para soma de pesos > 1
check_operation_id_unique = true  # custo de memória alto em bases enormes
max_reported_rows = 10            # posições de linhas violadoras guardadas por regra

[numerics]
z_tail = 15.0                     # desvios-padrão de cauda no tamanho inicial da grade
tol_tail = 1e-12                  # massa máxima no último 1% da grade
tol_moment = 1e-8                 # erro relativo máximo de média e variância
tol_clip = 1e-13                  # negativos menores que isso após a FFT são zerados
max_bands = 100_000               # limite de segurança para a maior banda
max_grid = 67_108_864             # 2**26, limite de segurança para a grade
max_sectors = 1000                # limite de segurança para o número de setores
var_smoothing_window = 0          # suavização das contribuições de VaR (0 = desligada)

[resources]
memory_budget_gb = 9.0            # orçamento do processo inteiro (30% de 32 GB)
obligor_partitions = "auto"       # "auto" ou inteiro >= 1
polars_threads = 8                # 8 > 16 em memória e velocidade (ADR 0006)
fft_workers = 8
numba_threads = 8
weight_dtype = "float64"          # "float64" | "float32" (pesos)

[output]
directory = "saida_crplus"
overwrite = false
write_contributions = true
`````

<!-- FILE: docs/adr/0001-fft-motor-principal.md -->
`````markdown
# ADR 0001 — FFT como motor principal, Panjer estável como referência

**Estado:** aceito (fase 0).

## Contexto

A distribuição de perdas precisa ser calculada para carteiras com milhares de bandas e grades
de até $2^{26}$ pontos. A recursão de Panjer clássica do CSFB é numericamente instável; a variante
de Haaf–Reiß–Schoenmakers (2004) é estável, mas tem custo $O(M \cdot \nu_{max})$ por setor e
sofre underflow de $g_0$ quando $\mu_k$ é grande.

## Decisão

- Motor principal: inversão da PGF por FFT (`rfft`/`irfft`), custo $O(K \cdot M \log M)$,
  acumulando $\log \varphi$ setor a setor (memória $O(M)$).
- Motor de referência: Panjer estável em numba, usado em carteiras pequenas/médias e na
  validação cruzada do motor FFT (`max|Δ| < 1e-10`).

## Consequências

- Exige controle de *aliasing* (checagem de massa de cauda e dobra da grade até `max_grid`).
- Probabilidades negativas minúsculas da FFT são zeradas abaixo de `tol_clip`; acima, erro.
`````

<!-- FILE: docs/adr/0002-banding-ceil.md -->
`````markdown
# ADR 0002 — Banding `ceil` com ajuste que preserva a perda esperada

**Estado:** aceito (fase 0).

## Decisão

Banda do devedor $\nu_j = \max(1, \lceil E_j / L_0 \rceil)$ por padrão (`round` configurável,
sempre >= 1), com intensidade ajustada $\tilde p_{jk} = \sum_{i \in j} w_{ik} p_i E_i / (\nu_j L_0)$.

## Justificativa

- `ceil` nunca subestima a severidade de uma perda individual (conservador na cauda).
- O ajuste da intensidade preserva exatamente a perda esperada:
  $L_0 \sum_j \sum_k \tilde p_{jk} \nu_j = \sum_i p_i E_i$ (propriedade testada).
- Banda mínima 1 evita perdas nulas para exposições menores que $L_0$.

## Consequências

A variância fica levemente alterada pelo arredondamento; o erro de banding é reportado nos
diagnósticos e reduzido com $L_0$ menor (ao custo de grade maior).
`````

<!-- FILE: docs/adr/0003-variancia-setorial.md -->
`````markdown
# ADR 0003 — Dois métodos de variância setorial

**Estado:** aceito (fase 0).

## Decisão

`sector_variance.method` escolhe entre:

- **`pd_vol`** (padrão, CSFB): $s_k = \sum_i w_{ik} \sigma_i E_i / (\nu_j L_0)$ e
  $v_k = (s_k / \mu_k)^2$; com `adjust_for_banding = false`, usa as somas sem ajuste.
- **`external`**: $v_k$ (ou $cv_k$) informado inline no TOML ou em arquivo CSV/parquet.

Ambos reportam o $v_k$ implícito pela `pd_vol` e o usado, para comparação.

## Consequências

- No método `external`, setores faltando ou sobrando são erro; `pd_vol` continua sendo validada.
- A configuração exige exatamente uma fonte de valores para `external` e nenhuma para `pd_vol`,
  eliminando ambiguidade sobre qual valor foi usado.
`````

<!-- FILE: docs/adr/0004-devedor-operacao.md -->
`````markdown
# ADR 0004 — Default por devedor com formulação linear por operação

**Estado:** aceito (fase 0).

## Contexto

O CR+ modela o default por devedor: todas as operações de um devedor entram em default juntas.
Materializar PD, volatilidade e pesos por devedor em centenas de milhões de linhas não cabe no
orçamento de memória.

## Decisão

- Apenas a tabela `obligor_id → E_j` é materializada (passo A, particionada por hash).
- Cada operação contribui linearmente para os agregados na banda do seu devedor:
  $\lambda_{k,\nu_j} \mathrel{+}= w_{ik} p_i E_i / (\nu_j L_0)$ e
  $s_k \mathrel{+}= w_{ik} \sigma_i E_i / (\nu_j L_0)$.
- Isso equivale a um devedor com PD, volatilidade e pesos médios ponderados por $p_i E_i$; quando
  são iguais entre as operações (caso esperado), coincide com o CR+ por devedor.
- Inconsistências intra-devedor geram aviso com contagem de devedores afetados.

## Consequências

Contribuições são por operação, com a banda do devedor; a soma das operações de um devedor é a
contribuição do devedor.
`````

<!-- FILE: docs/adr/0005-chaves-de-configuracao-adicionais.md -->
`````markdown
# ADR 0005 — Chaves de configuração além do exemplo da especificação

**Estado:** aceito (fase 0).

## Contexto

A especificação (CLAUDE.md) cita parâmetros que não aparecem no TOML de exemplo dela:
`tol_clip` (§5.4), `max_sectors` (§9), threads do numba (§6.0), as "primeiras N linhas" do
relatório de validação (§4.2) e a escolha entre $v_k$ e $cv_k$ no método externo (§5.2).

## Decisão

Adicionadas as chaves, todas com padrão e validação de faixa:

| Chave | Padrão | Motivo |
|-------|--------|--------|
| `numerics.tol_clip` | `1e-13` | Limiar para zerar negativos da FFT. |
| `numerics.max_sectors` | `1000` | Teto de setores; com `max_bands` limita as tabelas setor × banda. |
| `resources.numba_threads` | `8` | Threads dos kernels numba. |
| `validation.max_reported_rows` | `10` | N do relatório de validação. |
| `sector_variance.value_type` | `"variance"` | Interpretação dos valores externos ($v_k$ ou $cv_k$). |
| `resources.weight_dtype` | `"float64"` | Pesos em `float32` "conforme config" (§4.1). |

Também foram definidos tetos rígidos de segurança (`max_bands` <= 10⁷, `max_grid` <= 2³¹,
`max_sectors` <= 10⁴, até 16 níveis `alphas`), e `max_grid` passa a ser validado contra 60% do
orçamento de memória (64 bytes por ponto de grade).

## Consequências

O padrão de `max_sectors` (1000) foi escolhido para que $(K+1)(\nu_{max}+1)$ com os padrões caiba
no orçamento; a checagem efetiva usa o $K$ real da base (fase 2).
`````

<!-- FILE: docs/adr/0006-threads-e-memoria.md -->
`````markdown
# ADR 0006 — 8 threads do polars por padrão e contenção de memória do passo D

**Estado:** aceito (fase 6). Altera um padrão da especificação (`polars_threads = 16`).

## Contexto

Medições de pico de memória (máximo entre *working set* e memória privada) numa carteira de
50 milhões de operações, com grade no máximo ($M \approx 2^{26}$):

| Configuração | Pico | Tempo |
|--------------|------|-------|
| 16 threads, `join` da tabela $A$ no passo D | 9,98 GB | 107 s |
| 8 threads, `join` da tabela $A$ | 7,66 GB | 99 s |
| 8 threads, *gather*, estado FFT liberado antes do passo D | 6,9 GB | 92 s |

O streaming do polars mantém lotes em voo por thread; no passo D, o `join` com a tabela $A$
alargava cada lote com $2\,n_\alpha\,(K+1)$ colunas.

## Decisão

1. `resources.polars_threads` e o padrão de `POLARS_MAX_THREADS` passam de 16 para **8**: menos
   memória e, na máquina de referência, também mais rápido.
2. O passo D consulta $A_k(\nu_j)$ por `gather` em vetores literais pequenos, sem `join`.
3. As tabelas $A$ e a distribuição truncada são calculadas logo após o passo C; o estado
   completo da FFT ($g$ e $\log\varphi$) sai de escopo antes do passo D.
4. Operações numéricas sobre vetores de tamanho $M$ são feitas *in place*.

## Consequências

O pico passa a ser dominado pelo passo C (vetores de tamanho $M$, limitado por `max_grid`) e
pelos lotes em voo do polars (proporcionais ao número de threads), e não pelo número de linhas.
`````

<!-- FILE: docs/adr/0007-robustez-numerica.md -->
`````markdown
# ADR 0007 — Robustez numérica: L0 automático, quantis e consistência intra-devedor

**Estado:** aceito (fases 1–7). Não altera as fórmulas da §5; detalha a implementação.

## Decisões

1. **$L_0$ automático com recalibração.** A estimativa inicial de $\sigma$ (parte Poisson,
   disponível no passo A) subestima carteiras correlacionadas. Após o passo B, se a grade
   estimada com o $\sigma$ exato exceder `max_grid`, $L_0$ é recalibrado (até 3 vezes). Se a
   distribuição não convergir em `max_grid` (caudas muito pesadas, $z = 15$ insuficiente),
   $L_0$ é multiplicado por 4 e o cálculo refeito (até 4 vezes). Com $L_0$ fixo no TOML, nada
   disso ocorre: o erro é levantado.
2. **Quantil com folga de $10^{-14}$.** $q = \min\{x : \bar F(x) \le 1-\alpha + 10^{-14}\}$:
   empates exatos (como $F = 0{,}8$ obtido por $0{,}5 + 0{,}3$) resolvem para o menor quantil em
   vez de depender do último bit.
3. **Massa fora da grade conta na cauda.** $P(L > x) = \sum_{y>x} g_y + \max(0, 1-\sum g)$, para
   que uma grade truncada não produza um VaR artificialmente baixo.
4. **Consistência intra-devedor por amplitude.** Em vez de $E_j S_2 - S_1^2$, o passo A mede
   $\max - \min$ de PD e `pd_vol` por devedor (tolerância $10^{-12}$) e compara o *hash* do vetor
   de pesos (mínimo × máximo). Detecta exatamente "valores diferentes", inclusive para pesos,
   com custo fixo por devedor.
5. **Renormalização de pesos dentro da tolerância.** Pesos com soma em $(1, 1+\text{tol}]$ são
   divididos pela soma, mantendo $w_{i0} \ge 0$ e a perda esperada exata.
6. **"Resultados idênticos" = diferença relativa $\le 10^{-9}$.** As reduções paralelas do polars
   somam em ordem não determinística; execuções equivalentes diferem em ~$10^{-11}$.
`````

<!-- FILE: docs/adr/index.md -->
`````markdown
# Architecture Decision Records

Registro das decisões de arquitetura. Toda alteração nas fórmulas da especificação (CLAUDE.md,
seção 5) exige um novo ADR.

| ADR | Título | Estado |
|-----|--------|--------|
| [0001](0001-fft-motor-principal.md) | FFT como motor principal, Panjer estável como referência | Aceito |
| [0002](0002-banding-ceil.md) | Banding `ceil` com ajuste que preserva a perda esperada | Aceito |
| [0003](0003-variancia-setorial.md) | Dois métodos de variância setorial | Aceito |
| [0004](0004-devedor-operacao.md) | Default por devedor com formulação linear por operação | Aceito |
| [0005](0005-chaves-de-configuracao-adicionais.md) | Chaves de configuração além do exemplo da especificação | Aceito |
| [0006](0006-threads-e-memoria.md) | 8 threads do polars por padrão e contenção de memória do passo D | Aceito |
| [0007](0007-robustez-numerica.md) | Robustez numérica: L0 automático, quantis e consistência | Aceito |
`````

<!-- FILE: docs/configuracao.md -->
`````markdown
# Configuração

A execução é controlada por um arquivo **TOML** lido com `tomllib` (biblioteca padrão; não executa
código). O exemplo completo e comentado está em `crplus.example.toml`, e todos os valores dele
são os padrões do pacote (há um teste que garante isso).

```python
from crplus import load_config

config = load_config("crplus.toml")              # base = diretório do TOML
config = load_config("crplus.toml", base_dir=".")  # base explícito
```

## Regras gerais

- Seções ou chaves desconhecidas geram `ConfigError` com o nome qualificado (`numerics.max_band`).
- Booleanos **não** são aceitos onde se espera inteiro (`max_bands = true` é erro).
- Números devem ser finitos (`nan`/`inf` são rejeitados).
- Seções ausentes usam os padrões.
- O arquivo deve ser UTF-8, ter no máximo 1 MiB e não pode ser link simbólico.
- O hash SHA-256 do arquivo fica em `config.source_sha256` (vai para o `summary.json`).
- **Caminhos** (`output.directory`, `sector_variance.values_file`) são resolvidos a partir do
  diretório base e não podem sair dele nem atravessar links simbólicos.
- A configuração é imutável depois de criada.

## `[model]`

| Chave       | Padrão          | Faixa válida                               | Efeito |
|-------------|-----------------|--------------------------------------------|--------|
| `alphas`    | `[0.99, 0.999]` | 1 a 16 valores distintos em (0, 1)         | Níveis de VaR/ES; armazenados ordenados. |
| `engine`    | `"fft"`         | `"fft"`, `"panjer"`                         | Motor da distribuição. Panjer é a referência estável, para carteiras pequenas/médias. |
| `loss_unit` | `"auto"`        | `"auto"` ou número > 0 (moeda do EAD)      | Unidade de perda $L_0$. Menor $L_0$ = banding mais preciso, grade maior. `auto` escolhe o menor $L_0$ viável (ver [metodologia](metodologia.md#2-banding)). |
| `banding`   | `"ceil"`        | `"ceil"`, `"round"`                         | Arredondamento de $E_j/L_0$; a banda é sempre >= 1. |

## `[sector_variance]`

| Chave                | Padrão       | Faixa válida                         | Efeito |
|----------------------|--------------|--------------------------------------|--------|
| `method`             | `"pd_vol"`   | `"pd_vol"`, `"external"`             | Origem de $v_k$. |
| `adjust_for_banding` | `true`       | booleano                             | Só para `pd_vol`: aplica o ajuste de banding também às volatilidades. |
| `value_type`         | `"variance"` | `"variance"`, `"cv"`                 | Só para `external`: valores são $v_k$ ou $cv_k=\sqrt{v_k}$. |
| `values`             | —            | tabela `setor = número >= 0`, não vazia | Valores externos inline (`[sector_variance.values]`). |
| `values_file`        | —            | caminho dentro do diretório base     | CSV/parquet com colunas `sector` e `variance` (ou `cv`). |

Com `method = "external"` é obrigatório informar **exatamente um** entre `values` e
`values_file`; com `method = "pd_vol"` nenhum dos dois é aceito. A correspondência entre
setores informados e colunas da base é validada na leitura da base (fase 2).

## `[columns]`

| Chave           | Padrão           | Efeito |
|-----------------|------------------|--------|
| `operation_id`  | `"operation_id"` | Chave da operação. |
| `obligor_id`    | `"obligor_id"`   | Devedor (o default é por devedor). Recomenda-se id inteiro (memória). |
| `pd`            | `"pd"`           | Probabilidade de default em 1 ano. |
| `pd_vol`        | `"pd_vol"`       | Desvio-padrão **absoluto** da PD. |
| `lgd`           | `"lgd"`          | Loss Given Default. |
| `ead`           | `"ead"`          | Exposure at Default (moeda). |
| `weight_prefix` | `"w_"`           | Prefixo das colunas de peso setorial (`w_<setor>`). |

Os seis nomes devem ser distintos e nenhum pode começar com `weight_prefix`.

## `[validation]`

| Chave                       | Padrão | Faixa válida   | Efeito |
|-----------------------------|--------|----------------|--------|
| `strict`                    | `true` | booleano       | `true`: erro em qualquer violação; `false`: exclui linhas inválidas e reporta. |
| `pd_warn_threshold`         | `0.3`  | (0, 1]         | PD acima disso gera aviso (a aproximação de Poisson piora). |
| `weights_tolerance`         | `1e-9` | [0, 1)         | Tolerância para $\sum_k w_{ik} > 1$. |
| `check_operation_id_unique` | `true` | booleano       | Unicidade de `operation_id`; custo de memória alto em bases enormes. |
| `max_reported_rows`         | `10`   | inteiro [0, 1000] | Posições de linhas violadoras guardadas por regra (nunca valores ou ids). |

## `[numerics]`

| Chave                  | Padrão       | Faixa válida            | Efeito |
|------------------------|--------------|-------------------------|--------|
| `z_tail`               | `15.0`       | (0, 100]                | Tamanho inicial da grade: $EL_u + z\,\sigma_u + \nu_{max}$. |
| `tol_tail`             | `1e-12`      | (0, 1)                  | Massa máxima admitida no último 1% da grade. |
| `tol_moment`           | `1e-8`       | (0, 1)                  | Erro relativo máximo de média/variância vs. momentos analíticos. |
| `tol_clip`             | `1e-13`      | (0, 1)                  | Negativos da FFT com módulo abaixo disso são zerados; acima, erro. |
| `max_bands`            | `100000`     | inteiro [1, 10 000 000] | Teto de $\nu_{max}$ (protege contra $L_0$ minúsculo). Deve ser < `max_grid`. |
| `max_grid`             | `67108864`   | inteiro [16, 2³¹]       | Teto da grade $M$ ($2^{26}$ ≈ 4 GB de trabalho no pico). Validado contra o orçamento. |
| `max_sectors`          | `1000`       | inteiro [1, 10 000]     | Teto do número de setores $K$. |
| `var_smoothing_window` | `0`          | inteiro >= 0            | Janela de suavização das contribuições de VaR (0 = desligada). |

## `[resources]`

| Chave                | Padrão   | Faixa válida              | Efeito |
|----------------------|----------|---------------------------|--------|
| `memory_budget_gb`   | `9.0`    | (0, 4096]                 | Orçamento do processo inteiro; todas as decisões de tamanho derivam dele. |
| `obligor_partitions` | `"auto"` | `"auto"` ou [1, 65 536]   | Partições por hash de `obligor_id`. `auto` = menor $P$ cuja tabela cabe em 40% do orçamento. |
| `polars_threads`     | `8`      | inteiro [1, 1024]         | `POLARS_MAX_THREADS` (só vale se definido antes do primeiro `import polars`; ver ADR 0006). |
| `fft_workers`        | `8`      | inteiro [1, 1024]         | Workers do `scipy.fft`. |
| `numba_threads`      | `8`      | inteiro [1, 1024]         | Threads dos kernels numba. |
| `weight_dtype`       | `"float64"` | `"float64"`, `"float32"` | Armazenamento dos pesos; `float32` reduz leitura e memória (cálculos sempre em `float64`). |

`max_grid` precisa caber em 60% do orçamento (64 bytes por ponto de grade); caso contrário a
configuração é rejeitada em `numerics.max_grid`. Com 9 GB, o padrão $2^{26}$ usa ~4 GB.

## `[output]`

| Chave                 | Padrão           | Efeito |
|-----------------------|------------------|--------|
| `directory`           | `"saida_crplus"` | Diretório de saída, dentro do diretório base. |
| `overwrite`           | `false`          | Permite sobrescrever saídas existentes. |
| `write_contributions` | `true`           | Grava o parquet de contribuições (`<directory>/contributions`). |
`````

<!-- FILE: docs/guia-de-uso.md -->
`````markdown
# Guia de uso

## Execução mínima

```python
import polars as pl
from crplus import load_config, run_creditrisk_plus

config = load_config("crplus.toml")
result = run_creditrisk_plus(pl.scan_parquet("carteira/*.parquet"), config)

result.el, result.ul                       # perda esperada e inesperada (moeda do EAD)
result.var[0.999], result.es[0.999]        # VaR e Expected Shortfall
result.ec[0.999]                           # capital econômico = VaR - EL
result.sectors                             # tabela de setores (polars)
result.contributions_path                  # diretório do parquet de contribuições
result.diagnostics.alerts                  # vazio quando tudo está nas tolerâncias
```

## Contrato de entrada

Uma linha por **operação**. Nomes configuráveis em `[columns]`.

| Coluna         | Tipo                       | Domínio | Significado |
|----------------|----------------------------|---------|-------------|
| `operation_id` | inteiro ou texto           | único   | chave da operação (vai para a saída) |
| `obligor_id`   | inteiro ou texto           | —       | devedor; o default é por devedor |
| `pd`           | numérico                   | [0, 1]  | PD em 1 ano |
| `pd_vol`       | numérico                   | >= 0    | desvio-padrão **absoluto** da PD |
| `lgd`          | numérico                   | [0, 1]  | Loss Given Default |
| `ead`          | numérico                   | >= 0    | exposição (moeda) |
| `w_<setor>`    | numérico                   | [0, 1]  | peso no setor (uma coluna por setor) |

- O resíduo $1 - \sum_k w_k$ vai para o setor idiossincrático; $\sum_k w_k > 1 +$
  `weights_tolerance` é erro.
- PD, `pd_vol` e pesos deveriam ser iguais entre as operações de um mesmo devedor; se não forem,
  o modelo usa a média ponderada por perda esperada e emite alerta.
- Entradas aceitas: `pl.LazyFrame` (recomendado), `pl.DataFrame` e `pandas.DataFrame`
  (extra `pandas`).

## Preparando a base

- Grave a carteira em **parquet** com *row groups* de ~1 milhão de linhas; use
  `pl.scan_parquet("pasta/*.parquet")`. A base é relida em cada passo e partição — nunca é
  carregada inteira.
- Prefira **ids inteiros**: ids texto custam mais memória na tabela de devedores.
- Selecione na origem apenas as colunas necessárias, se a base tiver muitas outras (o `crplus`
  já faz `select`, mas evita ler colunas desnecessárias de arquivos não colunares).
- Pesos em `float32` (`resources.weight_dtype = "float32"`) reduzem leitura e memória.

## Validação

Com `validation.strict = true` (padrão), qualquer violação levanta `InputValidationError`, cujo
atributo `report` traz contagens por regra e posições das primeiras linhas violadoras (nunca
valores nem ids). Com `strict = false`, as linhas inválidas são excluídas e aparecem nos alertas.
`operation_id` repetido é sempre erro.

## Saídas (`output.directory`)

| Arquivo | Conteúdo |
|---------|----------|
| `summary.json` | EL, UL, VaR, ES, EC por nível, `L0`, `M`, setores, diagnósticos, versão e SHA-256 do TOML |
| `loss_distribution.parquet` | `loss` (moeda), `prob`, `cdf`, truncada onde a cauda < `tol_tail` |
| `contributions/part-<p>.parquet` | `operation_id`, `obligor_id`, `el`, `rc_sigma`, `rc_var_<α>`, `rc_es_<α>` |

As colunas de contribuição somam exatamente as medidas do portfólio (alocação de Euler); a soma
das operações de um devedor é a contribuição do devedor. Para contribuições agregadas (por
segmento, por exemplo), agregue o parquet ou passe ao modelo a base já agregada.

Saídas anteriores do `crplus` não são sobrescritas sem `output.overwrite = true` (e, mesmo
assim, apenas os arquivos do próprio `crplus` são removidos).

## Interpretação

- **`result.sectors`**: `mu_k` (intensidade), `s_k`, `v_k_pd_vol` (implícito pela `pd_vol`),
  `v_k_used`, `el_k` (moeda) e `variance_k` (contribuição sistêmica à variância).
- **`result.diagnostics`**: `L0`, $\nu_{max}$, grade e checagens de cauda e momentos, erro de
  banding, partições, contagens, relatório de validação, erros das somas de Euler, tempos e
  estimativas de memória.
- **Contribuições de VaR** são ruidosas em distribuições discretas; prefira as de ES ou use
  `numerics.var_smoothing_window`.

## Erros

| Exceção | Quando |
|---------|--------|
| `ConfigError` | TOML inválido, caminho inseguro, saída existente sem `overwrite`, $L_0$ inviável |
| `InputValidationError` | base inválida (modo estrito) ou `operation_id` repetido |
| `GridTooSmallError` | a distribuição não converge dentro de `max_grid` |
| `NumericalRangeError` | negativos relevantes na FFT, underflow no Panjer |
| `MemoryBudgetError` | alguma etapa não cabe no orçamento (checado antes de alocar) |

Todas derivam de `CRPlusError`.
`````

<!-- FILE: docs/index.md -->
`````markdown
# crplus — CreditRisk+ em Python

O `crplus` é uma réplica completa do **CreditRisk+** (Credit Suisse First Boston, 1997), com as
extensões numericamente estáveis da literatura (Haaf, Reiß e Schoenmakers, 2004; Haaf e Tasche,
2002). Ele foi projetado para carteiras de **centenas de milhões de operações**, processadas em
lotes com `polars` *lazy/streaming*, dentro de um orçamento de memória fixo (padrão 9 GB).

Entregas:

- distribuição de perdas completa (motor FFT; Panjer estável como referência);
- EL, UL, VaR, Expected Shortfall e capital econômico para cada nível de confiança;
- contribuições de risco (desvio-padrão, VaR e ES) **por operação**, em parquet;
- parâmetros e diagnósticos por setor.

## Instalação

```bash
uv sync --all-extras
```

## Exemplo mínimo

```python
import polars as pl
from crplus import load_config, run_creditrisk_plus

config = load_config("crplus.toml")
result = run_creditrisk_plus(pl.scan_parquet("carteira/*.parquet"), config)
print(result.var[0.999], result.es[0.999], result.ec[0.999])
```

Veja o [guia de uso](guia-de-uso.md) e a [configuração](configuracao.md).

## Verificação local

`make check` roda lint, tipos, testes (cobertura >= 95% de linhas e ramos), integração, SAST,
complexidade (grau A) e a construção desta documentação. Sem `make`, os comandos estão no
`Makefile` e podem ser executados individualmente (`uv run python -m <ferramenta>`).

## Páginas

- [Metodologia](metodologia.md): toda a matemática implementada.
- [Guia de uso](guia-de-uso.md): contrato de entrada, preparo da base, saídas e interpretação.
- [Configuração](configuracao.md): todas as chaves do TOML.
- [Performance](performance.md): arquitetura de passes, memória, *tuning* e benchmarks.
- [Validação e testes](validacao.md): estratégia de testes e oráculos.
- [Segurança](seguranca.md): controles de SAST e de entrada.
- [ADRs](adr/index.md): decisões de arquitetura.
`````

<!-- FILE: docs/javascripts/mathjax.js -->
`````javascript
window.MathJax = {
  tex: {
    inlineMath: [["\\(", "\\)"]],
    displayMath: [["\\[", "\\]"]],
    processEscapes: true,
    processEnvironments: true,
  },
  options: {
    ignoreHtmlClass: ".*|",
    processHtmlClass: "arithmatex",
  },
};
`````

<!-- FILE: docs/metodologia.md -->
`````markdown
# Metodologia

Esta página descreve exatamente o que o `crplus` implementa. Notação: operação $i$, devedor $j$
($i \in j$), setores sistêmicos $k = 1..K$ e setor idiossincrático $k = 0$;
$E_i = LGD_i \cdot EAD_i$.

## 1. Devedor × operação

O default no CreditRisk+ é do **devedor**: todas as operações de um devedor entram em default
juntas. A exposição do devedor é $E_j = \sum_{i \in j} E_i$ e a banda é dele ($\nu_j$).

Para não materializar PD, volatilidade e pesos por devedor, cada operação contribui
linearmente para os agregados na banda do seu devedor:

$$\lambda_{k,\nu_j} \mathrel{+}= \frac{w_{ik}\,p_i\,E_i}{\nu_j L_0}, \qquad
s_k \mathrel{+}= \frac{w_{ik}\,\sigma_i\,E_i}{\nu_j L_0}.$$

Isso equivale a um devedor com PD, $\sigma$ e pesos iguais às médias ponderadas por $p_i E_i$
das suas operações; quando elas são iguais (caso esperado), coincide exatamente com o CR+ por
devedor. Divergências intra-devedor são contadas e geram alerta (ADR 0004).

Pesos: $w_{i0} = 1 - \sum_k w_{ik}$ vai para o setor idiossincrático. Somas ligeiramente acima
de 1 (dentro de `weights_tolerance`) são renormalizadas por $\max(1, \sum_k w_{ik})$.

## 2. Banding

Com unidade de perda $L_0 > 0$:

$$\nu_j = \max\big(1, \lceil E_j / L_0 \rceil\big) \quad (\text{ou arredondamento ao mais próximo}),$$

$$\tilde p_{jk} = \sum_{i\in j} \frac{w_{ik}\,p_i\,E_i}{\nu_j L_0}
\quad\Rightarrow\quad L_0 \sum_j \sum_k \tilde p_{jk}\,\nu_j = \sum_i p_i E_i.$$

O ajuste de intensidade preserva exatamente a perda esperada (propriedade testada com
hypothesis). Para que $E_j = k L_0$ caia na banda $k$ apesar de erros de ponto flutuante na
divisão, o `ceil` usa uma folga relativa de $10^{-12}$.

**$L_0$ automático:** menor valor tal que $\nu_{max} \le$ `max_bands` e a grade estimada
$M \approx (EL + z\,\sigma + E_{max})/L_0 + 2 \le$ `max_grid`. O $\sigma$ inicial é o da parte
Poisson ($\sum_j E_j \sum_{i\in j} p_i E_i$); depois do passo B, com o $\sigma$ exato, $L_0$ é
recalibrado se necessário. Se a distribuição ainda não convergir em `max_grid` (caudas muito
pesadas), $L_0$ é multiplicado por 4 e o cálculo é refeito (até 4 vezes) — ADR 0007.

## 3. Parâmetros setoriais

$\lambda_{k,\nu} = \sum_{j:\,\nu_j = \nu} \tilde p_{jk}$ e $\mu_k = \sum_\nu \lambda_{k,\nu}$.

- **`pd_vol`** (padrão, CSFB): $v_k = (s_k/\mu_k)^2$. Com `adjust_for_banding = false`,
  $s_k = \sum_i w_{ik}\sigma_i$ e $\mu_k^{raw} = \sum_i w_{ik} p_i$.
- **`external`**: $v_k$ (ou $cv_k = \sqrt{v_k}$) informado no TOML ou em arquivo.

$v_0 = 0$; setores com $\mu_k = 0$ são ignorados e com $v_k = 0$ são Poisson. Os fatores são
$S_k \sim \text{Gama}(\alpha_k = 1/v_k,\ \beta_k = v_k)$, independentes, de média 1.

## 4. Função geradora e motores

Com $t_k(z) = \sum_\nu \lambda_{k,\nu}(z^\nu - 1)$:

$$G(z) = \exp\Big(\sum_{k:\,v_k=0} t_k(z)\Big)\ \prod_{k:\,v_k>0}\big(1 - v_k\,t_k(z)\big)^{-1/v_k}.$$

**FFT (principal).** Nas $M$ raízes da unidade, $t_k = \operatorname{rfft}(\lambda_k) - \mu_k$ e

$$\log\varphi = \sum_{\text{Poisson}} t_k - \sum_{\text{Gama}} \tfrac{1}{v_k}\log(1 - v_k t_k),
\qquad g = \operatorname{irfft}(e^{\log\varphi}).$$

$\operatorname{Re}(1 - v_k t_k) \ge 1$ garante a continuidade do ramo principal do logaritmo.
Setores são processados em sequência (memória $O(M)$); setores Poisson são somados numa única
FFT. Negativos de módulo menor que `tol_clip` são zerados; maiores são erro.

**Panjer estável (referência; Haaf, Reiß e Schoenmakers, 2004).** Cada setor Gama é binomial
negativa composta ($q = v\mu/(1+v\mu)$, $a = q$, $b = (1/v - 1)q$, $g_0 = (1-q)^{1/v}$) e o grupo
Poisson é Poisson composta ($a = 0$, $b = \mu$, $g_0 = e^{-\mu}$), com severidade
$h_\nu = \lambda_{k,\nu}/\mu_k$ e recursão

$$g_x = \sum_{j=1}^{\min(x,\nu_{max})}\Big(a + \frac{b\,j}{x}\Big) h_j\, g_{x-j},$$

de termos todos positivos. As componentes são convoluídas por FFT com preenchimento $2M$.
Underflow de $g_0$ gera `NumericalRangeError` sugerindo o motor FFT.

**Grade.** $M_0 = \text{next\_fast\_len}(\lceil EL_u + z\,\sigma_u\rceil + \nu_{max} + 1)$. Após o
cálculo exige-se massa no último 1% da grade $<$ `tol_tail` e erros relativos de média e
variância $<$ `tol_moment`; caso contrário $M$ dobra até `max_grid` (`GridTooSmallError`).

## 5. Momentos analíticos

$$EL_k = \sum_\nu \nu\,\lambda_{k,\nu},\quad EL_u = \sum_k EL_k,\quad
\operatorname{Var}_u = \sum_k\sum_\nu \nu^2\lambda_{k,\nu} + \sum_{k\ge1} v_k\,EL_k^2.$$

Em moeda: $EL = L_0\,EL_u$ e $UL = L_0\,\sigma_u$.

## 6. Medidas de risco

$F(x) = \sum_{y\le x} g_y$ e $q = \min\{x : F(x) \ge \alpha\}$:

$$\mathrm{VaR}_\alpha = q\,L_0,\qquad
\mathrm{ES}_\alpha = \frac{L_0}{1-\alpha}\Big[\sum_{x>q} x\,g_x + q\,\big(F(q) - \alpha\big)\Big],$$

$\mathrm{EC}_\alpha = \mathrm{VaR}_\alpha - EL$ e $\mathrm{ES}_\alpha - EL$. O ES é o de Acerbi e
Tasche (2002), coerente em distribuições discretas. As caudas usam soma acumulada reversa
($\bar F(x) = \sum_{y>x} g_y$) somada à massa que eventualmente não coube na grade; empates no
nível do ruído ($10^{-14}$) resolvem para o menor quantil.

## 7. Contribuições (alocação de Euler), por operação

**Desvio-padrão:**
$RC^\sigma_i = \dfrac{p_i E_i}{\sigma_u}\Big(\nu_j + \sum_{k\ge1} v_k\,w_{ik}\,EL_k\Big)$, com
$\sum_i RC^\sigma_i = \sigma_u L_0$.

**VaR e ES (Haaf e Tasche, 2002).** A distribuição "inclinada" do setor $k$ tem PGF
$G^{(k)}(z) = G(z)/(1 - v_k t_k(z))$ (e $g^{(k)} = g$ para setores Poisson), e vale a identidade
$x\,g_x = \sum_k\sum_\nu \nu\,\lambda_{k,\nu}\,g^{(k)}_{x-\nu}$. Com $\beta = (F(q)-\alpha)/g_q$ e
$T^{(k)}(x) = \sum_{y>x} g^{(k)}_y$ ($T = 1$, $g = 0$ para $x<0$):

$$A^{ES}_k(\nu) = \frac{T^{(k)}(q-\nu) + \beta\,g^{(k)}_{q-\nu}}{1-\alpha},\qquad
A^{VaR}_k(\nu) = \frac{g^{(k)}_{q-\nu}}{g_q},$$

$$RC^{ES}_i = p_i E_i \sum_k w_{ik}\,A^{ES}_k(\nu_j),\qquad
RC^{VaR}_i = p_i E_i \sum_k w_{ik}\,A^{VaR}_k(\nu_j).$$

As somas fecham em $\mathrm{ES}_\alpha$ e $\mathrm{VaR}_\alpha$. Cada $g^{(k)}$ é calculada,
reduzida às tabelas $A$ (forma $(n_\alpha, K+1, \nu_{max}+1)$) e descartada.

!!! note "Contribuições de VaR são ruidosas"
    Em distribuições discretas, $A^{VaR}$ depende de um único átomo $g_q$. Com
    `var_smoothing_window = w > 0`, usa-se a massa de $g^{(k)}$ na janela $[q-w, q+w]$,
    renormalizada por $\sum_{x\in W} x\,g_x$ — a soma continua igual ao VaR.

## 8. Monte Carlo (somente validação)

$S_k \sim \text{Gama}$ e $N_\nu \sim \text{Poisson}\big(\sum_k \lambda_{k,\nu}S_k\big)$,
$L = \sum_\nu \nu N_\nu$ — equivalente em distribuição à simulação por devedor (testado).
Gerador `PCG64` com seed explícita.

## Referências

- Credit Suisse First Boston (1997). *CreditRisk+: A Credit Risk Management Framework*.
- Gundlach, M.; Lehrbass, F. (orgs.) (2004). *CreditRisk+ in the Banking Industry*. Springer.
- Haaf, H.; Reiß, O.; Schoenmakers, J. (2004). *Numerically stable computation of CreditRisk+*.
- Haaf, H.; Tasche, D. (2002). *Credit portfolio measurements*. GARP Risk Review.
- Acerbi, C.; Tasche, D. (2002). *On the coherence of Expected Shortfall*.
- Tasche, D. (2004). *Capital allocation for credit portfolios with kernel estimators*.
- Panjer, H. (1981). *Recursive evaluation of a family of compound distributions*.
`````

<!-- FILE: docs/performance.md -->
`````markdown
# Performance e escala

## Arquitetura de passes

A base nunca é materializada: cada passo reexecuta o plano lazy (idealmente
`pl.scan_parquet`) em streaming, por partição de hash de `obligor_id`.

| Passo | O que faz | Toca as linhas? | Memória |
|-------|-----------|-----------------|---------|
| Validação | contagens por regra, HLL de devedores, unicidade de `operation_id` | sim (1 + P leituras) | lotes do polars |
| A | `group_by(obligor_id)`: $E_j$, perda esperada, consistência; grava `(id, E_j)` | sim (P leituras) | tabela de devedores da partição |
| B | `join` com a tabela de devedores, banda e `group_by(ν)` | sim (P leituras; 2–3 com $L_0$ automático) | $(K+1)(\nu_{max}+1)$ |
| C | distribuição (FFT ou Panjer), medidas, tabelas $A$ | não | $O(M)$, setores em sequência |
| D | contribuições por operação, `sink_parquet` por partição | sim (P leituras) | lotes do polars |

## Orçamento de memória

Todas as decisões de tamanho derivam de `resources.memory_budget_gb` (padrão 9 GB):

- **Partições** (`obligor_partitions = "auto"`): menor $P$ tal que a tabela de devedores de uma
  partição caiba em 40% do orçamento, estimada em 192 B/devedor com id inteiro (medido ~155 B
  no polars 2.1) mais o tamanho médio do id quando texto. A contagem de devedores vem de um
  HyperLogLog na passada de validação.
- **Grade**: `max_grid` tem de caber em 60% do orçamento a 64 B/ponto (distribuição,
  $\log\varphi$, distribuição inclinada, caudas). Com 9 GB, $2^{26}$ pontos (~4 GB) cabem.
- **Tabelas setor-banda**: checadas com o $K$ e o $\nu_{max}$ reais antes de alocar.

O pico de memória é dominado pelo passo C (limitado por `max_grid`) e pelos lotes em voo do
polars (proporcionais ao número de threads), e não pelo número de linhas (ADR 0006).

## Ajuste fino

| Parâmetro | Efeito |
|-----------|--------|
| `model.loss_unit` | Maior $L_0$ → grade menor (mais rápido, menos memória), banding mais grosseiro. `auto` usa o menor $L_0$ viável. |
| `numerics.max_grid` | Teto da grade; reduzir economiza memória do passo C e aumenta $L_0$ automático. |
| `numerics.max_bands` | Teto de $\nu_{max}$; também limita as tabelas $A$ e o custo do Panjer ($O(M\,\nu_{max})$). |
| `resources.polars_threads` | Mais threads = mais lotes em voo (memória). 8 foi mais rápido e mais leve que 16 (ADR 0006). |
| `resources.obligor_partitions` | Mais partições = menos memória no passo A, porém uma releitura da base por partição. |
| `resources.weight_dtype = "float32"` | Metade da leitura/memória dos pesos. |
| `validation.check_operation_id_unique` | Desligar economiza P leituras e a memória do conjunto de ids. |
| `output.write_contributions` | Desligar dispensa o passo D (o mais caro em disco). |

Prefira parquet com *row groups* de ~1 milhão de linhas e ids inteiros.

## Benchmarks

Máquina de referência (CPU de 8 núcleos/16 threads, 32 GB, sem GPU), polars 2.1, 8 setores,
pesos `float32`, $L_0$ automático, contribuições gravadas, checagem de unicidade ligada.
Pico = máximo entre *working set* e memória privada do processo, medido em subprocesso
(`tests/benchmarks/scale_runner.py`).

| Linhas | Devedores | Grade $M$ | $\nu_{max}$ | Tempo | Linhas/s | Pico |
|--------|-----------|-----------|-------------|-------|----------|------|
| 10 M | ~3,3 M | 17,5 M | 100.000 | 21 s | 483 mil | 4,5 GB |
| 30 M | ~10 M | 42,5 M | 100.000 | 67 s | 445 mil | 7,0 GB¹ |
| 50 M | ~16,7 M | 64,8 M | 91.662 | 92 s | 541 mil | 6,9 GB |
| **300 M** | ~100 M | 67,1 M ($2^{26}$) | 15.305 | 39,5 min² | 127 mil | **8,3 GB** |

¹ antes das otimizações da ADR 0006 (o mesmo cenário de 50 M tinha pico de 9,98 GB).

² 5 partições automáticas (cada passo relê a base 5 vezes); parte da execução concorreu com a
suíte de testes na mesma máquina. Tempos: validação 57 s, passo A 546 s, passos B + C 1.105 s,
passo D 657 s. **Meta da §6.2 atingida: 300 M de linhas com pico <= 9 GB.**

Distribuição do tempo em 50 M: validação 2 s, passo A 4 s, passos B + C (incluindo as tabelas
$A$) 69 s, passo D 16 s. O passo C a $M = 2^{26}$ com 8 setores domina; aumentar $L_0$ (grade
menor) reduz esse custo quase linearmente.

### Como reproduzir

```bash
uv run python -m tests.benchmarks.scale_runner generate --rows 50000000 --dir D:/bench/50m
uv run python -m tests.benchmarks.scale_runner run --dir D:/bench/50m --budget-gb 9
# ou, via pytest (marcador slow):
CRPLUS_BENCH_ROWS=50000000 CRPLUS_BENCH_DIR=D:/bench/50m uv run pytest -m slow
```

## Não implementado

A janela deslocada da FFT (§5.4, item 6 — opcional) não foi implementada: com `max_grid`
limitando a grade e $L_0$ automático, ela não foi necessária para cumprir o orçamento. Fica como
ponto de extensão (o `LossDistribution` já tem o campo `offset`).
`````

<!-- FILE: docs/referencia-api.md -->
`````markdown
# Referência da API

## Execução

::: crplus.api

## Configuração

::: crplus.config

## Resultados

::: crplus.results

## Exceções

::: crplus.exceptions

## Entrada e validação

::: crplus.sources

::: crplus.validation

::: crplus.schema

## Passos A e B

::: crplus.obligor

::: crplus.banding

::: crplus.aggregation

::: crplus.sectors

::: crplus.moments

## Distribuição de perdas

::: crplus.distribution

::: crplus.distribution.model

::: crplus.distribution.fft

::: crplus.distribution.panjer

::: crplus.distribution.grid

## Medidas e contribuições

::: crplus.risk_measures

::: crplus.contributions

## Validação por Monte Carlo

::: crplus.montecarlo

## Infraestrutura

::: crplus.memory

::: crplus.tempstore

::: crplus.paths
`````

<!-- FILE: docs/seguranca.md -->
`````markdown
# Segurança

Controles de SAST e de robustez do projeto (CLAUDE.md §9).

## Ferramentas

| Ferramenta          | Onde roda                   | O que verifica |
|---------------------|-----------------------------|----------------|
| `ruff` (regras `S`) | `make lint`, pre-commit     | Padrões do flake8-bandit. |
| `bandit -ll`        | `make security`, pre-commit | Achados de severidade média/alta em `src`. |
| `pip-audit`         | `make security`             | Vulnerabilidades conhecidas nas dependências travadas (`uv.lock`). |
| `detect-secrets`    | `make security`, pre-commit | Segredos versionados (linha de base em `.secrets.baseline`). |

## Construções proibidas

`eval`, `exec`, `compile`, `pickle`/`marshal`/`shelve`/`joblib`/`dill`/`yaml`, `subprocess`,
`shell=True`, `tempfile.mktemp` e `assert` para validação de runtime. `tests/unit/test_security.py`
varre a AST de todo o pacote e falha se qualquer uma aparecer.

## Validação de entrada

- Esquema checado antes de ler dados: colunas presentes e tipos compatíveis (ids inteiros ou
  texto; demais numéricos).
- Regras vetorizadas por linha: nulos, `NaN`/`inf`, domínios, soma de pesos, unicidade de
  `operation_id`; avisos para PD alta e inconsistência intra-devedor.
- Relatórios e mensagens contêm apenas **contagens e posições** — nunca valores nem ids (testado
  com ids e valores marcadores).

## Configuração

- Lida somente com `tomllib`; arquivo limitado a 1 MiB, UTF-8 e não pode ser link simbólico.
- Validação campo a campo no `__post_init__`; chaves e seções desconhecidas são rejeitadas;
  booleanos não passam por inteiros; números devem ser finitos.
- Tetos rígidos de recursos: `max_bands` <= 10⁷, `max_grid` <= 2³¹, `max_sectors` <= 10⁴,
  até 16 `alphas`, `memory_budget_gb` <= 4096; `max_grid` checado contra o orçamento.
- Mensagens de erro citam o campo e a restrição, **nunca o valor recebido**.

## Caminhos

`crplus.paths.resolve_within` resolve todo caminho da configuração a partir do diretório base,
rejeitando `..` que escape do base, caminhos absolutos fora dele e links simbólicos em qualquer
componente. Saídas anteriores não são sobrescritas sem `overwrite = true`, e só arquivos do
próprio `crplus` são removidos.

## Temporários

`crplus.tempstore.secure_tempdir` cria o diretório com `tempfile.mkdtemp`, aplica `0o700` e o
remove no `finally`, inclusive quando o cálculo falha (testado na API e na integração). Nomes
internos não podem conter separadores, unidade de disco nem `..`. Falha de remoção é registrada
em log (sem o caminho) e não mascara a exceção original.

## Recursos e numérico

- Toda etapa que aloca proporcionalmente aos dados estima a memória **antes** de alocar
  (`crplus.memory`) e levanta `MemoryBudgetError` com mensagem clara.
- Trechos críticos da FFT rodam sob `np.errstate(over="raise", invalid="raise")`; negativos
  relevantes e underflow de Panjer levantam `NumericalRangeError`.
- Aleatoriedade somente via `np.random.Generator(PCG64(seed))` (Monte Carlo de validação).

## Logging

Apenas agregados e contagens via `logging`; nenhum `print` no pacote; nunca ids, valores de EAD
ou linhas da base.
`````

<!-- FILE: docs/validacao.md -->
`````markdown
# Validação e testes

## Princípios

- Cada teste protege **uma regra de negócio, propriedade matemática ou contrato**, com docstring
  iniciada por `Intenção:` explicando o que quebra se ele falhar.
- Estrutura Arrange / Act / Assert; um comportamento por teste; oráculos independentes.
- Invariantes com `hypothesis`; cobertura >= 95% de linhas **e** ramos (atual: 100%).

## Organização

| Pasta / arquivo | Conteúdo |
|-----------------|----------|
| `tests/unit/test_<modulo>.py` | Um arquivo por módulo, mais `test_security.py`. |
| `tests/integration/test_end_to_end.py` | Teste ponta a ponta (marcador `integration`). |
| `tests/integration/golden/` | Golden file de regressão (atualizar só com `--update-golden`). |
| `tests/integration/reference/` | Casos de referência externos (pulado enquanto não houver casos). |
| `tests/benchmarks/` | Escala, pico de RSS e tempos (marcador `slow`, fora do `make check`). |
| `tests/synthetic.py`, `tests/pipeline.py` | Gerador de carteiras com seed e atalhos dos passos A–D. |

## Oráculos

| Propriedade | Oráculo |
|-------------|---------|
| Só idiossincrático, $\nu = 1$ | `scipy.stats.poisson` (FFT e Panjer, `atol = 1e-15`) |
| Um setor Gama, $\nu = 1$ | `scipy.stats.nbinom(1/v, 1/(1+v\mu))` (`atol = 1e-14`) |
| Bandas mistas, carteiras aleatórias | FFT == Panjer (`max|Δ| < 1e-10`), inclusive $g^{(k)}$ |
| Média e variância da distribuição | Momentos analíticos (§5.6), erro relativo $< 10^{-8}$ |
| Identidade de Haaf–Tasche | $x g_x = \sum_k\sum_\nu \nu\lambda_{k,\nu} g^{(k)}_{x-\nu}$ |
| Banding | $L_0 \sum \nu\lambda = \sum p E$ para qualquer $L_0$ (hypothesis) |
| Formulação linear por operação | Cálculo explícito por devedor |
| Partições | Soma dos agregados == agregado do todo, em qualquer ordem (hypothesis) |
| VaR/ES | Distribuições construídas à mão; ES >= VaR e monotonicidade em $\alpha$ (hypothesis) |
| Contribuições | Somas de Euler (σ, VaR, ES) == medidas do portfólio (`rel 1e-8`) |
| Simulação setor-banda | Simulação por devedor (mesma distribuição) |
| Ponta a ponta | Monte Carlo com 2 milhões de cenários (VaR/ES 99,9% no IC de 4 erros-padrão) |

## Teste de integração final

Carteira sintética (`seed = 2024`): 499.579 operações de 200 mil devedores, 8 setores +
idiossincrático, PD log-normal, EAD Pareto. Executa a partir de um `crplus.toml` e de
`pl.scan_parquet` e verifica: entradas `LazyFrame`/`DataFrame`/pandas iguais; 1 e 4 partições
iguais; distribuição soma 1 e reproduz os momentos; VaR/ES dentro do IC de Monte Carlo; FFT ==
Panjer; somas de Euler lidas do parquet; golden file; `pd_vol` == `external` com as variâncias
implícitas; `summary.json` consistente; nenhum alerta; diretório temporário removido, inclusive
em falha. Resultado na máquina de referência: 14 testes em ~4 s.

Resultado de Monte Carlo (99,9%): ES analítico 4.243.042 vs. MC 4.242.605 (erro-padrão 7.318);
VaR analítico 4.063.900 vs. MC 4.059.502 (erro-padrão 6.130).

!!! note "Resultados \"idênticos\""
    As reduções paralelas do polars somam em ordem não determinística; execuções equivalentes
    (tipos de entrada, número de partições) diferem em ~$10^{-11}$ relativo. Os testes usam
    tolerância relativa de $10^{-9}$ (ADR 0007).

## Bugs encontrados pelos testes

- `math.ceil(a / b)` em ponto flutuante subdimensionava partições para ~$10^{14}$ bytes
  (hypothesis) → divisão inteira exata.
- Quantil em empate exato de ponto flutuante ($0{,}5 + 0{,}3 \ne 0{,}8$) e grade truncada sem
  massa de cauda → folga de $10^{-14}$ e massa fora da grade somada à cauda.
- $L_0$ automático com $\sigma$ subestimado em carteiras muito correlacionadas → recalibração.

## Casos de referência externos

Ainda não há resultados de outra implementação do CR+. Para incluir um caso, crie
`tests/integration/reference/cases/<nome>/` com `portfolio.parquet`, `crplus.toml` e
`expected.json` (formato em `tests/integration/reference/cases.py`).
`````

<!-- FILE: mkdocs.yml -->
`````yaml
site_name: crplus — CreditRisk+ em Python
site_description: Réplica do CreditRisk+ para carteiras de centenas de milhões de operações
docs_dir: docs
strict: true

theme:
  name: material
  language: pt-BR
  features:
    - navigation.sections
    - content.code.copy

markdown_extensions:
  - admonition
  - tables
  - toc:
      permalink: true
  - pymdownx.superfences
  - pymdownx.arithmatex:
      generic: true

extra_javascript:
  - javascripts/mathjax.js
  - https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js

plugins:
  - search:
      lang: pt
  - mkdocstrings:
      handlers:
        python:
          paths: [src]
          options:
            docstring_style: numpy
            show_source: false
            show_root_heading: true
            members_order: source

nav:
  - Início: index.md
  - Metodologia: metodologia.md
  - Guia de uso: guia-de-uso.md
  - Configuração: configuracao.md
  - Performance: performance.md
  - Validação e testes: validacao.md
  - Segurança: seguranca.md
  - Referência da API: referencia-api.md
  - ADRs:
      - adr/index.md
      - adr/0001-fft-motor-principal.md
      - adr/0002-banding-ceil.md
      - adr/0003-variancia-setorial.md
      - adr/0004-devedor-operacao.md
      - adr/0005-chaves-de-configuracao-adicionais.md
      - adr/0006-threads-e-memoria.md
      - adr/0007-robustez-numerica.md
`````

<!-- FILE: pyproject.toml -->
`````toml
[project]
name = "crplus"
version = "0.1.0"
description = "Réplica do CreditRisk+ (CSFB, 1997) em Python para carteiras de centenas de milhões de operações."
readme = "README.md"
requires-python = ">=3.11"
license = { text = "Proprietary" }
dependencies = [
    "polars>=1.20",
    "numpy>=2.0",
    "scipy>=1.13",
    "pyarrow>=17.0",
    "numba>=0.60",
]

[project.optional-dependencies]
pandas = ["pandas>=2.2"]

[dependency-groups]
dev = [
    "pytest>=8.3",
    "pytest-cov>=6.0",
    "hypothesis>=6.120",
    "pytest-benchmark>=5.1",
    "mypy>=1.13",
    "ruff>=0.8",
    "bandit[toml]>=1.8",
    "pip-audit>=2.7",
    "xenon>=0.9",
    "detect-secrets>=1.5",
    "pre-commit>=4.0",
    "mkdocs>=1.6,<2",
    "mkdocs-material>=9.5",
    "mkdocstrings[python]>=0.27",
    "pandas-stubs>=3.1.0.261029",
]

[build-system]
requires = ["hatchling>=1.25"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/crplus"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.format]
exclude = ["*.md"]

[tool.ruff.lint]
select = ["E","F","W","I","B","C90","S","N","UP","SIM","RUF","PL","NPY","PD","PT","D","ANN","ERA"]
ignore = ["D203","D213"]

[tool.ruff.lint.mccabe]
max-complexity = 5

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101","PLR2004","D","ANN"]
"tests/benchmarks/**" = ["S101","PLR2004","D","ANN","S603"]

[tool.mypy]
strict = true
python_version = "3.11"
mypy_path = "src"

[[tool.mypy.overrides]]
module = ["numba.*", "scipy.*"]
ignore_missing_imports = true

[tool.bandit]
exclude_dirs = ["tests"]

[tool.pytest.ini_options]
markers = ["slow: testes de escala/benchmark", "integration: teste de integração ponta a ponta"]
addopts = "--strict-markers -ra"
testpaths = ["tests"]

[tool.coverage.run]
branch = true
source = ["crplus"]

[tool.coverage.report]
fail_under = 95
show_missing = true
`````

<!-- FILE: src/crplus/__init__.py -->
`````python
"""CreditRisk+ (CSFB, 1997) em Python, para carteiras de centenas de milhões de operações.

Uso mínimo::

    import polars as pl
    from crplus import load_config, run_creditrisk_plus

    config = load_config("crplus.toml")
    result = run_creditrisk_plus(pl.scan_parquet("carteira/*.parquet"), config)
    result.var[0.999], result.es[0.999], result.contributions_path
"""

from crplus._threads import DEFAULT_POLARS_THREADS
from crplus._version import __version__
from crplus.api import run_creditrisk_plus
from crplus.config import CRPlusConfig, config_from_mapping, load_config
from crplus.exceptions import (
    ConfigError,
    CRPlusError,
    GridTooSmallError,
    InputValidationError,
    MemoryBudgetError,
    NumericalRangeError,
)
from crplus.results import CRPlusResult

__all__ = [
    "DEFAULT_POLARS_THREADS",
    "CRPlusConfig",
    "CRPlusError",
    "CRPlusResult",
    "ConfigError",
    "GridTooSmallError",
    "InputValidationError",
    "MemoryBudgetError",
    "NumericalRangeError",
    "__version__",
    "config_from_mapping",
    "load_config",
    "run_creditrisk_plus",
]
`````

<!-- FILE: src/crplus/_checks.py -->
`````python
"""Predicados reutilizáveis para validação declarativa de campos de configuração.

Cada seção de configuração declara uma tupla de :class:`FieldCheck` e chama
:func:`run_checks` no ``__post_init__``. Isso mantém a complexidade ciclomática baixa:
nenhuma cadeia de ``if/elif`` por campo.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Iterable
from dataclasses import dataclass

from crplus.exceptions import ConfigError

Predicate = Callable[[object], bool]


@dataclass(frozen=True, slots=True)
class FieldCheck:
    """Regra de validação de um campo.

    Parameters
    ----------
    field : str
        Nome do atributo verificado.
    predicate : Predicate
        Função que devolve ``True`` quando o valor é válido.
    message : str
        Restrição descrita em português, usada na ``ConfigError``.

    """

    field: str
    predicate: Predicate
    message: str


def run_checks(obj: object, section: str, checks: Iterable[FieldCheck]) -> None:
    """Aplica as regras em ordem e levanta erro na primeira violada.

    Parameters
    ----------
    obj : object
        Instância cujos atributos são verificados.
    section : str
        Nome da seção TOML, usado para qualificar o campo no erro.
    checks : Iterable[FieldCheck]
        Regras a aplicar.

    Raises
    ------
    ConfigError
        Se algum predicado devolver ``False``.

    """
    for check in checks:
        if not check.predicate(getattr(obj, check.field)):
            raise ConfigError(f"{section}.{check.field}", check.message)


def is_bool(value: object) -> bool:
    """Indica se o valor é booleano."""
    return isinstance(value, bool)


def is_int(value: object) -> bool:
    """Indica se o valor é inteiro (booleanos não contam como inteiros)."""
    return isinstance(value, int) and not isinstance(value, bool)


def is_real(value: object) -> bool:
    """Indica se o valor é um número real finito (inteiro ou float, exceto booleano)."""
    if isinstance(value, bool) or not isinstance(value, int | float):
        return False
    return math.isfinite(value)


def is_text(value: object) -> bool:
    """Indica se o valor é uma string não vazia (ignorando espaços)."""
    return isinstance(value, str) and value.strip() != ""


def one_of(*options: str) -> Predicate:
    """Cria predicado que aceita apenas uma das strings informadas."""
    return lambda value: isinstance(value, str) and value in options


def either(*predicates: Predicate) -> Predicate:
    """Cria predicado que aceita o valor se qualquer um dos predicados aceitar."""
    return lambda value: any(predicate(value) for predicate in predicates)


def is_optional(predicate: Predicate) -> Predicate:
    """Cria predicado que aceita ``None`` ou um valor aceito por ``predicate``."""
    return lambda value: value is None or predicate(value)


def int_between(low: int, high: int) -> Predicate:
    """Cria predicado para inteiros no intervalo fechado ``[low, high]``."""

    def predicate(value: object) -> bool:
        return isinstance(value, int) and is_int(value) and low <= value <= high

    return predicate


def real_between(low: float, high: float, *, closed_low: bool, closed_high: bool) -> Predicate:
    """Cria predicado para reais finitos entre ``low`` e ``high``.

    Parameters
    ----------
    low, high : float
        Limites do intervalo.
    closed_low, closed_high : bool
        Se cada limite pertence ao intervalo.

    Returns
    -------
    Predicate
        Predicado do intervalo.

    """
    above: Callable[[float], bool] = (lambda v: v >= low) if closed_low else (lambda v: v > low)
    below: Callable[[float], bool] = (lambda v: v <= high) if closed_high else (lambda v: v < high)

    def predicate(value: object) -> bool:
        return isinstance(value, int | float) and is_real(value) and above(value) and below(value)

    return predicate
`````

<!-- FILE: src/crplus/_threads.py -->
`````python
"""Padrão de threads do polars, aplicado antes do primeiro ``import polars``.

O pool de threads do polars é fixado na importação (variável ``POLARS_MAX_THREADS``). Este
módulo é importado primeiro pelo ``crplus`` e define o padrão 8 (ver ADR 0006),
sem sobrescrever um valor já definido pelo usuário.
"""

from __future__ import annotations

import os
from typing import Final

POLARS_THREADS_ENV: Final = "POLARS_MAX_THREADS"
DEFAULT_POLARS_THREADS: Final = "8"

os.environ.setdefault(POLARS_THREADS_ENV, DEFAULT_POLARS_THREADS)
`````

<!-- FILE: src/crplus/_version.py -->
`````python
"""Versão do pacote."""

__version__ = "0.1.0"
`````

<!-- FILE: src/crplus/aggregation.py -->
`````python
r"""Passo B: agregação setorial por banda (map-reduce sobre as partições).

Cada operação contribui, na banda $\nu_j$ do seu devedor, com

$$\lambda_{k,\nu_j} \mathrel{+}= \frac{w_{ik}\,p_i\,E_i}{\nu_j L_0}, \qquad
s_k \mathrel{+}= \frac{w_{ik}\,\sigma_i\,E_i}{\nu_j L_0},$$

com $k = 0$ para o setor idiossincrático ($w_{i0} = 1 - \sum_k w_{ik}$). Os agregados são
pequenos ($(K+1) \times (\nu_{max}+1)$) e somáveis entre partições.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final

import numpy as np
import polars as pl
from numpy.typing import NDArray

from crplus.banding import Banding
from crplus.schema import BAND, EAD, LGD, OBLIGOR_EXPOSURE, OBLIGOR_ID, PD, PD_VOL, weight_columns

_FACTOR: Final = "_factor"
_EL: Final = "_el"
_ROWS: Final = "_rows"
_STATISTICS: Final = ("lam", "vol", "raw_vol", "raw_pd")

FloatArray = NDArray[np.float64]


def sector_weights(n_sectors: int) -> list[pl.Expr]:
    r"""Pesos $w_{i0}, w_{i1}, \dots, w_{iK}$ por operação, em ``Float64``.

    Parameters
    ----------
    n_sectors : int
        Número ``K`` de setores sistêmicos.

    Returns
    -------
    list of pl.Expr
        ``K + 1`` expressões; a primeira é o peso idiossincrático.

    Notes
    -----
    Pesos com soma ligeiramente acima de 1 (dentro de ``weights_tolerance``) são renormalizados
    por $\max(1, \sum_k w_{ik})$, de modo que $w_{i0} \ge 0$ e $\sum_{k=0}^K w_{ik} = 1$
    exatamente (a perda esperada é preservada).

    """
    columns = weight_columns(n_sectors)
    if not columns:
        return [pl.lit(1.0, dtype=pl.Float64)]
    weights = [pl.col(name).cast(pl.Float64) for name in columns]
    total = pl.sum_horizontal(weights)
    scale = pl.max_horizontal(total, pl.lit(1.0))
    return [1.0 - total / scale, *[weight / scale for weight in weights]]


@dataclass(frozen=True, slots=True, eq=False)
class SectorBandAggregate:
    r"""Agregados setoriais por banda.

    Parameters
    ----------
    intensity : FloatArray
        Matriz $(K+1) \times (B+1)$ com $\lambda_{k,\nu}$; a coluna $\nu = 0$ é zero.
    volatility : FloatArray
        $s_k = \sum_i w_{ik}\sigma_i E_i/(\nu_j L_0)$, comprimento $K+1$.
    raw_volatility : FloatArray
        $\sum_i w_{ik}\sigma_i$ (sem ajuste de banding).
    raw_intensity : FloatArray
        $\sum_i w_{ik} p_i$ (sem ajuste de banding).
    expected_loss : float
        $\sum_i p_i E_i$ em moeda (para checar a preservação da perda esperada).
    n_rows : int
        Operações agregadas.

    """

    intensity: FloatArray
    volatility: FloatArray
    raw_volatility: FloatArray
    raw_intensity: FloatArray
    expected_loss: float
    n_rows: int

    @classmethod
    def empty(cls, n_sectors: int) -> SectorBandAggregate:
        """Agregado neutro da soma (nenhuma operação)."""
        zeros = np.zeros(n_sectors + 1)
        return cls(np.zeros((n_sectors + 1, 1)), zeros, zeros, zeros, 0.0, 0)

    @property
    def n_sectors(self) -> int:
        """Número ``K`` de setores sistêmicos."""
        return int(self.intensity.shape[0]) - 1

    @property
    def max_band(self) -> int:
        """Maior banda representada ($B$)."""
        return int(self.intensity.shape[1]) - 1

    def __add__(self, other: SectorBandAggregate) -> SectorBandAggregate:
        """Soma agregados de partições disjuntas (bandas alinhadas por índice)."""
        width = max(self.max_band, other.max_band) + 1
        return SectorBandAggregate(
            _pad(self.intensity, width) + _pad(other.intensity, width),
            self.volatility + other.volatility,
            self.raw_volatility + other.raw_volatility,
            self.raw_intensity + other.raw_intensity,
            self.expected_loss + other.expected_loss,
            self.n_rows + other.n_rows,
        )


def _pad(matrix: FloatArray, width: int) -> FloatArray:
    return np.pad(matrix, ((0, 0), (0, width - matrix.shape[1])))


def _statistic_terms(weight: pl.Expr) -> dict[str, pl.Expr]:
    return {
        "lam": weight * pl.col(PD) * pl.col(_FACTOR),
        "vol": weight * pl.col(PD_VOL) * pl.col(_FACTOR),
        "raw_vol": weight * pl.col(PD_VOL),
        "raw_pd": weight * pl.col(PD),
    }


def _sector_sums(k: int, weight: pl.Expr) -> list[pl.Expr]:
    return [expr.sum().alias(f"{name}{k}") for name, expr in _statistic_terms(weight).items()]


def _sums(n_sectors: int) -> list[pl.Expr]:
    weights = sector_weights(n_sectors)
    return [expr for k, weight in enumerate(weights) for expr in _sector_sums(k, weight)]


def band_plan(frame: pl.LazyFrame, obligor_table: Path, banding: Banding) -> pl.LazyFrame:
    r"""Junta a partição à tabela de devedores e acrescenta a banda e o fator de ajuste.

    Parameters
    ----------
    frame : pl.LazyFrame
        Partição da base normalizada.
    obligor_table : Path
        Parquet ``(obligor_id, E_j)`` da mesma partição (passo A).
    banding : Banding
        Regra de banding.

    Returns
    -------
    pl.LazyFrame
        Plano com as colunas ``nu`` (banda) e ``_factor`` $= E_i/(\nu_j L_0)$.

    """
    exposures = pl.scan_parquet(obligor_table)
    joined = frame.join(exposures, on=OBLIGOR_ID, how="inner")
    with_band = joined.with_columns(banding.band(pl.col(OBLIGOR_EXPOSURE)).alias(BAND))
    factor = pl.col(LGD) * pl.col(EAD) / (pl.col(BAND).cast(pl.Float64) * banding.loss_unit)
    return with_band.with_columns(factor.alias(_FACTOR))


def aggregate_partition(
    frame: pl.LazyFrame, obligor_table: Path, n_sectors: int, banding: Banding
) -> SectorBandAggregate:
    """Executa o passo B numa partição (``group_by`` por banda, em streaming).

    Parameters
    ----------
    frame : pl.LazyFrame
        Partição da base normalizada.
    obligor_table : Path
        Parquet do passo A da mesma partição.
    n_sectors : int
        Número ``K`` de setores sistêmicos.
    banding : Banding
        Regra de banding.

    Returns
    -------
    SectorBandAggregate
        Agregados da partição.

    """
    planned = band_plan(frame, obligor_table, banding)
    expected_loss = (pl.col(PD) * pl.col(LGD) * pl.col(EAD)).sum().alias(_EL)
    grouped = planned.group_by(BAND).agg(*_sums(n_sectors), expected_loss, pl.len().alias(_ROWS))
    return _to_aggregate(grouped.collect(engine="streaming").sort(BAND), n_sectors)


def _sector_matrix(table: pl.DataFrame, name: str, n_sectors: int) -> FloatArray:
    columns = [f"{name}{k}" for k in range(n_sectors + 1)]
    return table.select(columns).to_numpy().astype(np.float64).T


def _to_aggregate(table: pl.DataFrame, n_sectors: int) -> SectorBandAggregate:
    if table.height == 0:
        return SectorBandAggregate.empty(n_sectors)
    bands = table[BAND].to_numpy()
    intensity = np.zeros((n_sectors + 1, int(bands.max()) + 1))
    intensity[:, bands] = _sector_matrix(table, "lam", n_sectors)
    totals = {name: _sector_matrix(table, name, n_sectors).sum(axis=1) for name in _STATISTICS}
    return SectorBandAggregate(
        intensity,
        totals["vol"],
        totals["raw_vol"],
        totals["raw_pd"],
        float(table[_EL].sum()),
        int(table[_ROWS].sum()),
    )
`````

<!-- FILE: src/crplus/api.py -->
`````python
"""Orquestração dos passos do CreditRisk+ (borda do pacote: I/O, logging e tempos).

Fluxo de :func:`run_creditrisk_plus`:

1. normalização do plano e validação (passada de streaming; erro ou exclusão de linhas);
2. partições por hash de ``obligor_id`` derivadas do orçamento de memória;
3. passo A (tabela de devedores) e escolha de $L_0$;
4. passo B (agregados setor-banda), parâmetros setoriais e momentos;
5. passo C (distribuição), medidas de risco;
6. passo D (contribuições por operação, gravadas por partição) e checagem das somas de Euler;
7. ``summary.json`` e ``loss_distribution.parquet``.

A base é relida em cada passo/partição e nunca é materializada inteira.
"""

from __future__ import annotations

import logging
import math
import os
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field, replace
from functools import reduce
from pathlib import Path
from typing import Final

import numba
import polars as pl

from crplus._version import __version__
from crplus.aggregation import SectorBandAggregate, aggregate_partition
from crplus.banding import Banding, LossUnitInputs, automatic_loss_unit
from crplus.config import CRPlusConfig, OutputConfig, ResourcesConfig, ValidationConfig
from crplus.contributions import (
    EL_COLUMN,
    SIGMA_COLUMN,
    ContributionInputs,
    ContributionPlanInputs,
    ContributionTables,
    contribution_plan,
    contribution_tables,
    es_column,
    var_column,
    write_contributions,
)
from crplus.distribution import GridRequest, SectorModel, compute_distribution, make_engine
from crplus.distribution.grid import GridDiagnostics
from crplus.exceptions import ConfigError, GridTooSmallError
from crplus.memory import (
    auto_obligor_partitions,
    band_table_bytes,
    check_partitions,
    grid_bytes,
    obligor_table_bytes,
)
from crplus.moments import Moments, analytic_moments
from crplus.obligor import ObligorStats, build_obligor_table
from crplus.results import (
    DISTRIBUTION_FILE,
    SUMMARY_FILE,
    CRPlusResult,
    Diagnostics,
    LossDistribution,
    sector_table,
    summary_document,
    truncated_distribution,
    write_distribution,
    write_summary,
)
from crplus.risk_measures import RiskMeasures, risk_measures
from crplus.sectors import SectorParameters, sector_parameters
from crplus.sources import PortfolioSource, iter_partitions, normalize_source
from crplus.tempstore import TempStore, secure_tempdir
from crplus.validation import (
    ValidationReport,
    build_rules,
    count_duplicate_ids,
    enforce,
    evaluate_rules,
    with_duplicates,
)

_logger = logging.getLogger(__name__)

OBLIGOR_ESTIMATE_MARGIN: Final = 1.1
"""Folga sobre a estimativa HyperLogLog do número de devedores."""
MAX_LOSS_UNIT_REFINEMENTS: Final = 3
LOSS_UNIT_GROWTH: Final = 1.05
MAX_GRID_RETRIES: Final = 4
LOSS_UNIT_RETRY_FACTOR: Final = 4.0
"""Fator de aumento de $L_0$ automático quando a distribuição não converge em ``max_grid``."""
EULER_ALERT_TOLERANCE: Final = 1e-6
BANDING_ALERT_TOLERANCE: Final = 1e-9


class _Timer:
    """Cronômetro de etapas (estado local de uma execução)."""

    def __init__(self) -> None:
        self.timings: dict[str, float] = {}

    @contextmanager
    def stage(self, name: str) -> Iterator[None]:
        start = time.perf_counter()
        try:
            yield
        finally:
            self.timings[name] = time.perf_counter() - start


@dataclass(frozen=True, slots=True)
class _Run:
    """Contexto imutável de uma execução."""

    source: PortfolioSource
    config: CRPlusConfig
    store: TempStore
    partitions: int
    timer: _Timer = field(default_factory=_Timer)

    @property
    def tables(self) -> list[Path]:
        return [self.store.path_for(f"obligors-{p:05d}.parquet") for p in range(self.partitions)]

    @property
    def frames(self) -> list[pl.LazyFrame]:
        return list(iter_partitions(self.source, self.partitions))


@dataclass(frozen=True, slots=True, eq=False)
class _Calibration:
    """Banding escolhido e agregados correspondentes."""

    banding: Banding
    aggregate: SectorBandAggregate
    params: SectorParameters
    moments: Moments


def run_creditrisk_plus(data: object, config: CRPlusConfig) -> CRPlusResult:
    """Executa o CreditRisk+ completo sobre a carteira.

    Parameters
    ----------
    data : object
        ``pl.LazyFrame`` (recomendado, ex.: ``pl.scan_parquet``), ``pl.DataFrame`` ou
        ``pandas.DataFrame`` com uma linha por operação.
    config : CRPlusConfig
        Configuração validada (:func:`crplus.load_config`).

    Returns
    -------
    CRPlusResult
        Medidas de risco, distribuição, setores, caminho das contribuições e diagnósticos.

    Raises
    ------
    InputValidationError
        Base inválida (modo estrito) ou ``operation_id`` repetido.
    ConfigError
        Saída existente sem ``overwrite`` ou unidade de perda inviável.
    GridTooSmallError, NumericalRangeError, MemoryBudgetError
        Limites numéricos ou de memória não atendidos.

    """
    prepare_output(config.output)
    configure_runtime(config.resources)
    timer = _Timer()
    with timer.stage("validation"):
        source, report, partitions = _validated(data, config)
    with secure_tempdir() as store:
        return _execute(_Run(source, config, store, partitions, timer), report)


# --- preparação ------------------------------------------------------------------------------


def _existing_outputs(output: OutputConfig) -> list[Path]:
    files = [output.directory / SUMMARY_FILE, output.directory / DISTRIBUTION_FILE]
    parts = sorted(output.contributions_path.glob("part-*.parquet"))
    return [path for path in files if path.exists()] + parts


def prepare_output(output: OutputConfig) -> None:
    """Cria o diretório de saída e remove saídas anteriores do crplus se ``overwrite``.

    Parameters
    ----------
    output : OutputConfig
        Seção ``[output]`` (caminho já confinado ao diretório base).

    Raises
    ------
    ConfigError
        Se já houver saídas do crplus e ``overwrite = false``.

    """
    existing = _existing_outputs(output)
    if existing and not output.overwrite:
        raise ConfigError("output.directory", "já contém saídas do crplus; use overwrite = true")
    for path in existing:
        path.unlink()
    output.contributions_path.mkdir(parents=True, exist_ok=True)


def configure_runtime(resources: ResourcesConfig) -> None:
    """Ajusta as threads do numba e avisa se o pool do polars difere do configurado.

    O pool do polars só pode ser definido antes do primeiro ``import polars``
    (variável ``POLARS_MAX_THREADS``); o ``crplus`` define o padrão 8 ao ser importado.
    """
    numba.set_num_threads(min(resources.numba_threads, os.cpu_count() or 1))
    if pl.thread_pool_size() != resources.polars_threads:
        _logger.info(
            "polars usa %d threads; para %d, defina POLARS_MAX_THREADS antes de importar polars.",
            pl.thread_pool_size(),
            resources.polars_threads,
        )


def resolve_partitions(resources: ResourcesConfig, n_obligors: int, id_kind: str) -> int:
    """Número de partições de devedores (``auto`` ou fixo, checado contra o orçamento).

    Parameters
    ----------
    resources : ResourcesConfig
        Orçamento e configuração de partições.
    n_obligors : int
        Estimativa do número de devedores.
    id_kind : {"int", "str"}
        Tipo do ``obligor_id``.

    Returns
    -------
    int
        Partições a usar.

    """
    estimate = math.ceil(n_obligors * OBLIGOR_ESTIMATE_MARGIN) + 1
    table = obligor_table_bytes(estimate, "str" if id_kind == "str" else "int")
    if resources.obligor_partitions == "auto":
        return auto_obligor_partitions(table, resources.budget)
    check_partitions(resources.obligor_partitions, table, resources.budget)
    return resources.obligor_partitions


def _with_duplicate_check(
    report: ValidationReport, frame: pl.LazyFrame, config: ValidationConfig, partitions: int
) -> ValidationReport:
    if not config.check_operation_id_unique:
        return report
    return with_duplicates(report, count_duplicate_ids(frame, partitions))


def _validated(data: object, config: CRPlusConfig) -> tuple[PortfolioSource, ValidationReport, int]:
    weight_dtype = config.resources.weight_dtype
    source = normalize_source(data, config.columns, weight_dtype, config.numerics.max_sectors)
    rules = build_rules(source.n_sectors, config.validation)
    report = evaluate_rules(source.frame, rules, config.validation.max_reported_rows)
    partitions = resolve_partitions(config.resources, report.n_obligors_estimate, source.id_kind)
    report = _with_duplicate_check(report, source.frame, config.validation, partitions)
    frame = enforce(report, source.frame, rules, config.validation.strict)
    _logger.info("Validação: %d linhas, %d partições.", report.n_rows, partitions)
    return source.with_frame(frame), report, partitions


# --- passos A e B ----------------------------------------------------------------------------


def _pass_a(run: _Run) -> ObligorStats:
    n_sectors = run.source.n_sectors
    stats = [
        build_obligor_table(frame, n_sectors, table)
        for frame, table in zip(run.frames, run.tables, strict=True)
    ]
    return reduce(lambda a, b: a + b, stats, ObligorStats())


def _pass_b(run: _Run, banding: Banding, stats: ObligorStats) -> SectorBandAggregate:
    numerics = run.config.numerics
    nu_max = banding.check_max_band(stats.max_exposure, numerics.max_bands)
    run.config.resources.budget.require(
        band_table_bytes(run.source.n_sectors, nu_max, 4), "os agregados setoriais"
    )
    parts = (
        aggregate_partition(frame, table, run.source.n_sectors, banding)
        for frame, table in zip(run.frames, run.tables, strict=True)
    )
    return reduce(lambda a, b: a + b, parts, SectorBandAggregate.empty(run.source.n_sectors))


def _calibration(run: _Run, banding: Banding, aggregate: SectorBandAggregate) -> _Calibration:
    params = sector_parameters(aggregate, run.source.sectors, run.config.sector_variance)
    moments = analytic_moments(aggregate.intensity, params.variance)
    return _Calibration(banding, aggregate, params, moments)


def _grid_fits(calibration: _Calibration, run: _Run) -> bool:
    numerics = run.config.numerics
    moments = calibration.moments
    reach = math.ceil(moments.expected_loss + numerics.z_tail * moments.std_dev)
    return reach + calibration.aggregate.max_band + 1 <= numerics.max_grid


def _auto_calibrate(run: _Run, stats: ObligorStats, scale: float) -> _Calibration:
    std_dev = math.sqrt(stats.poisson_variance)
    for _ in range(MAX_LOSS_UNIT_REFINEMENTS):
        inputs = LossUnitInputs(stats.max_exposure, stats.expected_loss, std_dev)
        unit = automatic_loss_unit(inputs, run.config.numerics) * scale
        banding = Banding(unit, run.config.model.banding)
        calibration = _calibration(run, banding, _pass_b(run, banding, stats))
        if _grid_fits(calibration, run):
            return calibration
        std_dev = calibration.moments.std_dev * banding.loss_unit * LOSS_UNIT_GROWTH
    raise GridTooSmallError("Não foi possível escolher uma unidade de perda que caiba em max_grid.")


def _fixed_model(run: _Run, stats: ObligorStats, unit: float) -> _Modeled:
    banding = Banding(unit, run.config.model.banding)
    calibration = _calibration(run, banding, _pass_b(run, banding, stats))
    return _distribution(run, calibration)


def _auto_model(run: _Run, stats: ObligorStats) -> _Modeled:
    scale = 1.0
    for _ in range(MAX_GRID_RETRIES):
        calibration = _auto_calibrate(run, stats, scale)
        try:
            return _distribution(run, calibration)
        except GridTooSmallError:
            _logger.info("Distribuição não convergiu em max_grid; aumentando L0 automático.")
            scale *= LOSS_UNIT_RETRY_FACTOR
    raise GridTooSmallError("A distribuição não converge em max_grid nem com L0 automático maior.")


def _model(run: _Run, stats: ObligorStats) -> _Modeled:
    unit = run.config.model.loss_unit
    if unit == "auto":
        return _auto_model(run, stats)
    return _fixed_model(run, stats, float(unit))


# --- passos C e D ----------------------------------------------------------------------------


@dataclass(frozen=True, slots=True, eq=False)
class _Modeled:
    r"""Calibração, medidas e insumos do passo D (sem o estado completo da FFT).

    A distribuição completa e o $\log\varphi$ (os maiores vetores da execução) saem de escopo
    ao final do passo C, antes de o passo D (polars) começar.
    """

    calibration: _Calibration
    measures: RiskMeasures
    grid: GridDiagnostics
    distribution: LossDistribution
    tables: ContributionTables | None


def _tables(run: _Run, inputs: ContributionInputs) -> ContributionTables | None:
    if not run.config.output.write_contributions:
        return None
    shape = inputs.model.intensity.shape
    tables_bytes = band_table_bytes(shape[0] - 1, shape[1] - 1, 2 * len(inputs.measures.var))
    run.config.resources.budget.require(tables_bytes, "as tabelas de contribuição")
    return contribution_tables(inputs)


def _distribution(run: _Run, calibration: _Calibration) -> _Modeled:
    config = run.config
    model = SectorModel(calibration.aggregate.intensity, calibration.params.variance)
    engine = make_engine(
        config.model.engine, config.resources.fft_workers, config.numerics.tol_clip
    )
    request = GridRequest(model, calibration.moments, config.numerics, config.resources.budget)
    distribution, grid = compute_distribution(engine, request)
    loss_unit = calibration.banding.loss_unit
    expected_loss = calibration.moments.expected_loss * loss_unit
    measures = risk_measures(distribution.probs, config.model.alphas, loss_unit, expected_loss)
    window = config.numerics.var_smoothing_window
    inputs = ContributionInputs(distribution, model, calibration.moments, measures, window)
    kept = truncated_distribution(distribution.probs, loss_unit, config.numerics.tol_tail)
    return _Modeled(calibration, measures, grid, kept, _tables(run, inputs))


def _write_partitions(run: _Run, tables: ContributionTables, banding: Banding) -> Path:
    directory = run.config.output.contributions_path
    for part, (frame, table) in enumerate(zip(run.frames, run.tables, strict=True)):
        plan_inputs = ContributionPlanInputs(table, tables, banding, run.source.n_sectors)
        write_contributions(
            contribution_plan(frame, plan_inputs), directory / f"part-{part:05d}.parquet"
        )
    return directory


def _euler_targets(modeled: _Modeled) -> dict[str, float]:
    moments = modeled.calibration.moments
    loss_unit = modeled.calibration.banding.loss_unit
    targets = {
        EL_COLUMN: moments.expected_loss * loss_unit,
        SIGMA_COLUMN: moments.std_dev * loss_unit,
    }
    for alpha in modeled.measures.var:
        targets[var_column(alpha)] = modeled.measures.var[alpha]
        targets[es_column(alpha)] = modeled.measures.es[alpha]
    return targets


def _relative(value: float, target: float) -> float:
    return abs(value - target) / abs(target) if target else abs(value)


def euler_errors(directory: Path, targets: dict[str, float]) -> dict[str, float]:
    """Erros relativos entre as somas das colunas do parquet e as medidas do portfólio.

    Parameters
    ----------
    directory : Path
        Diretório ``contributions`` com os ``part-*.parquet``.
    targets : dict
        Coluna → valor esperado da soma.

    Returns
    -------
    dict
        Coluna → erro relativo.

    """
    frame = pl.scan_parquet(directory / "part-*.parquet")
    sums = frame.select(pl.col(list(targets)).sum()).collect(engine="streaming").row(0, named=True)
    return {name: _relative(float(sums[name]), target) for name, target in targets.items()}


def _contributions(run: _Run, modeled: _Modeled) -> tuple[Path | None, dict[str, float]]:
    if modeled.tables is None:
        return None, {}
    directory = _write_partitions(run, modeled.tables, modeled.calibration.banding)
    return directory, euler_errors(directory, _euler_targets(modeled))


# --- resultado -------------------------------------------------------------------------------


def _validation_alerts(report: ValidationReport) -> list[str]:
    warned = [f"{o.name}: {o.count} linha(s)" for o in report.warnings if o.severity == "warning"]
    return warned + [f"{o.name}: {o.count} linha(s) excluída(s)" for o in report.errors]


def _obligor_alerts(stats: ObligorStats) -> list[str]:
    if not stats.inconsistent_obligors:
        return []
    return [f"{stats.inconsistent_obligors} devedor(es) com operações inconsistentes"]


def _numeric_alerts(diagnostics: Diagnostics) -> list[str]:
    errors = diagnostics.euler_errors.items()
    alerts = [f"soma de Euler de {k}: erro {v:.2e}" for k, v in errors if v > EULER_ALERT_TOLERANCE]
    if diagnostics.banding_error > BANDING_ALERT_TOLERANCE:
        alerts.append("erro de banding acima da tolerância")
    return alerts


def _alerts(
    report: ValidationReport, stats: ObligorStats, diagnostics: Diagnostics
) -> tuple[str, ...]:
    return (*_validation_alerts(report), *_obligor_alerts(stats), *_numeric_alerts(diagnostics))


@dataclass(frozen=True, slots=True, eq=False)
class _Outcome:
    """Peças finais de uma execução."""

    stats: ObligorStats
    modeled: _Modeled
    contributions_path: Path | None
    euler: dict[str, float]


def _diagnostics(run: _Run, report: ValidationReport, outcome: _Outcome) -> Diagnostics:
    calibration = outcome.modeled.calibration
    grid = outcome.modeled.grid
    banded_el = calibration.moments.expected_loss * calibration.banding.loss_unit
    memory = {
        "obligor_table": obligor_table_bytes(outcome.stats.n_obligors, run.source.id_kind),
        "grid": grid_bytes(grid.grid_size),
    }
    base = Diagnostics(
        loss_unit=calibration.banding.loss_unit,
        max_band=calibration.aggregate.max_band,
        grid=grid,
        banding_error=_relative(banded_el, calibration.aggregate.expected_loss),
        partitions=run.partitions,
        n_operations=outcome.stats.n_operations,
        n_obligors=outcome.stats.n_obligors,
        inconsistent_obligors=outcome.stats.inconsistent_obligors,
        validation=report,
        euler_errors=outcome.euler,
        timings=dict(run.timer.timings),
        memory_estimates=memory,
    )
    return _with_alerts(base, report, outcome.stats)


def _with_alerts(base: Diagnostics, report: ValidationReport, stats: ObligorStats) -> Diagnostics:
    return replace(base, alerts=_alerts(report, stats, base))


def _result(run: _Run, outcome: _Outcome, diagnostics: Diagnostics) -> CRPlusResult:
    modeled = outcome.modeled
    calibration = modeled.calibration
    loss_unit = calibration.banding.loss_unit
    return CRPlusResult(
        el=calibration.moments.expected_loss * loss_unit,
        ul=calibration.moments.std_dev * loss_unit,
        var=modeled.measures.var,
        es=modeled.measures.es,
        ec=modeled.measures.ec,
        es_minus_el=modeled.measures.es_minus_el,
        loss_distribution=modeled.distribution,
        sectors=sector_table(calibration.params, calibration.moments, loss_unit),
        contributions_path=outcome.contributions_path,
        summary_path=run.config.output.directory / SUMMARY_FILE,
        diagnostics=diagnostics,
    )


def _execute(run: _Run, report: ValidationReport) -> CRPlusResult:
    with run.timer.stage("pass_a"):
        stats = _pass_a(run)
    with run.timer.stage("pass_b_and_distribution"):
        modeled = _model(run, stats)
    with run.timer.stage("contributions"):
        path, euler = _contributions(run, modeled)
    outcome = _Outcome(stats, modeled, path, euler)
    result = _result(run, outcome, _diagnostics(run, report, outcome))
    _write_outputs(run, result)
    return result


def _write_outputs(run: _Run, result: CRPlusResult) -> None:
    document = summary_document(result, __version__, run.config.source_sha256)
    write_summary(document, result.summary_path)
    write_distribution(result.loss_distribution, run.config.output.directory / DISTRIBUTION_FILE)
    for alert in result.diagnostics.alerts:
        _logger.warning("Alerta: %s", alert)
`````

<!-- FILE: src/crplus/banding.py -->
`````python
r"""Banding das exposições e escolha da unidade de perda $L_0$.

A banda do devedor é $\nu_j = \max(1, \lceil E_j / L_0 \rceil)$ (ou arredondamento ao inteiro
mais próximo). O ajuste de intensidade $\tilde p_{jk} = \sum_{i\in j} w_{ik} p_i E_i/(\nu_j L_0)$
preserva exatamente a perda esperada: $L_0 \sum_j \sum_k \tilde p_{jk} \nu_j = \sum_i p_i E_i$.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass
from typing import Final

import polars as pl

from crplus.config import NumericsConfig
from crplus.exceptions import ConfigError

BAND_RELATIVE_EPS: Final = 1e-12
r"""Folga relativa no ``ceil``: $E_j = k L_0$ cai na banda $k$ mesmo com erro de arredondamento."""
LOSS_UNIT_MARGIN: Final = 1e-9
"""Margem relativa aplicada à unidade de perda automática."""
DEGENERATE_LOSS_UNIT: Final = 1.0
"""Unidade de perda usada quando a carteira não tem exposição (perda identicamente nula)."""


def _ceil_band(ratio: pl.Expr) -> pl.Expr:
    return (ratio * (1.0 - BAND_RELATIVE_EPS)).ceil()


def _round_band(ratio: pl.Expr) -> pl.Expr:
    return ratio.round(0, mode="half_away_from_zero")


_ROUNDERS: Final[dict[str, Callable[[pl.Expr], pl.Expr]]] = {
    "ceil": _ceil_band,
    "round": _round_band,
}


@dataclass(frozen=True, slots=True)
class Banding:
    """Regra de banding em uso.

    Parameters
    ----------
    loss_unit : float
        Unidade de perda $L_0 > 0$, na moeda do EAD.
    rule : {"ceil", "round"}
        Regra de arredondamento.

    """

    loss_unit: float
    rule: str = "ceil"

    def band(self, exposure: pl.Expr) -> pl.Expr:
        r"""Expressão da banda $\nu_j = \max(1, \operatorname{arred}(E_j / L_0))$, em ``Int64``.

        Parameters
        ----------
        exposure : pl.Expr
            Exposição do devedor $E_j$.

        Returns
        -------
        pl.Expr
            Banda inteira, sempre >= 1.

        """
        rounded = _ROUNDERS[self.rule](exposure / self.loss_unit)
        return rounded.clip(lower_bound=1.0).cast(pl.Int64)

    def max_band(self, max_exposure: float) -> int:
        r"""Banda da maior exposição, com exatamente a mesma aritmética da expressão polars.

        Parameters
        ----------
        max_exposure : float
            Maior $E_j$ da carteira.

        Returns
        -------
        int
            $\nu_{max}$.

        """
        frame = pl.DataFrame({"e": [max_exposure]}, schema={"e": pl.Float64})
        return int(frame.select(self.band(pl.col("e"))).item())

    def check_max_band(self, max_exposure: float, max_bands: int) -> int:
        r"""Calcula $\nu_{max}$ e rejeita valores acima de ``numerics.max_bands``.

        Raises
        ------
        ConfigError
            Se a unidade de perda gerar bandas demais.

        """
        nu_max = self.max_band(max_exposure)
        if nu_max > max_bands:
            raise ConfigError(
                "model.loss_unit",
                "unidade de perda pequena demais: a maior banda excede numerics.max_bands",
            )
        return nu_max


@dataclass(frozen=True, slots=True)
class LossUnitInputs:
    """Estatísticas da carteira usadas na escolha automática de $L_0$ (em moeda).

    Parameters
    ----------
    max_exposure : float
        Maior exposição de devedor.
    expected_loss : float
        Perda esperada da carteira.
    std_dev : float
        Estimativa do desvio-padrão da perda.

    """

    max_exposure: float
    expected_loss: float
    std_dev: float


def automatic_loss_unit(inputs: LossUnitInputs, numerics: NumericsConfig) -> float:
    r"""Menor $L_0$ tal que $\nu_{max} \le$ ``max_bands`` e a grade estimada $\le$ ``max_grid``.

    Parameters
    ----------
    inputs : LossUnitInputs
        Estatísticas da carteira.
    numerics : NumericsConfig
        Limites numéricos.

    Returns
    -------
    float
        Unidade de perda.

    Notes
    -----
    $M(L_0) \approx (EL + z\,\sigma + E_{max})/L_0 + 2$, logo
    $L_0 = \max\left(E_{max}/\nu_{lim},\ (EL + z\sigma + E_{max})/(M_{lim} - 2)\right)$.
    Quanto menor $L_0$, menor o erro de banding e maior a grade (custo de FFT e memória).

    """
    by_bands = inputs.max_exposure / numerics.max_bands
    spread = inputs.expected_loss + numerics.z_tail * inputs.std_dev + inputs.max_exposure
    by_grid = spread / (numerics.max_grid - 2)
    unit = max(by_bands, by_grid) * (1.0 + LOSS_UNIT_MARGIN)
    return unit if math.isfinite(unit) and unit > 0 else DEGENERATE_LOSS_UNIT
`````

<!-- FILE: src/crplus/config.py -->
`````python
"""Configuração do ``crplus``: leitura de TOML, validação campo a campo e caminhos seguros.

A configuração é lida exclusivamente com :mod:`tomllib` (sem execução de código), convertida
em dataclasses imutáveis e validada no ``__post_init__`` de cada seção. Chaves ou seções
desconhecidas são rejeitadas com :class:`~crplus.exceptions.ConfigError`, que informa o nome
qualificado do campo. O significado de cada chave está em ``docs/configuracao.md``.
"""

from __future__ import annotations

import hashlib
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass, field, fields, replace
from pathlib import Path
from types import MappingProxyType
from typing import Any, Literal

from crplus._checks import (
    FieldCheck,
    either,
    int_between,
    is_bool,
    is_optional,
    is_real,
    is_text,
    one_of,
    real_between,
    run_checks,
)
from crplus.exceptions import ConfigError
from crplus.memory import MemoryBudget, max_grid_within_budget
from crplus.paths import resolve_within

MAX_CONFIG_BYTES = 1_048_576
"""Tamanho máximo aceito para o arquivo TOML (proteção contra entrada abusiva)."""
MAX_ALPHAS = 16
HARD_MAX_BANDS = 10_000_000
HARD_MAX_GRID = 2**31
HARD_MAX_SECTORS = 10_000
MIN_GRID = 16
MAX_THREADS = 1024
MAX_PARTITIONS = 65_536
MAX_BUDGET_GB = 4096.0
MAX_REPORTED_ROWS = 1000
MAX_Z_TAIL = 100.0

_AUTO = "auto"


def _is_alpha(value: object) -> bool:
    return real_between(0.0, 1.0, closed_low=False, closed_high=False)(value)


def _is_alpha_tuple(value: object) -> bool:
    if not isinstance(value, tuple) or not 0 < len(value) <= MAX_ALPHAS:
        return False
    return all(_is_alpha(alpha) for alpha in value) and len(set(value)) == len(value)


def _sorted_alphas(value: object) -> object:
    if isinstance(value, list | tuple) and all(is_real(alpha) for alpha in value):
        return tuple(sorted(float(alpha) for alpha in value))
    return value


def _positive_real(value: object) -> bool:
    return real_between(0.0, float("inf"), closed_low=False, closed_high=False)(value)


def _non_negative_real(value: object) -> bool:
    return real_between(0.0, float("inf"), closed_low=True, closed_high=False)(value)


def _probability_tolerance(value: object) -> bool:
    return real_between(0.0, 1.0, closed_low=False, closed_high=False)(value)


def _is_auto(value: object) -> bool:
    return value == _AUTO


def _is_path(value: object) -> bool:
    return isinstance(value, Path)


def _as_path(value: object) -> object:
    return Path(value) if isinstance(value, str) else value


def _is_sector_entry(name: object, value: object) -> bool:
    return is_text(name) and _non_negative_real(value)


def _is_variance_table(value: object) -> bool:
    if not isinstance(value, Mapping) or len(value) == 0:
        return False
    return all(_is_sector_entry(name, item) for name, item in value.items())


def _frozen_mapping(value: object) -> object:
    return MappingProxyType(dict(value)) if isinstance(value, Mapping) else value


_MODEL_CHECKS = (
    FieldCheck("alphas", _is_alpha_tuple, f"lista de 1 a {MAX_ALPHAS} níveis distintos em (0, 1)"),
    FieldCheck("engine", one_of("fft", "panjer"), "deve ser 'fft' ou 'panjer'"),
    FieldCheck("loss_unit", either(_is_auto, _positive_real), "'auto' ou número positivo"),
    FieldCheck("banding", one_of("ceil", "round"), "deve ser 'ceil' ou 'round'"),
)


@dataclass(frozen=True, slots=True)
class ModelConfig:
    """Seção ``[model]``: níveis de confiança, motor, unidade de perda e banding.

    Parameters
    ----------
    alphas : tuple of float
        Níveis de confiança de VaR/ES, distintos, em ``(0, 1)``; armazenados ordenados.
    engine : {"fft", "panjer"}
        Motor da distribuição de perdas.
    loss_unit : float or "auto"
        Unidade de perda ``L0`` na moeda do EAD, ou escolha automática.
    banding : {"ceil", "round"}
        Regra de arredondamento de $E_j / L_0$ para a banda.

    """

    alphas: tuple[float, ...] = (0.99, 0.999)
    engine: Literal["fft", "panjer"] = "fft"
    loss_unit: float | Literal["auto"] = "auto"
    banding: Literal["ceil", "round"] = "ceil"

    def __post_init__(self) -> None:
        """Normaliza ``alphas`` para tupla ordenada e valida os campos."""
        object.__setattr__(self, "alphas", _sorted_alphas(self.alphas))
        run_checks(self, "model", _MODEL_CHECKS)


_SECTOR_VARIANCE_CHECKS = (
    FieldCheck("method", one_of("pd_vol", "external"), "deve ser 'pd_vol' ou 'external'"),
    FieldCheck("adjust_for_banding", is_bool, "deve ser booleano"),
    FieldCheck("value_type", one_of("variance", "cv"), "deve ser 'variance' ou 'cv'"),
    FieldCheck(
        "values",
        is_optional(_is_variance_table),
        "tabela não vazia de setor -> número finito >= 0",
    ),
    FieldCheck("values_file", is_optional(_is_path), "deve ser um caminho"),
)

_SOURCES_EXPECTED = {"pd_vol": 0, "external": 1}
_SOURCES_MESSAGE = {
    "pd_vol": "'values'/'values_file' só são permitidos com method = 'external'",
    "external": "method = 'external' exige exatamente um de 'values' ou 'values_file'",
}


@dataclass(frozen=True, slots=True)
class SectorVarianceConfig:
    r"""Seção ``[sector_variance]``: origem da variância dos fatores setoriais.

    Parameters
    ----------
    method : {"pd_vol", "external"}
        ``pd_vol`` deriva $v_k$ da volatilidade das PDs (CSFB); ``external`` usa
        valores informados pelo usuário.
    adjust_for_banding : bool
        Para ``pd_vol``: aplica às volatilidades o mesmo ajuste de banding das PDs.
    value_type : {"variance", "cv"}
        Para ``external``: se os valores são $v_k$ ou $cv_k = \sqrt{v_k}$.
    values : Mapping[str, float] or None
        Valores por setor (nome da coluna de peso), inline no TOML.
    values_file : Path or None
        Arquivo CSV/parquet com colunas ``sector`` e ``variance`` (ou ``cv``).

    """

    method: Literal["pd_vol", "external"] = "pd_vol"
    adjust_for_banding: bool = True
    value_type: Literal["variance", "cv"] = "variance"
    values: Mapping[str, float] | None = None
    values_file: Path | None = None

    def __post_init__(self) -> None:
        """Normaliza tipos, valida campos e a coerência entre método e fonte de valores."""
        object.__setattr__(self, "values", _frozen_mapping(self.values))
        object.__setattr__(self, "values_file", _as_path(self.values_file))
        run_checks(self, "sector_variance", _SECTOR_VARIANCE_CHECKS)
        self._check_value_source()

    def _check_value_source(self) -> None:
        provided = int(self.values is not None) + int(self.values_file is not None)
        if provided != _SOURCES_EXPECTED[self.method]:
            raise ConfigError("sector_variance.values", _SOURCES_MESSAGE[self.method])


_COLUMN_FIELDS = ("operation_id", "obligor_id", "pd", "pd_vol", "lgd", "ead")
_COLUMN_CHECKS = tuple(
    FieldCheck(name, is_text, "nome de coluna não vazio")
    for name in (*_COLUMN_FIELDS, "weight_prefix")
)


@dataclass(frozen=True, slots=True)
class ColumnMap:
    """Seção ``[columns]``: nomes das colunas na base de entrada.

    Parameters
    ----------
    operation_id, obligor_id, pd, pd_vol, lgd, ead : str
        Nome de cada coluna obrigatória.
    weight_prefix : str
        Prefixo das colunas de peso setorial (uma por setor, formato *wide*).

    """

    operation_id: str = "operation_id"
    obligor_id: str = "obligor_id"
    pd: str = "pd"
    pd_vol: str = "pd_vol"
    lgd: str = "lgd"
    ead: str = "ead"
    weight_prefix: str = "w_"

    def __post_init__(self) -> None:
        """Valida nomes não vazios, distintos e não confundíveis com colunas de peso."""
        run_checks(self, "columns", _COLUMN_CHECKS)
        self._check_distinct()
        self._check_prefix_unambiguous()

    @property
    def required(self) -> tuple[str, ...]:
        """Nomes das colunas obrigatórias, na ordem canônica."""
        return tuple(getattr(self, name) for name in _COLUMN_FIELDS)

    def _check_distinct(self) -> None:
        if len(set(self.required)) != len(_COLUMN_FIELDS):
            raise ConfigError("columns", "os nomes das colunas obrigatórias devem ser distintos")

    def _check_prefix_unambiguous(self) -> None:
        if any(name.startswith(self.weight_prefix) for name in self.required):
            raise ConfigError(
                "columns.weight_prefix",
                "nenhuma coluna obrigatória pode começar com o prefixo de pesos",
            )


_VALIDATION_CHECKS = (
    FieldCheck("strict", is_bool, "deve ser booleano"),
    FieldCheck(
        "pd_warn_threshold",
        real_between(0.0, 1.0, closed_low=False, closed_high=True),
        "deve estar em (0, 1]",
    ),
    FieldCheck(
        "weights_tolerance",
        real_between(0.0, 1.0, closed_low=True, closed_high=False),
        "deve estar em [0, 1)",
    ),
    FieldCheck("check_operation_id_unique", is_bool, "deve ser booleano"),
    FieldCheck(
        "max_reported_rows",
        int_between(0, MAX_REPORTED_ROWS),
        f"inteiro em [0, {MAX_REPORTED_ROWS}]",
    ),
)


@dataclass(frozen=True, slots=True)
class ValidationConfig:
    r"""Seção ``[validation]``: regras de validação da base de entrada.

    Parameters
    ----------
    strict : bool
        ``True`` levanta erro em qualquer violação; ``False`` exclui as linhas inválidas.
    pd_warn_threshold : float
        PD acima da qual se emite aviso (a aproximação de Poisson piora).
    weights_tolerance : float
        Tolerância para $\sum_k w_{ik} > 1$.
    check_operation_id_unique : bool
        Verifica unicidade de ``operation_id`` (custo de memória alto em bases enormes).
    max_reported_rows : int
        Quantidade de posições de linhas violadoras guardadas por regra no relatório.

    """

    strict: bool = True
    pd_warn_threshold: float = 0.3
    weights_tolerance: float = 1e-9
    check_operation_id_unique: bool = True
    max_reported_rows: int = 10

    def __post_init__(self) -> None:
        """Valida os campos."""
        run_checks(self, "validation", _VALIDATION_CHECKS)


_NUMERICS_CHECKS = (
    FieldCheck(
        "z_tail",
        real_between(0.0, MAX_Z_TAIL, closed_low=False, closed_high=True),
        f"deve estar em (0, {MAX_Z_TAIL:g}]",
    ),
    FieldCheck("tol_tail", _probability_tolerance, "deve estar em (0, 1)"),
    FieldCheck("tol_moment", _probability_tolerance, "deve estar em (0, 1)"),
    FieldCheck("tol_clip", _probability_tolerance, "deve estar em (0, 1)"),
    FieldCheck("max_bands", int_between(1, HARD_MAX_BANDS), f"inteiro em [1, {HARD_MAX_BANDS}]"),
    FieldCheck("max_grid", int_between(MIN_GRID, HARD_MAX_GRID), f"inteiro em [{MIN_GRID}, 2**31]"),
    FieldCheck(
        "max_sectors",
        int_between(1, HARD_MAX_SECTORS),
        f"inteiro em [1, {HARD_MAX_SECTORS}]",
    ),
    FieldCheck(
        "var_smoothing_window",
        int_between(0, HARD_MAX_BANDS),
        "inteiro não negativo",
    ),
)


@dataclass(frozen=True, slots=True)
class NumericsConfig:
    r"""Seção ``[numerics]``: tolerâncias e limites numéricos.

    Parameters
    ----------
    z_tail : float
        Desvios-padrão além da média usados no tamanho inicial da grade.
    tol_tail : float
        Massa máxima admitida no último 1% da grade.
    tol_moment : float
        Erro relativo máximo entre momentos da distribuição e momentos analíticos.
    tol_clip : float
        Magnitude máxima de probabilidade negativa zerada após a FFT.
    max_bands : int
        Limite de segurança para $\nu_{max}$.
    max_grid : int
        Limite de segurança para o tamanho ``M`` da grade.
    max_sectors : int
        Limite de segurança para o número de setores ``K``.
    var_smoothing_window : int
        Janela (em unidades de perda) de suavização das contribuições de VaR; 0 desliga.

    """

    z_tail: float = 15.0
    tol_tail: float = 1e-12
    tol_moment: float = 1e-8
    tol_clip: float = 1e-13
    max_bands: int = 100_000
    max_grid: int = 2**26
    max_sectors: int = 1000
    var_smoothing_window: int = 0

    def __post_init__(self) -> None:
        """Valida os campos e exige ``max_bands < max_grid``."""
        run_checks(self, "numerics", _NUMERICS_CHECKS)
        if self.max_bands >= self.max_grid:
            raise ConfigError("numerics.max_bands", "deve ser menor que numerics.max_grid")


_RESOURCES_CHECKS = (
    FieldCheck(
        "memory_budget_gb",
        real_between(0.0, MAX_BUDGET_GB, closed_low=False, closed_high=True),
        f"deve estar em (0, {MAX_BUDGET_GB:g}]",
    ),
    FieldCheck(
        "obligor_partitions",
        either(_is_auto, int_between(1, MAX_PARTITIONS)),
        f"'auto' ou inteiro em [1, {MAX_PARTITIONS}]",
    ),
    FieldCheck("polars_threads", int_between(1, MAX_THREADS), f"inteiro em [1, {MAX_THREADS}]"),
    FieldCheck("fft_workers", int_between(1, MAX_THREADS), f"inteiro em [1, {MAX_THREADS}]"),
    FieldCheck("numba_threads", int_between(1, MAX_THREADS), f"inteiro em [1, {MAX_THREADS}]"),
    FieldCheck("weight_dtype", one_of("float64", "float32"), "deve ser 'float64' ou 'float32'"),
)


@dataclass(frozen=True, slots=True)
class ResourcesConfig:
    """Seção ``[resources]``: orçamento de memória e paralelismo.

    Parameters
    ----------
    memory_budget_gb : float
        Orçamento de memória do processo inteiro, em GB.
    obligor_partitions : int or "auto"
        Número de partições por hash de ``obligor_id``.
    polars_threads : int
        Threads do polars (``POLARS_MAX_THREADS``).
    fft_workers : int
        Workers do ``scipy.fft``.
    numba_threads : int
        Threads dos kernels numba.
    weight_dtype : {"float64", "float32"}
        Tipo de armazenamento dos pesos setoriais (``float32`` reduz memória e leitura).

    """

    memory_budget_gb: float = 9.0
    obligor_partitions: int | Literal["auto"] = "auto"
    polars_threads: int = 8
    fft_workers: int = 8
    numba_threads: int = 8
    weight_dtype: Literal["float64", "float32"] = "float64"

    def __post_init__(self) -> None:
        """Valida os campos."""
        run_checks(self, "resources", _RESOURCES_CHECKS)

    @property
    def budget(self) -> MemoryBudget:
        """Orçamento de memória correspondente a ``memory_budget_gb``."""
        return MemoryBudget.from_gb(self.memory_budget_gb)


_OUTPUT_CHECKS = (
    FieldCheck("directory", _is_path, "deve ser um caminho"),
    FieldCheck("overwrite", is_bool, "deve ser booleano"),
    FieldCheck("write_contributions", is_bool, "deve ser booleano"),
)


@dataclass(frozen=True, slots=True)
class OutputConfig:
    """Seção ``[output]``: destino dos resultados.

    Parameters
    ----------
    directory : Path
        Diretório de saída (relativo ao diretório base).
    overwrite : bool
        Permite sobrescrever saídas existentes.
    write_contributions : bool
        Grava o parquet de contribuições por operação.

    """

    directory: Path = Path("saida_crplus")
    overwrite: bool = False
    write_contributions: bool = True

    def __post_init__(self) -> None:
        """Normaliza o caminho e valida os campos."""
        object.__setattr__(self, "directory", _as_path(self.directory))
        run_checks(self, "output", _OUTPUT_CHECKS)

    @property
    def contributions_path(self) -> Path:
        """Diretório do parquet particionado de contribuições por operação."""
        return self.directory / "contributions"


_SECTIONS: dict[str, type] = {
    "model": ModelConfig,
    "sector_variance": SectorVarianceConfig,
    "columns": ColumnMap,
    "validation": ValidationConfig,
    "numerics": NumericsConfig,
    "resources": ResourcesConfig,
    "output": OutputConfig,
}


@dataclass(frozen=True, slots=True)
class CRPlusConfig:
    """Configuração completa e validada de uma execução.

    Parameters
    ----------
    model, sector_variance, columns, validation, numerics, resources, output
        Seções da configuração (ver ``docs/configuracao.md``).
    base_dir : Path
        Diretório base; caminhos relativos são resolvidos a partir dele e nenhum caminho pode
        sair dele. Padrão: diretório corrente (ou o diretório do TOML em :func:`load_config`).
    source_sha256 : str or None
        Hash SHA-256 do arquivo TOML de origem, para reprodutibilidade.

    """

    model: ModelConfig = field(default_factory=ModelConfig)
    sector_variance: SectorVarianceConfig = field(default_factory=SectorVarianceConfig)
    columns: ColumnMap = field(default_factory=ColumnMap)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    numerics: NumericsConfig = field(default_factory=NumericsConfig)
    resources: ResourcesConfig = field(default_factory=ResourcesConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    base_dir: Path = field(default_factory=Path.cwd)
    source_sha256: str | None = None

    def __post_init__(self) -> None:
        """Valida tipos das seções, coerência com o orçamento e resolve os caminhos."""
        self._check_section_types()
        self._check_grid_budget()
        self._resolve_paths()

    def _check_section_types(self) -> None:
        for name, section_type in _SECTIONS.items():
            if not isinstance(getattr(self, name), section_type):
                raise ConfigError(name, "tipo de seção inválido")

    def _check_grid_budget(self) -> None:
        if self.numerics.max_grid > max_grid_within_budget(self.resources.budget):
            raise ConfigError(
                "numerics.max_grid",
                "a grade máxima não cabe no orçamento de memória (resources.memory_budget_gb)",
            )

    def _resolve_paths(self) -> None:
        base = _existing_dir(Path(self.base_dir))
        object.__setattr__(self, "base_dir", base)
        directory = resolve_within(base, self.output.directory, "output.directory")
        object.__setattr__(self, "output", replace(self.output, directory=directory))
        values_file = self.sector_variance.values_file
        if values_file is not None:
            resolved = resolve_within(base, values_file, "sector_variance.values_file")
            object.__setattr__(
                self, "sector_variance", replace(self.sector_variance, values_file=resolved)
            )


def _existing_dir(path: Path) -> Path:
    resolved = path.resolve()
    if not resolved.is_dir():
        raise ConfigError("base_dir", "o diretório base deve existir")
    return resolved


def config_from_mapping(
    raw: Mapping[str, Any],
    *,
    base_dir: str | Path | None = None,
    source_sha256: str | None = None,
) -> CRPlusConfig:
    """Constrói e valida a configuração a partir de um mapeamento (TOML já lido).

    Parameters
    ----------
    raw : Mapping[str, Any]
        Seções do TOML. Seções ausentes usam os padrões.
    base_dir : str or Path or None, default None
        Diretório base para caminhos; ``None`` usa o diretório corrente.
    source_sha256 : str or None, default None
        Hash do arquivo de origem.

    Returns
    -------
    CRPlusConfig
        Configuração validada.

    Raises
    ------
    ConfigError
        Em seção/chave desconhecida ou valor inválido.

    """
    unknown = sorted(set(raw) - set(_SECTIONS))
    if unknown:
        raise ConfigError(unknown[0], "seção desconhecida")
    sections: dict[str, Any] = {
        name: _build_section(name, kind, raw.get(name, {})) for name, kind in _SECTIONS.items()
    }
    base = Path.cwd() if base_dir is None else Path(base_dir)
    return CRPlusConfig(**sections, base_dir=base, source_sha256=source_sha256)


def _build_section(name: str, kind: type, raw: object) -> object:
    if not isinstance(raw, Mapping):
        raise ConfigError(name, "deve ser uma tabela TOML")
    unknown = sorted(set(raw) - {item.name for item in fields(kind)})
    if unknown:
        raise ConfigError(f"{name}.{unknown[0]}", "chave desconhecida")
    return kind(**raw)


def load_config(path: str | Path, base_dir: str | Path | None = None) -> CRPlusConfig:
    """Lê e valida um arquivo de configuração TOML.

    Parameters
    ----------
    path : str or Path
        Arquivo TOML. Links simbólicos e arquivos acima de 1 MiB são rejeitados.
    base_dir : str or Path or None, default None
        Diretório base para os caminhos da configuração; ``None`` usa o diretório do TOML.

    Returns
    -------
    CRPlusConfig
        Configuração validada, com ``source_sha256`` do arquivo lido.

    Raises
    ------
    ConfigError
        Se o arquivo for inacessível, inválido como TOML/UTF-8 ou tiver valores inválidos.

    """
    config_path = _checked_config_file(Path(path))
    payload = config_path.read_bytes()
    raw = _parse_toml(payload)
    base = config_path.parent if base_dir is None else base_dir
    digest = hashlib.sha256(payload).hexdigest()
    return config_from_mapping(raw, base_dir=base, source_sha256=digest)


def _checked_config_file(path: Path) -> Path:
    if path.is_symlink():
        raise ConfigError("arquivo de configuração", "links simbólicos não são aceitos")
    if not path.is_file():
        raise ConfigError("arquivo de configuração", "arquivo não encontrado")
    if path.stat().st_size > MAX_CONFIG_BYTES:
        raise ConfigError("arquivo de configuração", "arquivo maior que 1 MiB")
    return path.resolve()


def _parse_toml(payload: bytes) -> dict[str, Any]:
    try:
        return tomllib.loads(payload.decode("utf-8"))
    except UnicodeDecodeError as error:
        raise ConfigError("arquivo de configuração", "o arquivo deve estar em UTF-8") from error
    except tomllib.TOMLDecodeError as error:
        raise ConfigError("arquivo de configuração", f"TOML inválido ({error})") from error


__all__ = [
    "CRPlusConfig",
    "ColumnMap",
    "ModelConfig",
    "NumericsConfig",
    "OutputConfig",
    "ResourcesConfig",
    "SectorVarianceConfig",
    "ValidationConfig",
    "config_from_mapping",
    "load_config",
]
`````

<!-- FILE: src/crplus/contributions.py -->
`````python
r"""Contribuições de risco por operação (alocação de Euler) e passo D.

Desvio-padrão (analítico), em moeda:

$$RC^\sigma_i = \frac{p_i E_i}{\sigma_u}\Big(\nu_j + \sum_{k\ge1} v_k\,w_{ik}\,EL_k\Big),
\qquad \sum_i RC^\sigma_i = \sigma_u L_0.$$

VaR e ES (Haaf e Tasche, 2002), a partir das distribuições inclinadas $g^{(k)}$:

$$A^{ES}_k(\nu) = \frac{T^{(k)}(q-\nu) + \beta\,g^{(k)}_{q-\nu}}{1-\alpha},\qquad
A^{VaR}_k(\nu) = \frac{g^{(k)}_{q-\nu}}{g_q},$$

com $T^{(k)}(x) = \sum_{y>x} g^{(k)}_y$ ($T = 1$ e $g = 0$ para $x < 0$) e
$\beta = (F(q)-\alpha)/g_q$. Por operação, $RC_i = p_i E_i \sum_k w_{ik} A_k(\nu_j)$. A tabela
$A$ tem forma $(n_\alpha, K+1, \nu_{max}+1)$; cada $g^{(k)}$ é calculada, reduzida e descartada.

Notes
-----
Contribuições de VaR em distribuições discretas são ruidosas (dependem de um único átomo
$g_q$). Com ``var_smoothing_window = w > 0``, usa-se a massa de $g^{(k)}$ na janela
$[q-w, q+w]$, renormalizada por $\sum_{x \in W} x\,g_x$ para que a soma continue igual ao VaR.

"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Final

import numpy as np
import polars as pl
from numpy.typing import NDArray

from crplus.aggregation import band_plan, sector_weights
from crplus.banding import Banding
from crplus.distribution.model import ComputedDistribution, SectorModel
from crplus.moments import Moments
from crplus.risk_measures import QuantileInfo, RiskMeasures
from crplus.schema import BAND, EAD, LGD, OBLIGOR_ID, OPERATION_ID, PD

FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int64]

EL_COLUMN: Final = "el"
SIGMA_COLUMN: Final = "rc_sigma"


def alpha_label(alpha: float) -> str:
    """Rótulo estável de um nível de confiança para nomes de colunas (ex.: ``0.999``)."""
    return format(alpha, ".12g")


def var_column(alpha: float) -> str:
    """Nome da coluna de contribuição de VaR para ``alpha``."""
    return f"rc_var_{alpha_label(alpha)}"


def es_column(alpha: float) -> str:
    """Nome da coluna de contribuição de ES para ``alpha``."""
    return f"rc_es_{alpha_label(alpha)}"


def contribution_columns(alphas: Sequence[float]) -> list[str]:
    """Colunas de valores do parquet de contribuições, na ordem de gravação."""
    measures = [name for alpha in alphas for name in (var_column(alpha), es_column(alpha))]
    return [EL_COLUMN, SIGMA_COLUMN, *measures]


@dataclass(frozen=True, slots=True, eq=False)
class _Lookups:
    r"""Acesso vetorizado a $g$, à cauda $\sum_{y>x} g_y$ e a somas em janelas."""

    probs: FloatArray
    upper: FloatArray  # upper[j] = sum_{y > j-1} g_y, j = 0..M

    @classmethod
    def of(cls, probs: FloatArray) -> _Lookups:
        upper = np.zeros(probs.shape[0] + 1)
        upper[0] = probs.sum()
        np.cumsum(probs[:0:-1], out=upper[-2:0:-1])
        return cls(probs, upper)

    def prob_at(self, index: IntArray) -> FloatArray:
        inside = (index >= 0) & (index < self.probs.shape[0])
        return np.where(inside, self.probs[np.clip(index, 0, self.probs.shape[0] - 1)], 0.0)

    def tail_at(self, index: IntArray) -> FloatArray:
        return self.upper[np.clip(index + 1, 0, self.probs.shape[0])]

    def window_mass(self, index: IntArray, window: int) -> FloatArray:
        if window == 0:
            return self.prob_at(index)
        return self.tail_at(index - window - 1) - self.tail_at(index + window)


def _es_row(lookups: _Lookups, info: QuantileInfo, index: IntArray) -> FloatArray:
    tail = np.where(index >= 0, lookups.tail_at(index), 1.0)
    return (tail + info.beta * lookups.prob_at(index)) / (1.0 - info.alpha)


def _window_denominator(probs: FloatArray, info: QuantileInfo, window: int) -> float:
    low = max(0, info.quantile - window)
    high = min(probs.shape[0], info.quantile + window + 1)
    return float(np.arange(low, high, dtype=np.float64) @ probs[low:high])


@dataclass(frozen=True, slots=True, eq=False)
class ContributionTables:
    r"""Tabelas pequenas, indexadas por banda, para o passo D.

    Parameters
    ----------
    alphas : tuple of float
        Níveis de confiança.
    var_table, es_table : FloatArray
        $A^{VaR}$ e $A^{ES}$, forma $(n_\alpha, K+1, B+1)$.
    sigma : float
        $\sigma_u$.
    systematic : FloatArray
        $v_k\,EL_k$ ($k \ge 1$; zero no setor 0), em unidades de perda.

    """

    alphas: tuple[float, ...]
    var_table: FloatArray
    es_table: FloatArray
    sigma: float
    systematic: FloatArray

    def lookups(self, measure: str, alpha: float) -> list[pl.Expr]:
        r"""Expressões $A_k(\nu_j)$, $k = 0..K$, por *gather* na banda de cada linha.

        Usa vetores literais pequenos (comprimento $\nu_{max}+1$) indexados pela coluna ``nu``,
        sem ``join``: não alarga os lotes do streaming com $2 n_\alpha (K+1)$ colunas.

        Parameters
        ----------
        measure : {"var", "es"}
            Tabela usada.
        alpha : float
            Nível de confiança.

        Returns
        -------
        list of pl.Expr
            Uma expressão por setor.

        """
        table = {"var": self.var_table, "es": self.es_table}[measure][self.alphas.index(alpha)]
        return [pl.lit(pl.Series(row)).gather(pl.col(BAND)) for row in table]


@dataclass(frozen=True, slots=True)
class ContributionInputs:
    """Insumos das tabelas de contribuição.

    Parameters
    ----------
    distribution : ComputedDistribution
        Distribuição calculada (com acesso a $g^{(k)}$).
    model : SectorModel
        Modelo setorial.
    moments : Moments
        Momentos analíticos.
    measures : RiskMeasures
        Medidas de risco (quantis).
    smoothing_window : int
        ``numerics.var_smoothing_window``.

    """

    distribution: ComputedDistribution
    model: SectorModel
    moments: Moments
    measures: RiskMeasures
    smoothing_window: int


def contribution_tables(inputs: ContributionInputs) -> ContributionTables:
    """Calcula as tabelas $A^{VaR}$ e $A^{ES}$ setor a setor (uma $g^{(k)}$ por vez).

    Parameters
    ----------
    inputs : ContributionInputs
        Distribuição, modelo, momentos, medidas e janela de suavização.

    Returns
    -------
    ContributionTables
        Tabelas para o passo D.

    """
    alphas = tuple(inputs.measures.quantiles)
    shape = (len(alphas), *inputs.model.intensity.shape)
    var_table, es_table = np.zeros(shape), np.zeros(shape)
    for k in range(shape[1]):
        lookups = _Lookups.of(inputs.distribution.tilted(k))
        for i, alpha in enumerate(alphas):
            var_table[i, k], es_table[i, k] = _rows(inputs, lookups, alpha)
    systematic = inputs.model.variance * inputs.moments.sector_expected_loss
    systematic[0] = 0.0
    return ContributionTables(alphas, var_table, es_table, inputs.moments.std_dev, systematic)


def _rows(
    inputs: ContributionInputs, lookups: _Lookups, alpha: float
) -> tuple[FloatArray, FloatArray]:
    info = inputs.measures.quantiles[alpha]
    index = info.quantile - np.arange(inputs.model.intensity.shape[1], dtype=np.int64)
    window = inputs.smoothing_window
    denominator = _window_denominator(inputs.distribution.probs, info, window)
    scale = 1.0 / denominator if denominator > 0 else 0.0
    var_row = info.quantile * lookups.window_mass(index, window) * scale
    return var_row, _es_row(lookups, info, index)


def _weighted(weights: list[pl.Expr], lookups: list[pl.Expr]) -> pl.Expr:
    return pl.sum_horizontal([w * a for w, a in zip(weights, lookups, strict=True)])


def _sigma_expr(tables: ContributionTables, weights: list[pl.Expr], base: pl.Expr) -> pl.Expr:
    if tables.sigma == 0:
        return pl.lit(0.0, dtype=pl.Float64).alias(SIGMA_COLUMN)
    systematic = pl.sum_horizontal(
        [float(tables.systematic[k]) * weights[k] for k in range(len(weights))]
    )
    return (base / tables.sigma * (pl.col(BAND) + systematic)).alias(SIGMA_COLUMN)


def _measure_exprs(
    tables: ContributionTables, weights: list[pl.Expr], base: pl.Expr
) -> list[pl.Expr]:
    exprs: list[pl.Expr] = []
    for alpha in tables.alphas:
        var_terms = _weighted(weights, tables.lookups("var", alpha))
        es_terms = _weighted(weights, tables.lookups("es", alpha))
        exprs.append((base * var_terms).alias(var_column(alpha)))
        exprs.append((base * es_terms).alias(es_column(alpha)))
    return exprs


@dataclass(frozen=True, slots=True)
class ContributionPlanInputs:
    r"""Insumos do plano do passo D para uma partição.

    Parameters
    ----------
    obligor_table : Path
        Parquet do passo A da partição.
    tables : ContributionTables
        Tabelas $A$ e parâmetros de $\sigma$.
    banding : Banding
        Regra de banding.
    n_sectors : int
        Número ``K`` de setores sistêmicos.

    """

    obligor_table: Path
    tables: ContributionTables
    banding: Banding
    n_sectors: int


def contribution_plan(frame: pl.LazyFrame, inputs: ContributionPlanInputs) -> pl.LazyFrame:
    """Plano lazy das contribuições por operação de uma partição.

    Parameters
    ----------
    frame : pl.LazyFrame
        Partição da base normalizada (já validada).
    inputs : ContributionPlanInputs
        Tabela de devedores, tabelas $A$, banding e número de setores.

    Returns
    -------
    pl.LazyFrame
        Colunas ``operation_id``, ``obligor_id``, ``el``, ``rc_sigma``, ``rc_var_<a>``,
        ``rc_es_<a>`` (moeda).

    """
    planned = band_plan(frame, inputs.obligor_table, inputs.banding)
    weights = sector_weights(inputs.n_sectors)
    base = pl.col(PD) * pl.col(LGD) * pl.col(EAD)
    return planned.select(
        OPERATION_ID,
        OBLIGOR_ID,
        base.alias(EL_COLUMN),
        _sigma_expr(inputs.tables, weights, base),
        *_measure_exprs(inputs.tables, weights, base),
    )


def write_contributions(plan: pl.LazyFrame, destination: Path) -> None:
    """Grava o plano de contribuições em parquet (zstd) por streaming, sem materializar.

    Parameters
    ----------
    plan : pl.LazyFrame
        Plano de :func:`contribution_plan`.
    destination : Path
        Arquivo ``part-<p>.parquet``.

    """
    plan.sink_parquet(destination, compression="zstd", maintain_order=False)
`````

<!-- FILE: src/crplus/distribution/__init__.py -->
`````python
"""Motores da distribuição de perdas e registro por nome (``model.engine``)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Final

from crplus.distribution.fft import FFTEngine
from crplus.distribution.grid import GridDiagnostics, GridRequest, compute_distribution
from crplus.distribution.model import ComputedDistribution, LossDistributionEngine, SectorModel
from crplus.distribution.panjer import PanjerEngine

_ENGINES: Final[dict[str, Callable[[int, float], LossDistributionEngine]]] = {
    "fft": lambda workers, tol: FFTEngine(workers=workers, tol_clip=tol),
    "panjer": lambda workers, tol: PanjerEngine(workers=workers, tol_clip=tol),
}


def make_engine(name: str, workers: int, tol_clip: float) -> LossDistributionEngine:
    """Instancia o motor configurado.

    Parameters
    ----------
    name : {"fft", "panjer"}
        Nome do motor (``model.engine``).
    workers : int
        Threads do ``scipy.fft``.
    tol_clip : float
        Tolerância para negativos numéricos.

    Returns
    -------
    LossDistributionEngine
        Motor pronto para uso.

    """
    return _ENGINES[name](workers, tol_clip)


__all__ = [
    "ComputedDistribution",
    "FFTEngine",
    "GridDiagnostics",
    "GridRequest",
    "LossDistributionEngine",
    "PanjerEngine",
    "SectorModel",
    "compute_distribution",
    "make_engine",
]
`````

<!-- FILE: src/crplus/distribution/fft.py -->
`````python
r"""Motor principal: inversão da PGF por FFT.

Para cada setor, $T_k = \operatorname{rfft}(\lambda_k)$ e $t_k = T_k - \mu_k$ (a PGF avaliada
nas raízes da unidade). Acumula-se

$$\log\varphi = \sum_{\text{Poisson}} t_k
  \;+\; \sum_{\text{Gama}} -\tfrac{1}{v_k}\log(1 - v_k t_k)$$

setor a setor (memória $O(M)$) e $g = \operatorname{irfft}(e^{\log\varphi})$. O ramo principal
do logaritmo é contínuo porque $\operatorname{Re}(1 - v_k t_k) \ge 1$ (já que
$|T_k| \le \mu_k$). Os setores Poisson são somados antes, numa única FFT.

Notes
-----
Massa além da grade reaparece no início dela (*aliasing*); por isso a grade é verificada pela
massa de cauda e pelos momentos (:mod:`crplus.distribution.grid`).

"""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

import numpy as np
from numpy.typing import NDArray
from scipy import fft

from crplus.distribution.model import FloatArray, SectorModel, clip_negatives

ComplexArray = NDArray[np.complex128]


def log_one_minus(transform: ComplexArray, variance: float) -> ComplexArray:
    r"""Calcula $\log(1 - v\,t)$ **no próprio vetor** ``transform`` (sem cópias).

    Parameters
    ----------
    transform : ComplexArray
        $t_k$ nas frequências da grade; é sobrescrito.
    variance : float
        $v_k > 0$.

    Returns
    -------
    ComplexArray
        O mesmo vetor, agora com $\log(1 - v_k t_k)$.

    """
    transform *= -variance
    return cast(ComplexArray, np.log1p(transform, out=transform))


def gamma_log_term(transform: ComplexArray, variance: float) -> ComplexArray:
    r"""Termo $-\frac{1}{v}\log(1 - v\,t)$ de um setor Gama (sobrescreve ``transform``).

    Parameters
    ----------
    transform : ComplexArray
        $t_k$ nas frequências da grade.
    variance : float
        $v_k > 0$.

    Returns
    -------
    ComplexArray
        Contribuição do setor para $\log\varphi$.

    """
    term = log_one_minus(transform, variance)
    term *= -1.0 / variance
    return term


@dataclass(frozen=True, slots=True)
class FFTEngine:
    """Motor FFT (``scipy.fft``).

    Parameters
    ----------
    workers : int, default 1
        Threads do ``scipy.fft``.
    tol_clip : float, default 1e-13
        Tolerância para negativos numéricos (``numerics.tol_clip``).

    """

    workers: int = 1
    tol_clip: float = 1e-13

    def sector_transform(self, intensity: FloatArray, grid_size: int) -> ComplexArray:
        r"""$t(z) = \sum_\nu \lambda_\nu (z^\nu - 1)$ nas raízes da unidade de ordem ``grid_size``.

        Parameters
        ----------
        intensity : FloatArray
            $\lambda_\nu$ de um setor (ou soma de setores Poisson).
        grid_size : int
            Tamanho ``M`` da grade.

        Returns
        -------
        ComplexArray
            Vetor de comprimento ``M // 2 + 1``.

        """
        transform: ComplexArray = fft.rfft(intensity, n=grid_size, workers=self.workers)
        transform -= float(intensity.sum())
        return transform

    def invert(self, log_phi: ComplexArray, grid_size: int) -> FloatArray:
        r"""Inverte $e^{\log\varphi}$ para probabilidades (sobrescreve ``log_phi``)."""
        spectrum = np.exp(log_phi, out=log_phi)
        probs: FloatArray = fft.irfft(spectrum, n=grid_size, workers=self.workers)
        return clip_negatives(probs, self.tol_clip)

    def log_pgf(self, model: SectorModel, grid_size: int) -> ComplexArray:
        r"""Acumula $\log\varphi$ setor a setor (Poisson somados numa única FFT)."""
        log_phi = self.sector_transform(model.poisson_intensity(), grid_size)
        for k in model.gamma_sectors():
            transform = self.sector_transform(model.intensity[k], grid_size)
            log_phi += gamma_log_term(transform, float(model.variance[k]))
        return log_phi

    def compute(self, model: SectorModel, grid_size: int) -> FFTDistribution:
        """Calcula a distribuição de perdas na grade de tamanho ``grid_size``.

        Parameters
        ----------
        model : SectorModel
            Intensidades e variâncias setoriais.
        grid_size : int
            Tamanho ``M`` da grade (maior que a maior banda).

        Returns
        -------
        FFTDistribution
            Probabilidades e estado para as distribuições inclinadas.

        """
        model.require_grid(grid_size)
        with np.errstate(over="raise", invalid="raise"):
            log_phi = self.log_pgf(model, grid_size)
            probs = self.invert(log_phi.copy(), grid_size)
        return FFTDistribution(probs, log_phi, model, grid_size, self)


@dataclass(frozen=True, slots=True, eq=False)
class FFTDistribution:
    r"""Distribuição calculada pelo motor FFT.

    Parameters
    ----------
    probs : FloatArray
        $g_x$, $x = 0..M-1$.
    log_phi : ComplexArray
        $\log\varphi$ nas frequências da grade.
    model : SectorModel
        Modelo usado.
    grid_size : int
        Tamanho ``M`` da grade.
    engine : FFTEngine
        Motor que produziu a distribuição.

    """

    probs: FloatArray
    log_phi: ComplexArray
    model: SectorModel
    grid_size: int
    engine: FFTEngine

    def tilted(self, sector: int) -> FloatArray:
        r"""Distribuição inclinada $g^{(k)}$, com PGF $G(z)/(1 - v_k t_k(z))$.

        Parameters
        ----------
        sector : int
            Índice ``k`` do setor.

        Returns
        -------
        FloatArray
            $g^{(k)}$; igual a $g$ para setores Poisson.

        """
        if self.model.poisson_mask[sector]:
            return self.probs
        variance = float(self.model.variance[sector])
        transform = self.engine.sector_transform(self.model.intensity[sector], self.grid_size)
        with np.errstate(over="raise", invalid="raise"):
            spectrum = log_one_minus(transform, variance)
            np.subtract(self.log_phi, spectrum, out=spectrum)
            return self.engine.invert(spectrum, self.grid_size)
`````

<!-- FILE: src/crplus/distribution/grid.py -->
`````python
r"""Escolha da grade $M$ e verificações pós-cálculo (cauda e momentos).

$M_0 = \operatorname{next\_fast\_len}(\lceil EL_u + z\,\sigma_u \rceil + \nu_{max} + 1)$, limitado a
``max_grid``. Depois do cálculo, exige-se massa no último 1% da grade $<$ ``tol_tail`` e erros
relativos de média e variância $<$ ``tol_moment``; se falhar, a grade dobra até ``max_grid`` e,
esgotada, levanta :class:`~crplus.exceptions.GridTooSmallError`.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final

import numpy as np
from scipy import fft

from crplus.config import NumericsConfig
from crplus.distribution.model import (
    ComputedDistribution,
    FloatArray,
    LossDistributionEngine,
    SectorModel,
)
from crplus.exceptions import GridTooSmallError
from crplus.memory import GRID_FRACTION, MemoryBudget, grid_bytes
from crplus.moments import Moments

MIN_GRID_SIZE: Final = 16
TAIL_FRACTION: Final = 0.01


@dataclass(frozen=True, slots=True)
class GridDiagnostics:
    r"""Diagnósticos da grade usada.

    Parameters
    ----------
    grid_size : int
        Tamanho final ``M``.
    attempts : int
        Número de tamanhos de grade tentados.
    total_mass : float
        $\sum_x g_x$.
    tail_mass : float
        Massa no último 1% da grade.
    mean_error, variance_error : float
        Erros relativos de média e variância contra os momentos analíticos.

    """

    grid_size: int
    attempts: int
    total_mass: float
    tail_mass: float
    mean_error: float
    variance_error: float

    def within(self, numerics: NumericsConfig) -> bool:
        """Indica se todas as tolerâncias foram atendidas."""
        moments_ok = max(self.mean_error, self.variance_error) < numerics.tol_moment
        return self.tail_mass < numerics.tol_tail and moments_ok


def _fit(size: int, max_grid: int) -> int:
    if size > max_grid:
        raise GridTooSmallError(
            "A grade necessária excede numerics.max_grid; aumente model.loss_unit ou max_grid."
        )
    return min(int(fft.next_fast_len(max(size, MIN_GRID_SIZE), real=True)), max_grid)


def initial_grid_size(moments: Moments, max_band: int, numerics: NumericsConfig) -> int:
    r"""Tamanho inicial $M_0$ da grade.

    Parameters
    ----------
    moments : Moments
        Momentos analíticos em unidades de perda.
    max_band : int
        $\nu_{max}$.
    numerics : NumericsConfig
        ``z_tail`` e ``max_grid``.

    Returns
    -------
    int
        Tamanho "rápido" para FFT, limitado a ``max_grid``.

    """
    reach = math.ceil(moments.expected_loss + numerics.z_tail * moments.std_dev)
    return _fit(reach + max_band + 1, numerics.max_grid)


def _relative_error(value: float, reference: float) -> float:
    return abs(value - reference) / reference if reference > 0 else abs(value)


def diagnose(probs: FloatArray, moments: Moments, attempts: int) -> GridDiagnostics:
    """Mede massa total, massa de cauda e erros de momentos da distribuição.

    Parameters
    ----------
    probs : FloatArray
        Probabilidades $g_x$.
    moments : Moments
        Momentos analíticos.
    attempts : int
        Tentativas realizadas até aqui.

    Returns
    -------
    GridDiagnostics
        Diagnósticos.

    """
    size = probs.shape[0]
    losses = np.arange(size, dtype=np.float64)
    mean = float(losses @ probs)
    variance = float(((losses - mean) ** 2) @ probs)
    tail = float(probs[size - max(1, int(size * TAIL_FRACTION)) :].sum())
    return GridDiagnostics(
        size,
        attempts,
        float(probs.sum()),
        tail,
        _relative_error(mean, moments.expected_loss),
        _relative_error(variance, moments.variance),
    )


def _grow(size: int, max_grid: int) -> int:
    if size >= max_grid:
        raise GridTooSmallError(
            "A distribuição não converge dentro de numerics.max_grid (massa de cauda ou "
            "momentos fora da tolerância); aumente model.loss_unit ou max_grid."
        )
    return _fit(min(2 * size, max_grid), max_grid)


@dataclass(frozen=True, slots=True)
class GridRequest:
    """Entrada da busca de grade.

    Parameters
    ----------
    model : SectorModel
        Modelo setorial.
    moments : Moments
        Momentos analíticos.
    numerics : NumericsConfig
        Tolerâncias e limites.
    budget : MemoryBudget
        Orçamento de memória.

    """

    model: SectorModel
    moments: Moments
    numerics: NumericsConfig
    budget: MemoryBudget


def compute_distribution(
    engine: LossDistributionEngine, request: GridRequest
) -> tuple[ComputedDistribution, GridDiagnostics]:
    """Calcula a distribuição, dobrando a grade até atender às tolerâncias.

    Parameters
    ----------
    engine : LossDistributionEngine
        Motor configurado.
    request : GridRequest
        Modelo, momentos, tolerâncias e orçamento.

    Returns
    -------
    tuple
        Distribuição calculada e diagnósticos da grade.

    Raises
    ------
    GridTooSmallError
        Se nem ``max_grid`` atender às tolerâncias.
    MemoryBudgetError
        Se a grade não couber no orçamento (checado antes de alocar).

    """
    size = initial_grid_size(request.moments, request.model.max_band, request.numerics)
    attempts = 0
    while True:
        attempts += 1
        request.budget.require(grid_bytes(size), "a grade da distribuição", GRID_FRACTION)
        distribution = engine.compute(request.model, size)
        diagnostics = diagnose(distribution.probs, request.moments, attempts)
        if diagnostics.within(request.numerics):
            return distribution, diagnostics
        size = _grow(size, request.numerics.max_grid)
`````

<!-- FILE: src/crplus/distribution/model.py -->
`````python
r"""Modelo setorial de entrada dos motores e interfaces (``Protocol``) dos motores.

A PGF da perda em unidades é

$$G(z) = \exp\Big(\sum_{k:\,v_k=0} t_k(z)\Big) \prod_{k:\,v_k>0} (1 - v_k\,t_k(z))^{-1/v_k},
\qquad t_k(z) = \sum_\nu \lambda_{k,\nu}(z^\nu - 1).$$

A distribuição "inclinada" do setor $k$ tem PGF $G^{(k)}(z) = G(z)/(1 - v_k t_k(z))$ (e
$G^{(k)} = G$ para setores Poisson); ela é a base das contribuições de VaR/ES (Haaf e Tasche,
2002).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np
from numpy.typing import NDArray

from crplus.exceptions import GridTooSmallError, NumericalRangeError

FloatArray = NDArray[np.float64]

_MATRIX_NDIM = 2


@dataclass(frozen=True, slots=True, eq=False)
class SectorModel:
    r"""Intensidades por setor e banda e variâncias dos fatores.

    Parameters
    ----------
    intensity : FloatArray
        Matriz $(K+1)\times(B+1)$ com $\lambda_{k,\nu} \ge 0$; a coluna $\nu = 0$ deve ser zero.
    variance : FloatArray
        $v_k \ge 0$ para $k = 0..K$.

    Raises
    ------
    NumericalRangeError
        Se as formas forem incoerentes ou houver valores negativos, não finitos ou banda 0.

    """

    intensity: FloatArray
    variance: FloatArray

    def __post_init__(self) -> None:
        """Valida forma, sinal e finitude dos parâmetros."""
        rows = self.intensity.shape[0] if self.intensity.ndim == _MATRIX_NDIM else -1
        if self.variance.shape != (rows,):
            raise NumericalRangeError("Formas incoerentes entre intensidades e variâncias.")
        _require_non_negative(self.intensity, "intensidades")
        _require_non_negative(self.variance, "variâncias")
        if np.any(self.intensity[:, 0] != 0):
            raise NumericalRangeError("A banda 0 não pode ter intensidade.")

    @property
    def mean(self) -> FloatArray:
        r"""$\mu_k = \sum_\nu \lambda_{k,\nu}$."""
        return self.intensity.sum(axis=1)

    @property
    def max_band(self) -> int:
        """Maior banda representada ($B$)."""
        return int(self.intensity.shape[1]) - 1

    @property
    def poisson_mask(self) -> NDArray[np.bool_]:
        r"""Setores tratados como Poisson ($v_k = 0$ ou $\mu_k = 0$)."""
        mask: NDArray[np.bool_] = (self.variance == 0) | (self.mean == 0)
        return mask

    def poisson_intensity(self) -> FloatArray:
        """Intensidades somadas de todos os setores Poisson (uma única FFT/recursão)."""
        return self.intensity[self.poisson_mask].sum(axis=0)

    def gamma_sectors(self) -> tuple[int, ...]:
        r"""Índices dos setores com fator Gama ($v_k > 0$ e $\mu_k > 0$)."""
        return tuple(int(k) for k in np.flatnonzero(~self.poisson_mask))

    def require_grid(self, grid_size: int) -> None:
        """Exige uma grade maior que a maior banda.

        Raises
        ------
        GridTooSmallError
            Se ``grid_size <= max_band``.

        """
        if grid_size <= self.max_band:
            raise GridTooSmallError("A grade deve ser maior que a maior banda.")


def _require_non_negative(values: FloatArray, what: str) -> None:
    if not np.all(np.isfinite(values)) or np.any(values < 0):
        raise NumericalRangeError(f"As {what} devem ser finitas e não negativas.")


class ComputedDistribution(Protocol):
    """Distribuição calculada por um motor, com acesso às distribuições inclinadas."""

    @property
    def probs(self) -> FloatArray:
        """Probabilidades $g_x$, $x = 0..M-1$ (unidades de perda)."""
        ...  # pragma: no cover

    def tilted(self, sector: int) -> FloatArray:
        """Probabilidades $g^{(k)}_x$ da distribuição inclinada do setor ``sector``."""
        ...  # pragma: no cover


class LossDistributionEngine(Protocol):
    """Motor de cálculo da distribuição de perdas."""

    def compute(self, model: SectorModel, grid_size: int) -> ComputedDistribution:
        """Calcula a distribuição numa grade de tamanho ``grid_size``."""
        ...  # pragma: no cover


def clip_negatives(probs: FloatArray, tolerance: float) -> FloatArray:
    """Zera probabilidades negativas minúsculas (ruído numérico) e rejeita as relevantes.

    Parameters
    ----------
    probs : FloatArray
        Probabilidades calculadas.
    tolerance : float
        Módulo máximo de um negativo aceito como ruído (``numerics.tol_clip``).

    Returns
    -------
    FloatArray
        Probabilidades não negativas.

    Raises
    ------
    NumericalRangeError
        Se houver probabilidade menor que ``-tolerance``.

    """
    if np.any(probs < -tolerance):
        raise NumericalRangeError(
            "A distribuição calculada tem probabilidades negativas acima de numerics.tol_clip."
        )
    return np.maximum(probs, 0.0, out=probs)
`````

<!-- FILE: src/crplus/distribution/panjer.py -->
`````python
r"""Motor de referência: recursão de Panjer estável (Haaf, Reiß e Schoenmakers, 2004).

Cada setor Gama é uma binomial negativa composta e o grupo Poisson é uma Poisson composta;
ambas pertencem à classe $(a, b, 0)$ com todos os termos positivos, o que torna a recursão

$$g_x = \sum_{j=1}^{\min(x,\nu_{max})} \left(a + \frac{b\,j}{x}\right) h_j\, g_{x-j}$$

numericamente estável. Parâmetros, com severidade $h_\nu = \lambda_{k,\nu}/\mu_k$:

- Gama ($r = 1/v_k$): $q = v_k\mu_k/(1+v_k\mu_k)$, $a = q$, $b = (r-1)q$, $g_0 = (1-q)^r$;
- Poisson: $a = 0$, $b = \mu$, $g_0 = e^{-\mu}$.

As componentes são convoluídas por FFT com preenchimento a $2M$ (convolução linear exata nos
índices $< M$). Custo $O(M\cdot\nu_{max})$ por setor: indicado para carteiras pequenas/médias e
para validar o motor FFT.
"""

from __future__ import annotations

import importlib
import math
from collections.abc import Callable
from dataclasses import dataclass
from types import ModuleType
from typing import Final, cast

import numpy as np
from scipy import fft

from crplus.distribution.model import FloatArray, SectorModel, clip_negatives
from crplus.exceptions import NumericalRangeError


def _load_numba() -> ModuleType | None:
    try:
        return importlib.import_module("numba")
    except ImportError:  # pragma: no cover - numba é dependência de runtime
        return None


LOG_UNDERFLOW: Final = 0.95 * math.log(np.finfo(np.float64).tiny)
"""Menor $\\log g_0$ aceito antes de a recursão perder representação (underflow)."""

Kernel = Callable[[float, float, float, FloatArray, int], FloatArray]


def panjer_loops(a: float, b: float, g0: float, severity: FloatArray, size: int) -> FloatArray:
    r"""Recursão de Panjer em laços explícitos (compilada pelo numba).

    Parameters
    ----------
    a, b : float
        Parâmetros da classe $(a, b, 0)$.
    g0 : float
        Probabilidade de perda zero.
    severity : FloatArray
        $h_\nu$, $\nu = 0..B$, com $h_0 = 0$.
    size : int
        Tamanho ``M`` da grade.

    Returns
    -------
    FloatArray
        $g_x$, $x = 0..M-1$.

    """
    g = np.zeros(size)
    g[0] = g0
    top = severity.shape[0] - 1
    for x in range(1, size):
        acc = 0.0
        for j in range(1, min(x, top) + 1):
            acc += (a + b * j / x) * severity[j] * g[x - j]
        g[x] = acc
    return g


def panjer_numpy(a: float, b: float, g0: float, severity: FloatArray, size: int) -> FloatArray:
    """Recursão de Panjer com o somatório interno vetorizado (alternativa sem numba)."""
    g = np.zeros(size)
    g[0] = g0
    top = severity.shape[0] - 1
    for x in range(1, size):
        j = np.arange(1, min(x, top) + 1)
        g[x] = np.dot((a + b * j / x) * severity[j], g[x - j])
    return g


def select_kernel(module: ModuleType | None) -> Kernel:
    """Kernel compilado pelo numba quando disponível; caso contrário, a versão numpy."""
    if module is None:
        return panjer_numpy
    return cast(Kernel, module.njit(cache=True)(panjer_loops))


_KERNEL: Final = select_kernel(_load_numba())


@dataclass(frozen=True, slots=True)
class PanjerClass:
    r"""Parâmetros $(a, b)$ e $\log g_0$ de uma distribuição da classe $(a, b, 0)$."""

    a: float
    b: float
    log_g0: float

    @classmethod
    def poisson(cls, mean: float) -> PanjerClass:
        """Poisson composta de média de contagem ``mean``."""
        return cls(0.0, mean, -mean)

    @classmethod
    def negative_binomial(cls, mean: float, variance: float, shape: float) -> PanjerClass:
        r"""Binomial negativa de forma ``shape`` e $q = v\mu/(1+v\mu)$."""
        q = variance * mean / (1.0 + variance * mean)
        return cls(q, (shape - 1.0) * q, -shape * math.log1p(variance * mean))

    def compound(self, severity: FloatArray, size: int) -> FloatArray:
        """Distribuição composta na grade ``size``.

        Raises
        ------
        NumericalRangeError
            Se $g_0$ sofrer underflow (média de contagem grande demais para Panjer).

        """
        if self.log_g0 < LOG_UNDERFLOW:
            raise NumericalRangeError(
                "Underflow de g_0 na recursão de Panjer (setor com intensidade alta demais); "
                "use model.engine = 'fft'."
            )
        return _KERNEL(self.a, self.b, math.exp(self.log_g0), severity, size)


def _severity(intensity: FloatArray) -> FloatArray:
    severity: FloatArray = intensity / float(intensity.sum())
    return severity


@dataclass(frozen=True, slots=True)
class PanjerEngine:
    """Motor de Panjer estável.

    Parameters
    ----------
    workers : int, default 1
        Threads do ``scipy.fft`` (convolução entre setores).
    tol_clip : float, default 1e-13
        Tolerância para negativos numéricos da convolução.

    """

    workers: int = 1
    tol_clip: float = 1e-13

    def convolve(self, left: FloatArray, right: FloatArray, size: int) -> FloatArray:
        """Convolução linear truncada aos primeiros ``size`` pontos."""
        spectrum = fft.rfft(left, 2 * size, workers=self.workers)
        spectrum *= fft.rfft(right, 2 * size, workers=self.workers)
        full: FloatArray = fft.irfft(spectrum, 2 * size, workers=self.workers)
        return clip_negatives(full[:size].copy(), self.tol_clip)

    def components(self, model: SectorModel, size: int) -> list[FloatArray]:
        """Distribuições compostas do grupo Poisson e de cada setor Gama."""
        poisson = model.poisson_intensity()
        parts = [_unit(size)]
        if poisson.sum() > 0:
            parts.append(
                PanjerClass.poisson(float(poisson.sum())).compound(_severity(poisson), size)
            )
        return parts + [self._gamma(model, k, size, 0.0) for k in model.gamma_sectors()]

    def _gamma(self, model: SectorModel, sector: int, size: int, extra: float) -> FloatArray:
        variance = float(model.variance[sector])
        mean = float(model.mean[sector])
        family = PanjerClass.negative_binomial(mean, variance, 1.0 / variance + extra)
        return family.compound(_severity(model.intensity[sector]), size)

    def compute(self, model: SectorModel, grid_size: int) -> PanjerDistribution:
        """Calcula a distribuição de perdas na grade de tamanho ``grid_size``.

        Parameters
        ----------
        model : SectorModel
            Intensidades e variâncias setoriais.
        grid_size : int
            Tamanho ``M`` da grade.

        Returns
        -------
        PanjerDistribution
            Probabilidades e estado para as distribuições inclinadas.

        """
        model.require_grid(grid_size)
        probs = _unit(grid_size)
        for part in self.components(model, grid_size):
            probs = self.convolve(probs, part, grid_size)
        return PanjerDistribution(probs, model, grid_size, self)


def _unit(size: int) -> FloatArray:
    delta = np.zeros(size)
    delta[0] = 1.0
    return delta


@dataclass(frozen=True, slots=True, eq=False)
class PanjerDistribution:
    """Distribuição calculada pelo motor de Panjer.

    Parameters
    ----------
    probs : FloatArray
        $g_x$, $x = 0..M-1$.
    model : SectorModel
        Modelo usado.
    grid_size : int
        Tamanho ``M`` da grade.
    engine : PanjerEngine
        Motor que produziu a distribuição.

    """

    probs: FloatArray
    model: SectorModel
    grid_size: int
    engine: PanjerEngine

    def tilted(self, sector: int) -> FloatArray:
        r"""Distribuição inclinada $g^{(k)} = g \ast c_k$.

        $c_k$ tem PGF $(1 - v_k t_k)^{-1}$: binomial negativa composta de forma 1
        ($a = q$, $b = 0$, $g_0 = 1 - q$).
        """
        if self.model.poisson_mask[sector]:
            return self.probs
        mean = float(self.model.mean[sector])
        variance = float(self.model.variance[sector])
        factor = PanjerClass.negative_binomial(mean, variance, 1.0)
        extra = factor.compound(_severity(self.model.intensity[sector]), self.grid_size)
        return self.engine.convolve(self.probs, extra, self.grid_size)
`````

<!-- FILE: src/crplus/exceptions.py -->
`````python
"""Hierarquia de exceções do pacote ``crplus``.

Todas as exceções derivam de :class:`CRPlusError`, permitindo que o chamador capture qualquer
falha do pacote com um único ``except``. As mensagens nunca contêm valores de linhas nem
identificadores de operações ou devedores (ver ``docs/seguranca.md``).
"""

from __future__ import annotations


class CRPlusError(Exception):
    """Erro base de todas as falhas levantadas pelo ``crplus``."""


class ConfigError(CRPlusError):
    """Configuração inválida (tipo, faixa, chave desconhecida ou caminho inseguro).

    Parameters
    ----------
    field : str
        Nome qualificado do campo inválido, por exemplo ``"numerics.max_bands"``.
    message : str
        Descrição da restrição violada, sem repetir o valor recebido.

    """

    def __init__(self, field: str, message: str) -> None:
        """Guarda o campo inválido e monta a mensagem."""
        self.field = field
        super().__init__(f"Configuração inválida em '{field}': {message}")


class InputValidationError(CRPlusError):
    """Base de entrada inválida (colunas, tipos, domínios ou valores não finitos).

    Parameters
    ----------
    message : str
        Resumo das violações (somente contagens e posições, nunca valores ou ids).
    report : object or None, default None
        ``ValidationReport`` completo, quando disponível.

    """

    def __init__(self, message: str, report: object | None = None) -> None:
        """Guarda o relatório de validação junto da mensagem."""
        self.report = report
        super().__init__(message)


class GridTooSmallError(CRPlusError):
    """A grade da distribuição não comporta a cauda mesmo no tamanho máximo permitido."""


class NumericalRangeError(CRPlusError):
    """Um cálculo saiu da faixa numérica representável (underflow, overflow ou negativos)."""


class MemoryBudgetError(CRPlusError):
    """A memória estimada para uma etapa excede o orçamento configurado."""
`````

<!-- FILE: src/crplus/memory.py -->
`````python
"""Orçamento de memória: estimativas de consumo e checagens antes de alocar.

Todas as decisões de tamanho (partições de devedores, grade FFT, tabelas por banda) são
derivadas de ``resources.memory_budget_gb``. As estimativas são deliberadamente simples e
conservadoras; os coeficientes por elemento estão nas constantes deste módulo e serão
calibrados pelos benchmarks de pico de RSS (``docs/performance.md``).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

from crplus.exceptions import MemoryBudgetError

BYTES_PER_GB = 1024**3
FLOAT64_BYTES = 8
FFT_BYTES_PER_GRID_POINT = 64
"""Bytes por ponto da grade no pico (distribuição, log da PGF, distribuição inclinada e cauda)."""
OBLIGOR_BYTES_INT_ID = 192
"""Bytes por devedor no ``group_by`` do passo A (medido: ~155 B no polars 2.1, ver performance)."""
STRING_ID_OVERHEAD_BYTES = 24
"""Custo adicional por devedor quando o id é string (offsets, validade, hash)."""
OBLIGOR_TABLE_FRACTION = 0.4
"""Fração do orçamento reservada à tabela de devedores de uma partição."""
GRID_FRACTION = 0.6
"""Fração do orçamento reservada aos vetores de trabalho da distribuição."""
MAX_PARTITIONS = 65_536
"""Limite de segurança para o número de partições de devedores."""

IdKind = Literal["int", "str"]

_ID_EXTRA_BYTES: dict[str, Callable[[int], int]] = {
    "int": lambda _avg_len: 0,
    "str": lambda avg_len: avg_len + STRING_ID_OVERHEAD_BYTES,
}


@dataclass(frozen=True, slots=True)
class MemoryBudget:
    """Orçamento de memória do processo, em bytes.

    Parameters
    ----------
    total_bytes : int
        Total disponível para o processo inteiro (inclui o polars).

    """

    total_bytes: int

    def __post_init__(self) -> None:
        """Rejeita orçamentos não positivos."""
        if self.total_bytes <= 0:
            raise MemoryBudgetError("O orçamento de memória deve ser positivo.")

    @classmethod
    def from_gb(cls, gigabytes: float) -> MemoryBudget:
        """Cria o orçamento a partir de gigabytes (base 1024).

        Parameters
        ----------
        gigabytes : float
            Orçamento em GB.

        Returns
        -------
        MemoryBudget
            Orçamento equivalente em bytes.

        """
        return cls(int(gigabytes * BYTES_PER_GB))

    def share(self, fraction: float) -> int:
        """Devolve, em bytes, a parcela ``fraction`` do orçamento.

        Parameters
        ----------
        fraction : float
            Fração do orçamento, em ``(0, 1]``.

        Returns
        -------
        int
            Bytes disponíveis na parcela.

        """
        return int(self.total_bytes * fraction)

    def require(self, nbytes: int, what: str, fraction: float = 1.0) -> None:
        """Verifica, antes de alocar, se ``nbytes`` cabe na parcela do orçamento.

        Parameters
        ----------
        nbytes : int
            Memória estimada da etapa.
        what : str
            Descrição da etapa para a mensagem de erro.
        fraction : float, default 1.0
            Parcela do orçamento disponível para a etapa.

        Raises
        ------
        MemoryBudgetError
            Se a estimativa exceder a parcela disponível.

        """
        limit = self.share(fraction)
        if nbytes > limit:
            raise MemoryBudgetError(
                f"Memória estimada para {what} ({nbytes / BYTES_PER_GB:.2f} GB) excede o "
                f"limite disponível ({limit / BYTES_PER_GB:.2f} GB). Ajuste a configuração "
                "(partições, unidade de perda ou orçamento)."
            )


def _ceil_div(numerator: int, denominator: int) -> int:
    """Divisão inteira arredondada para cima, exata (sem ponto flutuante)."""
    return -(-numerator // denominator)


def grid_bytes(grid_size: int) -> int:
    r"""Estima a memória de pico do motor FFT para uma grade de tamanho ``M``.

    Parameters
    ----------
    grid_size : int
        Tamanho ``M`` da grade.

    Returns
    -------
    int
        Bytes estimados.

    Notes
    -----
    $\text{bytes} = 64 \cdot M$ (oito vetores ``float64`` equivalentes).

    """
    return grid_size * FFT_BYTES_PER_GRID_POINT


def obligor_table_bytes(n_obligors: int, id_kind: IdKind = "int", avg_id_len: int = 16) -> int:
    r"""Estima a memória da tabela de devedores do passo A.

    Parameters
    ----------
    n_obligors : int
        Número de devedores.
    id_kind : {"int", "str"}, default "int"
        Tipo do ``obligor_id``. Ids string custam mais; recomenda-se ids inteiros.
    avg_id_len : int, default 16
        Comprimento médio do id quando string.

    Returns
    -------
    int
        Bytes estimados.

    Notes
    -----
    $\text{bytes} = n \cdot (192 + c_{id})$, com $c_{id} = 0$ para inteiros e
    $c_{id} = \bar{\ell} + 24$ para strings.

    """
    return n_obligors * (OBLIGOR_BYTES_INT_ID + _ID_EXTRA_BYTES[id_kind](avg_id_len))


def band_table_bytes(n_sectors: int, max_bands: int, n_tables: int = 2) -> int:
    r"""Estima a memória de tabelas setor-banda (agregados setoriais ou tabela ``A``).

    Parameters
    ----------
    n_sectors : int
        Número ``K`` de setores sistêmicos (o idiossincrático é somado internamente).
    max_bands : int
        Maior banda $\nu_{max}$.
    n_tables : int, default 2
        Quantidade de tabelas ``float64`` de mesma forma.

    Returns
    -------
    int
        Bytes estimados.

    Notes
    -----
    $\text{bytes} = 8 \cdot n_{tab} \cdot (K + 1) \cdot (\nu_{max} + 1)$.

    """
    return FLOAT64_BYTES * n_tables * (n_sectors + 1) * (max_bands + 1)


def max_grid_within_budget(budget: MemoryBudget) -> int:
    """Maior tamanho de grade cujos vetores de trabalho cabem na parcela da distribuição.

    Parameters
    ----------
    budget : MemoryBudget
        Orçamento do processo.

    Returns
    -------
    int
        Tamanho máximo de grade.

    """
    return budget.share(GRID_FRACTION) // FFT_BYTES_PER_GRID_POINT


def auto_obligor_partitions(table_bytes: int, budget: MemoryBudget) -> int:
    r"""Menor número de partições cuja tabela de devedores cabe em 40% do orçamento.

    Parameters
    ----------
    table_bytes : int
        Memória estimada da tabela de devedores da base inteira.
    budget : MemoryBudget
        Orçamento do processo.

    Returns
    -------
    int
        Número de partições.

    Raises
    ------
    MemoryBudgetError
        Se seriam necessárias mais de ``MAX_PARTITIONS`` partições.

    Notes
    -----
    $P = \max(1, \lceil B_{tab} / (0{,}4 \cdot B) \rceil)$.

    """
    partitions = max(1, _ceil_div(table_bytes, budget.share(OBLIGOR_TABLE_FRACTION)))
    if partitions > MAX_PARTITIONS:
        raise MemoryBudgetError(
            f"Seriam necessárias mais de {MAX_PARTITIONS} partições de devedores para o "
            "orçamento de memória configurado."
        )
    return partitions


def check_partitions(partitions: int, table_bytes: int, budget: MemoryBudget) -> None:
    """Verifica se ``partitions`` partições mantêm a tabela de devedores dentro do orçamento.

    Parameters
    ----------
    partitions : int
        Número de partições escolhido pelo usuário.
    table_bytes : int
        Memória estimada da tabela de devedores da base inteira.
    budget : MemoryBudget
        Orçamento do processo.

    Raises
    ------
    MemoryBudgetError
        Se a tabela de uma partição exceder 40% do orçamento.

    """
    per_partition = _ceil_div(table_bytes, partitions)
    budget.require(per_partition, "a tabela de devedores de uma partição", OBLIGOR_TABLE_FRACTION)
`````

<!-- FILE: src/crplus/moments.py -->
`````python
r"""Momentos analíticos da perda (oráculo de validação da distribuição).

Em unidades de perda:

$$EL_k = \sum_\nu \nu\,\lambda_{k,\nu}, \qquad EL_u = \sum_k EL_k, \qquad
\operatorname{Var}_u = \sum_k \sum_\nu \nu^2 \lambda_{k,\nu} + \sum_{k \ge 1} v_k\,EL_k^2.$$

Em moeda, multiplica-se por $L_0$ (média e desvio) ou $L_0^2$ (variância).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


@dataclass(frozen=True, slots=True, eq=False)
class Moments:
    r"""Momentos da perda em unidades de perda.

    Parameters
    ----------
    expected_loss : float
        $EL_u$.
    variance : float
        $\operatorname{Var}_u$.
    sector_expected_loss : FloatArray
        $EL_k$ para $k = 0..K$.

    """

    expected_loss: float
    variance: float
    sector_expected_loss: FloatArray

    @property
    def std_dev(self) -> float:
        r"""$\sigma_u = \sqrt{\operatorname{Var}_u}$."""
        return math.sqrt(self.variance)


def analytic_moments(intensity: FloatArray, variance: FloatArray) -> Moments:
    r"""Calcula $EL_u$, $\operatorname{Var}_u$ e $EL_k$ a partir de $\lambda_{k,\nu}$ e $v_k$.

    Parameters
    ----------
    intensity : FloatArray
        Matriz $(K+1)\times(B+1)$ de intensidades por setor e banda.
    variance : FloatArray
        Variâncias $v_k$ dos fatores (com $v_0 = 0$).

    Returns
    -------
    Moments
        Momentos em unidades de perda.

    """
    bands = np.arange(intensity.shape[1], dtype=np.float64)
    sector_el = intensity @ bands
    poisson_part = float((intensity @ bands**2).sum())
    systematic_part = float((variance[1:] * sector_el[1:] ** 2).sum())
    return Moments(float(sector_el.sum()), poisson_part + systematic_part, sector_el)
`````

<!-- FILE: src/crplus/montecarlo.py -->
`````python
r"""Monte Carlo do CreditRisk+ — **somente para validação** dos motores analíticos.

Por cenário: $S_k \sim \text{Gama}(1/v_k, v_k)$ (setores Poisson: $S_k = 1$) e, para cada banda,
$N_\nu \sim \text{Poisson}\big(\sum_k \lambda_{k,\nu} S_k\big)$, com perda $L = \sum_\nu \nu N_\nu$.
Isso equivale em distribuição à simulação por devedor (soma de Poissons condicionalmente
independentes) e é muito mais barato. A variante por devedor (lenta) existe para validar essa
equivalência em carteiras pequenas.

A aleatoriedade usa exclusivamente ``np.random.Generator(PCG64(seed))``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final

import numpy as np
from numpy.typing import NDArray

from crplus.distribution.model import SectorModel
from crplus.risk_measures import risk_measures

FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int64]

DEFAULT_BATCH: Final = 20_000


@dataclass(frozen=True, slots=True)
class MonteCarloSettings:
    """Parâmetros da simulação.

    Parameters
    ----------
    n_scenarios : int
        Número de cenários.
    seed : int
        Semente do gerador PCG64.
    batch_size : int, default 20000
        Cenários por lote (limita a memória).

    """

    n_scenarios: int
    seed: int
    batch_size: int = DEFAULT_BATCH


def _factors(rng: np.random.Generator, variance: FloatArray, size: int) -> FloatArray:
    factors = np.ones((size, variance.shape[0]))
    for k in np.flatnonzero(variance > 0):
        factors[:, k] = rng.gamma(1.0 / variance[k], variance[k], size)
    return factors


def _batches(settings: MonteCarloSettings) -> list[int]:
    full, rest = divmod(settings.n_scenarios, settings.batch_size)
    return [settings.batch_size] * full + ([rest] if rest else [])


def simulate_losses(model: SectorModel, settings: MonteCarloSettings) -> IntArray:
    """Simula perdas em unidades de perda pelo esquema setor-banda.

    Parameters
    ----------
    model : SectorModel
        Intensidades e variâncias.
    settings : MonteCarloSettings
        Cenários, semente e lote.

    Returns
    -------
    IntArray
        Perda de cada cenário (unidades de perda).

    """
    rng = np.random.Generator(np.random.PCG64(settings.seed))
    bands = np.flatnonzero(model.intensity.sum(axis=0) > 0)
    intensity = model.intensity[:, bands]
    losses = [
        rng.poisson(_factors(rng, model.variance, size) @ intensity) @ bands
        for size in _batches(settings)
    ]
    return np.concatenate(losses).astype(np.int64)


@dataclass(frozen=True, slots=True, eq=False)
class ObligorPortfolio:
    r"""Carteira explícita por devedor (variante lenta de validação).

    Parameters
    ----------
    intensity : FloatArray
        Matriz (devedores por $(K+1)$ setores) com $\tilde p_{jk}$.
    bands : IntArray
        Banda $\nu_j$ de cada devedor.
    variance : FloatArray
        $v_k$ por setor.

    """

    intensity: FloatArray
    bands: IntArray
    variance: FloatArray


def simulate_obligor_losses(portfolio: ObligorPortfolio, settings: MonteCarloSettings) -> IntArray:
    r"""Simula perdas devedor a devedor: $N_j \sim \text{Poisson}(\sum_k \tilde p_{jk} S_k)$.

    Parameters
    ----------
    portfolio : ObligorPortfolio
        Carteira por devedor.
    settings : MonteCarloSettings
        Cenários, semente e lote.

    Returns
    -------
    IntArray
        Perda de cada cenário (unidades de perda).

    """
    rng = np.random.Generator(np.random.PCG64(settings.seed))
    losses = [
        rng.poisson(_factors(rng, portfolio.variance, size) @ portfolio.intensity.T)
        @ portfolio.bands
        for size in _batches(settings)
    ]
    return np.concatenate(losses).astype(np.int64)


@dataclass(frozen=True, slots=True)
class TailEstimate:
    """Estimativa de Monte Carlo com erro-padrão por médias de lotes.

    Parameters
    ----------
    var, es : float
        VaR e ES em moeda (amostra completa).
    var_se, es_se : float
        Erros-padrão (desvio entre lotes / raiz do número de lotes).

    """

    var: float
    es: float
    var_se: float
    es_se: float


def _empirical(losses: IntArray, alpha: float, loss_unit: float) -> tuple[float, float]:
    probs = np.bincount(losses).astype(np.float64) / losses.shape[0]
    measures = risk_measures(probs, [alpha], loss_unit, 0.0)
    return measures.var[alpha], measures.es[alpha]


def tail_estimate(
    losses: IntArray, alpha: float, loss_unit: float, n_batches: int = 20
) -> TailEstimate:
    """Estima VaR e ES empíricos e seus erros-padrão.

    Parameters
    ----------
    losses : IntArray
        Perdas simuladas (unidades de perda).
    alpha : float
        Nível de confiança.
    loss_unit : float
        $L_0$.
    n_batches : int, default 20
        Lotes para o erro-padrão.

    Returns
    -------
    TailEstimate
        Estimativas e erros-padrão.

    """
    var, es = _empirical(losses, alpha, loss_unit)
    pieces = np.array(
        [_empirical(part, alpha, loss_unit) for part in np.array_split(losses, n_batches)]
    )
    errors = pieces.std(axis=0, ddof=1) / math.sqrt(n_batches)
    return TailEstimate(var, es, float(errors[0]), float(errors[1]))
`````

<!-- FILE: src/crplus/obligor.py -->
`````python
r"""Passo A: tabela de devedores e estatísticas de exposição (por partição).

Para cada partição (hash de ``obligor_id``), agrega em streaming a exposição do devedor
$E_j = \sum_{i \in j} LGD_i \cdot EAD_i$, detecta inconsistências intra-devedor (PD, ``pd_vol``
ou pesos diferentes entre operações do mesmo devedor) e grava somente ``(obligor_id, E_j)`` em
parquet no diretório temporário. As estatísticas resultantes são somáveis entre partições.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from pathlib import Path
from typing import Final

import polars as pl

from crplus.schema import (
    EAD,
    HASH_SEED,
    LGD,
    OBLIGOR_EXPOSURE,
    OBLIGOR_ID,
    PD,
    PD_VOL,
    weight_columns,
)

CONSISTENCY_TOLERANCE: Final = 1e-12
"""Diferença máxima entre o maior e o menor valor de PD (ou ``pd_vol``) de um devedor."""

_EL: Final = "_el"
_N_OPS: Final = "_n_ops"
_PD_SPREAD: Final = "_pd_spread"
_VOL_SPREAD: Final = "_vol_spread"
_WEIGHTS_DIFFER: Final = "_weights_differ"


@dataclass(frozen=True, slots=True)
class ObligorStats:
    r"""Estatísticas do passo A, somáveis entre partições.

    Parameters
    ----------
    n_operations : int
        Operações processadas.
    n_obligors : int
        Devedores distintos.
    inconsistent_pd, inconsistent_pd_vol, inconsistent_weights : int
        Devedores cujas operações têm PD, ``pd_vol`` ou pesos diferentes.
    inconsistent_obligors : int
        Devedores com qualquer uma das inconsistências acima.
    max_exposure : float
        $\max_j E_j$.
    total_exposure : float
        $\sum_j E_j$.
    expected_loss : float
        $\sum_i p_i E_i$.
    poisson_variance : float
        $\sum_j E_j \sum_{i \in j} p_i E_i$ (variância sem efeito setorial, em moeda²).

    """

    n_operations: int = 0
    n_obligors: int = 0
    inconsistent_pd: int = 0
    inconsistent_pd_vol: int = 0
    inconsistent_weights: int = 0
    inconsistent_obligors: int = 0
    max_exposure: float = 0.0
    total_exposure: float = 0.0
    expected_loss: float = 0.0
    poisson_variance: float = 0.0

    def __add__(self, other: ObligorStats) -> ObligorStats:
        """Combina as estatísticas de duas partições disjuntas."""
        merged = {
            item.name: getattr(self, item.name) + getattr(other, item.name) for item in fields(self)
        }
        merged["max_exposure"] = max(self.max_exposure, other.max_exposure)
        return ObligorStats(**merged)


def _weights_differ(n_sectors: int) -> pl.Expr:
    if n_sectors == 0:
        return pl.lit(value=False).alias(_WEIGHTS_DIFFER)
    digest = pl.struct(weight_columns(n_sectors)).hash(seed=HASH_SEED)
    return (digest.max() != digest.min()).alias(_WEIGHTS_DIFFER)


def _spread(column: str, alias: str) -> pl.Expr:
    return (pl.col(column).max() - pl.col(column).min()).alias(alias)


def obligor_aggregation(frame: pl.LazyFrame, n_sectors: int) -> pl.LazyFrame:
    """Plano do ``group_by(obligor_id)`` do passo A.

    Parameters
    ----------
    frame : pl.LazyFrame
        Partição da base normalizada.
    n_sectors : int
        Número ``K`` de setores sistêmicos.

    Returns
    -------
    pl.LazyFrame
        Uma linha por devedor com exposição, perda esperada e indicadores de consistência.

    """
    exposure = pl.col(LGD) * pl.col(EAD)
    return frame.group_by(OBLIGOR_ID).agg(
        exposure.sum().alias(OBLIGOR_EXPOSURE),
        (exposure * pl.col(PD)).sum().alias(_EL),
        pl.len().alias(_N_OPS),
        _spread(PD, _PD_SPREAD),
        _spread(PD_VOL, _VOL_SPREAD),
        _weights_differ(n_sectors),
    )


def _aliased(expressions: list[pl.Expr]) -> list[pl.Expr]:
    return [expr.alias(f"_s{i}") for i, expr in enumerate(expressions)]


def _as_int(value: object) -> int:
    return 0 if value is None else int(value)  # type: ignore[call-overload]


def _as_float(value: object) -> float:
    return 0.0 if value is None else float(value)  # type: ignore[arg-type]


def _stats(table: pl.DataFrame) -> ObligorStats:
    pd_bad = pl.col(_PD_SPREAD) > CONSISTENCY_TOLERANCE
    vol_bad = pl.col(_VOL_SPREAD) > CONSISTENCY_TOLERANCE
    weights_bad = pl.col(_WEIGHTS_DIFFER)
    aggregates = [
        pl.col(_N_OPS).sum(),
        pl.len(),
        pd_bad.sum(),
        vol_bad.sum(),
        weights_bad.sum(),
        (pd_bad | vol_bad | weights_bad).sum(),
        pl.col(OBLIGOR_EXPOSURE).max(),
        pl.col(OBLIGOR_EXPOSURE).sum(),
        pl.col(_EL).sum(),
        (pl.col(_EL) * pl.col(OBLIGOR_EXPOSURE)).sum(),
    ]
    row = table.select(_aliased(aggregates)).row(0)
    n_ops, n_obl, bad_pd, bad_vol, bad_w, bad_any = map(_as_int, row[:6])
    max_e, total_e, el, poisson = map(_as_float, row[6:])
    return ObligorStats(
        n_operations=n_ops,
        n_obligors=n_obl,
        inconsistent_pd=bad_pd,
        inconsistent_pd_vol=bad_vol,
        inconsistent_weights=bad_w,
        inconsistent_obligors=bad_any,
        max_exposure=max_e,
        total_exposure=total_e,
        expected_loss=el,
        poisson_variance=poisson,
    )


def build_obligor_table(frame: pl.LazyFrame, n_sectors: int, destination: Path) -> ObligorStats:
    """Executa o passo A numa partição e grava ``(obligor_id, E_j)`` em parquet.

    Parameters
    ----------
    frame : pl.LazyFrame
        Partição da base normalizada.
    n_sectors : int
        Número ``K`` de setores sistêmicos.
    destination : Path
        Arquivo parquet de saída (no diretório temporário).

    Returns
    -------
    ObligorStats
        Estatísticas da partição.

    """
    table = obligor_aggregation(frame, n_sectors).collect(engine="streaming")
    table.select(OBLIGOR_ID, OBLIGOR_EXPOSURE).write_parquet(destination)
    return _stats(table)
`````

<!-- FILE: src/crplus/paths.py -->
`````python
"""Resolução segura de caminhos de arquivo (proteção contra *path traversal*).

Todo caminho vindo da configuração (arquivo de variâncias externas, diretório de saída) é
resolvido relativamente a um diretório base e rejeitado se escapar dele ou atravessar links
simbólicos.
"""

from __future__ import annotations

import os
from pathlib import Path

from crplus.exceptions import ConfigError


def resolve_within(base: Path, candidate: Path, field: str) -> Path:
    """Resolve ``candidate`` dentro de ``base``, rejeitando fugas e links simbólicos.

    Parameters
    ----------
    base : Path
        Diretório base existente. Caminhos relativos são interpretados a partir dele.
    candidate : Path
        Caminho relativo ou absoluto a validar; não precisa existir.
    field : str
        Nome do campo de configuração, usado na mensagem de erro.

    Returns
    -------
    Path
        Caminho absoluto e resolvido, garantidamente dentro de ``base``.

    Raises
    ------
    ConfigError
        Se o caminho sair de ``base`` ou algum componente abaixo de ``base`` for link simbólico.

    """
    root = base.resolve(strict=True)
    joined = Path(os.path.normpath(root / candidate))
    _require_inside(root, joined, field)
    _reject_symlinks(root, joined, field)
    resolved = joined.resolve()
    _require_inside(root, resolved, field)
    return resolved


def _require_inside(root: Path, path: Path, field: str) -> None:
    if not path.is_relative_to(root):
        raise ConfigError(field, "o caminho deve ficar dentro do diretório base")


def _reject_symlinks(root: Path, path: Path, field: str) -> None:
    current = root
    for part in path.relative_to(root).parts:
        current = current / part
        if current.is_symlink():
            raise ConfigError(field, "links simbólicos não são aceitos no caminho")
`````

<!-- FILE: src/crplus/py.typed -->
`````
`````

<!-- FILE: src/crplus/results.py -->
`````python
"""Resultado da execução, tabela de setores, diagnósticos e escrita das saídas.

Saídas gravadas em ``output.directory``:

- ``summary.json``: medidas, ``L0``, ``M``, setores, diagnósticos, versão e SHA-256 do TOML;
- ``loss_distribution.parquet``: ``(loss, prob, cdf)``, truncada onde a cauda < ``tol_tail``;
- ``contributions/part-<p>.parquet``: contribuições por operação (passo D).

Nenhuma saída contém ids ou valores individuais além do parquet de contribuições, que é o
produto pedido pelo usuário.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Final, cast

import numpy as np
import polars as pl
from numpy.typing import NDArray

from crplus.contributions import alpha_label
from crplus.distribution.grid import GridDiagnostics
from crplus.moments import Moments
from crplus.risk_measures import loss_tail
from crplus.sectors import SectorParameters
from crplus.validation import ValidationReport

FloatArray = NDArray[np.float64]

SUMMARY_FILE: Final = "summary.json"
DISTRIBUTION_FILE: Final = "loss_distribution.parquet"

_logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, eq=False)
class LossDistribution:
    """Distribuição de perdas em unidades de perda.

    Parameters
    ----------
    probs : FloatArray
        $g_x$ para $x = $ ``offset`` .. ``offset + len(probs) - 1`` (truncada na cauda).
    loss_unit : float
        $L_0$ (perda em moeda $= x L_0$).
    offset : int, default 0
        Primeira perda representada, em unidades.

    """

    probs: FloatArray
    loss_unit: float
    offset: int = 0

    def frame(self) -> pl.DataFrame:
        """Tabela ``(loss, prob, cdf)`` com a perda em moeda."""
        losses = (np.arange(self.probs.shape[0]) + self.offset) * self.loss_unit
        return pl.DataFrame({"loss": losses, "prob": self.probs, "cdf": np.cumsum(self.probs)})


def truncated_distribution(
    probs: FloatArray, loss_unit: float, tol_tail: float
) -> LossDistribution:
    """Trunca a distribuição no primeiro ponto em que a cauda fica abaixo de ``tol_tail``.

    Parameters
    ----------
    probs : FloatArray
        Probabilidades na grade completa.
    loss_unit : float
        $L_0$.
    tol_tail : float
        Massa de cauda desprezada.

    Returns
    -------
    LossDistribution
        Distribuição truncada.

    """
    below = np.flatnonzero(loss_tail(probs) < tol_tail)
    end = int(below[0]) + 1 if below.size else probs.shape[0]
    return LossDistribution(probs[:end].copy(), loss_unit)


@dataclass(frozen=True, slots=True)
class Diagnostics:
    r"""Diagnósticos da execução (somente agregados).

    Parameters
    ----------
    loss_unit : float
        $L_0$ usado.
    max_band : int
        $\nu_{max}$.
    grid : GridDiagnostics
        Grade final e checagens de cauda e momentos.
    banding_error : float
        Erro relativo da perda esperada após o banding.
    partitions : int
        Partições de devedores.
    n_operations, n_obligors, inconsistent_obligors : int
        Contagens do passo A.
    validation : ValidationReport
        Relatório de validação da base.
    euler_errors : Mapping[str, float]
        Erro relativo das somas de Euler lidas do parquet de contribuições.
    timings : Mapping[str, float]
        Tempo (s) de cada etapa.
    memory_estimates : Mapping[str, int]
        Estimativas de memória (bytes) das estruturas principais.
    alerts : tuple of str
        Alertas para o usuário (vazio quando tudo está dentro das tolerâncias).

    """

    loss_unit: float
    max_band: int
    grid: GridDiagnostics
    banding_error: float
    partitions: int
    n_operations: int
    n_obligors: int
    inconsistent_obligors: int
    validation: ValidationReport
    euler_errors: Mapping[str, float] = field(default_factory=dict)
    timings: Mapping[str, float] = field(default_factory=dict)
    memory_estimates: Mapping[str, int] = field(default_factory=dict)
    alerts: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True, eq=False)
class CRPlusResult:
    """Resultado de :func:`crplus.run_creditrisk_plus` (valores em moeda do EAD).

    Parameters
    ----------
    el : float
        Perda esperada.
    ul : float
        Perda inesperada (desvio-padrão).
    var, es, ec, es_minus_el : Mapping[float, float]
        VaR, Expected Shortfall, capital econômico (VaR - EL) e ES - EL por nível.
    loss_distribution : LossDistribution
        Distribuição de perdas (truncada onde a cauda < ``tol_tail``).
    sectors : pl.DataFrame
        Parâmetros e contribuições por setor.
    contributions_path : Path or None
        Diretório do parquet de contribuições por operação (``None`` se desligado).
    summary_path : Path
        Caminho do ``summary.json``.
    diagnostics : Diagnostics
        Diagnósticos da execução.

    """

    el: float
    ul: float
    var: Mapping[float, float]
    es: Mapping[float, float]
    ec: Mapping[float, float]
    es_minus_el: Mapping[float, float]
    loss_distribution: LossDistribution
    sectors: pl.DataFrame
    contributions_path: Path | None
    summary_path: Path
    diagnostics: Diagnostics


def sector_table(params: SectorParameters, moments: Moments, loss_unit: float) -> pl.DataFrame:
    r"""Tabela de setores para ``result.sectors``.

    Colunas: ``sector``, ``mu_k``, ``s_k``, ``v_k_pd_vol``, ``v_k_used``, ``el_k`` (moeda) e
    ``variance_k`` $= v_k\,EL_k^2 L_0^2$ (contribuição sistêmica do setor à variância, moeda²).

    Parameters
    ----------
    params : SectorParameters
        Parâmetros setoriais.
    moments : Moments
        Momentos analíticos (unidades de perda).
    loss_unit : float
        $L_0$.

    Returns
    -------
    pl.DataFrame
        Uma linha por setor (o idiossincrático primeiro).

    """
    el_units = moments.sector_expected_loss
    return pl.DataFrame(
        {
            "sector": list(params.names),
            "mu_k": params.mean,
            "s_k": params.volatility,
            "v_k_pd_vol": params.variance_pd_vol,
            "v_k_used": params.variance,
            "el_k": el_units * loss_unit,
            "variance_k": params.variance * (el_units * loss_unit) ** 2,
        }
    )


def _by_alpha(values: Mapping[float, float]) -> dict[str, float]:
    return {alpha_label(alpha): value for alpha, value in values.items()}


def _jsonable(value: Mapping[str, object]) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(json.dumps(value, default=str)))


def summary_document(
    result: CRPlusResult, version: str, config_sha256: str | None
) -> dict[str, Any]:
    """Documento do ``summary.json`` (somente agregados).

    Parameters
    ----------
    result : CRPlusResult
        Resultado da execução.
    version : str
        Versão do pacote.
    config_sha256 : str or None
        Hash do TOML usado.

    Returns
    -------
    dict
        Estrutura serializável em JSON.

    """
    return {
        "crplus_version": version,
        "config_sha256": config_sha256,
        "el": result.el,
        "ul": result.ul,
        "var": _by_alpha(result.var),
        "es": _by_alpha(result.es),
        "ec": _by_alpha(result.ec),
        "es_minus_el": _by_alpha(result.es_minus_el),
        "loss_unit": result.diagnostics.loss_unit,
        "grid_size": result.diagnostics.grid.grid_size,
        "sectors": result.sectors.to_dicts(),
        "diagnostics": _jsonable(asdict(result.diagnostics)),
    }


def write_summary(document: Mapping[str, Any], path: Path) -> None:
    """Grava o ``summary.json`` (UTF-8, indentado)."""
    path.write_text(json.dumps(document, indent=2, ensure_ascii=False), encoding="utf-8")
    _logger.info("Resumo gravado em %s.", path.name)


def write_distribution(distribution: LossDistribution, path: Path) -> None:
    """Grava a distribuição de perdas em parquet (zstd)."""
    distribution.frame().write_parquet(path, compression="zstd")
    _logger.info("Distribuição de perdas gravada (%d pontos).", distribution.probs.shape[0])
`````

<!-- FILE: src/crplus/risk_measures.py -->
`````python
r"""Medidas de risco sobre a distribuição discreta de perdas.

Com $F(x) = \sum_{y \le x} g_y$ e, para cada $\alpha$, $q = \min\{x : F(x) \ge \alpha\}$:

- $\mathrm{VaR}_\alpha = q\,L_0$;
- $\mathrm{ES}_\alpha = \frac{L_0}{1-\alpha}\Big[\sum_{x>q} x\,g_x + q\,(F(q) - \alpha)\Big]$
  (Acerbi e Tasche, 2002: coerente em distribuições discretas);
- $\mathrm{EC}_\alpha = \mathrm{VaR}_\alpha - EL$ e $\mathrm{ES}_\alpha - EL$.

As caudas são calculadas por **soma acumulada reversa** ($\bar F(x) = \sum_{y>x} g_y$), e não
por $1 - F$, para não perder precisão perto de 1. Usa-se $F(q) - \alpha = (1-\alpha) - \bar F(q)$.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import Final

import numpy as np
from numpy.typing import NDArray

from crplus.exceptions import GridTooSmallError

FloatArray = NDArray[np.float64]

QUANTILE_TOLERANCE: Final = 1e-14
r"""Folga absoluta em $\bar F(x) \le 1 - \alpha$ (empates no nível do ruído numérico)."""


def tail_above(probs: FloatArray) -> FloatArray:
    r"""$\bar F(x) = \sum_{y > x} g_y$ por soma acumulada reversa.

    Parameters
    ----------
    probs : FloatArray
        Probabilidades $g_x$ (ou qualquer vetor não negativo, como $x\,g_x$).

    Returns
    -------
    FloatArray
        Cauda estrita em cada ponto da grade (o último valor é 0).

    """
    tail = np.zeros_like(probs)
    np.cumsum(probs[:0:-1], out=tail[-2::-1])
    return tail


def loss_tail(probs: FloatArray) -> FloatArray:
    r"""Cauda $P(L > x)$ incluindo a massa que não coube na grade, $1 - \sum_x g_x$.

    Parameters
    ----------
    probs : FloatArray
        Probabilidades $g_x$.

    Returns
    -------
    FloatArray
        $\bar F(x) + \max(0, 1 - \sum_y g_y)$.

    """
    return tail_above(probs) + max(0.0, 1.0 - float(probs.sum()))


@dataclass(frozen=True, slots=True)
class QuantileInfo:
    r"""Quantil discreto de um nível $\alpha$.

    Parameters
    ----------
    alpha : float
        Nível de confiança.
    quantile : int
        $q$ em unidades de perda.
    excess : float
        $F(q) - \alpha \ge 0$.
    probability : float
        $g_q > 0$.

    """

    alpha: float
    quantile: int
    excess: float
    probability: float

    @property
    def beta(self) -> float:
        r"""$\beta = (F(q) - \alpha)/g_q$, peso do átomo em $q$ no ES."""
        return self.excess / self.probability


def quantile(probs: FloatArray, tail: FloatArray, alpha: float) -> QuantileInfo:
    r"""Quantil $q = \min\{x : F(x) \ge \alpha\} = \min\{x : \bar F(x) \le 1 - \alpha\}$.

    Parameters
    ----------
    probs : FloatArray
        Probabilidades $g_x$.
    tail : FloatArray
        $P(L > x)$ de :func:`loss_tail`.
    alpha : float
        Nível de confiança.

    Returns
    -------
    QuantileInfo
        Quantil e grandezas auxiliares.

    Raises
    ------
    GridTooSmallError
        Se a grade não alcança o nível $\alpha$.

    """
    reached = tail <= (1.0 - alpha) + QUANTILE_TOLERANCE
    if not reached.any():
        raise GridTooSmallError("A grade não alcança o nível de confiança solicitado.")
    q = int(np.argmax(reached))
    excess = max(0.0, (1.0 - alpha) - float(tail[q]))
    return QuantileInfo(alpha, q, excess, float(probs[q]))


@dataclass(frozen=True, slots=True)
class RiskMeasures:
    """Medidas de risco em moeda, indexadas por nível de confiança.

    Parameters
    ----------
    var, es, ec, es_minus_el : Mapping[float, float]
        VaR, Expected Shortfall, capital econômico (VaR - EL) e ES - EL.
    quantiles : Mapping[float, QuantileInfo]
        Quantis discretos (usados nas contribuições).

    """

    var: Mapping[float, float]
    es: Mapping[float, float]
    ec: Mapping[float, float]
    es_minus_el: Mapping[float, float]
    quantiles: Mapping[float, QuantileInfo]


def _expected_shortfall(weighted_tail: FloatArray, info: QuantileInfo) -> float:
    beyond = float(weighted_tail[info.quantile])
    return (beyond + info.quantile * info.excess) / (1.0 - info.alpha)


def risk_measures(
    probs: FloatArray, alphas: Sequence[float], loss_unit: float, expected_loss: float
) -> RiskMeasures:
    """Calcula VaR, ES e capital econômico para cada nível de confiança.

    Parameters
    ----------
    probs : FloatArray
        Probabilidades $g_x$ em unidades de perda.
    alphas : Sequence[float]
        Níveis de confiança.
    loss_unit : float
        $L_0$ (conversão para moeda).
    expected_loss : float
        Perda esperada em moeda.

    Returns
    -------
    RiskMeasures
        Medidas por nível.

    """
    tail = loss_tail(probs)
    weighted_tail = tail_above(np.arange(probs.shape[0], dtype=np.float64) * probs)
    infos = {alpha: quantile(probs, tail, alpha) for alpha in alphas}
    var = _frozen({a: info.quantile * loss_unit for a, info in infos.items()})
    es = _frozen({a: loss_unit * _expected_shortfall(weighted_tail, i) for a, i in infos.items()})
    return RiskMeasures(
        var,
        es,
        _shifted(var, -expected_loss),
        _shifted(es, -expected_loss),
        MappingProxyType(infos),
    )


def _frozen(values: dict[float, float]) -> Mapping[float, float]:
    return MappingProxyType(values)


def _shifted(values: Mapping[float, float], shift: float) -> Mapping[float, float]:
    return MappingProxyType({alpha: value + shift for alpha, value in values.items()})
`````

<!-- FILE: src/crplus/schema.py -->
`````python
"""Nomes canônicos das colunas internas da engine.

Depois da normalização (:mod:`crplus.sources`), as colunas obrigatórias passam a ter os nomes
canônicos abaixo, independentemente dos nomes configurados em ``[columns]``, e as colunas de
peso setorial passam a se chamar ``_w1 .. _wK`` (na ordem alfabética dos nomes originais).
"""

from __future__ import annotations

from typing import Final

import polars as pl

OPERATION_ID: Final = "operation_id"
OBLIGOR_ID: Final = "obligor_id"
PD: Final = "pd"
PD_VOL: Final = "pd_vol"
LGD: Final = "lgd"
EAD: Final = "ead"

CANONICAL_COLUMNS: Final = (OPERATION_ID, OBLIGOR_ID, PD, PD_VOL, LGD, EAD)
ID_COLUMNS: Final = (OPERATION_ID, OBLIGOR_ID)
FLOAT_COLUMNS: Final = (PD, PD_VOL, LGD, EAD)

OBLIGOR_EXPOSURE: Final = "obligor_exposure"
"""Exposição do devedor $E_j$ (tabela do passo A)."""
BAND: Final = "nu"
"""Banda do devedor $\\nu_j$."""

HASH_SEED: Final = 20_240_517
"""Semente fixa do hash de particionamento (determinístico dentro do processo)."""


def weight_column(sector: int) -> str:
    """Nome interno da coluna de peso do setor ``sector`` (1..K).

    Parameters
    ----------
    sector : int
        Índice do setor sistêmico, a partir de 1.

    Returns
    -------
    str
        Nome interno, por exemplo ``"_w3"``.

    """
    return f"_w{sector}"


def weight_columns(n_sectors: int) -> tuple[str, ...]:
    """Nomes internos das colunas de peso dos setores ``1..n_sectors``.

    Parameters
    ----------
    n_sectors : int
        Número ``K`` de setores sistêmicos.

    Returns
    -------
    tuple of str
        Nomes internos em ordem.

    """
    return tuple(weight_column(k) for k in range(1, n_sectors + 1))


def partition_predicate(column: str, partition: int, partitions: int) -> pl.Expr:
    r"""Expressão que seleciona as linhas da partição ``partition`` por hash de ``column``.

    Parameters
    ----------
    column : str
        Coluna de particionamento (``obligor_id`` ou ``operation_id``).
    partition : int
        Índice da partição, em ``[0, partitions)``.
    partitions : int
        Número total de partições.

    Returns
    -------
    pl.Expr
        Predicado booleano; com uma única partição, sempre verdadeiro.

    Notes
    -----
    $\operatorname{hash}(id) \bmod P = p$: todas as linhas com o mesmo id caem na mesma
    partição, e as partições cobrem a base sem sobreposição.

    """
    if partitions == 1:
        return pl.lit(value=True)
    return (pl.col(column).hash(seed=HASH_SEED) % partitions) == partition
`````

<!-- FILE: src/crplus/sectors.py -->
`````python
r"""Parâmetros setoriais: médias $\mu_k$, volatilidades $s_k$ e variâncias $v_k$ dos fatores.

Dois métodos (``sector_variance.method``):

- ``pd_vol`` (CSFB): $v_k = (s_k/\mu_k)^2$, com $s_k$ e $\mu_k$ ajustados pelo banding
  (``adjust_for_banding = true``) ou brutos, $s_k = \sum_i w_{ik}\sigma_i$ e
  $\mu_k = \sum_i w_{ik} p_i$.
- ``external``: $v_k$ (ou $cv_k = \sqrt{v_k}$) informado pelo usuário.

O setor idiossincrático ($k = 0$) tem sempre $v_0 = 0$; setores com $\mu_k = 0$ são ignorados
($v_k = 0$); setores com $v_k = 0$ são tratados como Poisson. Os fatores são
$S_k \sim \text{Gama}(1/v_k, v_k)$, independentes.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Final

import numpy as np
import polars as pl
from numpy.typing import NDArray

from crplus.aggregation import SectorBandAggregate
from crplus.config import SectorVarianceConfig
from crplus.exceptions import ConfigError

FloatArray = NDArray[np.float64]

IDIOSYNCRATIC: Final = "idiossincratico"
"""Nome do setor 0 nas saídas."""

_FIELD: Final = "sector_variance.values"
_FILE_FIELD: Final = "sector_variance.values_file"
_READERS: Final[dict[str, Callable[[Path], pl.DataFrame]]] = {
    ".csv": pl.read_csv,
    ".parquet": pl.read_parquet,
}


@dataclass(frozen=True, slots=True, eq=False)
class SectorParameters:
    r"""Parâmetros por setor ($k = 0..K$; o índice 0 é o idiossincrático).

    Parameters
    ----------
    names : tuple of str
        Nome de cada setor (``idiossincratico`` e os nomes originais das colunas de peso).
    mean : FloatArray
        $\mu_k = \sum_\nu \lambda_{k,\nu}$.
    volatility : FloatArray
        $s_k$ usado na variância implícita pela ``pd_vol``.
    variance_pd_vol : FloatArray
        $v_k$ implícito pela ``pd_vol`` (sempre calculado, para comparação).
    variance : FloatArray
        $v_k$ efetivamente usado.

    """

    names: tuple[str, ...]
    mean: FloatArray
    volatility: FloatArray
    variance_pd_vol: FloatArray
    variance: FloatArray


def _banded(aggregate: SectorBandAggregate) -> tuple[FloatArray, FloatArray]:
    return aggregate.volatility, aggregate.intensity.sum(axis=1)


def _raw(aggregate: SectorBandAggregate) -> tuple[FloatArray, FloatArray]:
    return aggregate.raw_volatility, aggregate.raw_intensity


_VOLATILITY_SOURCES: Final = {True: _banded, False: _raw}


def implied_variance(aggregate: SectorBandAggregate, adjust_for_banding: bool) -> FloatArray:
    r"""Variância $v_k = (s_k/\mu_k)^2$ implícita pela volatilidade das PDs.

    Parameters
    ----------
    aggregate : SectorBandAggregate
        Agregados do passo B.
    adjust_for_banding : bool
        Usa $s_k$ e $\mu_k$ com o ajuste de banding (padrão) ou as somas brutas.

    Returns
    -------
    FloatArray
        $v_k$ para $k = 0..K$, com $v_0 = 0$ e $v_k = 0$ quando $\mu_k = 0$.

    """
    volatility, mean = _VOLATILITY_SOURCES[adjust_for_banding](aggregate)
    variance = np.zeros_like(mean)
    np.divide(volatility**2, mean**2, out=variance, where=mean > 0)
    variance[0] = 0.0
    return variance


def _check_names(values: Mapping[str, float], sectors: tuple[str, ...]) -> None:
    missing = sorted(set(sectors) - set(values))
    extra = sorted(set(values) - set(sectors))
    if missing:
        raise ConfigError(_FIELD, f"setores da base sem variância: {', '.join(missing)}")
    if extra:
        raise ConfigError(_FIELD, f"setores inexistentes na base: {', '.join(extra)}")


def _check_values(values: Mapping[str, float]) -> None:
    if not all(math.isfinite(value) and value >= 0 for value in values.values()):
        raise ConfigError(_FIELD, "as variâncias externas devem ser finitas e >= 0")


def read_variance_file(path: Path, value_type: str) -> dict[str, float]:
    """Lê o arquivo de variâncias externas (CSV ou parquet, colunas ``sector`` e o valor).

    Parameters
    ----------
    path : Path
        Arquivo já validado contra *path traversal* pela configuração.
    value_type : {"variance", "cv"}
        Nome da coluna de valores.

    Returns
    -------
    dict
        Setor → valor.

    Raises
    ------
    ConfigError
        Formato não suportado, colunas ausentes ou setores repetidos.

    """
    reader = _READERS.get(path.suffix.lower())
    if reader is None:
        raise ConfigError(_FILE_FIELD, "formato não suportado (use .csv ou .parquet)")
    table = reader(path)
    if not {"sector", value_type} <= set(table.columns):
        raise ConfigError(_FILE_FIELD, f"o arquivo deve ter as colunas 'sector' e '{value_type}'")
    if not table["sector"].is_unique().all():
        raise ConfigError(_FILE_FIELD, "setores repetidos no arquivo")
    pairs = table.select(pl.col("sector").cast(pl.String), pl.col(value_type).cast(pl.Float64))
    return dict(pairs.iter_rows())


def _external_values(config: SectorVarianceConfig) -> Mapping[str, float]:
    if config.values is not None:
        return config.values
    return read_variance_file(config.values_file or Path(), config.value_type)


def external_variance(config: SectorVarianceConfig, sectors: tuple[str, ...]) -> FloatArray:
    r"""Variâncias $v_k$ externas, alinhadas à ordem dos setores da base.

    Parameters
    ----------
    config : SectorVarianceConfig
        Configuração com ``values`` ou ``values_file``.
    sectors : tuple of str
        Nomes originais das colunas de peso, na ordem do modelo.

    Returns
    -------
    FloatArray
        $v_k$ para $k = 0..K$ ($v_0 = 0$); valores ``cv`` são elevados ao quadrado.

    Raises
    ------
    ConfigError
        Setor faltando ou sobrando, ou valor inválido.

    """
    values = _external_values(config)
    _check_names(values, sectors)
    _check_values(values)
    ordered = np.array([values[name] for name in sectors], dtype=np.float64)
    power = 2.0 if config.value_type == "cv" else 1.0
    return np.concatenate([[0.0], ordered**power])


def sector_parameters(
    aggregate: SectorBandAggregate, sectors: tuple[str, ...], config: SectorVarianceConfig
) -> SectorParameters:
    r"""Calcula os parâmetros setoriais pelo método configurado.

    Parameters
    ----------
    aggregate : SectorBandAggregate
        Agregados do passo B (todas as partições somadas).
    sectors : tuple of str
        Nomes originais das colunas de peso.
    config : SectorVarianceConfig
        Método de variância setorial.

    Returns
    -------
    SectorParameters
        Parâmetros por setor; setores com $\mu_k = 0$ recebem $v_k = 0$.

    """
    implied = implied_variance(aggregate, config.adjust_for_banding)
    chosen = implied if config.method == "pd_vol" else external_variance(config, sectors)
    mean = aggregate.intensity.sum(axis=1)
    volatility = _VOLATILITY_SOURCES[config.adjust_for_banding](aggregate)[0]
    used = np.where(mean > 0, chosen, 0.0)
    return SectorParameters((IDIOSYNCRATIC, *sectors), mean, volatility, implied, used)
`````

<!-- FILE: src/crplus/sources.py -->
`````python
"""Normalização da entrada: ``LazyFrame``/``DataFrame``/pandas → plano lazy canônico.

A normalização só constrói o plano: seleciona as colunas necessárias, renomeia para os nomes
canônicos de :mod:`crplus.schema` e aplica os casts mínimos, sem ler dados. A fonte ideal é um
parquet com *row groups* de ~1M linhas (``pl.scan_parquet``), pois o plano é reexecutado em
cada passo e partição.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Iterator
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Final, cast

import polars as pl

from crplus.config import ColumnMap
from crplus.exceptions import InputValidationError
from crplus.memory import IdKind
from crplus.schema import (
    CANONICAL_COLUMNS,
    FLOAT_COLUMNS,
    ID_COLUMNS,
    OBLIGOR_ID,
    partition_predicate,
    weight_column,
)
from crplus.validation import check_schema

if TYPE_CHECKING:
    import pandas as pd

_logger = logging.getLogger(__name__)

_WEIGHT_DTYPES: Final[dict[str, type[pl.DataType]]] = {
    "float64": pl.Float64,
    "float32": pl.Float32,
}


@dataclass(frozen=True, slots=True)
class PortfolioSource:
    """Plano lazy canônico da carteira.

    Parameters
    ----------
    frame : pl.LazyFrame
        Plano com colunas canônicas: ids, ``pd``, ``pd_vol``, ``lgd``, ``ead``, ``_w1.._wK``.
    sectors : tuple of str
        Nomes originais das colunas de peso, em ordem alfabética (setor ``k`` = posição ``k``).
    id_kind : {"int", "str"}
        Natureza do ``obligor_id`` (usada nas estimativas de memória).

    """

    frame: pl.LazyFrame
    sectors: tuple[str, ...]
    id_kind: IdKind

    @property
    def n_sectors(self) -> int:
        """Número ``K`` de setores sistêmicos."""
        return len(self.sectors)

    def with_frame(self, frame: pl.LazyFrame) -> PortfolioSource:
        """Cópia com outro plano (por exemplo, após excluir linhas inválidas)."""
        return replace(self, frame=frame)


def _from_polars_lazy(data: object) -> pl.LazyFrame:
    return cast(pl.LazyFrame, data)


def _from_polars_eager(data: object) -> pl.LazyFrame:
    return cast(pl.DataFrame, data).lazy()


def _from_pandas(data: object) -> pl.LazyFrame:
    return pl.from_pandas(cast("pd.DataFrame", data)).lazy()


_CONVERTERS: Final[dict[str, Callable[[object], pl.LazyFrame]]] = {
    "lazy": _from_polars_lazy,
    "eager": _from_polars_eager,
    "pandas": _from_pandas,
}


_POLARS_KINDS: Final = ((pl.LazyFrame, "lazy"), (pl.DataFrame, "eager"))


def _module_kind(data: object) -> str | None:
    return "pandas" if type(data).__module__.startswith("pandas") else None


def _input_kind(data: object) -> str:
    polars_kind = (name for cls, name in _POLARS_KINDS if isinstance(data, cls))
    kind = next(polars_kind, None) or _module_kind(data)
    if kind is None:
        raise InputValidationError(
            "A entrada deve ser polars.LazyFrame, polars.DataFrame ou pandas.DataFrame."
        )
    return kind


def to_lazy(data: object) -> pl.LazyFrame:
    """Plano ``pl.LazyFrame`` equivalente à entrada, sem materializar dados polars.

    Parameters
    ----------
    data : object
        ``pl.LazyFrame`` (produção), ``pl.DataFrame`` ou ``pandas.DataFrame``.

    Returns
    -------
    pl.LazyFrame
        Plano lazy equivalente.

    Raises
    ------
    InputValidationError
        Para tipos não suportados.

    """
    return _CONVERTERS[_input_kind(data)](data)


def discover_sectors(schema: pl.Schema, prefix: str) -> tuple[str, ...]:
    """Colunas de peso (que começam com ``prefix``), em ordem alfabética estável.

    Parameters
    ----------
    schema : pl.Schema
        Esquema da base.
    prefix : str
        Prefixo configurado em ``columns.weight_prefix``.

    Returns
    -------
    tuple of str
        Nomes originais das colunas de peso.

    """
    return tuple(sorted(name for name in schema.names() if name.startswith(prefix)))


def _projection(columns: ColumnMap, sectors: tuple[str, ...], weight_dtype: str) -> list[pl.Expr]:
    ids = [pl.col(getattr(columns, name)).alias(name) for name in ID_COLUMNS]
    floats = [pl.col(getattr(columns, name)).cast(pl.Float64).alias(name) for name in FLOAT_COLUMNS]
    dtype = _WEIGHT_DTYPES[weight_dtype]
    weights = [
        pl.col(name).cast(dtype).alias(weight_column(k)) for k, name in enumerate(sectors, start=1)
    ]
    return ids + floats + weights


def _id_kind(schema: pl.Schema, column: str) -> IdKind:
    return "int" if schema[column].is_integer() else "str"


def normalize_source(
    data: object, columns: ColumnMap, weight_dtype: str, max_sectors: int
) -> PortfolioSource:
    """Constrói o plano canônico (select + renomeação + casts) a partir da entrada.

    Parameters
    ----------
    data : object
        Entrada suportada por :func:`to_lazy`.
    columns : ColumnMap
        Nomes configurados das colunas.
    weight_dtype : {"float64", "float32"}
        Tipo de armazenamento dos pesos.
    max_sectors : int
        Limite de segurança para o número de setores.

    Returns
    -------
    PortfolioSource
        Plano canônico e metadados.

    Raises
    ------
    InputValidationError
        Se faltar coluna, algum tipo for incompatível ou houver setores demais.

    """
    frame = to_lazy(data)
    schema = frame.collect_schema()
    sectors = discover_sectors(schema, columns.weight_prefix)
    if len(sectors) > max_sectors:
        raise InputValidationError(
            f"A base tem {len(sectors)} setores; o limite é numerics.max_sectors = {max_sectors}."
        )
    check_schema(schema, columns, sectors)
    plan = frame.select(_projection(columns, sectors, weight_dtype))
    _logger.info("Base normalizada: %d setores sistêmicos.", len(sectors))
    return PortfolioSource(plan, sectors, _id_kind(schema, columns.obligor_id))


def iter_partitions(source: PortfolioSource, partitions: int) -> Iterator[pl.LazyFrame]:
    """Planos das partições por hash de ``obligor_id`` (cada devedor em uma única partição).

    Parameters
    ----------
    source : PortfolioSource
        Carteira normalizada.
    partitions : int
        Número de partições.

    Yields
    ------
    pl.LazyFrame
        Plano filtrado de cada partição, na ordem ``0..partitions-1``.

    """
    for part in range(partitions):
        yield source.frame.filter(partition_predicate(OBLIGOR_ID, part, partitions))


__all__ = [
    "CANONICAL_COLUMNS",
    "PortfolioSource",
    "discover_sectors",
    "iter_partitions",
    "normalize_source",
    "to_lazy",
]
`````

<!-- FILE: src/crplus/tempstore.py -->
`````python
"""Diretório temporário seguro, com permissão restrita e limpeza garantida.

Uso::

    with secure_tempdir() as store:
        caminho = store.path_for("obligors-0.parquet")

O diretório é criado com :func:`tempfile.mkdtemp` (nunca ``mktemp``), com permissão ``0o700``,
e removido no ``finally`` — inclusive quando o bloco levanta exceção.
"""

from __future__ import annotations

import logging
import os
import shutil
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from crplus.exceptions import CRPlusError

TEMP_DIR_MODE = 0o700
_FORBIDDEN_NAMES = frozenset({"", ".", ".."})

_logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class TempStore:
    """Diretório temporário em uso.

    Parameters
    ----------
    root : Path
        Caminho absoluto do diretório temporário.

    """

    root: Path

    def path_for(self, name: str) -> Path:
        """Devolve o caminho de um arquivo diretamente dentro do diretório temporário.

        Parameters
        ----------
        name : str
            Nome simples do arquivo (sem separadores de diretório).

        Returns
        -------
        Path
            ``root / name``.

        Raises
        ------
        CRPlusError
            Se ``name`` contiver separadores, unidade de disco ou for ``.``/``..``.

        """
        if not _is_plain_name(name):
            raise CRPlusError("Nome de arquivo temporário inválido.")
        return self.root / name


def _is_plain_name(name: str) -> bool:
    return name not in _FORBIDDEN_NAMES and Path(name).name == name and "\\" not in name


@contextmanager
def secure_tempdir(parent: Path | None = None, prefix: str = "crplus-") -> Iterator[TempStore]:
    """Cria um diretório temporário privado e garante sua remoção ao sair do contexto.

    Parameters
    ----------
    parent : Path or None, default None
        Diretório onde criar o temporário; ``None`` usa o padrão do sistema.
    prefix : str, default "crplus-"
        Prefixo do nome do diretório.

    Yields
    ------
    TempStore
        O diretório temporário criado.

    """
    root = Path(tempfile.mkdtemp(prefix=prefix, dir=parent))
    os.chmod(root, TEMP_DIR_MODE)
    try:
        yield TempStore(root)
    finally:
        _remove_tree(root)


def _remove_tree(root: Path) -> None:
    try:
        shutil.rmtree(root)
    except OSError:
        _logger.warning("Não foi possível remover completamente o diretório temporário do crplus.")
`````

<!-- FILE: src/crplus/validation.py -->
`````python
"""Validação vetorizada da base de entrada (expressões polars, em modo streaming).

As regras são declaradas como uma lista de :class:`Rule` (nome + expressão booleana de violação
+ severidade) e avaliadas uniformemente numa única passada de agregação sobre a base. O
relatório guarda somente **contagens** e **posições** das primeiras linhas violadoras — nunca
valores nem identificadores.

Notes
-----
Em polars, ``NaN`` compara como maior que qualquer número; por isso toda regra de domínio
exige explicitamente ``is_finite`` antes das comparações de faixa.

"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, replace
from typing import Final, Literal

import polars as pl

from crplus.config import ColumnMap, ValidationConfig
from crplus.exceptions import InputValidationError
from crplus.schema import (
    EAD,
    FLOAT_COLUMNS,
    LGD,
    OBLIGOR_ID,
    OPERATION_ID,
    PD,
    PD_VOL,
    partition_predicate,
    weight_columns,
)

Severity = Literal["error", "warning", "info"]

_ROWS: Final = "__rows"
_OBLIGORS: Final = "__obligors"
_ROW_INDEX: Final = "__row"


@dataclass(frozen=True, slots=True)
class Rule:
    """Regra de validação por linha.

    Parameters
    ----------
    name : str
        Identificador estável da regra (usado no relatório).
    violation : pl.Expr
        Expressão booleana, sem nulos, verdadeira nas linhas que violam a regra.
    severity : {"error", "warning", "info"}
        ``error`` invalida a linha; ``warning`` e ``info`` apenas contam.
    description : str
        Descrição da regra em português.

    """

    name: str
    violation: pl.Expr
    severity: Severity
    description: str


@dataclass(frozen=True, slots=True)
class RuleOutcome:
    """Resultado de uma regra sobre a base.

    Parameters
    ----------
    name : str
        Nome da regra.
    severity : {"error", "warning", "info"}
        Severidade da regra.
    description : str
        Descrição da regra.
    count : int
        Número de linhas que violam a regra.
    first_rows : tuple of int
        Posições (base 0) das primeiras linhas violadoras, apenas para erros.

    """

    name: str
    severity: Severity
    description: str
    count: int
    first_rows: tuple[int, ...] = ()


@dataclass(frozen=True, slots=True)
class ValidationReport:
    """Relatório de validação da base (somente agregados).

    Parameters
    ----------
    n_rows : int
        Linhas avaliadas.
    n_obligors_estimate : int
        Estimativa (HyperLogLog) do número de devedores distintos.
    outcomes : tuple of RuleOutcome
        Resultado de cada regra, na ordem de declaração.
    duplicate_operation_ids : int
        Linhas excedentes com ``operation_id`` repetido (0 se a checagem estiver desligada).

    """

    n_rows: int
    n_obligors_estimate: int
    outcomes: tuple[RuleOutcome, ...]
    duplicate_operation_ids: int = 0

    @property
    def errors(self) -> tuple[RuleOutcome, ...]:
        """Regras de erro com pelo menos uma violação."""
        return tuple(o for o in self.outcomes if o.severity == "error" and o.count > 0)

    @property
    def warnings(self) -> tuple[RuleOutcome, ...]:
        """Regras de aviso ou informação com pelo menos uma ocorrência."""
        return tuple(o for o in self.outcomes if o.severity != "error" and o.count > 0)

    def count(self, name: str) -> int:
        """Número de violações da regra ``name`` (0 se a regra não existir)."""
        return next((o.count for o in self.outcomes if o.name == name), 0)

    def summary(self) -> str:
        """Resumo legível das violações de erro, sem valores nem identificadores."""
        lines = [f"- {_describe(outcome)}" for outcome in self.errors]
        return "Validação da base de entrada falhou:\n" + "\n".join(lines)


def _describe(outcome: RuleOutcome) -> str:
    positions = ", ".join(str(row) for row in outcome.first_rows)
    suffix = f" (primeiras posições: {positions})" if positions else ""
    return f"{outcome.name}: {outcome.count} linha(s) — {outcome.description}{suffix}"


# --- esquema --------------------------------------------------------------------------------


def _is_id_dtype(dtype: pl.DataType) -> bool:
    return dtype.is_integer() or isinstance(dtype, pl.String | pl.Categorical | pl.Enum)


def check_schema(schema: pl.Schema, columns: ColumnMap, sectors: Sequence[str]) -> None:
    """Verifica presença e tipo das colunas da base (antes de qualquer leitura de dados).

    Parameters
    ----------
    schema : pl.Schema
        Esquema da base de entrada (nomes originais).
    columns : ColumnMap
        Mapeamento de nomes configurado.
    sectors : Sequence[str]
        Nomes originais das colunas de peso.

    Raises
    ------
    InputValidationError
        Se faltar coluna obrigatória ou se algum tipo for incompatível.

    """
    missing = [name for name in columns.required if name not in schema]
    if missing:
        raise InputValidationError(f"Colunas obrigatórias ausentes: {', '.join(missing)}.")
    bad = _incompatible_columns(schema, columns, sectors)
    if bad:
        raise InputValidationError(f"Colunas com tipo incompatível: {', '.join(bad)}.")


def _incompatible_columns(
    schema: pl.Schema, columns: ColumnMap, sectors: Sequence[str]
) -> list[str]:
    numeric = [getattr(columns, field) for field in FLOAT_COLUMNS] + list(sectors)
    ids = [columns.operation_id, columns.obligor_id]
    return _failing(schema, numeric, _is_numeric_dtype) + _failing(schema, ids, _is_id_dtype)


def _is_numeric_dtype(dtype: pl.DataType) -> bool:
    return dtype.is_numeric()


def _failing(
    schema: pl.Schema, names: Sequence[str], accepts: Callable[[pl.DataType], bool]
) -> list[str]:
    return [name for name in names if not accepts(schema[name])]


# --- regras ---------------------------------------------------------------------------------


def _within(column: str, low: float, high: float | None) -> pl.Expr:
    value = pl.col(column)
    valid = value.is_not_null() & value.is_finite() & (value >= low)
    return valid if high is None else valid & (value <= high)


def _violates(valid: pl.Expr) -> pl.Expr:
    return ~valid.fill_null(False)


def _base_rules() -> list[Rule]:
    return [
        Rule("operation_id_null", pl.col(OPERATION_ID).is_null(), "error", "operation_id nulo"),
        Rule("obligor_id_null", pl.col(OBLIGOR_ID).is_null(), "error", "obligor_id nulo"),
        Rule("pd_domain", _violates(_within(PD, 0.0, 1.0)), "error", "PD fora de [0, 1]"),
        Rule("pd_vol_domain", _violates(_within(PD_VOL, 0.0, None)), "error", "pd_vol negativa"),
        Rule("lgd_domain", _violates(_within(LGD, 0.0, 1.0)), "error", "LGD fora de [0, 1]"),
        Rule("ead_domain", _violates(_within(EAD, 0.0, None)), "error", "EAD negativa"),
    ]


def _weight_rules(n_sectors: int, tolerance: float) -> list[Rule]:
    weights = weight_columns(n_sectors)
    domain = pl.any_horizontal([_violates(_within(w, 0.0, 1.0)) for w in weights])
    total = (pl.sum_horizontal(weights) > 1.0 + tolerance).fill_null(False)
    return [
        Rule("weights_domain", domain, "error", "peso setorial fora de [0, 1]"),
        Rule("weights_sum", total, "error", "soma dos pesos setoriais maior que 1"),
    ]


def _warning_rules(config: ValidationConfig) -> list[Rule]:
    high_pd = (pl.col(PD) > config.pd_warn_threshold).fill_null(False)
    zero = ((pl.col(LGD) * pl.col(EAD)) == 0).fill_null(False)
    return [
        Rule("pd_above_threshold", high_pd, "warning", "PD acima de pd_warn_threshold"),
        Rule("zero_exposure", zero, "info", "lgd * ead igual a zero (contribuição nula)"),
    ]


def build_rules(n_sectors: int, config: ValidationConfig) -> tuple[Rule, ...]:
    """Monta a lista de regras para uma base com ``n_sectors`` setores sistêmicos.

    Parameters
    ----------
    n_sectors : int
        Número ``K`` de colunas de peso.
    config : ValidationConfig
        Parâmetros de validação.

    Returns
    -------
    tuple of Rule
        Regras de erro seguidas das regras de aviso.

    """
    weights = _weight_rules(n_sectors, config.weights_tolerance) if n_sectors else []
    return (*_base_rules(), *weights, *_warning_rules(config))


# --- execução -------------------------------------------------------------------------------


def evaluate_rules(frame: pl.LazyFrame, rules: Sequence[Rule], max_rows: int) -> ValidationReport:
    """Avalia as regras numa passada de streaming e coleta posições dos erros.

    Parameters
    ----------
    frame : pl.LazyFrame
        Base normalizada (nomes canônicos).
    rules : Sequence[Rule]
        Regras a avaliar.
    max_rows : int
        Quantidade máxima de posições guardadas por regra de erro.

    Returns
    -------
    ValidationReport
        Relatório sem a checagem de unicidade de ``operation_id``.

    """
    totals = frame.select(
        *[rule.violation.sum().alias(rule.name) for rule in rules],
        pl.len().alias(_ROWS),
        pl.col(OBLIGOR_ID).approx_n_unique().alias(_OBLIGORS),
    ).collect(engine="streaming")
    outcomes = tuple(_outcome(frame, rule, int(totals[rule.name][0]), max_rows) for rule in rules)
    return ValidationReport(int(totals[_ROWS][0]), int(totals[_OBLIGORS][0]), outcomes)


def _outcome(frame: pl.LazyFrame, rule: Rule, count: int, max_rows: int) -> RuleOutcome:
    wants_rows = rule.severity == "error" and count > 0 and max_rows > 0
    rows = _first_rows(frame, rule.violation, max_rows) if wants_rows else ()
    return RuleOutcome(rule.name, rule.severity, rule.description, count, rows)


def _first_rows(frame: pl.LazyFrame, violation: pl.Expr, max_rows: int) -> tuple[int, ...]:
    rows = (
        frame.with_row_index(_ROW_INDEX)
        .filter(violation)
        .select(_ROW_INDEX)
        .head(max_rows)
        .collect(engine="streaming")
    )
    return tuple(int(row) for row in rows[_ROW_INDEX].to_list())


def count_duplicate_ids(frame: pl.LazyFrame, partitions: int) -> int:
    r"""Conta linhas excedentes de ``operation_id`` repetido, particionando por hash do id.

    Parameters
    ----------
    frame : pl.LazyFrame
        Base normalizada.
    partitions : int
        Número de partições (limita a memória do conjunto de ids distintos).

    Returns
    -------
    int
        $\sum_p (n_p - \text{distintos}_p)$.

    """
    total = 0
    for part in range(partitions):
        subset = frame.filter(partition_predicate(OPERATION_ID, part, partitions))
        counts = subset.select(pl.len(), pl.col(OPERATION_ID).n_unique().alias("u"))
        row = counts.collect(engine="streaming").row(0)
        total += int(row[0]) - int(row[1])
    return total


def with_duplicates(report: ValidationReport, duplicates: int) -> ValidationReport:
    """Devolve uma cópia do relatório com a contagem de ids duplicados."""
    return replace(report, duplicate_operation_ids=duplicates)


def _reject_duplicates(report: ValidationReport) -> None:
    if report.duplicate_operation_ids:
        message = f"operation_id repetido em {report.duplicate_operation_ids} linha(s)."
        raise InputValidationError(message, report)


def enforce(
    report: ValidationReport, frame: pl.LazyFrame, rules: Sequence[Rule], strict: bool
) -> pl.LazyFrame:
    """Aplica o resultado da validação: erro em modo estrito, exclusão de linhas caso contrário.

    Parameters
    ----------
    report : ValidationReport
        Relatório já avaliado.
    frame : pl.LazyFrame
        Base normalizada.
    rules : Sequence[Rule]
        Regras usadas no relatório.
    strict : bool
        Modo estrito.

    Returns
    -------
    pl.LazyFrame
        A base (sem as linhas inválidas, em modo não estrito).

    Raises
    ------
    InputValidationError
        Em modo estrito com qualquer erro, ou em qualquer modo com ``operation_id`` repetido
        (não há como escolher, sem arbitrariedade, qual das linhas repetidas manter).

    """
    _reject_duplicates(report)
    if not report.errors:
        return frame
    if strict:
        raise InputValidationError(report.summary(), report)
    invalid = pl.any_horizontal([rule.violation for rule in rules if rule.severity == "error"])
    return frame.filter(~invalid)
`````

<!-- FILE: tests/__init__.py -->
`````python
`````

<!-- FILE: tests/benchmarks/__init__.py -->
`````python
`````

<!-- FILE: tests/benchmarks/scale_runner.py -->
`````python
"""Execução de escala em subprocesso: gera a carteira em parquet por lote e mede o pico de RSS.

Uso::

    uv run python -m tests.benchmarks.scale_runner generate --rows 50000000 --dir D:/bench
    uv run python -m tests.benchmarks.scale_runner run --dir D:/bench --budget-gb 9

O comando ``run`` imprime um JSON com linhas, tempos por etapa, throughput e pico de RSS.
"""

from __future__ import annotations

import argparse
import ctypes
import json
import os
import sys
import time
from ctypes import wintypes
from pathlib import Path

import numpy as np
import polars as pl

CHUNK_ROWS = 5_000_000
N_SECTORS = 8


def peak_rss_bytes() -> int:
    """Pico de memória residente do processo atual (Windows ou POSIX)."""
    if os.name == "nt":
        return _windows_peak()
    import resource  # noqa: PLC0415 - módulo só existe em POSIX

    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(peak) * (1 if sys.platform == "darwin" else 1024)


class _Counters(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("PageFaultCount", wintypes.DWORD),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
    ]


def _windows_peak() -> int:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)  # type: ignore[attr-defined]
    kernel32.GetCurrentProcess.restype = wintypes.HANDLE
    query = kernel32.K32GetProcessMemoryInfo
    query.argtypes = [wintypes.HANDLE, ctypes.POINTER(_Counters), wintypes.DWORD]
    query.restype = wintypes.BOOL
    counters = _Counters()
    counters.cb = ctypes.sizeof(_Counters)
    if not query(kernel32.GetCurrentProcess(), ctypes.byref(counters), counters.cb):
        raise OSError(ctypes.get_last_error())  # type: ignore[attr-defined]
    return int(max(counters.PeakWorkingSetSize, counters.PeakPagefileUsage))


def _chunk(rows: int, offset: int, seed: int) -> pl.DataFrame:
    rng = np.random.default_rng(seed)
    n_obligors = max(1, rows // 3)
    obligor = rng.integers(0, n_obligors, rows) + offset
    pd_obl = np.clip(0.01 * rng.lognormal(0.0, 0.8, n_obligors), 1e-5, 0.25)
    weights = rng.dirichlet(np.ones(N_SECTORS), n_obligors).astype(np.float32) * 0.8
    local = obligor - offset
    columns: dict[str, object] = {
        "operation_id": np.arange(rows, dtype=np.int64) + offset * 3,
        "obligor_id": obligor.astype(np.int64),
        "pd": pd_obl[local],
        "pd_vol": 0.6 * pd_obl[local],
        "lgd": rng.uniform(0.1, 0.9, rows),
        "ead": 1000.0 * (rng.pareto(2.5, rows) + 0.05),
    }
    for k in range(N_SECTORS):
        columns[f"w_s{k + 1}"] = weights[local, k]
    return pl.DataFrame(columns)


def generate(rows: int, directory: Path) -> None:
    """Grava ``rows`` operações em arquivos parquet de até 5 milhões de linhas."""
    directory.mkdir(parents=True, exist_ok=True)
    written = 0
    for index, start in enumerate(range(0, rows, CHUNK_ROWS)):
        size = min(CHUNK_ROWS, rows - start)
        frame = _chunk(size, offset=start, seed=index)
        frame.write_parquet(directory / f"part-{index:04d}.parquet", row_group_size=1_000_000)
        written += size
    print(json.dumps({"generated_rows": written}))


def run(directory: Path, budget_gb: float) -> None:
    """Executa o CreditRisk+ completo sobre os parquet e imprime as métricas em JSON."""
    from crplus import config_from_mapping, run_creditrisk_plus  # noqa: PLC0415

    raw = {
        "resources": {"memory_budget_gb": budget_gb, "weight_dtype": "float32"},
        "validation": {"check_operation_id_unique": True},
        "output": {"directory": "saida", "overwrite": True},
    }
    config = config_from_mapping(raw, base_dir=directory)
    start = time.perf_counter()
    result = run_creditrisk_plus(pl.scan_parquet(directory / "part-*.parquet"), config)
    elapsed = time.perf_counter() - start
    rows = result.diagnostics.n_operations
    metrics = {
        "rows": rows,
        "seconds": elapsed,
        "rows_per_second": rows / elapsed,
        "peak_rss_gb": peak_rss_bytes() / 1024**3,
        "partitions": result.diagnostics.partitions,
        "loss_unit": result.diagnostics.loss_unit,
        "grid_size": result.diagnostics.grid.grid_size,
        "max_band": result.diagnostics.max_band,
        "timings": dict(result.diagnostics.timings),
        "alerts": list(result.diagnostics.alerts),
    }
    print(json.dumps(metrics))


def main() -> None:
    """Ponto de entrada de linha de comando."""
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["generate", "run"])
    parser.add_argument("--rows", type=int, default=50_000_000)
    parser.add_argument("--dir", type=Path, required=True)
    parser.add_argument("--budget-gb", type=float, default=9.0)
    args = parser.parse_args()
    if args.command == "generate":
        generate(args.rows, args.dir)
    else:
        run(args.dir, args.budget_gb)


if __name__ == "__main__":
    main()
`````

<!-- FILE: tests/benchmarks/test_scale.py -->
`````python
"""Benchmarks de escala (marcador ``slow``; fora do ``make check``).

- ``test_scale_peak_rss_within_budget``: gera ``CRPLUS_BENCH_ROWS`` linhas (padrão 50 milhões)
  em parquet e roda o CreditRisk+ completo num **subprocesso**, medindo o pico de RSS.
  Diretório de trabalho: ``CRPLUS_BENCH_DIR`` (padrão: ``tmp_path``; exige alguns GB livres).
- benchmarks ``pytest-benchmark`` do passo C em função de ``M`` e ``K``.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
from pytest_benchmark.fixture import BenchmarkFixture

from crplus.distribution import FFTEngine, SectorModel

pytestmark = pytest.mark.slow

ROWS = int(os.environ.get("CRPLUS_BENCH_ROWS", "50000000"))
BUDGET_GB = float(os.environ.get("CRPLUS_BENCH_BUDGET_GB", "9.0"))
REPO = Path(__file__).resolve().parents[2]


def _runner(*args: str) -> dict[str, object]:
    command = [sys.executable, "-m", "tests.benchmarks.scale_runner", *args]
    completed = subprocess.run(command, cwd=REPO, check=True, capture_output=True, text=True)
    return dict(json.loads(completed.stdout.strip().splitlines()[-1]))


def test_scale_peak_rss_within_budget(tmp_path: Path) -> None:
    """Intenção: a base completa roda com pico de RSS <= memory_budget_gb (meta da §6.2).
    Se falhar, a engine materializa dados proporcionais à base e não escala."""
    directory = Path(os.environ.get("CRPLUS_BENCH_DIR", str(tmp_path)))
    if not list(directory.glob("part-*.parquet")):
        _runner("generate", "--rows", str(ROWS), "--dir", str(directory))

    metrics = _runner("run", "--dir", str(directory), "--budget-gb", str(BUDGET_GB))

    (REPO / "tests" / "benchmarks" / "last_scale_run.json").write_text(
        json.dumps(metrics, indent=2), encoding="utf-8"
    )
    assert float(metrics["peak_rss_gb"]) <= BUDGET_GB  # type: ignore[arg-type]


def _model(n_sectors: int, bands: int) -> SectorModel:
    rng = np.random.default_rng(0)
    intensity = rng.uniform(0.0, 1.0, size=(n_sectors + 1, bands + 1))
    intensity[:, 0] = 0.0
    variance = np.concatenate([[0.0], np.full(n_sectors, 0.5)])
    return SectorModel(intensity, variance)


@pytest.mark.parametrize("grid", [1 << 16, 1 << 20, 1 << 22])
def test_benchmark_fft_by_grid_size(benchmark: BenchmarkFixture, grid: int) -> None:
    """Intenção: medir o custo do passo C em função de M (O(K M log M)).
    Se o tempo crescer acima do esperado, há regressão de desempenho no motor FFT."""
    model = _model(8, 1000)
    engine = FFTEngine(workers=8)

    benchmark.pedantic(engine.compute, args=(model, grid), rounds=3, iterations=1)


@pytest.mark.parametrize("sectors", [1, 8, 32])
def test_benchmark_fft_by_sector_count(benchmark: BenchmarkFixture, sectors: int) -> None:
    """Intenção: medir o custo do passo C em função de K (setores processados em sequência).
    Se o tempo crescer acima do linear em K, a acumulação de log(phi) regrediu."""
    model = _model(sectors, 1000)
    engine = FFTEngine(workers=8)

    benchmark.pedantic(engine.compute, args=(model, 1 << 20), rounds=3, iterations=1)
`````

<!-- FILE: tests/conftest.py -->
`````python
"""Fixtures compartilhadas e perfis do hypothesis."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from hypothesis import HealthCheck, settings

settings.register_profile(
    "default",
    deadline=None,
    max_examples=100,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
settings.load_profile("default")

REPO_ROOT = Path(__file__).resolve().parents[1]


def pytest_addoption(parser: pytest.Parser) -> None:
    """Opção para regenerar os golden files (exige justificativa no commit)."""
    parser.addoption(
        "--update-golden",
        action="store_true",
        default=False,
        help="regrava tests/integration/golden/*.json com os resultados atuais",
    )


EXAMPLE_CONFIG = REPO_ROOT / "crplus.example.toml"


@pytest.fixture
def example_config_path(tmp_path: Path) -> Path:
    """Cópia do ``crplus.example.toml`` num diretório temporário isolado."""
    target = tmp_path / "crplus.toml"
    shutil.copyfile(EXAMPLE_CONFIG, target)
    return target


@pytest.fixture
def symlink_dir(tmp_path: Path) -> Path:
    """Link simbólico ``tmp_path/link`` para um diretório real; pula se o SO não permitir."""
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "link"
    try:
        link.symlink_to(real, target_is_directory=True)
    except OSError:
        pytest.skip("o sistema não permite criar links simbólicos")
    return link
`````

<!-- FILE: tests/integration/__init__.py -->
`````python
`````

<!-- FILE: tests/integration/golden/end_to_end.json -->
`````json
{
  "el": 2467955.7247486576,
  "ul": 431282.9816229468,
  "loss_unit": 2199.0799616825493,
  "grid_size": 4320.0,
  "n_operations": 499579.0,
  "var_0.99": 3602092.9772360157,
  "var_0.999": 4063899.7691893512,
  "es_0.99": 3805671.594244234,
  "es_0.999": 4243041.895967657
}
`````

<!-- FILE: tests/integration/reference/__init__.py -->
`````python
"""Casos de referência externos (resultados de outra implementação do CreditRisk+)."""
`````

<!-- FILE: tests/integration/reference/cases.py -->
`````python
"""Leitor de casos de referência.

Cada caso é um subdiretório de ``tests/integration/reference/cases/`` com:

- ``portfolio.parquet``: carteira no contrato de entrada do crplus;
- ``crplus.toml``: configuração usada (caminhos relativos ao próprio diretório);
- ``expected.json``: ``{"el": ..., "ul": ..., "var": {"0.999": ...}, "es": {...},
  "rel_tolerance": 1e-6, "source": "descrição da implementação de referência"}``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CASES_DIR = Path(__file__).parent / "cases"


@dataclass(frozen=True)
class ReferenceCase:
    """Um caso de referência externo."""

    name: str
    portfolio: Path
    config: Path
    expected: dict[str, Any]

    @property
    def tolerance(self) -> float:
        return float(self.expected.get("rel_tolerance", 1e-6))


def _read_case(directory: Path) -> ReferenceCase:
    expected = json.loads((directory / "expected.json").read_text(encoding="utf-8"))
    return ReferenceCase(
        directory.name, directory / "portfolio.parquet", directory / "crplus.toml", expected
    )


def load_cases(root: Path = CASES_DIR) -> list[ReferenceCase]:
    """Lê todos os casos completos (com os três arquivos) em ``root``."""
    required = ("portfolio.parquet", "crplus.toml", "expected.json")
    folders = sorted(p for p in root.glob("*") if p.is_dir()) if root.is_dir() else []
    return [_read_case(p) for p in folders if all((p / f).exists() for f in required)]
`````

<!-- FILE: tests/integration/reference/test_reference.py -->
`````python
"""Comparação com valores de referência de outra implementação do CreditRisk+.

Ainda não há casos de referência (CLAUDE.md §10.3); o teste é pulado até que o usuário inclua
casos em ``tests/integration/reference/cases/`` (formato em ``cases.py``).
"""

from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest

from crplus import load_config, run_creditrisk_plus
from tests.integration.reference.cases import ReferenceCase, load_cases

CASES = load_cases()


@pytest.mark.integration
@pytest.mark.skipif(not CASES, reason="nenhum caso de referência externo disponível")
@pytest.mark.parametrize("case", CASES, ids=[c.name for c in CASES])
def test_reference_case_matches_external_implementation(case: ReferenceCase) -> None:
    """Intenção: os resultados batem com os de uma implementação externa do CreditRisk+.
    Se falhar, há divergência metodológica ou numérica em relação à referência."""
    config = load_config(case.config)

    result = run_creditrisk_plus(pl.scan_parquet(case.portfolio), config)

    expected = case.expected
    assert result.el == pytest.approx(expected["el"], rel=case.tolerance)
    assert result.ul == pytest.approx(expected["ul"], rel=case.tolerance)
    for label, value in expected.get("var", {}).items():
        assert result.var[float(label)] == pytest.approx(value, rel=case.tolerance)
    for label, value in expected.get("es", {}).items():
        assert result.es[float(label)] == pytest.approx(value, rel=case.tolerance)


def test_reference_loader_reads_complete_cases_only(tmp_path: Path) -> None:
    """Intenção: o leitor ignora diretórios incompletos e lê os completos.
    Se falhar, um caso parcialmente copiado quebraria a suíte ou seria ignorado sem aviso."""
    complete = tmp_path / "caso_a"
    complete.mkdir()
    for name in ("portfolio.parquet", "crplus.toml"):
        (complete / name).write_bytes(b"")
    (complete / "expected.json").write_text('{"el": 1.0, "rel_tolerance": 1e-4}', encoding="utf-8")
    (tmp_path / "caso_incompleto").mkdir()

    cases = load_cases(tmp_path)

    assert [c.name for c in cases] == ["caso_a"]
    assert cases[0].tolerance == 1e-4
`````

<!-- FILE: tests/integration/test_end_to_end.py -->
`````python
"""Teste de integração final (CLAUDE.md §10.3): API pública ponta a ponta.

Carteira sintética com seed: ~500 mil operações, 8 setores + idiossincrático, PD log-normal,
EAD de cauda pesada e devedores com várias operações, lida de arquivos parquet com
``pl.scan_parquet`` e configurada por um ``crplus.toml``.
"""

from __future__ import annotations

import json
import tempfile
from collections.abc import Iterator
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import numpy as np
import polars as pl
import pytest

from crplus import CRPlusConfig, CRPlusResult, load_config, run_creditrisk_plus
from crplus import api as crplus_api
from crplus.banding import Banding
from crplus.config import SectorVarianceConfig
from crplus.contributions import EL_COLUMN, SIGMA_COLUMN, alpha_label, es_column, var_column
from crplus.distribution import SectorModel
from crplus.montecarlo import MonteCarloSettings, simulate_losses, tail_estimate
from crplus.sectors import sector_parameters
from tests.pipeline import aggregate, source_of
from tests.synthetic import PortfolioSpec, make_portfolio

pytestmark = pytest.mark.integration

GOLDEN = Path(__file__).parent / "golden" / "end_to_end.json"
SPEC = PortfolioSpec(n_obligors=200_000, n_sectors=8, max_ops_per_obligor=4, seed=2024)
ALPHAS = (0.99, 0.999)
TARGET_BANDS = 150
MC_SCENARIOS = 2_000_000
SAME = 1e-9
"""Tolerância de "resultados idênticos": as reduções paralelas do polars somam em ordem
não determinística, então execuções equivalentes diferem no último dígito (~1e-11 relativo)."""


@dataclass(frozen=True)
class Workspace:
    """Diretório com a carteira em parquet e o TOML."""

    root: Path
    data: pl.DataFrame
    config_path: Path

    def scan(self) -> pl.LazyFrame:
        return pl.scan_parquet(self.root / "carteira" / "*.parquet")

    def config(self, output: str, **sections: Any) -> CRPlusConfig:
        config = load_config(self.config_path)
        config = replace(config, output=replace(config.output, directory=Path(output)))
        return replace(config, **sections)


def _write_toml(path: Path, loss_unit: float) -> None:
    path.write_text(
        "\n".join(
            [
                "[model]",
                f"alphas = [{', '.join(repr(a) for a in ALPHAS)}]",
                f"loss_unit = {loss_unit!r}",
                "[output]",
                'directory = "saida"',
            ]
        ),
        encoding="utf-8",
    )


@pytest.fixture(scope="module")
def workspace(tmp_path_factory: pytest.TempPathFactory) -> Workspace:
    root = tmp_path_factory.mktemp("e2e")
    data = make_portfolio(SPEC)
    folder = root / "carteira"
    folder.mkdir()
    for i, part in enumerate(data.iter_slices(n_rows=data.height // 4 + 1)):
        part.write_parquet(folder / f"part-{i}.parquet", row_group_size=50_000)
    exposure = data.group_by("obligor_id").agg((pl.col("lgd") * pl.col("ead")).sum())
    loss_unit = float(exposure["lgd"].max()) / TARGET_BANDS  # type: ignore[arg-type]
    _write_toml(root / "crplus.toml", loss_unit)
    return Workspace(root, data, root / "crplus.toml")


@pytest.fixture(scope="module")
def scratch(tmp_path_factory: pytest.TempPathFactory) -> Iterator[Path]:
    directory = tmp_path_factory.mktemp("scratch")
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(tempfile, "tempdir", str(directory))
        yield directory


@pytest.fixture(scope="module")
def result(workspace: Workspace, scratch: Path) -> CRPlusResult:
    return run_creditrisk_plus(workspace.scan(), workspace.config("saida_lazy"))


def _measures(result: CRPlusResult) -> list[float]:
    return [result.el, result.ul, *result.var.values(), *result.es.values()]


# 0 e 10 ---------------------------------------------------------------------------------------


def test_e2e_runs_from_toml_and_scan_parquet_without_alerts(
    result: CRPlusResult, workspace: Workspace, scratch: Path
) -> None:
    """Intenção: a API pública roda a partir de um TOML e de pl.scan_parquet, sem alertas,
    e remove o diretório temporário. Se falhar, o caminho de produção não está íntegro."""
    assert result.diagnostics.n_operations == workspace.data.height
    assert result.diagnostics.alerts == ()
    assert list(scratch.iterdir()) == []


def test_e2e_temporary_directory_is_removed_when_run_fails(
    workspace: Workspace, scratch: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Intenção: mesmo com falha no meio do cálculo, os temporários são apagados.
    Se falhar, tabelas de devedores ficariam no disco após um erro."""

    def boom(*_args: object) -> None:
        raise RuntimeError

    monkeypatch.setattr(crplus_api, "_distribution", boom)

    with pytest.raises(RuntimeError):
        run_creditrisk_plus(workspace.scan(), workspace.config("saida_falha"))

    assert list(scratch.iterdir()) == []


# 1 e 2 ----------------------------------------------------------------------------------------


@pytest.mark.parametrize("kind", ["eager", "pandas"])
def test_e2e_dataframe_and_pandas_inputs_match_lazyframe(
    result: CRPlusResult, workspace: Workspace, kind: str
) -> None:
    """Intenção: LazyFrame, DataFrame e pandas produzem resultados idênticos.
    Se falhar, o tipo de entrada alteraria as medidas de risco."""
    data = {"eager": workspace.data, "pandas": workspace.data.to_pandas()}[kind]

    other = run_creditrisk_plus(data, workspace.config(f"saida_{kind}"))

    assert _measures(other) == pytest.approx(_measures(result), rel=SAME)


def test_e2e_partitioned_run_matches_single_partition(
    result: CRPlusResult, workspace: Workspace
) -> None:
    """Intenção: 1 partição e N partições produzem resultados idênticos.
    Se falhar, o resultado dependeria do orçamento de memória."""
    config = workspace.config("saida_particoes")
    config = replace(config, resources=replace(config.resources, obligor_partitions=4))

    other = run_creditrisk_plus(workspace.scan(), config)

    assert other.diagnostics.partitions == 4
    assert _measures(other) == pytest.approx(_measures(result), rel=SAME)


# 3 --------------------------------------------------------------------------------------------


def test_e2e_distribution_sums_to_one_and_matches_analytic_moments(result: CRPlusResult) -> None:
    """Intenção: a distribuição soma 1 e reproduz média e variância analíticas (rel 1e-8).
    Se falhar, a grade ou o motor estariam truncando ou distorcendo a distribuição."""
    grid = result.diagnostics.grid

    assert grid.total_mass == pytest.approx(1.0, abs=1e-12)
    assert grid.mean_error < 1e-8
    assert grid.variance_error < 1e-8


# 4 --------------------------------------------------------------------------------------------


def _model_for(workspace: Workspace, result: CRPlusResult, directory: Path) -> SectorModel:
    banding = Banding(result.diagnostics.loss_unit)
    agg = aggregate(workspace.data, banding, directory)
    sectors = source_of(workspace.data).sectors
    params = sector_parameters(agg, sectors, SectorVarianceConfig())
    return SectorModel(agg.intensity, params.variance)


def test_e2e_var_and_es_within_monte_carlo_confidence_interval(
    result: CRPlusResult, workspace: Workspace, tmp_path: Path
) -> None:
    """Intenção: VaR e ES a 99,9% caem no intervalo de confiança de um Monte Carlo com 2 milhões
    de cenários (oráculo independente). Se falhar, o motor analítico diverge do modelo simulado."""
    model = _model_for(workspace, result, tmp_path)
    losses = simulate_losses(model, MonteCarloSettings(MC_SCENARIOS, seed=77))

    estimate = tail_estimate(losses, 0.999, result.diagnostics.loss_unit)

    assert abs(result.es[0.999] - estimate.es) < 4 * estimate.es_se
    assert (
        abs(result.var[0.999] - estimate.var) <= 4 * estimate.var_se + result.diagnostics.loss_unit
    )


# 5 --------------------------------------------------------------------------------------------


def test_e2e_fft_engine_matches_panjer_engine(result: CRPlusResult, workspace: Workspace) -> None:
    """Intenção: motor FFT == motor Panjer na carteira completa.
    Se falhar, o motor principal tem erro numérico relevante em escala realista."""
    config = workspace.config("saida_panjer")
    config = replace(config, model=replace(config.model, engine="panjer"))

    panjer = run_creditrisk_plus(workspace.scan(), config)
    size = min(panjer.loss_distribution.probs.shape[0], result.loss_distribution.probs.shape[0])
    delta = panjer.loss_distribution.probs[:size] - result.loss_distribution.probs[:size]

    assert np.max(np.abs(delta)) < 1e-10
    assert _measures(panjer) == pytest.approx(_measures(result), rel=1e-9)


# 6 e 9 ----------------------------------------------------------------------------------------


def test_e2e_contribution_parquet_sums_match_portfolio_measures(result: CRPlusResult) -> None:
    """Intenção: as somas por coluna do parquet de contribuições fecham nas medidas (Euler).
    Se falhar, o arquivo entregue ao usuário não reconciliaria com o portfólio."""
    frame = pl.scan_parquet(result.contributions_path / "part-*.parquet")  # type: ignore[operator]
    columns = [EL_COLUMN, SIGMA_COLUMN, *(f(a) for a in ALPHAS for f in (var_column, es_column))]
    sums = frame.select(pl.col(columns).sum()).collect().row(0, named=True)
    expected = {EL_COLUMN: result.el, SIGMA_COLUMN: result.ul}
    expected |= {var_column(a): result.var[a] for a in ALPHAS}
    expected |= {es_column(a): result.es[a] for a in ALPHAS}

    assert {k: sums[k] for k in expected} == pytest.approx(expected, rel=1e-8)


def test_e2e_contribution_parquet_has_one_row_per_operation(
    result: CRPlusResult, workspace: Workspace
) -> None:
    """Intenção: uma linha por operação válida, com o operation_id original.
    Se falhar, contribuições estariam faltando ou duplicadas."""
    frame = pl.scan_parquet(result.contributions_path / "part-*.parquet")  # type: ignore[operator]
    ids = frame.select("operation_id").collect()["operation_id"]

    assert ids.len() == workspace.data.height
    assert ids.n_unique() == workspace.data.height


def test_e2e_summary_json_is_consistent_with_result(result: CRPlusResult) -> None:
    """Intenção: summary.json reflete as medidas e o hash do TOML usado.
    Se falhar, o resumo gravado não seria uma prova reprodutível do resultado."""
    summary = json.loads(result.summary_path.read_text(encoding="utf-8"))

    assert summary["es"][alpha_label(0.999)] == pytest.approx(result.es[0.999])
    assert summary["el"] == pytest.approx(result.el)
    assert len(summary["config_sha256"]) == 64


# 7 --------------------------------------------------------------------------------------------


def _golden_payload(result: CRPlusResult) -> dict[str, float]:
    payload = {
        "el": result.el,
        "ul": result.ul,
        "loss_unit": result.diagnostics.loss_unit,
        "grid_size": float(result.diagnostics.grid.grid_size),
        "n_operations": float(result.diagnostics.n_operations),
    }
    payload |= {f"var_{alpha_label(a)}": v for a, v in result.var.items()}
    return payload | {f"es_{alpha_label(a)}": v for a, v in result.es.items()}


def test_e2e_matches_golden_file(result: CRPlusResult, request: pytest.FixtureRequest) -> None:
    """Intenção: regressão — o resultado da carteira de referência não muda sem decisão explícita.
    Se falhar, uma alteração mudou números; atualize só com --update-golden e justificativa."""
    payload = _golden_payload(result)
    if request.config.getoption("--update-golden"):
        GOLDEN.parent.mkdir(exist_ok=True)
        GOLDEN.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))

    assert payload == pytest.approx(golden, rel=1e-9)


# 8 --------------------------------------------------------------------------------------------


def test_e2e_external_variances_equal_to_pd_vol_reproduce_result(
    result: CRPlusResult, workspace: Workspace
) -> None:
    """Intenção: o método 'external' com as variâncias implícitas da pd_vol reproduz 'pd_vol'.
    Se falhar, os dois métodos de variância setorial não seriam o mesmo modelo."""
    sectors = result.sectors.filter(pl.col("sector") != "idiossincratico")
    values = dict(zip(sectors["sector"], sectors["v_k_pd_vol"], strict=True))
    config = workspace.config(
        "saida_external",
        sector_variance=SectorVarianceConfig(method="external", values=values),
    )

    other = run_creditrisk_plus(workspace.scan(), config)

    assert _measures(other) == pytest.approx(_measures(result), rel=SAME)
`````

<!-- FILE: tests/pipeline.py -->
`````python
"""Atalhos de teste que encadeiam os passos A a D sobre um DataFrame pequeno."""

from __future__ import annotations

from dataclasses import dataclass
from functools import reduce
from pathlib import Path

import polars as pl

from crplus.aggregation import SectorBandAggregate, aggregate_partition
from crplus.banding import Banding
from crplus.config import ColumnMap, NumericsConfig, SectorVarianceConfig
from crplus.contributions import (
    ContributionInputs,
    ContributionPlanInputs,
    ContributionTables,
    contribution_plan,
    contribution_tables,
    write_contributions,
)
from crplus.distribution import GridRequest, SectorModel, compute_distribution, make_engine
from crplus.memory import MemoryBudget
from crplus.moments import Moments, analytic_moments
from crplus.obligor import build_obligor_table
from crplus.risk_measures import RiskMeasures, risk_measures
from crplus.sectors import sector_parameters
from crplus.sources import PortfolioSource, iter_partitions, normalize_source


def source_of(data: pl.DataFrame) -> PortfolioSource:
    """Normaliza um DataFrame com a configuração de colunas padrão."""
    return normalize_source(data, ColumnMap(), "float64", 1000)


def _table(directory: Path, partitions: int, part: int) -> Path:
    return directory / f"obligors-{partitions}-{part}.parquet"


def aggregate(
    data: pl.DataFrame, banding: Banding, directory: Path, partitions: int = 1
) -> SectorBandAggregate:
    """Executa os passos A e B e devolve o agregado setorial somado."""
    source = source_of(data)
    parts: list[SectorBandAggregate] = []
    for p, frame in enumerate(iter_partitions(source, partitions)):
        table = _table(directory, partitions, p)
        build_obligor_table(frame, source.n_sectors, table)
        parts.append(aggregate_partition(frame, table, source.n_sectors, banding))
    return reduce(lambda a, b: a + b, parts, SectorBandAggregate.empty(source.n_sectors))


@dataclass(frozen=True)
class SmallRun:
    """Resultado de uma execução de teste dos passos A a D."""

    model: SectorModel
    moments: Moments
    measures: RiskMeasures
    tables: ContributionTables
    contributions: pl.DataFrame
    expected_loss: float


def run_model(
    data: pl.DataFrame,
    banding: Banding,
    directory: Path,
    alphas: tuple[float, ...] = (0.99, 0.999),
    window: int = 0,
) -> SmallRun:
    """Executa o modelo completo (motor FFT, uma partição) e lê as contribuições."""
    directory.mkdir(parents=True, exist_ok=True)
    source = source_of(data)
    agg = aggregate(data, banding, directory)
    params = sector_parameters(agg, source.sectors, SectorVarianceConfig())
    model = SectorModel(agg.intensity, params.variance)
    moments = analytic_moments(model.intensity, model.variance)
    request = GridRequest(model, moments, NumericsConfig(), MemoryBudget.from_gb(2.0))
    dist, _ = compute_distribution(make_engine("fft", 1, 1e-13), request)
    expected_loss = moments.expected_loss * banding.loss_unit
    measures = risk_measures(dist.probs, alphas, banding.loss_unit, expected_loss)
    tables = contribution_tables(ContributionInputs(dist, model, moments, measures, window))
    plan_inputs = ContributionPlanInputs(_table(directory, 1, 0), tables, banding, source.n_sectors)
    output = directory / "contributions.parquet"
    write_contributions(contribution_plan(source.frame, plan_inputs), output)
    return SmallRun(model, moments, measures, tables, pl.read_parquet(output), expected_loss)
`````

<!-- FILE: tests/synthetic.py -->
`````python
"""Geradores sintéticos de carteiras, determinísticos por seed."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import polars as pl


@dataclass(frozen=True)
class PortfolioSpec:
    """Parâmetros da carteira sintética."""

    n_obligors: int = 200
    n_sectors: int = 3
    max_ops_per_obligor: int = 3
    seed: int = 7
    pd_median: float = 0.01
    pd_sigma: float = 0.8
    vol_ratio: float = 0.6
    ead_scale: float = 1000.0
    pareto_shape: float = 2.5
    residual_share: float = 0.2


def make_portfolio(spec: PortfolioSpec | None = None) -> pl.DataFrame:
    """Carteira com PD log-normal, EAD de cauda pesada e devedores com várias operações.

    PD, ``pd_vol`` e pesos são iguais entre as operações de um mesmo devedor.
    """
    spec = spec or PortfolioSpec()
    rng = np.random.default_rng(spec.seed)
    n_obl = spec.n_obligors
    ops = rng.integers(1, spec.max_ops_per_obligor + 1, size=n_obl)
    obligor = np.repeat(np.arange(n_obl, dtype=np.int64) * 7 + 3, ops)
    pd_obl = np.clip(spec.pd_median * rng.lognormal(0.0, spec.pd_sigma, n_obl), 1e-5, 0.25)
    vol_obl = pd_obl * spec.vol_ratio
    n_ops = int(ops.sum())
    columns: dict[str, object] = {
        "operation_id": np.arange(n_ops, dtype=np.int64) + 1_000,
        "obligor_id": obligor,
        "pd": np.repeat(pd_obl, ops),
        "pd_vol": np.repeat(vol_obl, ops),
        "lgd": rng.uniform(0.1, 0.9, n_ops),
        "ead": spec.ead_scale * (rng.pareto(spec.pareto_shape, n_ops) + 0.05),
    }
    if spec.n_sectors:
        raw = rng.dirichlet(np.ones(spec.n_sectors), size=n_obl) * (1.0 - spec.residual_share)
        for k in range(spec.n_sectors):
            columns[f"w_s{k + 1}"] = np.repeat(raw[:, k], ops)
    return pl.DataFrame(columns)
`````

<!-- FILE: tests/unit/__init__.py -->
`````python
`````

<!-- FILE: tests/unit/test_aggregation.py -->
`````python
from __future__ import annotations

from pathlib import Path

import numpy as np
import polars as pl
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from crplus.aggregation import SectorBandAggregate, sector_weights
from crplus.banding import Banding
from tests.pipeline import aggregate
from tests.synthetic import PortfolioSpec, make_portfolio

BANDING = Banding(250.0)


def _assert_same(a: SectorBandAggregate, b: SectorBandAggregate) -> None:
    np.testing.assert_allclose(a.intensity, b.intensity, rtol=1e-12, atol=1e-15)
    np.testing.assert_allclose(a.volatility, b.volatility, rtol=1e-12)
    np.testing.assert_allclose(a.raw_volatility, b.raw_volatility, rtol=1e-12)
    np.testing.assert_allclose(a.raw_intensity, b.raw_intensity, rtol=1e-12)
    assert a.n_rows == b.n_rows


@settings(max_examples=10)
@given(partitions=st.integers(2, 6), seed=st.integers(0, 10_000))
def test_aggregation_partitions_sum_to_whole_regardless_of_row_order(
    tmp_path: Path, partitions: int, seed: int
) -> None:
    """Intenção: agregados de partições somados == agregado da base inteira, em qualquer ordem.
    Se falhar, o resultado dependeria do número de partições ou da ordem das linhas na fonte."""
    data = make_portfolio()
    shuffled = data.sample(fraction=1.0, shuffle=True, seed=seed)

    whole = aggregate(data, BANDING, tmp_path, 1)
    parts = aggregate(shuffled, BANDING, tmp_path, partitions)

    _assert_same(whole, parts)


def _explicit_obligor_intensity(data: pl.DataFrame, loss_unit: float) -> np.ndarray:
    weights = [c for c in data.columns if c.startswith("w_")]
    obligors = data.group_by("obligor_id").agg(
        (pl.col("lgd") * pl.col("ead")).sum().alias("e"),
        pl.col("pd").first(),
        *[pl.col(w).first() for w in weights],
    )
    bands = np.maximum(1, np.ceil(obligors["e"].to_numpy() * (1 - 1e-12) / loss_unit)).astype(int)
    adjusted = obligors["pd"].to_numpy() * obligors["e"].to_numpy() / (bands * loss_unit)
    w = obligors.select(weights).to_numpy()
    w_all = np.column_stack([1.0 - w.sum(axis=1), w])
    result = np.zeros((len(weights) + 1, bands.max() + 1))
    for k in range(len(weights) + 1):
        np.add.at(result[k], bands, w_all[:, k] * adjusted)
    return result


def test_aggregation_linear_per_operation_equals_explicit_obligor_model(tmp_path: Path) -> None:
    """Intenção: a formulação linear por operação coincide com o CR+ por devedor (PD/pesos iguais).
    Se falhar, a simplificação de memória da §5.0 mudaria o modelo."""
    data = make_portfolio()

    agg = aggregate(data, BANDING, tmp_path)

    np.testing.assert_allclose(agg.intensity, _explicit_obligor_intensity(data, 250.0), rtol=1e-12)


def test_aggregation_residual_weight_goes_to_idiosyncratic_sector(tmp_path: Path) -> None:
    """Intenção: o resíduo 1 - sum(w) vira intensidade do setor 0.
    Se falhar, parte da PD de cada operação desapareceria do modelo."""
    data = make_portfolio(PortfolioSpec(residual_share=0.3))
    expected = (data["pd"] * data["lgd"] * data["ead"]).sum()

    agg = aggregate(data, BANDING, tmp_path)
    share = (agg.intensity[0] @ np.arange(agg.max_band + 1)) * 250.0 / expected

    assert share == pytest.approx(0.3, rel=1e-12)


def test_aggregation_empty_is_neutral_for_addition(tmp_path: Path) -> None:
    """Intenção: o agregado vazio é o elemento neutro da soma entre partições.
    Se falhar, partições vazias alterariam o resultado."""
    agg = aggregate(make_portfolio(), BANDING, tmp_path)

    _assert_same(SectorBandAggregate.empty(3) + agg, agg)


def test_aggregation_renormalizes_weights_slightly_above_one() -> None:
    """Intenção: soma de pesos 1+eps (dentro da tolerância) é renormalizada: w0 >= 0, soma = 1.
    Se falhar, o setor 0 receberia intensidade negativa e a perda esperada mudaria."""
    frame = pl.DataFrame({"_w1": [0.5], "_w2": [0.5 + 1e-10]})

    values = frame.select([w.alias(f"k{k}") for k, w in enumerate(sector_weights(2))]).row(0)

    assert min(values) >= 0.0
    assert sum(values) == pytest.approx(1.0, abs=1e-15)


def test_aggregation_without_sectors_is_fully_idiosyncratic(tmp_path: Path) -> None:
    """Intenção: sem colunas de peso, toda a intensidade fica no setor 0.
    Se falhar, o caso K = 0 perderia intensidade."""
    agg = aggregate(make_portfolio(PortfolioSpec(n_sectors=0)), BANDING, tmp_path)

    assert agg.n_sectors == 0
    assert agg.raw_intensity[0] > 0


def test_aggregation_of_empty_partition_is_empty_aggregate(tmp_path: Path) -> None:
    """Intenção: uma partição sem linhas produz o agregado vazio, sem erro.
    Se falhar, o hash que deixa uma partição vazia derrubaria o passo B."""
    data = make_portfolio().filter(pl.col("obligor_id") < 0)

    agg = aggregate(data, BANDING, tmp_path)

    assert (agg.n_rows, agg.max_band) == (0, 0)
`````

<!-- FILE: tests/unit/test_api.py -->
`````python
from __future__ import annotations

import json
import tempfile
from dataclasses import replace
from pathlib import Path
from typing import Any

import numpy as np
import polars as pl
import pytest

from crplus import api
from crplus.api import prepare_output, resolve_partitions, run_creditrisk_plus
from crplus.config import CRPlusConfig, ResourcesConfig, config_from_mapping
from crplus.contributions import es_column, var_column
from crplus.exceptions import (
    ConfigError,
    GridTooSmallError,
    InputValidationError,
    MemoryBudgetError,
)
from crplus.results import CRPlusResult
from tests.synthetic import PortfolioSpec, make_portfolio

DATA = make_portfolio(PortfolioSpec(n_obligors=400, n_sectors=3, seed=5))


def _config(tmp_path: Path, **sections: dict[str, Any]) -> CRPlusConfig:
    raw: dict[str, Any] = {"model": {"loss_unit": 250.0}, "output": {"directory": "out"}}
    for name, values in sections.items():
        raw[name] = {**raw.get(name, {}), **values}
    return config_from_mapping(raw, base_dir=tmp_path)


def _measures(result: CRPlusResult) -> list[float]:
    return [result.el, result.ul, *result.var.values(), *result.es.values()]


@pytest.fixture(scope="module")
def baseline(tmp_path_factory: pytest.TempPathFactory) -> CRPlusResult:
    return run_creditrisk_plus(DATA, _config(tmp_path_factory.mktemp("base")))


def test_api_writes_summary_distribution_and_contributions(baseline: CRPlusResult) -> None:
    """Intenção: a execução grava summary.json, a distribuição e o parquet de contribuições.
    Se falhar, o usuário não teria as saídas documentadas em §6.4."""
    summary = json.loads(baseline.summary_path.read_text(encoding="utf-8"))
    parts = sorted(baseline.contributions_path.glob("part-*.parquet"))  # type: ignore[union-attr]

    assert summary["var"]["0.999"] == pytest.approx(baseline.var[0.999])
    assert (baseline.summary_path.parent / "loss_distribution.parquet").exists()
    assert pl.read_parquet(parts).height == DATA.height


def test_api_summary_has_no_identifiers(tmp_path: Path) -> None:
    """Intenção: o summary.json contém só agregados — nenhum id de operação ou devedor.
    Se falhar, um arquivo de resumo compartilhável vazaria identificadores da carteira."""
    data = DATA.with_columns(
        obligor_id=pl.format("DEVEDOR-{}", "obligor_id"),
        operation_id=pl.format("OPERACAO-{}", "operation_id"),
    )
    result = run_creditrisk_plus(data, _config(tmp_path))

    text = result.summary_path.read_text(encoding="utf-8")

    assert "DEVEDOR-" not in text
    assert "OPERACAO-" not in text


def test_api_clean_portfolio_has_no_alerts(baseline: CRPlusResult) -> None:
    """Intenção: carteira consistente e dentro das tolerâncias não gera alertas.
    Se falhar, alertas espúrios esconderiam problemas reais."""
    assert baseline.diagnostics.alerts == ()


def test_api_euler_sums_close_from_written_parquet(baseline: CRPlusResult) -> None:
    """Intenção: as somas das colunas do parquet fecham nas medidas (lidas do disco).
    Se falhar, o parquet gravado não corresponde às medidas reportadas."""
    assert max(baseline.diagnostics.euler_errors.values()) < 1e-8


@pytest.mark.parametrize("convert", [lambda d: d.lazy(), lambda d: d.to_pandas()])
def test_api_lazy_and_pandas_inputs_match_dataframe(
    tmp_path: Path, baseline: CRPlusResult, convert: Any
) -> None:
    """Intenção: LazyFrame, DataFrame e pandas produzem o mesmo resultado.
    Se falhar, o tipo da entrada alteraria as medidas de risco."""
    result = run_creditrisk_plus(convert(DATA), _config(tmp_path))

    assert _measures(result) == pytest.approx(_measures(baseline), rel=1e-12)


def test_api_partitioned_run_matches_single_partition(
    tmp_path: Path, baseline: CRPlusResult
) -> None:
    """Intenção: N partições por hash produzem o mesmo resultado que uma partição.
    Se falhar, o resultado dependeria do orçamento de memória."""
    config = _config(tmp_path, resources={"obligor_partitions": 3})

    result = run_creditrisk_plus(DATA, config)

    assert result.diagnostics.partitions == 3
    assert _measures(result) == pytest.approx(_measures(baseline), rel=1e-12)


def test_api_panjer_engine_matches_fft(tmp_path: Path, baseline: CRPlusResult) -> None:
    """Intenção: o motor de referência reproduz o motor principal ponta a ponta.
    Se falhar, há divergência numérica entre os motores na configuração real."""
    result = run_creditrisk_plus(DATA, _config(tmp_path, model={"engine": "panjer"}))

    np.testing.assert_allclose(
        result.loss_distribution.probs[:2000], baseline.loss_distribution.probs[:2000], atol=1e-10
    )


def test_api_automatic_loss_unit_respects_limits(tmp_path: Path) -> None:
    """Intenção: L0 automático produz uma grade dentro de max_grid e bandas dentro de max_bands.
    Se falhar, a configuração padrão (loss_unit = 'auto') estouraria os limites."""
    numerics = {"max_bands": 500, "max_grid": 1 << 14}
    config = _config(tmp_path, model={"loss_unit": "auto"}, numerics=numerics)

    result = run_creditrisk_plus(DATA, config)

    assert result.diagnostics.max_band <= 500
    assert result.diagnostics.grid.grid_size <= 1 << 14


def test_api_automatic_loss_unit_refines_for_strong_sector_variance(tmp_path: Path) -> None:
    """Intenção: quando a variância setorial supera a estimativa inicial, L0 é recalibrado.
    Se falhar, carteiras muito correlacionadas gerariam GridTooSmallError com L0 automático."""
    data = make_portfolio(PortfolioSpec(n_obligors=400, vol_ratio=4.0, residual_share=0.0))
    numerics = {"max_bands": 200, "max_grid": 1 << 12}
    config = _config(tmp_path, model={"loss_unit": "auto"}, numerics=numerics)

    result = run_creditrisk_plus(data, config)

    assert result.diagnostics.grid.grid_size <= 1 << 12


def test_api_non_strict_mode_excludes_invalid_rows_and_alerts(tmp_path: Path) -> None:
    """Intenção: com strict = false, linhas inválidas saem do cálculo e geram alerta.
    Se falhar, linhas inválidas entrariam no modelo ou seriam excluídas silenciosamente."""
    data = DATA.with_columns(pd=pl.when(pl.col("operation_id") == 1000).then(2.0).otherwise("pd"))

    result = run_creditrisk_plus(data, _config(tmp_path, validation={"strict": False}))
    written = pl.read_parquet(result.contributions_path / "part-*.parquet")  # type: ignore[operator]

    assert written.height == DATA.height - 1
    assert any("pd_domain" in alert for alert in result.diagnostics.alerts)


def test_api_strict_mode_rejects_invalid_portfolio(tmp_path: Path) -> None:
    """Intenção: em modo estrito (padrão), qualquer linha inválida interrompe a execução.
    Se falhar, dados inválidos seriam processados por padrão."""
    data = DATA.with_columns(
        ead=pl.when(pl.col("operation_id") == 1000).then(-1.0).otherwise("ead")
    )

    with pytest.raises(InputValidationError):
        run_creditrisk_plus(data, _config(tmp_path))


def test_api_without_contributions_skips_pass_d(tmp_path: Path) -> None:
    """Intenção: write_contributions = false não grava o parquet de contribuições.
    Se falhar, a opção de economizar o passo D (o mais caro em disco) não funcionaria."""
    result = run_creditrisk_plus(DATA, _config(tmp_path, output={"write_contributions": False}))

    assert result.contributions_path is None
    assert result.diagnostics.euler_errors == {}


def test_api_can_skip_operation_id_uniqueness_check(tmp_path: Path) -> None:
    """Intenção: check_operation_id_unique = false evita a passada de unicidade (cara em memória).
    Se falhar, bases enormes não teriam como desligar essa checagem."""
    config = _config(tmp_path, validation={"check_operation_id_unique": False})

    result = run_creditrisk_plus(DATA, config)

    assert result.diagnostics.validation.duplicate_operation_ids == 0


def test_api_refuses_to_overwrite_previous_outputs(tmp_path: Path, baseline: CRPlusResult) -> None:
    """Intenção: saídas existentes não são sobrescritas sem overwrite = true.
    Se falhar, uma execução apagaria resultados anteriores sem consentimento."""
    config = _config(tmp_path)
    run_creditrisk_plus(DATA, config)

    with pytest.raises(ConfigError) as error:
        prepare_output(config.output)

    assert error.value.field == "output.directory"


def test_api_overwrite_removes_only_crplus_outputs(tmp_path: Path) -> None:
    """Intenção: overwrite = true remove apenas arquivos do crplus, não outros do usuário.
    Se falhar, o diretório de saída poderia perder arquivos alheios ao crplus."""
    config = _config(tmp_path, output={"overwrite": True})
    run_creditrisk_plus(DATA, config)
    keep = config.output.directory / "anotacoes.txt"
    keep.write_text("x", encoding="utf-8")

    prepare_output(config.output)

    assert keep.exists()
    assert not (config.output.directory / "summary.json").exists()
    assert list(config.output.contributions_path.glob("part-*.parquet")) == []


def test_api_resolves_partitions_from_budget() -> None:
    """Intenção: 'auto' usa o orçamento; valor fixo pequeno demais é rejeitado antes de alocar.
    Se falhar, a tabela de devedores de uma partição estouraria a memória."""
    tight = ResourcesConfig(memory_budget_gb=0.001, obligor_partitions="auto")
    fixed = ResourcesConfig(memory_budget_gb=0.001, obligor_partitions=1)

    assert resolve_partitions(tight, 1_000_000, "int") > 1
    with pytest.raises(MemoryBudgetError):
        resolve_partitions(fixed, 1_000_000, "int")


def test_api_removes_temporary_directory_even_when_run_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Intenção: o diretório temporário (tabelas de devedores) é removido mesmo em falha.
    Se falhar, dados da carteira ficariam no disco após um erro."""
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(scratch))

    def boom(*_args: object) -> None:
        raise RuntimeError

    monkeypatch.setattr(api, "_distribution", boom)

    with pytest.raises(RuntimeError):
        run_creditrisk_plus(DATA, _config(tmp_path))

    assert list(scratch.iterdir()) == []


def test_api_sector_table_reports_all_sectors(baseline: CRPlusResult) -> None:
    """Intenção: result.sectors lista o idiossincrático e cada setor, com v_k implícito e usado.
    Se falhar, o usuário não conseguiria auditar a calibração setorial."""
    assert baseline.sectors["sector"].to_list() == ["idiossincratico", "w_s1", "w_s2", "w_s3"]
    assert {"v_k_pd_vol", "v_k_used", "el_k"} <= set(baseline.sectors.columns)
    assert baseline.sectors["el_k"].sum() == pytest.approx(baseline.el, rel=1e-12)


def test_api_contribution_columns_exist_for_each_alpha(baseline: CRPlusResult) -> None:
    """Intenção: há colunas rc_var/rc_es para cada alpha configurado.
    Se falhar, níveis de confiança do TOML ficariam sem contribuições."""
    columns = pl.read_parquet_schema(next(baseline.contributions_path.glob("*.parquet")))  # type: ignore[union-attr]

    assert {var_column(0.99), es_column(0.999)} <= set(columns)


def test_api_automatic_loss_unit_refines_when_poisson_estimate_underestimates_sigma(
    tmp_path: Path,
) -> None:
    """Intenção: L0 é recalibrado quando o sigma sistêmico excede a estimativa Poisson inicial.
    Se falhar, a grade estimada com sigma subestimado ultrapassaria max_grid."""
    data = make_portfolio(PortfolioSpec(n_obligors=400, vol_ratio=1.5, residual_share=0.0))
    numerics = {"max_bands": 2000, "max_grid": 1 << 12}
    config = _config(tmp_path, model={"loss_unit": "auto"}, numerics=numerics)

    result = run_creditrisk_plus(data, config)

    assert result.diagnostics.grid.grid_size <= 1 << 12


def test_api_automatic_loss_unit_gives_up_after_retries(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Intenção: se nenhuma unidade de perda converge, o erro é explícito (sem laço infinito).
    Se falhar, uma carteira inviável travaria a execução."""

    def never_converges(*_args: object) -> None:
        raise GridTooSmallError

    monkeypatch.setattr(api, "_distribution", never_converges)

    with pytest.raises(GridTooSmallError, match="L0"):
        run_creditrisk_plus(DATA, _config(tmp_path, model={"loss_unit": "auto"}))


def test_api_alerts_on_inconsistent_obligors(tmp_path: Path) -> None:
    """Intenção: devedor com PDs diferentes entre operações gera alerta nos diagnósticos.
    Se falhar, a combinação ponderada por EL seria aplicada sem o usuário saber."""
    first = DATA.row(0, named=True)
    twin = pl.DataFrame([{**first, "operation_id": -1, "pd": first["pd"] / 2}], schema=DATA.schema)

    result = run_creditrisk_plus(pl.concat([DATA, twin]), _config(tmp_path))

    assert any("inconsistentes" in alert for alert in result.diagnostics.alerts)


def test_api_alerts_on_banding_error(baseline: CRPlusResult) -> None:
    """Intenção: erro de banding acima da tolerância vira alerta.
    Se falhar, uma perda esperada viesada pelo banding passaria despercebida."""
    diagnostics = replace(baseline.diagnostics, banding_error=1e-3)

    assert api._numeric_alerts(diagnostics) == ["erro de banding acima da tolerância"]


def test_api_logs_when_polars_pool_differs_from_config(caplog: pytest.LogCaptureFixture) -> None:
    """Intenção: o usuário é avisado de que polars_threads só vale antes do import do polars.
    Se falhar, a configuração seria ignorada em silêncio."""
    with caplog.at_level("INFO"):
        api.configure_runtime(ResourcesConfig(polars_threads=pl.thread_pool_size() + 1))

    assert "POLARS_MAX_THREADS" in caplog.text


def test_api_automatic_loss_unit_stops_refining_after_limit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Intenção: a recalibração de L0 tem número máximo de iterações.
    Se falhar, uma grade que nunca cabe faria o passo B rodar indefinidamente."""
    monkeypatch.setattr(api, "_grid_fits", lambda *_args: False)

    with pytest.raises(GridTooSmallError, match="unidade de perda"):
        run_creditrisk_plus(DATA, _config(tmp_path, model={"loss_unit": "auto"}))
`````

<!-- FILE: tests/unit/test_banding.py -->
`````python
from __future__ import annotations

from pathlib import Path

import numpy as np
import polars as pl
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from crplus.banding import (
    DEGENERATE_LOSS_UNIT,
    Banding,
    LossUnitInputs,
    automatic_loss_unit,
)
from crplus.config import NumericsConfig
from crplus.exceptions import ConfigError
from tests.pipeline import aggregate
from tests.synthetic import PortfolioSpec, make_portfolio


def _bands(exposures: list[float], banding: Banding) -> list[int]:
    frame = pl.DataFrame({"e": exposures}, schema={"e": pl.Float64})
    return frame.select(banding.band(pl.col("e")))["e"].to_list()


@settings(max_examples=25)
@given(
    loss_unit=st.floats(min_value=1.0, max_value=20_000.0),
    seed=st.integers(0, 1000),
    rule=st.sampled_from(["ceil", "round"]),
)
def test_banding_preserves_expected_loss_for_any_loss_unit(
    tmp_path: Path, loss_unit: float, seed: int, rule: str
) -> None:
    """Intenção: o ajuste de PD no banding deve preservar exatamente a perda esperada do portfólio.
    Se falhar, EL e todas as medidas derivadas ficam viesadas pelo arredondamento de exposições."""
    data = make_portfolio(PortfolioSpec(n_obligors=60, seed=seed))
    expected = (data["pd"] * data["lgd"] * data["ead"]).sum()

    agg = aggregate(data, Banding(loss_unit, rule), tmp_path)
    banded = loss_unit * float(agg.intensity.sum(axis=0) @ np.arange(agg.max_band + 1))

    assert banded == pytest.approx(expected, rel=1e-12)


@pytest.mark.parametrize("rule", ["ceil", "round"])
def test_banding_band_is_at_least_one(rule: str) -> None:
    """Intenção: exposições nulas ou menores que L0 caem na banda 1 (nunca 0).
    Se falhar, perdas de pequenas exposições sumiriam da distribuição."""
    assert _bands([0.0, 1e-9, 0.3], Banding(1.0, rule)) == [1, 1, 1]


def test_banding_exact_multiple_falls_in_its_band() -> None:
    """Intenção: E_j = k·L0 cai na banda k, mesmo com erro de ponto flutuante na divisão.
    Se falhar, exposições exatas seriam empurradas para a banda seguinte pelo ceil."""
    loss_unit = 0.1
    exposures = [k * loss_unit for k in range(1, 200)]

    assert _bands(exposures, Banding(loss_unit)) == list(range(1, 200))


def test_banding_ceil_rounds_up_partial_units() -> None:
    """Intenção: com 'ceil', qualquer fração acima de k·L0 vai para a banda k+1.
    Se falhar, a regra conservadora de banding não estaria sendo aplicada."""
    assert _bands([10.01, 19.99], Banding(10.0)) == [2, 2]


def test_banding_round_rounds_half_away_from_zero() -> None:
    """Intenção: com 'round', meia unidade sobe (sem arredondamento bancário).
    Se falhar, a regra de banding mudaria conforme a paridade da banda."""
    assert _bands([14.9, 15.0, 25.0], Banding(10.0, "round")) == [1, 2, 3]


def test_banding_max_band_matches_expression() -> None:
    """Intenção: a maior banda calculada em Python coincide com a expressão polars.
    Se falhar, a checagem de max_bands avaliaria uma banda diferente da usada no modelo."""
    banding = Banding(0.37)

    assert banding.max_band(123.456) == _bands([123.456], banding)[0]


def test_banding_rejects_loss_unit_that_exceeds_max_bands() -> None:
    """Intenção: L0 minúsculo é bloqueado por max_bands (proteção de memória).
    Se falhar, uma unidade de perda errada alocaria grades gigantescas."""
    with pytest.raises(ConfigError) as error:
        Banding(1.0).check_max_band(1001.0, max_bands=1000)

    assert error.value.field == "model.loss_unit"


def test_banding_obligor_with_several_operations_uses_summed_exposure(tmp_path: Path) -> None:
    """Intenção: a banda é do devedor (exposição somada), não de cada operação.
    Se falhar, o default conjunto das operações de um devedor seria modelado como independente."""
    data = make_portfolio(PortfolioSpec(n_obligors=1, max_ops_per_obligor=1, n_sectors=0))
    data = pl.concat([data, data.with_columns(operation_id=pl.lit(1, dtype=pl.Int64))])
    data = data.with_columns(lgd=pl.lit(1.0), ead=pl.lit(30.0))

    agg = aggregate(data, Banding(10.0), tmp_path)

    assert agg.max_band == 6
    assert np.flatnonzero(agg.intensity[0]).tolist() == [6]


@given(
    max_exposure=st.floats(1.0, 1e9),
    expected_loss=st.floats(0.0, 1e9),
    std_dev=st.floats(0.0, 1e9),
)
def test_automatic_loss_unit_respects_band_and_grid_limits(
    max_exposure: float, expected_loss: float, std_dev: float
) -> None:
    """Intenção: L0 automático garante nu_max <= max_bands e grade estimada <= max_grid.
    Se falhar, a escolha automática produziria configurações rejeitadas ou estouro de memória."""
    numerics = NumericsConfig()
    inputs = LossUnitInputs(max_exposure, expected_loss, std_dev)

    unit = automatic_loss_unit(inputs, numerics)
    grid = (expected_loss + numerics.z_tail * std_dev + max_exposure) / unit + 2

    assert Banding(unit).max_band(max_exposure) <= numerics.max_bands
    assert grid <= numerics.max_grid


def test_automatic_loss_unit_is_binding_on_bands_for_concentrated_portfolio() -> None:
    """Intenção: L0 é o MENOR valor viável — sem folga além da margem numérica.
    Se falhar, o banding seria mais grosseiro (menos preciso) do que o necessário."""
    numerics = NumericsConfig()
    unit = automatic_loss_unit(LossUnitInputs(1e6, 10.0, 10.0), numerics)

    assert unit == pytest.approx(1e6 / numerics.max_bands, rel=1e-8)


def test_automatic_loss_unit_handles_portfolio_without_exposure() -> None:
    """Intenção: carteira sem exposição usa L0 = 1 (perda identicamente nula), sem dividir por 0.
    Se falhar, uma carteira toda com EAD = 0 derrubaria a execução."""
    unit = automatic_loss_unit(LossUnitInputs(0.0, 0.0, 0.0), NumericsConfig())

    assert unit == DEGENERATE_LOSS_UNIT


def test_banding_check_max_band_returns_band_within_limit() -> None:
    """Intenção: dentro do limite, a checagem devolve a maior banda para dimensionar as tabelas.
    Se falhar, configurações válidas seriam rejeitadas ou nu_max ficaria indefinido."""
    assert Banding(10.0).check_max_band(95.0, max_bands=10) == 10
`````

<!-- FILE: tests/unit/test_checks.py -->
`````python
from __future__ import annotations

import math

import pytest
from hypothesis import given
from hypothesis import strategies as st

from crplus._checks import (
    FieldCheck,
    either,
    int_between,
    is_int,
    is_optional,
    is_real,
    is_text,
    one_of,
    real_between,
    run_checks,
)
from crplus.exceptions import ConfigError


@pytest.mark.parametrize("value", [True, False])
def test_is_int_rejects_booleans_even_though_bool_subclasses_int(value: bool) -> None:
    """Intenção: `max_bands = true` no TOML não pode virar max_bands = 1.
    Se falhar, booleanos passam como inteiros e limites viram 0/1 silenciosamente."""
    assert not is_int(value)


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf, True, "1.0", None])
def test_is_real_rejects_non_finite_and_non_numeric_values(value: object) -> None:
    """Intenção: tolerâncias e limites só aceitam números reais finitos.
    Se falhar, NaN/inf entram na configuração e contaminam todos os cálculos."""
    assert not is_real(value)


@pytest.mark.parametrize("value", ["", "   ", 3, None])
def test_is_text_rejects_blank_or_non_string(value: object) -> None:
    """Intenção: nomes de coluna vazios ou não-string são inválidos.
    Se falhar, o select da base pediria uma coluna inexistente sem diagnóstico claro."""
    assert not is_text(value)


@given(st.floats(allow_nan=False, allow_infinity=False))
def test_real_between_closed_bounds_matches_interval_definition(value: float) -> None:
    """Intenção: o predicado de intervalo fechado deve coincidir com a definição matemática.
    Se falhar, valores de fronteira válidos (ex.: pd_warn_threshold = 1) seriam rejeitados."""
    predicate = real_between(-1.0, 1.0, closed_low=True, closed_high=True)

    assert predicate(value) == (-1.0 <= value <= 1.0)


@given(st.floats(allow_nan=False, allow_infinity=False))
def test_real_between_open_bounds_matches_interval_definition(value: float) -> None:
    """Intenção: o predicado de intervalo aberto exclui as fronteiras.
    Se falhar, tolerâncias iguais a 0 ou 1 seriam aceitas."""
    predicate = real_between(-1.0, 1.0, closed_low=False, closed_high=False)

    assert predicate(value) == (-1.0 < value < 1.0)


@given(st.integers(min_value=-10, max_value=10))
def test_int_between_matches_closed_interval(value: int) -> None:
    """Intenção: limites inteiros são inclusivos nas duas pontas.
    Se falhar, valores-limite documentados seriam rejeitados ou extrapolados."""
    assert int_between(-3, 3)(value) == (-3 <= value <= 3)


def test_combinators_accept_alternatives_and_none() -> None:
    """Intenção: 'auto' ou número e campos opcionais são expressos por combinadores.
    Se falhar, chaves como loss_unit e values_file não aceitam suas formas válidas."""
    auto_or_int = either(one_of("auto"), int_between(1, 5))
    optional_text = is_optional(is_text)

    assert [auto_or_int("auto"), auto_or_int(3), auto_or_int("x")] == [True, True, False]
    assert [optional_text(None), optional_text("a"), optional_text(1)] == [True, True, False]


def test_run_checks_raises_with_qualified_field_name() -> None:
    """Intenção: a primeira regra violada gera ConfigError com 'secao.campo'.
    Se falhar, o usuário não sabe qual chave do TOML corrigir."""

    class Section:
        size = -1

    checks = (FieldCheck("size", int_between(0, 10), "inteiro em [0, 10]"),)

    with pytest.raises(ConfigError) as error:
        run_checks(Section(), "numerics", checks)

    assert error.value.field == "numerics.size"
`````

<!-- FILE: tests/unit/test_config.py -->
`````python
from __future__ import annotations

import dataclasses
import hashlib
import math
from pathlib import Path
from typing import Any

import pytest

from crplus.config import (
    MAX_CONFIG_BYTES,
    ColumnMap,
    CRPlusConfig,
    ModelConfig,
    NumericsConfig,
    OutputConfig,
    ResourcesConfig,
    SectorVarianceConfig,
    ValidationConfig,
    config_from_mapping,
    load_config,
)
from crplus.exceptions import ConfigError


def _build(tmp_path: Path, raw: dict[str, Any]) -> CRPlusConfig:
    return config_from_mapping(raw, base_dir=tmp_path)


# --- arquivo de exemplo e leitura ------------------------------------------------------------


def test_load_config_example_file_matches_documented_defaults(example_config_path: Path) -> None:
    """Intenção: crplus.example.toml documenta exatamente os padrões do pacote.
    Se falhar, o exemplo comentado e o comportamento padrão divergiram."""
    loaded = load_config(example_config_path)
    defaults = CRPlusConfig(base_dir=example_config_path.parent)

    assert dataclasses.replace(loaded, source_sha256=None) == defaults


def test_load_config_records_sha256_of_file_bytes(example_config_path: Path) -> None:
    """Intenção: o hash do TOML usado vai para o summary.json (reprodutibilidade).
    Se falhar, não é possível provar com qual configuração um resultado foi gerado."""
    expected = hashlib.sha256(example_config_path.read_bytes()).hexdigest()

    assert load_config(example_config_path).source_sha256 == expected


def test_load_config_uses_config_directory_as_base(example_config_path: Path) -> None:
    """Intenção: caminhos relativos do TOML são resolvidos a partir do diretório do arquivo.
    Se falhar, a saída dependeria do diretório corrente de quem executa."""
    config = load_config(example_config_path)

    assert config.output.directory == (example_config_path.parent / "saida_crplus").resolve()


def test_load_config_rejects_missing_file(tmp_path: Path) -> None:
    """Intenção: arquivo inexistente gera ConfigError, não FileNotFoundError cru.
    Se falhar, o usuário recebe um traceback em vez de uma mensagem do pacote."""
    with pytest.raises(ConfigError, match="não encontrado"):
        load_config(tmp_path / "nao_existe.toml")


def test_load_config_rejects_invalid_toml(tmp_path: Path) -> None:
    """Intenção: TOML malformado gera ConfigError.
    Se falhar, erros de sintaxe escapam como exceções genéricas."""
    path = tmp_path / "c.toml"
    path.write_text("[model\nalphas = ", encoding="utf-8")

    with pytest.raises(ConfigError, match="TOML inválido"):
        load_config(path)


def test_load_config_rejects_non_utf8_file(tmp_path: Path) -> None:
    """Intenção: o arquivo deve ser UTF-8 (TOML exige).
    Se falhar, bytes inválidos causariam UnicodeDecodeError não tratado."""
    path = tmp_path / "c.toml"
    path.write_bytes(b"[model]\nengine = '\xff'\n")

    with pytest.raises(ConfigError, match="UTF-8"):
        load_config(path)


def test_load_config_rejects_oversized_file(tmp_path: Path) -> None:
    """Intenção: arquivos de configuração enormes são recusados antes da leitura (DoS).
    Se falhar, um arquivo gigante seria carregado inteiro em memória."""
    path = tmp_path / "c.toml"
    path.write_bytes(b"#" * (MAX_CONFIG_BYTES + 1))

    with pytest.raises(ConfigError, match="1 MiB"):
        load_config(path)


def test_load_config_rejects_symlinked_file(tmp_path: Path, symlink_dir: Path) -> None:
    """Intenção: o próprio TOML não pode ser um link simbólico.
    Se falhar, um link poderia apontar para um arquivo fora do controle do usuário."""
    target = tmp_path / "real.toml"
    target.write_text("", encoding="utf-8")
    link = symlink_dir / "c.toml"
    link.symlink_to(target)

    with pytest.raises(ConfigError, match="links simbólicos"):
        load_config(link)


# --- estrutura ------------------------------------------------------------------------------


def test_config_rejects_unknown_section(tmp_path: Path) -> None:
    """Intenção: seções desconhecidas (ex.: erro de digitação) são rejeitadas.
    Se falhar, uma seção com nome errado seria ignorada e os padrões usados sem aviso."""
    with pytest.raises(ConfigError) as error:
        _build(tmp_path, {"modle": {}})

    assert error.value.field == "modle"


def test_config_rejects_unknown_key_with_qualified_name(tmp_path: Path) -> None:
    """Intenção: chaves desconhecidas são rejeitadas apontando 'secao.chave'.
    Se falhar, um parâmetro digitado errado seria silenciosamente ignorado."""
    with pytest.raises(ConfigError) as error:
        _build(tmp_path, {"numerics": {"max_band": 10}})

    assert error.value.field == "numerics.max_band"


def test_config_rejects_section_that_is_not_a_table(tmp_path: Path) -> None:
    """Intenção: `model = 3` não é uma seção válida.
    Se falhar, a construção da seção quebraria com TypeError genérico."""
    with pytest.raises(ConfigError) as error:
        _build(tmp_path, {"model": 3})

    assert error.value.field == "model"


def test_config_rejects_section_object_of_wrong_type(tmp_path: Path) -> None:
    """Intenção: construção programática com seção do tipo errado é rejeitada.
    Se falhar, uma seção trocada (ex.: numerics no lugar de model) passaria sem validação."""
    with pytest.raises(ConfigError) as error:
        CRPlusConfig(model=NumericsConfig(), base_dir=tmp_path)  # type: ignore[arg-type]

    assert error.value.field == "model"


def test_config_is_immutable(tmp_path: Path) -> None:
    """Intenção: a configuração validada não pode ser alterada depois de criada.
    Se falhar, um valor inválido poderia ser injetado após a validação."""
    config = CRPlusConfig(base_dir=tmp_path)

    with pytest.raises(dataclasses.FrozenInstanceError):
        config.model = ModelConfig()  # type: ignore[misc]


def test_config_rejects_missing_base_dir(tmp_path: Path) -> None:
    """Intenção: o diretório base deve existir para que os caminhos sejam confinados nele.
    Se falhar, a checagem de path traversal operaria sobre um diretório fictício."""
    with pytest.raises(ConfigError) as error:
        CRPlusConfig(base_dir=tmp_path / "nao_existe")

    assert error.value.field == "base_dir"


# --- valores inválidos por campo -----------------------------------------------------------

INVALID_FIELDS = [
    ("model", "alphas", []),
    ("model", "alphas", [1.0]),
    ("model", "alphas", [0.0]),
    ("model", "alphas", [0.99, 0.99]),
    ("model", "alphas", "0.99"),
    ("model", "alphas", [True]),
    ("model", "alphas", [0.5] * 17),
    ("model", "engine", "montecarlo"),
    ("model", "loss_unit", 0),
    ("model", "loss_unit", -5.0),
    ("model", "loss_unit", "manual"),
    ("model", "loss_unit", True),
    ("model", "loss_unit", math.inf),
    ("model", "banding", "floor"),
    ("sector_variance", "method", "historico"),
    ("sector_variance", "adjust_for_banding", 1),
    ("sector_variance", "value_type", "sd"),
    ("columns", "pd", ""),
    ("columns", "ead", 3),
    ("columns", "weight_prefix", " "),
    ("validation", "strict", "sim"),
    ("validation", "pd_warn_threshold", 0),
    ("validation", "pd_warn_threshold", 1.5),
    ("validation", "weights_tolerance", -1e-9),
    ("validation", "weights_tolerance", math.nan),
    ("validation", "check_operation_id_unique", 0),
    ("validation", "max_reported_rows", -1),
    ("numerics", "z_tail", 0),
    ("numerics", "z_tail", 1000),
    ("numerics", "tol_tail", 0),
    ("numerics", "tol_moment", 1),
    ("numerics", "tol_clip", -1e-13),
    ("numerics", "max_bands", 0),
    ("numerics", "max_bands", 1.5),
    ("numerics", "max_bands", True),
    ("numerics", "max_bands", 10**12),
    ("numerics", "max_grid", 8),
    ("numerics", "max_sectors", 0),
    ("numerics", "var_smoothing_window", -1),
    ("resources", "memory_budget_gb", 0),
    ("resources", "memory_budget_gb", math.nan),
    ("resources", "obligor_partitions", 0),
    ("resources", "obligor_partitions", "manual"),
    ("resources", "polars_threads", 0),
    ("resources", "fft_workers", 2.0),
    ("resources", "numba_threads", 10_000),
    ("output", "directory", 3),
    ("output", "overwrite", "no"),
    ("output", "write_contributions", None),
]


@pytest.mark.parametrize(("section", "key", "value"), INVALID_FIELDS)
def test_config_rejects_invalid_field_naming_it(
    tmp_path: Path, section: str, key: str, value: object
) -> None:
    """Intenção: cada campo com tipo ou faixa inválida gera ConfigError com o nome do campo.
    Se falhar, um parâmetro inválido chegaria ao cálculo (ex.: max_bands negativo)."""
    with pytest.raises(ConfigError) as error:
        _build(tmp_path, {section: {key: value}})

    assert error.value.field == f"{section}.{key}"


VALID_BOUNDARIES = [
    ("model", "alphas", [0.5]),
    ("model", "loss_unit", 1),
    ("model", "loss_unit", 1e-6),
    ("validation", "pd_warn_threshold", 1.0),
    ("validation", "weights_tolerance", 0),
    ("validation", "max_reported_rows", 0),
    ("numerics", "max_bands", 1),
    ("numerics", "var_smoothing_window", 0),
    ("resources", "obligor_partitions", 1),
    ("resources", "memory_budget_gb", 4096),
]


@pytest.mark.parametrize(("section", "key", "value"), VALID_BOUNDARIES)
def test_config_accepts_valid_boundary_values(
    tmp_path: Path, section: str, key: str, value: object
) -> None:
    """Intenção: valores-limite documentados como válidos são aceitos.
    Se falhar, a validação é mais restritiva que o documentado em docs/configuracao.md."""
    config = _build(tmp_path, {section: {key: value}})

    assert getattr(getattr(config, section), key) is not None


def test_model_stores_alphas_as_sorted_float_tuple() -> None:
    """Intenção: alphas viram tupla imutável e ordenada, independentemente da ordem no TOML.
    Se falhar, resultados indexados por alpha ficariam em ordem dependente da entrada."""
    assert ModelConfig(alphas=[0.999, 0.99]).alphas == (0.99, 0.999)  # type: ignore[arg-type]


def test_numerics_rejects_max_bands_not_below_max_grid() -> None:
    """Intenção: a grade sempre tem de comportar a maior banda.
    Se falhar, uma única exposição não caberia na grade da distribuição."""
    with pytest.raises(ConfigError) as error:
        NumericsConfig(max_bands=1024, max_grid=1024)

    assert error.value.field == "numerics.max_bands"


def test_config_rejects_max_grid_beyond_memory_budget(tmp_path: Path) -> None:
    """Intenção: max_grid é validado contra o orçamento de memória já na configuração.
    Se falhar, a FFT tentaria alocar mais memória do que o orçamento permite."""
    with pytest.raises(ConfigError) as error:
        _build(tmp_path, {"resources": {"memory_budget_gb": 1.0}})

    assert error.value.field == "numerics.max_grid"


# --- colunas ---------------------------------------------------------------------------------


def test_columns_rejects_duplicate_names() -> None:
    """Intenção: duas colunas obrigatórias não podem apontar para o mesmo nome.
    Se falhar, por exemplo pd e pd_vol leriam a mesma coluna sem aviso."""
    with pytest.raises(ConfigError) as error:
        ColumnMap(pd_vol="pd")

    assert error.value.field == "columns"


def test_columns_rejects_required_column_matching_weight_prefix() -> None:
    """Intenção: uma coluna obrigatória não pode ser confundida com coluna de peso setorial.
    Se falhar, a EAD seria tratada como peso de um setor."""
    with pytest.raises(ConfigError) as error:
        ColumnMap(ead="w_ead")

    assert error.value.field == "columns.weight_prefix"


def test_columns_required_lists_names_in_canonical_order() -> None:
    """Intenção: a lista de colunas obrigatórias segue a ordem canônica com renomeações.
    Se falhar, o select da base pegaria colunas na posição errada."""
    columns = ColumnMap(pd="prob_default", ead="exposicao")

    assert columns.required == (
        "operation_id",
        "obligor_id",
        "prob_default",
        "pd_vol",
        "lgd",
        "exposicao",
    )


# --- variância setorial ----------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw",
    [
        {"method": "external"},
        {"method": "external", "values": {"w_a": 0.5}, "values_file": "v.csv"},
        {"method": "pd_vol", "values": {"w_a": 0.5}},
        {"method": "pd_vol", "values_file": "v.csv"},
    ],
)
def test_sector_variance_requires_exactly_one_source_only_for_external(
    tmp_path: Path, raw: dict[str, Any]
) -> None:
    """Intenção: 'external' exige exatamente uma fonte de valores; 'pd_vol' não aceita nenhuma.
    Se falhar, valores externos seriam ignorados ou ficaria ambíguo qual fonte vale."""
    with pytest.raises(ConfigError) as error:
        _build(tmp_path, {"sector_variance": raw})

    assert error.value.field == "sector_variance.values"


@pytest.mark.parametrize("values", [{}, {"w_a": -0.1}, {"w_a": math.nan}, {"": 0.5}])
def test_sector_variance_rejects_invalid_inline_values(values: dict[str, float]) -> None:
    """Intenção: variâncias externas devem ser finitas, >= 0 e ter nome de setor.
    Se falhar, uma variância negativa ou NaN quebraria a PGF."""
    with pytest.raises(ConfigError) as error:
        SectorVarianceConfig(method="external", values=values)

    assert error.value.field == "sector_variance.values"


def test_sector_variance_accepts_inline_values_and_freezes_them() -> None:
    """Intenção: valores inline válidos são aceitos e ficam imutáveis.
    Se falhar, a configuração 'congelada' poderia ser alterada através do dicionário."""
    config = SectorVarianceConfig(method="external", value_type="cv", values={"w_a": 0.0})

    with pytest.raises(TypeError):
        config.values["w_a"] = 1.0  # type: ignore[index]


def test_sector_variance_resolves_values_file_inside_base(tmp_path: Path) -> None:
    """Intenção: o arquivo de variâncias é resolvido relativamente ao diretório base.
    Se falhar, o arquivo seria procurado no diretório corrente."""
    config = _build(tmp_path, {"sector_variance": {"method": "external", "values_file": "v.csv"}})

    assert config.sector_variance.values_file == (tmp_path / "v.csv").resolve()


def test_sector_variance_rejects_values_file_outside_base(tmp_path: Path) -> None:
    """Intenção: o arquivo de variâncias não pode escapar do diretório base.
    Se falhar, a configuração poderia ler arquivos arbitrários do sistema."""
    raw = {"sector_variance": {"method": "external", "values_file": "../v.csv"}}

    with pytest.raises(ConfigError) as error:
        _build(tmp_path, raw)

    assert error.value.field == "sector_variance.values_file"


def test_output_directory_outside_base_is_rejected(tmp_path: Path) -> None:
    """Intenção: a saída não pode ser gravada fora do diretório base.
    Se falhar, uma configuração poderia sobrescrever arquivos fora do projeto."""
    with pytest.raises(ConfigError) as error:
        _build(tmp_path, {"output": {"directory": "../../fora"}})

    assert error.value.field == "output.directory"


def test_output_contributions_path_is_inside_output_directory(tmp_path: Path) -> None:
    """Intenção: o parquet de contribuições fica dentro do diretório de saída.
    Se falhar, contribuições seriam gravadas fora do destino validado."""
    config = _build(tmp_path, {})

    assert config.output.contributions_path.parent == config.output.directory


def test_resources_budget_matches_configured_gigabytes() -> None:
    """Intenção: o orçamento derivado corresponde a memory_budget_gb.
    Se falhar, todas as decisões de tamanho usariam um orçamento errado."""
    assert ResourcesConfig(memory_budget_gb=2.0).budget.total_bytes == 2 * 1024**3


def test_config_sections_construct_with_defaults() -> None:
    """Intenção: cada seção é construível só com padrões (uso programático sem TOML).
    Se falhar, algum padrão documentado é inválido."""
    sections = [ValidationConfig(), OutputConfig(), SectorVarianceConfig(), ColumnMap()]

    assert all(dataclasses.is_dataclass(section) for section in sections)


def test_load_config_rejects_file_reported_as_symlink(
    example_config_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Intenção: a recusa de TOML via link simbólico vale em qualquer SO.
    Se falhar, o controle só seria exercitado onde symlinks podem ser criados."""
    monkeypatch.setattr(Path, "is_symlink", lambda self: self == example_config_path)

    with pytest.raises(ConfigError, match="links simbólicos"):
        load_config(example_config_path)
`````

<!-- FILE: tests/unit/test_contributions.py -->
`````python
from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest

from crplus.banding import Banding
from crplus.contributions import (
    EL_COLUMN,
    SIGMA_COLUMN,
    alpha_label,
    contribution_columns,
    es_column,
    var_column,
)
from tests.pipeline import SmallRun, run_model
from tests.synthetic import PortfolioSpec, make_portfolio

BANDING = Banding(200.0)
ALPHAS = (0.99, 0.999)


@pytest.fixture(scope="module")
def portfolio() -> pl.DataFrame:
    return make_portfolio(PortfolioSpec(n_obligors=300, n_sectors=3, seed=21))


@pytest.fixture(scope="module")
def run(portfolio: pl.DataFrame, tmp_path_factory: pytest.TempPathFactory) -> SmallRun:
    return run_model(portfolio, BANDING, tmp_path_factory.mktemp("contrib"), ALPHAS)


def test_contributions_sigma_sum_closes_on_portfolio_std_dev(run: SmallRun) -> None:
    """Intenção: a soma das contribuições de desvio-padrão fecha em sigma (alocação de Euler).
    Se falhar, o capital alocado às operações não somaria o risco do portfólio."""
    total = run.contributions[SIGMA_COLUMN].sum()

    assert total == pytest.approx(run.moments.std_dev * BANDING.loss_unit, rel=1e-8)


@pytest.mark.parametrize("alpha", ALPHAS)
def test_contributions_var_and_es_sums_close_on_portfolio_measures(
    run: SmallRun, alpha: float
) -> None:
    """Intenção: somas de Euler de VaR e ES fecham nas medidas do portfólio (Haaf-Tasche).
    Se falhar, as contribuições de cauda estariam mal escaladas ou com setores trocados."""
    var_total = run.contributions[var_column(alpha)].sum()
    es_total = run.contributions[es_column(alpha)].sum()

    assert var_total == pytest.approx(run.measures.var[alpha], rel=1e-8)
    assert es_total == pytest.approx(run.measures.es[alpha], rel=1e-8)


def test_contributions_expected_loss_column_sums_to_portfolio_el(run: SmallRun) -> None:
    """Intenção: a coluna el soma a perda esperada do portfólio.
    Se falhar, a perda esperada por operação não seria p_i * LGD_i * EAD_i."""
    assert run.contributions[EL_COLUMN].sum() == pytest.approx(run.expected_loss, rel=1e-12)


def test_contributions_parquet_has_one_row_per_operation_with_ids(
    run: SmallRun, portfolio: pl.DataFrame
) -> None:
    """Intenção: o parquet tem exatamente uma linha por operação, com operation_id e obligor_id.
    Se falhar, o usuário não conseguiria ligar contribuições às suas operações."""
    ids = run.contributions.sort("operation_id")["operation_id"]

    assert run.contributions.columns == [
        "operation_id",
        "obligor_id",
        *contribution_columns(ALPHAS),
    ]
    assert ids.to_list() == portfolio.sort("operation_id")["operation_id"].to_list()


def test_contributions_idiosyncratic_operation_has_no_systematic_sigma_term(
    portfolio: pl.DataFrame, tmp_path: Path
) -> None:
    """Intenção: operação 100% idiossincrática recebe RC_sigma = p E nu / sigma (sem setor).
    Se falhar, risco sistêmico seria atribuído a operações sem exposição setorial."""
    weights = [c for c in portfolio.columns if c.startswith("w_")]
    first = portfolio["operation_id"][0]
    data = portfolio.with_columns(
        [
            pl.when(pl.col("operation_id") == first).then(0.0).otherwise(pl.col(w)).alias(w)
            for w in weights
        ]
    )
    run = run_model(data, BANDING, tmp_path, ALPHAS)
    row = run.contributions.filter(pl.col("operation_id") == first).row(0, named=True)
    exposure = (
        data.filter(pl.col("operation_id") == first)
        .select(pl.col("lgd") * pl.col("ead") * pl.col("pd"))
        .item()
    )
    obligor_exposure = (
        data.filter(pl.col("obligor_id") == row["obligor_id"])
        .select((pl.col("lgd") * pl.col("ead")).sum())
        .item()
    )
    band = BANDING.max_band(obligor_exposure)

    assert row[SIGMA_COLUMN] == pytest.approx(exposure * band / run.moments.std_dev, rel=1e-12)


def test_contributions_splitting_operation_halves_contribution_and_keeps_portfolio(
    portfolio: pl.DataFrame, tmp_path: Path
) -> None:
    """Intenção: dividir uma operação em duas metades do mesmo devedor divide a contribuição
    e não altera o portfólio. Se falhar, a alocação dependeria da granularidade dos contratos."""
    first = portfolio.row(0, named=True)
    halves = pl.DataFrame(
        [
            {**first, "ead": first["ead"] / 2},
            {**first, "operation_id": -1, "ead": first["ead"] / 2},
        ],
        schema=portfolio.schema,
    )
    split = pl.concat([halves, portfolio.slice(1)])
    whole_run = run_model(portfolio, BANDING, tmp_path / "a", ALPHAS)
    split_run = run_model(split, BANDING, tmp_path / "b", ALPHAS)
    column = es_column(0.999)
    original = whole_run.contributions.filter(pl.col("operation_id") == first["operation_id"])
    parts = split_run.contributions.filter(pl.col("obligor_id") == first["obligor_id"])
    parts = parts.filter(pl.col("operation_id").is_in([first["operation_id"], -1]))

    assert split_run.measures.es[0.999] == pytest.approx(whole_run.measures.es[0.999], rel=1e-12)
    assert parts[column].to_list() == pytest.approx([original[column].item() / 2] * 2, rel=1e-10)


def test_contributions_smoothing_window_still_closes_on_var(
    portfolio: pl.DataFrame, tmp_path: Path
) -> None:
    """Intenção: a suavização das contribuições de VaR é renormalizada para fechar no VaR.
    Se falhar, var_smoothing_window > 0 quebraria a propriedade de Euler."""
    run = run_model(portfolio, BANDING, tmp_path, ALPHAS, window=3)

    total = run.contributions[var_column(0.999)].sum()

    assert total == pytest.approx(run.measures.var[0.999], rel=1e-8)


def test_contributions_zero_var_quantile_gives_zero_var_contributions(tmp_path: Path) -> None:
    """Intenção: quando VaR = 0 (carteira de PDs minúsculas), as contribuições de VaR são 0.
    Se falhar, haveria divisão por zero na renormalização da tabela A."""
    data = make_portfolio(PortfolioSpec(n_obligors=5, pd_median=1e-5, pd_sigma=0.0))

    run = run_model(data, BANDING, tmp_path, (0.5,))

    assert run.measures.var[0.5] == 0.0
    assert run.contributions[var_column(0.5)].abs().max() == 0.0


def test_contributions_zero_exposure_portfolio_has_zero_sigma_contributions(
    tmp_path: Path,
) -> None:
    """Intenção: carteira sem exposição (sigma = 0) não divide por zero.
    Se falhar, uma base com EAD toda nula derrubaria o passo D."""
    data = make_portfolio(PortfolioSpec(n_obligors=5)).with_columns(ead=pl.lit(0.0))

    run = run_model(data, BANDING, tmp_path, (0.99,))

    assert run.contributions[SIGMA_COLUMN].abs().max() == 0.0


def test_contributions_alpha_labels_are_stable_and_readable() -> None:
    """Intenção: nomes de coluna por alpha são estáveis (sem ruído de ponto flutuante).
    Se falhar, o usuário não encontraria a coluna rc_var_0.999 no parquet."""
    assert [alpha_label(0.999), var_column(0.99), es_column(0.9995)] == [
        "0.999",
        "rc_var_0.99",
        "rc_es_0.9995",
    ]
`````

<!-- FILE: tests/unit/test_distribution.py -->
`````python
from __future__ import annotations

import numpy as np
import pytest
from scipy import stats

from crplus.config import NumericsConfig
from crplus.distribution import (
    FFTEngine,
    GridRequest,
    PanjerEngine,
    SectorModel,
    compute_distribution,
    make_engine,
)
from crplus.distribution.grid import diagnose, initial_grid_size
from crplus.distribution.model import clip_negatives
from crplus.distribution.panjer import PanjerClass, panjer_loops, panjer_numpy, select_kernel
from crplus.exceptions import GridTooSmallError, MemoryBudgetError, NumericalRangeError
from crplus.memory import MemoryBudget
from crplus.moments import analytic_moments

ENGINES = [FFTEngine(), PanjerEngine()]
ENGINE_IDS = ["fft", "panjer"]
GRID = 512


def random_model(seed: int, n_sectors: int = 3, bands: int = 12) -> SectorModel:
    """Modelo pequeno com bandas mistas, setor 0 Poisson e setores Gama."""
    rng = np.random.default_rng(seed)
    intensity = rng.uniform(0.0, 0.05, size=(n_sectors + 1, bands + 1))
    intensity[:, 0] = 0.0
    intensity[rng.uniform(size=intensity.shape) < 0.3] = 0.0
    variance = np.concatenate([[0.0], rng.uniform(0.2, 2.0, n_sectors)])
    return SectorModel(intensity, variance)


def _single_band_model(mean: float, variance: float) -> SectorModel:
    return SectorModel(np.array([[0.0, mean]]), np.array([variance]))


@pytest.mark.parametrize("engine", ENGINES, ids=ENGINE_IDS)
def test_distribution_idiosyncratic_unit_band_is_poisson(engine: FFTEngine) -> None:
    """Intenção: só setor idiossincrático com nu = 1 dá contagem Poisson (oráculo scipy).
    Se falhar, o caso base do CR+ (defaults independentes) estaria errado."""
    probs = engine.compute(_single_band_model(2.5, 0.0), GRID).probs

    np.testing.assert_allclose(probs[:40], stats.poisson(2.5).pmf(np.arange(40)), atol=1e-15)


@pytest.mark.parametrize("engine", ENGINES, ids=ENGINE_IDS)
def test_distribution_single_gamma_sector_unit_band_is_negative_binomial(
    engine: FFTEngine,
) -> None:
    """Intenção: um setor Gama com nu = 1 dá binomial negativa nbinom(1/v, 1/(1+v mu)).
    Se falhar, a mistura Gama (correlação setorial) estaria mal implementada."""
    mean, variance = 3.0, 0.7
    model = SectorModel(np.array([[0.0, 0.0], [0.0, mean]]), np.array([0.0, variance]))
    oracle = stats.nbinom(n=1 / variance, p=1 / (1 + variance * mean))

    probs = engine.compute(model, GRID).probs

    np.testing.assert_allclose(probs[:60], oracle.pmf(np.arange(60)), atol=1e-14)


def test_distribution_compound_poisson_mixed_bands_fft_equals_panjer() -> None:
    """Intenção: Poisson composta com bandas mistas coincide entre FFT e Panjer.
    Se falhar, um dos motores trata severidades com bandas > 1 de forma errada."""
    model = SectorModel(np.array([[0.0, 0.3, 0.0, 0.2, 0.1]]), np.array([0.0]))

    fft_probs = FFTEngine().compute(model, GRID).probs
    panjer_probs = PanjerEngine().compute(model, GRID).probs

    assert np.max(np.abs(fft_probs - panjer_probs)) < 1e-14


@pytest.mark.parametrize("seed", range(5))
def test_distribution_fft_equals_panjer_on_random_portfolio(seed: int) -> None:
    """Intenção: os dois motores concordam em carteiras aleatórias (validação cruzada).
    Se falhar, o motor principal (FFT) diverge da referência numericamente estável."""
    model = random_model(seed)

    delta = FFTEngine().compute(model, GRID).probs - PanjerEngine().compute(model, GRID).probs

    assert np.max(np.abs(delta)) < 1e-10


@pytest.mark.parametrize("engine", ENGINES, ids=ENGINE_IDS)
def test_distribution_sums_to_one_without_negatives_and_matches_moments(
    engine: FFTEngine,
) -> None:
    """Intenção: probabilidades somam 1, não são negativas e reproduzem os momentos da §5.6.
    Se falhar, VaR/ES seriam calculados sobre uma distribuição inválida."""
    model = random_model(11)
    moments = analytic_moments(model.intensity, model.variance)

    probs = engine.compute(model, GRID).probs
    diagnostics = diagnose(probs, moments, 1)

    assert probs.min() >= 0.0
    assert diagnostics.total_mass == pytest.approx(1.0, abs=1e-12)
    assert diagnostics.mean_error < 1e-10
    assert diagnostics.variance_error < 1e-10


@pytest.mark.parametrize("seed", range(3))
def test_distribution_tilted_fft_equals_tilted_panjer(seed: int) -> None:
    """Intenção: as distribuições inclinadas g^(k) coincidem entre os motores.
    Se falhar, as contribuições de VaR/ES dependeriam do motor escolhido."""
    model = random_model(seed)
    fft_dist = FFTEngine().compute(model, GRID)
    panjer_dist = PanjerEngine().compute(model, GRID)

    deltas = [np.abs(fft_dist.tilted(k) - panjer_dist.tilted(k)).max() for k in range(4)]

    assert max(deltas) < 1e-10


@pytest.mark.parametrize("engine", ENGINES, ids=ENGINE_IDS)
def test_distribution_tilted_satisfies_haaf_tasche_identity(engine: FFTEngine) -> None:
    """Intenção: x g_x = sum_k sum_nu nu lambda_{k,nu} g^(k)_{x-nu} (base da alocação de Euler).
    Se falhar, as contribuições de VaR/ES não fechariam nas medidas do portfólio."""
    model = random_model(3)
    dist = engine.compute(model, GRID)
    lhs = np.arange(GRID) * dist.probs

    rhs = np.zeros(GRID)
    for k in range(model.intensity.shape[0]):
        tilted = dist.tilted(k)
        for band in np.flatnonzero(model.intensity[k]):
            rhs[band:] += band * model.intensity[k, band] * tilted[: GRID - band]

    np.testing.assert_allclose(lhs[:200], rhs[:200], atol=1e-13)


def test_distribution_poisson_sector_tilted_is_base_distribution() -> None:
    """Intenção: para setores Poisson (incluindo o idiossincrático) g^(k) = g.
    Se falhar, setores sem fator Gama receberiam um termo sistêmico indevido."""
    dist = FFTEngine().compute(random_model(1), GRID)

    assert dist.tilted(0) is dist.probs


def test_distribution_log_branch_real_part_is_at_least_one() -> None:
    """Intenção: Re(1 - v t_k) >= 1, garantindo continuidade do ramo principal do log.
    Se falhar, o log complexo saltaria de ramo e a FFT produziria lixo."""
    model = random_model(5)
    engine = FFTEngine()

    reals = [
        (1 - model.variance[k] * engine.sector_transform(model.intensity[k], GRID)).real.min()
        for k in model.gamma_sectors()
    ]

    assert min(reals) >= 1.0 - 1e-15


def test_panjer_numba_python_and_numpy_kernels_agree() -> None:
    """Intenção: o kernel numba, a versão em laços e a versão numpy dão o mesmo resultado.
    Se falhar, o fallback sem numba (ou o kernel compilado) estaria errado."""
    severity = np.array([0.0, 0.5, 0.3, 0.2])
    family = PanjerClass.negative_binomial(2.0, 0.5, 2.0)
    args = (family.a, family.b, np.exp(family.log_g0), severity, 64)

    compiled = select_kernel(__import__("numba"))(*args)

    np.testing.assert_allclose(compiled, panjer_loops(*args), rtol=1e-14)
    np.testing.assert_allclose(select_kernel(None)(*args), panjer_numpy(*args), rtol=0)
    np.testing.assert_allclose(panjer_numpy(*args), panjer_loops(*args), rtol=1e-13)


def test_panjer_raises_on_g0_underflow() -> None:
    """Intenção: média de contagem grande (g_0 subrepresentável) gera erro sugerindo FFT.
    Se falhar, a recursão devolveria uma distribuição identicamente nula."""
    with pytest.raises(NumericalRangeError, match="fft"):
        PanjerEngine().compute(_single_band_model(800.0, 0.0), 2048)


def test_clip_negatives_zeroes_noise_and_rejects_large_negatives() -> None:
    """Intenção: negativos da ordem do ruído viram 0; negativos relevantes são erro.
    Se falhar, ou o ruído da FFT vaza para VaR/ES, ou um erro numérico grave passa despercebido."""
    clipped = clip_negatives(np.array([0.5, -1e-16, 0.5]), 1e-13)

    assert clipped.tolist() == [0.5, 0.0, 0.5]
    with pytest.raises(NumericalRangeError):
        clip_negatives(np.array([1.0, -1e-6]), 1e-13)


@pytest.mark.parametrize(
    ("intensity", "variance"),
    [
        (np.array([[0.0, -0.1]]), np.array([0.0])),
        (np.array([[0.0, np.nan]]), np.array([0.0])),
        (np.array([[0.1, 0.1]]), np.array([0.0])),
        (np.array([[0.0, 0.1]]), np.array([0.0, 1.0])),
        (np.array([0.0, 0.1]), np.array([0.0])),
    ],
)
def test_sector_model_rejects_invalid_parameters(
    intensity: np.ndarray, variance: np.ndarray
) -> None:
    """Intenção: intensidades negativas/NaN, banda 0 ou formas incoerentes são rejeitadas.
    Se falhar, parâmetros inválidos produziriam distribuições sem sentido."""
    with pytest.raises(NumericalRangeError):
        SectorModel(intensity, variance)


@pytest.mark.parametrize("name", ["fft", "panjer"])
def test_distribution_grid_smaller_than_band_is_rejected(name: str) -> None:
    """Intenção: a grade precisa comportar a maior banda.
    Se falhar, exposições grandes seriam dobradas para o início da grade (aliasing)."""
    with pytest.raises(GridTooSmallError):
        make_engine(name, 1, 1e-13).compute(random_model(0, bands=40), 32)


def _request(model: SectorModel, numerics: NumericsConfig, budget_gb: float = 1.0) -> GridRequest:
    moments = analytic_moments(model.intensity, model.variance)
    return GridRequest(model, moments, numerics, MemoryBudget.from_gb(budget_gb))


def test_distribution_small_initial_grid_grows_until_tolerances_met() -> None:
    """Intenção: grade inicial pequena demais (z_tail baixo) é dobrada automaticamente.
    Se falhar, a cauda truncada distorceria VaR/ES sem nenhum aviso."""
    numerics = NumericsConfig(z_tail=0.5, max_bands=100, max_grid=1 << 16)

    _, diagnostics = compute_distribution(FFTEngine(), _request(random_model(2), numerics))

    assert diagnostics.attempts > 1
    assert diagnostics.within(numerics)


def test_distribution_raises_grid_too_small_when_max_grid_is_insufficient() -> None:
    """Intenção: se nem max_grid atende às tolerâncias, o erro é explícito.
    Se falhar, uma distribuição truncada seria usada silenciosamente."""
    numerics = NumericsConfig(z_tail=0.5, max_bands=12, max_grid=16)

    with pytest.raises(GridTooSmallError):
        compute_distribution(FFTEngine(), _request(random_model(2), numerics))


def test_distribution_initial_grid_above_max_grid_is_rejected() -> None:
    """Intenção: a grade estimada acima de max_grid é rejeitada antes de qualquer alocação.
    Se falhar, max_grid não protegeria contra carteiras grandes demais para a unidade de perda."""
    moments = analytic_moments(random_model(2).intensity, random_model(2).variance)

    with pytest.raises(GridTooSmallError):
        initial_grid_size(moments, 10_000, NumericsConfig(max_bands=100, max_grid=1024))


def test_distribution_checks_memory_budget_before_computing() -> None:
    """Intenção: a grade é checada contra o orçamento antes de alocar os vetores da FFT.
    Se falhar, o processo seria morto pelo sistema operacional por falta de memória."""
    with pytest.raises(MemoryBudgetError):
        compute_distribution(FFTEngine(), _request(random_model(2), NumericsConfig(), 1e-6))
`````

<!-- FILE: tests/unit/test_exceptions.py -->
`````python
from __future__ import annotations

import pytest

from crplus.exceptions import (
    ConfigError,
    CRPlusError,
    GridTooSmallError,
    InputValidationError,
    MemoryBudgetError,
    NumericalRangeError,
)


@pytest.mark.parametrize(
    "error_type",
    [ConfigError, InputValidationError, GridTooSmallError, NumericalRangeError, MemoryBudgetError],
)
def test_exceptions_derive_from_crplus_error_for_single_catch(error_type: type) -> None:
    """Intenção: o usuário deve conseguir capturar qualquer falha do pacote com CRPlusError.
    Se falhar, uma exceção escapa do contrato público de erros."""
    assert issubclass(error_type, CRPlusError)


def test_config_error_exposes_field_and_mentions_it_in_message() -> None:
    """Intenção: o erro de configuração deve apontar qual campo está errado.
    Se falhar, o usuário não consegue localizar o problema no TOML."""
    error = ConfigError("numerics.max_bands", "inteiro positivo")

    assert error.field == "numerics.max_bands"
    assert "numerics.max_bands" in str(error)
`````

<!-- FILE: tests/unit/test_memory.py -->
`````python
from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from crplus.exceptions import MemoryBudgetError
from crplus.memory import (
    BYTES_PER_GB,
    MAX_PARTITIONS,
    OBLIGOR_TABLE_FRACTION,
    MemoryBudget,
    auto_obligor_partitions,
    band_table_bytes,
    check_partitions,
    grid_bytes,
    max_grid_within_budget,
    obligor_table_bytes,
)

sizes = st.integers(min_value=0, max_value=10**10)


@given(sizes, sizes)
def test_grid_bytes_is_monotonic_in_grid_size(a: int, b: int) -> None:
    """Intenção: grade maior nunca custa menos memória.
    Se falhar, a checagem de orçamento poderia aprovar grades maiores que as rejeitadas."""
    assert grid_bytes(min(a, b)) <= grid_bytes(max(a, b))


@given(sizes, sizes)
def test_obligor_table_bytes_is_monotonic_in_obligors(a: int, b: int) -> None:
    """Intenção: mais devedores nunca custam menos memória.
    Se falhar, o número automático de partições ficaria subdimensionado."""
    assert obligor_table_bytes(min(a, b)) <= obligor_table_bytes(max(a, b))


@given(st.integers(0, 1000), st.integers(0, 10**6), st.integers(0, 1000), st.integers(0, 10**6))
def test_band_table_bytes_is_monotonic_in_sectors_and_bands(
    k1: int, nu1: int, k2: int, nu2: int
) -> None:
    """Intenção: mais setores ou bandas nunca reduzem a memória das tabelas setor-banda.
    Se falhar, o limite de max_bands/max_sectors não protegeria contra estouro."""
    small = band_table_bytes(min(k1, k2), min(nu1, nu2))
    large = band_table_bytes(max(k1, k2), max(nu1, nu2))

    assert small <= large


def test_string_ids_cost_more_than_integer_ids() -> None:
    """Intenção: a estimativa reflete que ids string multiplicam o custo da tabela de devedores.
    Se falhar, bases com ids string estourariam o orçamento sem aviso."""
    assert obligor_table_bytes(1000, "str") > obligor_table_bytes(1000, "int")


@given(st.integers(min_value=0, max_value=10**14))
def test_auto_partitions_is_smallest_count_that_fits_budget(table_bytes: int) -> None:
    """Intenção: 'auto' escolhe o MENOR P cuja partição cabe em 40% do orçamento.
    Se falhar, ou estoura memória (P pequeno demais) ou relê a fonte mais vezes que o necessário."""
    budget = MemoryBudget.from_gb(9.0)
    limit = budget.share(OBLIGOR_TABLE_FRACTION)

    partitions = auto_obligor_partitions(table_bytes, budget)

    assert -(-table_bytes // partitions) <= limit
    assert partitions == 1 or -(-table_bytes // (partitions - 1)) > limit


def test_auto_partitions_raises_when_cap_would_be_exceeded() -> None:
    """Intenção: uma base absurdamente grande para o orçamento falha com mensagem clara.
    Se falhar, o pipeline tentaria dezenas de milhares de releituras da fonte."""
    budget = MemoryBudget(1000)
    table = budget.share(OBLIGOR_TABLE_FRACTION) * (MAX_PARTITIONS + 1)

    with pytest.raises(MemoryBudgetError):
        auto_obligor_partitions(table, budget)


def test_check_partitions_rejects_too_few_partitions_before_allocating() -> None:
    """Intenção: P fixo no TOML pequeno demais é rejeitado antes de construir a tabela.
    Se falhar, o processo estouraria a memória no meio do passo A."""
    budget = MemoryBudget.from_gb(1.0)

    with pytest.raises(MemoryBudgetError, match="GB"):
        check_partitions(1, 2 * BYTES_PER_GB, budget)


def test_check_partitions_accepts_enough_partitions() -> None:
    """Intenção: P suficiente passa na checagem.
    Se falhar, configurações válidas seriam rejeitadas."""
    budget = MemoryBudget.from_gb(1.0)

    check_partitions(6, 2 * BYTES_PER_GB, budget)


def test_require_raises_memory_budget_error_when_estimate_exceeds_share() -> None:
    """Intenção: a checagem de orçamento rejeita estimativas acima da parcela disponível.
    Se falhar, alocações grandes acontecem e o processo é morto pelo SO."""
    budget = MemoryBudget.from_gb(9.0)

    with pytest.raises(MemoryBudgetError):
        budget.require(grid_bytes(2**30), "grade FFT", 0.5)


@pytest.mark.parametrize("total", [0, -1])
def test_memory_budget_rejects_non_positive_total(total: int) -> None:
    """Intenção: orçamento nulo ou negativo é um erro de configuração.
    Se falhar, todas as checagens passariam ou falhariam de forma sem sentido."""
    with pytest.raises(MemoryBudgetError):
        MemoryBudget(total)


def test_default_max_grid_fits_default_budget() -> None:
    """Intenção: o padrão max_grid = 2**26 (~2 GB de trabalho) cabe no orçamento de 9 GB.
    Se falhar, a configuração padrão seria inválida na máquina de referência."""
    assert max_grid_within_budget(MemoryBudget.from_gb(9.0)) >= 2**26
`````

<!-- FILE: tests/unit/test_moments.py -->
`````python
from __future__ import annotations

import numpy as np
import pytest

from crplus.moments import analytic_moments


def test_moments_single_obligor_is_scaled_poisson() -> None:
    """Intenção: um devedor na banda 3 com intensidade p tem EL = 3p e Var = 9p (Poisson).
    Se falhar, o oráculo de momentos usado para validar a distribuição estaria errado."""
    intensity = np.array([[0.0, 0.0, 0.0, 0.02]])

    moments = analytic_moments(intensity, np.array([0.0]))

    assert moments.expected_loss == pytest.approx(0.06)
    assert moments.variance == pytest.approx(0.18)


def test_moments_single_sector_adds_gamma_variance() -> None:
    """Intenção: um setor Gama acrescenta v_k * EL_k^2 à variância Poisson composta.
    Se falhar, a variância sistêmica (correlação de defaults) seria ignorada."""
    intensity = np.array([[0.0, 0.1, 0.0], [0.0, 0.2, 0.3]])
    variance = np.array([0.0, 0.5])
    el_sector = 0.2 + 2 * 0.3

    moments = analytic_moments(intensity, variance)

    assert moments.expected_loss == pytest.approx(0.1 + el_sector)
    assert moments.variance == pytest.approx(0.1 + 0.2 + 4 * 0.3 + 0.5 * el_sector**2)
    assert moments.std_dev == pytest.approx(moments.variance**0.5)
    assert moments.sector_expected_loss.tolist() == pytest.approx([0.1, el_sector])
`````

<!-- FILE: tests/unit/test_montecarlo.py -->
`````python
from __future__ import annotations

import numpy as np
import pytest

from crplus.distribution import FFTEngine, SectorModel
from crplus.moments import analytic_moments
from crplus.montecarlo import (
    MonteCarloSettings,
    ObligorPortfolio,
    simulate_losses,
    simulate_obligor_losses,
    tail_estimate,
)
from crplus.risk_measures import risk_measures

MODEL = SectorModel(
    np.array([[0.0, 0.4, 0.2, 0.0], [0.0, 0.3, 0.0, 0.1], [0.0, 0.0, 0.2, 0.2]]),
    np.array([0.0, 0.8, 1.5]),
)


def test_montecarlo_is_reproducible_with_same_seed() -> None:
    """Intenção: a mesma seed reproduz exatamente os mesmos cenários (determinismo).
    Se falhar, testes de integração baseados em Monte Carlo seriam instáveis."""
    settings = MonteCarloSettings(5_000, seed=42, batch_size=1_000)

    first = simulate_losses(MODEL, settings)

    np.testing.assert_array_equal(first, simulate_losses(MODEL, settings))
    assert not np.array_equal(first, simulate_losses(MODEL, MonteCarloSettings(5_000, seed=43)))


def test_montecarlo_moments_match_analytic_moments() -> None:
    """Intenção: média e variância simuladas convergem para os momentos analíticos.
    Se falhar, o simulador não representa o mesmo modelo que os motores analíticos."""
    moments = analytic_moments(MODEL.intensity, MODEL.variance)

    losses = simulate_losses(MODEL, MonteCarloSettings(400_000, seed=1)).astype(float)

    assert losses.mean() == pytest.approx(moments.expected_loss, rel=0.01)
    assert losses.var() == pytest.approx(moments.variance, rel=0.03)


def test_montecarlo_band_and_obligor_simulations_are_equivalent() -> None:
    """Intenção: simular por setor-banda equivale em distribuição a simular por devedor.
    Se falhar, o atalho de simulação usado na validação seria um modelo diferente."""
    portfolio = ObligorPortfolio(
        intensity=np.array([[0.2, 0.15, 0.0], [0.2, 0.15, 0.0], [0.2, 0.0, 0.2], [0.0, 0.1, 0.2]]),
        bands=np.array([1, 1, 2, 3]),
        variance=MODEL.variance,
    )
    settings = MonteCarloSettings(300_000, seed=9)

    by_obligor = simulate_obligor_losses(portfolio, settings)
    by_band = simulate_losses(MODEL, MonteCarloSettings(300_000, seed=10))
    exact = FFTEngine().compute(MODEL, 256).probs

    for losses in (by_obligor, by_band):
        empirical = np.bincount(losses, minlength=256)[:10] / losses.shape[0]
        np.testing.assert_allclose(empirical, exact[:10], atol=4e-3)


def test_montecarlo_tail_estimate_brackets_exact_measures() -> None:
    """Intenção: VaR/ES de Monte Carlo ficam dentro de poucos erros-padrão dos exatos.
    Se falhar, o critério do teste de integração (intervalo de MC) não seria confiável."""
    exact = risk_measures(FFTEngine().compute(MODEL, 256).probs, [0.99], 1.0, 0.0)

    estimate = tail_estimate(simulate_losses(MODEL, MonteCarloSettings(400_000, seed=3)), 0.99, 1.0)

    assert abs(estimate.es - exact.es[0.99]) < 5 * estimate.es_se
    assert abs(estimate.var - exact.var[0.99]) <= 5 * estimate.var_se + 1.0
`````

<!-- FILE: tests/unit/test_obligor.py -->
`````python
from __future__ import annotations

from functools import reduce
from pathlib import Path

import polars as pl
import pytest

from crplus.config import ColumnMap
from crplus.obligor import ObligorStats, build_obligor_table
from crplus.schema import OBLIGOR_EXPOSURE, OBLIGOR_ID
from crplus.sources import PortfolioSource, iter_partitions, normalize_source
from tests.synthetic import PortfolioSpec, make_portfolio


def _source(data: pl.DataFrame) -> PortfolioSource:
    return normalize_source(data, ColumnMap(), "float64", 100)


def _run(data: pl.DataFrame, tmp_path: Path, partitions: int = 1) -> ObligorStats:
    source = _source(data)
    stats = [
        build_obligor_table(frame, source.n_sectors, tmp_path / f"o{p}.parquet")
        for p, frame in enumerate(iter_partitions(source, partitions))
    ]
    return reduce(lambda a, b: a + b, stats)


def test_obligor_exposure_is_sum_of_lgd_times_ead(tmp_path: Path) -> None:
    """Intenção: E_j = soma de LGD*EAD das operações do devedor (oráculo: group_by explícito).
    Se falhar, a banda do devedor e todo o modelo usariam exposições erradas."""
    data = make_portfolio()
    expected = data.group_by("obligor_id").agg((pl.col("lgd") * pl.col("ead")).sum().alias("e"))

    build_obligor_table(_source(data).frame, 3, tmp_path / "o.parquet")
    table = pl.read_parquet(tmp_path / "o.parquet").join(expected, on=OBLIGOR_ID)

    assert table.columns == [OBLIGOR_ID, OBLIGOR_EXPOSURE, "e"]
    assert (table[OBLIGOR_EXPOSURE] - table["e"]).abs().max() < 1e-9  # type: ignore[operator]


def test_obligor_stats_summarize_exposures_and_expected_loss(tmp_path: Path) -> None:
    """Intenção: as estatísticas que alimentam a escolha de L0 batem com cálculos diretos.
    Se falhar, L0 automático e a grade seriam dimensionados com números errados."""
    data = make_portfolio()
    exposure = data["lgd"] * data["ead"]
    per_obligor = data.with_columns(e=exposure).group_by("obligor_id").agg(pl.col("e").sum())

    stats = _run(data, tmp_path)

    assert stats.n_operations == data.height
    assert stats.n_obligors == per_obligor.height
    assert stats.max_exposure == pytest.approx(per_obligor["e"].max())
    assert stats.expected_loss == pytest.approx((exposure * data["pd"]).sum())


def test_obligor_consistent_portfolio_has_no_inconsistencies(tmp_path: Path) -> None:
    """Intenção: devedores com PD, pd_vol e pesos iguais entre operações não geram aviso.
    Se falhar, o caso esperado (dados consistentes) dispararia avisos espúrios."""
    assert _run(make_portfolio(), tmp_path).inconsistent_obligors == 0


@pytest.mark.parametrize(
    ("column", "field"),
    [
        ("pd", "inconsistent_pd"),
        ("pd_vol", "inconsistent_pd_vol"),
        ("w_s2", "inconsistent_weights"),
    ],
)
def test_obligor_detects_intra_obligor_inconsistency(
    tmp_path: Path, column: str, field: str
) -> None:
    """Intenção: um devedor com operações de PD, pd_vol ou pesos diferentes é contado uma vez.
    Se falhar, a combinação ponderada por EL seria aplicada sem que o usuário soubesse."""
    data = make_portfolio(PortfolioSpec(max_ops_per_obligor=1))
    first = data.row(0, named=True)
    twin = {**first, "operation_id": -1, column: first[column] * 0.5}
    data = pl.concat([data, pl.DataFrame([twin], schema=data.schema)])

    stats = _run(data, tmp_path)

    assert getattr(stats, field) == 1
    assert stats.inconsistent_obligors == 1


def test_obligor_one_partition_equals_many_partitions(tmp_path: Path) -> None:
    """Intenção: o particionamento por hash não altera as estatísticas agregadas.
    Se falhar, o resultado dependeria de obligor_partitions (memória disponível)."""
    data = make_portfolio()

    one = _run(data, tmp_path, 1)
    many = _run(data, tmp_path, 4)

    assert many.n_obligors == one.n_obligors
    assert many.max_exposure == one.max_exposure
    assert many.expected_loss == pytest.approx(one.expected_loss, rel=1e-13)


def test_obligor_stats_add_takes_max_of_max_exposure() -> None:
    """Intenção: a soma entre partições usa máximo para max_exposure e soma para o resto.
    Se falhar, a maior exposição (que define a maior banda) seria somada entre partições."""
    left = ObligorStats(n_obligors=2, max_exposure=5.0)
    total = left + ObligorStats(n_obligors=3, max_exposure=7.0)

    assert (total.n_obligors, total.max_exposure) == (5, 7.0)


def test_obligor_handles_empty_partition(tmp_path: Path) -> None:
    """Intenção: uma partição sem linhas produz estatísticas nulas, sem erro.
    Se falhar, um hash que deixe uma partição vazia derrubaria a execução."""
    frame = _source(make_portfolio()).frame.filter(pl.lit(value=False))

    stats = build_obligor_table(frame, 3, tmp_path / "o.parquet")

    assert stats == ObligorStats()


def test_obligor_without_sectors_never_reports_weight_inconsistency(tmp_path: Path) -> None:
    """Intenção: carteira sem colunas de peso (K = 0) não tem como divergir em pesos.
    Se falhar, o caso só idiossincrático quebraria o passo A."""
    data = make_portfolio(PortfolioSpec(n_sectors=0))

    assert _run(data, tmp_path).inconsistent_weights == 0
`````

<!-- FILE: tests/unit/test_paths.py -->
`````python
from __future__ import annotations

from pathlib import Path

import pytest

from crplus.exceptions import ConfigError
from crplus.paths import resolve_within


def test_resolve_within_returns_absolute_path_inside_base(tmp_path: Path) -> None:
    """Intenção: caminhos relativos são interpretados a partir do diretório base.
    Se falhar, saídas seriam gravadas em diretórios inesperados."""
    resolved = resolve_within(tmp_path, Path("saida/sub"), "output.directory")

    assert resolved == (tmp_path / "saida" / "sub").resolve()


def test_resolve_within_accepts_absolute_path_inside_base(tmp_path: Path) -> None:
    """Intenção: um caminho absoluto dentro do base é legítimo.
    Se falhar, usuários não conseguem informar caminhos absolutos válidos."""
    target = tmp_path / "dados.csv"

    assert resolve_within(tmp_path, target, "f") == target.resolve()


@pytest.mark.parametrize("candidate", ["../fora", "a/../../fora", "a/./../../../x"])
def test_resolve_within_rejects_parent_traversal(tmp_path: Path, candidate: str) -> None:
    """Intenção: '..' não pode levar um caminho para fora do diretório base (path traversal).
    Se falhar, uma configuração maliciosa poderia ler ou sobrescrever arquivos arbitrários."""
    base = tmp_path / "base"
    base.mkdir()

    with pytest.raises(ConfigError) as error:
        resolve_within(base, Path(candidate), "output.directory")

    assert error.value.field == "output.directory"


def test_resolve_within_rejects_absolute_path_outside_base(tmp_path: Path) -> None:
    """Intenção: caminho absoluto fora do base é rejeitado.
    Se falhar, o controle de path traversal é contornado com um caminho absoluto."""
    base = tmp_path / "base"
    base.mkdir()

    with pytest.raises(ConfigError):
        resolve_within(base, tmp_path / "outro", "f")


def test_resolve_within_rejects_symlink_component(tmp_path: Path, symlink_dir: Path) -> None:
    """Intenção: links simbólicos dentro do base não podem ser atravessados.
    Se falhar, um link poderia redirecionar saídas para fora do diretório base."""
    with pytest.raises(ConfigError, match="links simbólicos"):
        resolve_within(tmp_path, Path(symlink_dir.name) / "arquivo.parquet", "f")


def test_resolve_within_rejects_component_reported_as_symlink(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Intenção: a rejeição de links vale em qualquer SO, inclusive sem privilégio de criá-los.
    Se falhar, o controle dependeria de o ambiente de teste permitir symlinks reais."""
    linked = (tmp_path / "pasta").resolve()
    monkeypatch.setattr(Path, "is_symlink", lambda self: self == linked)

    with pytest.raises(ConfigError, match="links simbólicos"):
        resolve_within(tmp_path, Path("pasta/arquivo.csv"), "f")
`````

<!-- FILE: tests/unit/test_results.py -->
`````python
from __future__ import annotations

import numpy as np
import pytest

from crplus.results import LossDistribution, truncated_distribution


def test_results_distribution_is_truncated_where_tail_is_negligible() -> None:
    """Intenção: a distribuição salva para no primeiro ponto com cauda < tol_tail.
    Se falhar, o parquet de distribuição teria milhões de zeros (ou perderia massa relevante)."""
    probs = np.array([0.5, 0.4, 0.1 - 1e-14, 1e-14, 0.0, 0.0])

    truncated = truncated_distribution(probs, 2.0, 1e-12)

    assert truncated.probs.tolist() == probs[:3].tolist()
    assert truncated.probs.sum() == pytest.approx(1.0, abs=1e-12)


def test_results_distribution_frame_reports_currency_losses_and_cdf() -> None:
    """Intenção: a tabela (loss, prob, cdf) usa perdas em moeda (x * L0) e cdf acumulada.
    Se falhar, o usuário leria perdas em unidades internas em vez da moeda do EAD."""
    frame = LossDistribution(np.array([0.5, 0.3, 0.2]), 10.0).frame()

    assert frame["loss"].to_list() == [0.0, 10.0, 20.0]
    assert frame["cdf"].to_list() == pytest.approx([0.5, 0.8, 1.0])
`````

<!-- FILE: tests/unit/test_risk_measures.py -->
`````python
from __future__ import annotations

import itertools

import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st
from hypothesis.extra.numpy import arrays

from crplus.exceptions import GridTooSmallError
from crplus.risk_measures import loss_tail, quantile, risk_measures, tail_above

# Distribuição de mão: P(0)=0.5, P(1)=0.3, P(2)=0.15, P(3)=0.05.
HAND = np.array([0.5, 0.3, 0.15, 0.05])


def test_risk_measures_var_on_hand_built_distribution() -> None:
    """Intenção: VaR = menor x com F(x) >= alpha, em moeda (x * L0).
    Se falhar, o capital econômico seria calculado num quantil errado."""
    measures = risk_measures(HAND, [0.5, 0.8, 0.9, 0.96], 10.0, 0.0)

    assert dict(measures.var) == {0.5: 0.0, 0.8: 10.0, 0.9: 20.0, 0.96: 30.0}


def test_risk_measures_es_follows_acerbi_tasche_formula() -> None:
    """Intenção: ES_alpha = L0/(1-alpha) [sum_{x>q} x g_x + q (F(q) - alpha)] (caso de mão).
    Se falhar, o ES não seria coerente numa distribuição discreta."""
    alpha = 0.9  # q = 2, F(q) = 0.95
    expected = 10.0 / 0.1 * (3 * 0.05 + 2 * (0.95 - 0.9))

    assert risk_measures(HAND, [alpha], 10.0, 0.0).es[alpha] == pytest.approx(expected)


def test_risk_measures_ec_subtracts_expected_loss() -> None:
    """Intenção: EC = VaR - EL e ES - EL usam a perda esperada em moeda.
    Se falhar, o capital econômico incluiria a perda esperada (já provisionada)."""
    measures = risk_measures(HAND, [0.9], 10.0, 7.5)

    assert measures.ec[0.9] == pytest.approx(20.0 - 7.5)
    assert measures.es_minus_el[0.9] == pytest.approx(measures.es[0.9] - 7.5)


def test_risk_measures_tail_uses_reverse_cumulative_sum() -> None:
    """Intenção: a cauda estrita é sum_{y>x} g_y, preservando precisão em caudas minúsculas.
    Se falhar (ex.: 1 - cdf), probabilidades de 1e-17 sumiriam por cancelamento."""
    probs = np.array([1.0 - 2e-17, 1e-17, 1e-17])

    assert tail_above(probs).tolist() == [2e-17, 1e-17, 0.0]


def test_risk_measures_quantile_exposes_beta_for_contributions() -> None:
    """Intenção: beta = (F(q) - alpha)/g_q, usado pela alocação do ES.
    Se falhar, as contribuições de ES não fechariam no ES do portfólio."""
    info = quantile(HAND, loss_tail(HAND), 0.9)

    assert (info.quantile, info.beta) == (2, pytest.approx(0.05 / 0.15))


def test_risk_measures_raises_when_grid_does_not_reach_alpha() -> None:
    """Intenção: grade truncada que não acumula alpha gera erro explícito.
    Se falhar, o VaR seria o índice 0 por engano (argmax de vetor falso)."""
    truncated = np.array([0.5, 0.3])

    with pytest.raises(GridTooSmallError):
        quantile(truncated, loss_tail(truncated), 0.99)


distributions = (
    arrays(np.float64, st.integers(2, 30), elements=st.floats(0.0, 1.0))
    .filter(lambda a: a.sum() > 0)
    .map(lambda a: a / a.sum())
)
levels = st.lists(st.floats(0.01, 0.99), min_size=2, max_size=5, unique=True).map(sorted)


@given(distributions, levels)
def test_risk_measures_es_dominates_var_and_both_are_monotonic(
    probs: np.ndarray, alphas: list[float]
) -> None:
    """Intenção: ES >= VaR e ambos são não decrescentes em alpha (propriedades de medida de risco).
    Se falhar, a fórmula de ES ou a busca do quantil estaria inconsistente."""
    measures = risk_measures(probs, alphas, 1.0, 0.0)
    var = [measures.var[a] for a in alphas]
    es = [measures.es[a] for a in alphas]

    assert all(e >= v - 1e-9 for e, v in zip(es, var, strict=True))
    assert var == sorted(var)
    assert all(b >= a - 1e-9 for a, b in itertools.pairwise(es))
`````

<!-- FILE: tests/unit/test_sectors.py -->
`````python
from __future__ import annotations

from pathlib import Path

import numpy as np
import polars as pl
import pytest

from crplus.aggregation import SectorBandAggregate
from crplus.config import SectorVarianceConfig
from crplus.exceptions import ConfigError
from crplus.sectors import (
    IDIOSYNCRATIC,
    external_variance,
    implied_variance,
    read_variance_file,
    sector_parameters,
)


def _aggregate() -> SectorBandAggregate:
    """Caso de mão: setor 1 com mu = 0.02 (bandas 1 e 2) e s = 0.01; setor 2 vazio."""
    intensity = np.array([[0.0, 0.03, 0.0], [0.0, 0.015, 0.005], [0.0, 0.0, 0.0]])
    volatility = np.array([0.5, 0.01, 0.0])
    raw_volatility = np.array([0.7, 0.03, 0.0])
    raw_intensity = np.array([0.04, 0.05, 0.0])
    return SectorBandAggregate(intensity, volatility, raw_volatility, raw_intensity, 1.0, 3)


def test_sectors_pd_vol_variance_matches_hand_calculation() -> None:
    """Intenção: v_k = (s_k / mu_k)^2 com o ajuste de banding (método CSFB padrão).
    Se falhar, toda a correlação setorial do modelo estaria errada."""
    variance = implied_variance(_aggregate(), adjust_for_banding=True)

    np.testing.assert_allclose(variance, [0.0, (0.01 / 0.02) ** 2, 0.0])


def test_sectors_pd_vol_without_banding_adjustment_uses_raw_sums() -> None:
    """Intenção: adjust_for_banding = false usa s_k = sum(w sigma) e mu_k = sum(w p).
    Se falhar, a sub-opção documentada não teria efeito."""
    variance = implied_variance(_aggregate(), adjust_for_banding=False)

    assert variance[1] == pytest.approx((0.03 / 0.05) ** 2)


def test_sectors_idiosyncratic_sector_always_has_zero_variance() -> None:
    """Intenção: o setor 0 é Poisson puro (v_0 = 0) mesmo com pd_vol não nula.
    Se falhar, o risco idiossincrático ganharia correlação espúria."""
    params = sector_parameters(_aggregate(), ("w_a", "w_b"), SectorVarianceConfig())

    assert params.variance[0] == 0.0
    assert params.names == (IDIOSYNCRATIC, "w_a", "w_b")


def test_sectors_with_zero_mean_are_ignored() -> None:
    """Intenção: setor sem intensidade (mu_k = 0) recebe v_k = 0, mesmo com valor externo.
    Se falhar, haveria divisão por zero ou um fator Gama sem exposição."""
    config = SectorVarianceConfig(method="external", values={"w_a": 1.0, "w_b": 2.0})

    params = sector_parameters(_aggregate(), ("w_a", "w_b"), config)

    np.testing.assert_allclose(params.variance, [0.0, 1.0, 0.0])


def test_sectors_external_method_reports_both_implied_and_used_variance() -> None:
    """Intenção: a tabela de setores mostra o v_k implícito pela pd_vol e o v_k usado.
    Se falhar, o usuário não conseguiria comparar a calibração externa com a implícita."""
    config = SectorVarianceConfig(method="external", values={"w_a": 0.9, "w_b": 0.1})

    params = sector_parameters(_aggregate(), ("w_a", "w_b"), config)

    assert params.variance[1] == pytest.approx(0.9)
    assert params.variance_pd_vol[1] == pytest.approx(0.25)


def test_sectors_external_cv_values_are_squared() -> None:
    """Intenção: com value_type = 'cv', o valor informado é sqrt(v_k).
    Se falhar, coeficientes de variação seriam usados como variâncias."""
    config = SectorVarianceConfig(method="external", value_type="cv", values={"w_a": 0.5})

    assert external_variance(config, ("w_a",)).tolist() == [0.0, 0.25]


@pytest.mark.parametrize(
    ("values", "message"),
    [({"w_a": 1.0}, "sem variância"), ({"w_a": 1.0, "w_b": 1.0, "w_c": 1.0}, "inexistentes")],
)
def test_sectors_external_requires_exact_sector_set(values: dict[str, float], message: str) -> None:
    """Intenção: setor da base sem variância, ou variância de setor inexistente, é erro.
    Se falhar, um setor ficaria sem fator ou um erro de digitação passaria despercebido."""
    config = SectorVarianceConfig(method="external", values=values)

    with pytest.raises(ConfigError, match=message):
        external_variance(config, ("w_a", "w_b"))


@pytest.mark.parametrize("suffix", [".csv", ".parquet"])
def test_sectors_reads_external_variances_from_file(tmp_path: Path, suffix: str) -> None:
    """Intenção: variâncias podem vir de CSV ou parquet com colunas sector/variance.
    Se falhar, a opção values_file documentada não funcionaria."""
    path = tmp_path / f"v{suffix}"
    table = pl.DataFrame({"sector": ["w_b", "w_a"], "variance": [0.2, 0.4]})
    {".csv": table.write_csv, ".parquet": table.write_parquet}[suffix](path)
    config = SectorVarianceConfig(method="external", values_file=path)

    assert external_variance(config, ("w_a", "w_b")).tolist() == [0.0, 0.4, 0.2]


@pytest.mark.parametrize(
    ("name", "table", "message"),
    [
        ("v.txt", pl.DataFrame({"sector": ["w_a"], "variance": [0.1]}), "formato"),
        ("v.csv", pl.DataFrame({"setor": ["w_a"], "variance": [0.1]}), "colunas"),
        ("v.csv", pl.DataFrame({"sector": ["w_a", "w_a"], "variance": [0.1, 0.2]}), "repetidos"),
    ],
)
def test_sectors_rejects_malformed_variance_file(
    tmp_path: Path, name: str, table: pl.DataFrame, message: str
) -> None:
    """Intenção: arquivo com formato, colunas ou setores inválidos é rejeitado com ConfigError.
    Se falhar, um arquivo malformado causaria erro obscuro ou valores ambíguos."""
    path = tmp_path / name
    table.write_csv(path)

    with pytest.raises(ConfigError, match=message):
        read_variance_file(path, "variance")


def test_sectors_rejects_negative_variance_from_file(tmp_path: Path) -> None:
    """Intenção: valores do arquivo passam pela mesma checagem de finitude e sinal do TOML.
    Se falhar, uma variância negativa no arquivo quebraria a PGF."""
    path = tmp_path / "v.csv"
    pl.DataFrame({"sector": ["w_a"], "variance": [-0.1]}).write_csv(path)
    config = SectorVarianceConfig(method="external", values_file=path)

    with pytest.raises(ConfigError, match="finitas"):
        external_variance(config, ("w_a",))
`````

<!-- FILE: tests/unit/test_security.py -->
`````python
"""Testes explícitos dos controles de segurança (CLAUDE.md, seção 9)."""

from __future__ import annotations

import ast
import math
from pathlib import Path

import polars as pl
import pytest

from crplus.config import (
    HARD_MAX_BANDS,
    HARD_MAX_GRID,
    ColumnMap,
    ValidationConfig,
    config_from_mapping,
)
from crplus.exceptions import ConfigError, InputValidationError
from crplus.sources import normalize_source
from crplus.validation import build_rules, enforce, evaluate_rules
from tests.synthetic import PortfolioSpec, make_portfolio

SRC = Path(__file__).resolve().parents[2] / "src" / "crplus"
SOURCE_FILES = sorted(SRC.rglob("*.py"))

FORBIDDEN_CALLS = {"eval", "exec", "compile", "__import__"}
FORBIDDEN_MODULES = {"pickle", "marshal", "shelve", "joblib", "dill", "yaml", "subprocess"}
FORBIDDEN_ATTRIBUTES = {"mktemp"}


def _trees() -> list[tuple[Path, ast.Module]]:
    return [(path, ast.parse(path.read_text(encoding="utf-8"))) for path in SOURCE_FILES]


def _called_names(tree: ast.Module) -> set[str]:
    calls = (node.func for node in ast.walk(tree) if isinstance(node, ast.Call))
    return {func.id for func in calls if isinstance(func, ast.Name)}


def _imported_roots(tree: ast.Module) -> set[str]:
    names = {alias.name for n in ast.walk(tree) if isinstance(n, ast.Import) for alias in n.names}
    modules = {n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
    return {name.split(".")[0] for name in names | modules}


def _attributes(tree: ast.Module) -> set[str]:
    return {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}


def _shell_true_keywords(tree: ast.Module) -> list[ast.keyword]:
    keywords = (kw for node in ast.walk(tree) if isinstance(node, ast.Call) for kw in node.keywords)
    return [kw for kw in keywords if kw.arg == "shell"]


def test_security_source_tree_is_not_empty() -> None:
    """Intenção: as varreduras abaixo de fato inspecionam o código do pacote.
    Se falhar, os testes de segurança passariam vacuamente."""
    assert len(SOURCE_FILES) > 0


@pytest.mark.parametrize(("path", "tree"), _trees(), ids=lambda value: str(value)[-30:])
def test_security_source_does_not_call_dynamic_code_execution(path: Path, tree: ast.Module) -> None:
    """Intenção: eval/exec/compile são proibidos no pacote.
    Se falhar, existe um vetor de execução de código arbitrário."""
    assert _called_names(tree).isdisjoint(FORBIDDEN_CALLS), path


@pytest.mark.parametrize(("path", "tree"), _trees(), ids=lambda value: str(value)[-30:])
def test_security_source_does_not_import_unsafe_modules(path: Path, tree: ast.Module) -> None:
    """Intenção: desserialização insegura (pickle, yaml) e subprocess são proibidos.
    Se falhar, dados não confiáveis poderiam executar código ao serem lidos."""
    assert _imported_roots(tree).isdisjoint(FORBIDDEN_MODULES), path


@pytest.mark.parametrize(("path", "tree"), _trees(), ids=lambda value: str(value)[-30:])
def test_security_source_has_no_assert_or_mktemp_or_shell(path: Path, tree: ast.Module) -> None:
    """Intenção: sem assert para validação de runtime (some com -O), sem mktemp, sem shell=True.
    Se falhar, validações poderiam ser desligadas ou temporários ficariam sujeitos a corrida."""
    asserts = [node for node in ast.walk(tree) if isinstance(node, ast.Assert)]

    assert asserts == [], path
    assert _attributes(tree).isdisjoint(FORBIDDEN_ATTRIBUTES), path
    assert _shell_true_keywords(tree) == [], path


@pytest.mark.parametrize(
    ("key", "value"), [("max_bands", HARD_MAX_BANDS + 1), ("max_grid", HARD_MAX_GRID + 1)]
)
def test_security_resource_limits_above_hard_cap_are_rejected(
    tmp_path: Path, key: str, value: int
) -> None:
    """Intenção: limites de recursos não podem ser elevados acima do teto de segurança.
    Se falhar, um TOML malicioso poderia provocar alocação ilimitada (DoS)."""
    with pytest.raises(ConfigError):
        config_from_mapping({"numerics": {key: value}}, base_dir=tmp_path)


def test_security_config_error_message_does_not_echo_value(tmp_path: Path) -> None:
    """Intenção: mensagens de erro descrevem a restrição sem repetir o valor recebido.
    Se falhar, valores sensíveis poderiam vazar para logs via mensagens de erro."""
    marker = "valor-sensivel-123"

    with pytest.raises(ConfigError) as error:
        config_from_mapping({"model": {"engine": marker}}, base_dir=tmp_path)

    assert marker not in str(error.value)


def test_security_injected_nan_is_rejected_without_echoing_row_values() -> None:
    """Intenção: NaN injetado numa coluna numérica é rejeitado e a mensagem não expõe a linha.
    Se falhar, um NaN contaminaria a distribuição ou o erro vazaria dados da carteira."""
    data = make_portfolio(PortfolioSpec(n_obligors=10, n_sectors=1)).with_columns(
        ead=pl.when(pl.col("operation_id") == 1002)
        .then(math.nan)
        .otherwise(pl.col("ead") + 0.123456)
    )
    source = normalize_source(data, ColumnMap(), "float64", 10)
    rules = build_rules(source.n_sectors, ValidationConfig())
    report = evaluate_rules(source.frame, rules, 5)

    with pytest.raises(InputValidationError) as error:
        enforce(report, source.frame, rules, strict=True)

    assert report.count("ead_domain") == 1
    assert "1002" not in str(error.value)
    assert ".123456" not in str(error.value)
`````

<!-- FILE: tests/unit/test_sources.py -->
`````python
from __future__ import annotations

import polars as pl
import pytest
from hypothesis import given
from hypothesis import strategies as st
from polars.testing import assert_frame_equal

from crplus.config import ColumnMap
from crplus.exceptions import InputValidationError
from crplus.schema import CANONICAL_COLUMNS, OBLIGOR_ID, weight_columns
from crplus.sources import discover_sectors, iter_partitions, normalize_source, to_lazy
from tests.synthetic import PortfolioSpec, make_portfolio


def _normalize(data: object, columns: ColumnMap | None = None) -> pl.DataFrame:
    source = normalize_source(data, columns or ColumnMap(), "float64", 100)
    return source.frame.collect()


def test_sources_dataframe_lazyframe_and_pandas_produce_same_frame() -> None:
    """Intenção: os três tipos de entrada aceitos levam ao mesmo plano canônico.
    Se falhar, o resultado do modelo dependeria do tipo de DataFrame passado pelo usuário."""
    data = make_portfolio()

    eager = _normalize(data)

    assert_frame_equal(_normalize(data.lazy()), eager)
    assert_frame_equal(_normalize(data.to_pandas()), eager)


def test_sources_rejects_unsupported_input_type() -> None:
    """Intenção: entradas que não são DataFrames (ex.: dict) são rejeitadas com erro do pacote.
    Se falhar, o usuário receberia um erro interno obscuro do polars."""
    with pytest.raises(InputValidationError):
        to_lazy({"pd": [0.1]})


def test_sources_renames_configured_columns_to_canonical_names() -> None:
    """Intenção: nomes configurados em [columns] são mapeados para os nomes canônicos.
    Se falhar, bases com nomes próprios do usuário não poderiam ser usadas."""
    data = make_portfolio().rename({"pd": "prob", "ead": "exposicao", "w_s1": "setor_a"})
    columns = ColumnMap(pd="prob", ead="exposicao", weight_prefix="setor_")

    frame = _normalize(data, columns)

    assert frame.columns == [*CANONICAL_COLUMNS, *weight_columns(1)]


def test_sources_discovers_sectors_in_alphabetical_order() -> None:
    """Intenção: a ordem dos setores é estável (alfabética), independentemente da base.
    Se falhar, o setor k mudaria de significado entre execuções e contribuições se embaralhariam."""
    schema = pl.Schema({"w_b": pl.Float64, "pd": pl.Float64, "w_a": pl.Float64})

    assert discover_sectors(schema, "w_") == ("w_a", "w_b")


def test_sources_selects_only_needed_columns_and_casts_floats() -> None:
    """Intenção: colunas extras são descartadas e numéricas inteiras viram Float64 no plano.
    Se falhar, a base carregaria colunas inúteis (memória) ou faria aritmética inteira."""
    data = make_portfolio().with_columns(pl.col("ead").cast(pl.Int64), extra=pl.lit("x"))

    frame = _normalize(data)

    assert "extra" not in frame.columns
    assert frame.schema["ead"] == pl.Float64


def test_sources_casts_weights_to_float32_when_configured() -> None:
    """Intenção: weight_dtype = 'float32' reduz o armazenamento dos pesos.
    Se falhar, a opção de economia de memória não teria efeito."""
    source = normalize_source(make_portfolio(), ColumnMap(), "float32", 100)

    assert source.frame.collect_schema()["_w1"] == pl.Float32


@pytest.mark.parametrize("missing", ["pd", "obligor_id", "ead"])
def test_sources_rejects_missing_required_column_naming_it(missing: str) -> None:
    """Intenção: coluna obrigatória ausente gera erro citando a coluna.
    Se falhar, o usuário não saberia qual coluna falta na base."""
    data = make_portfolio().drop(missing)

    with pytest.raises(InputValidationError, match=missing):
        normalize_source(data, ColumnMap(), "float64", 100)


@pytest.mark.parametrize(
    ("column", "values"),
    [("pd", ["0.1"]), ("w_s1", ["a"]), ("obligor_id", [1.5]), ("lgd", [True])],
)
def test_sources_rejects_incompatible_dtype(column: str, values: list[object]) -> None:
    """Intenção: tipos incompatíveis (texto em PD, float em id) são rejeitados antes da leitura.
    Se falhar, um cast silencioso viraria nulos ou fundiria ids distintos."""
    data = make_portfolio(PortfolioSpec(n_obligors=1, max_ops_per_obligor=1)).with_columns(
        pl.Series(column, values)
    )

    with pytest.raises(InputValidationError, match=column):
        normalize_source(data, ColumnMap(), "float64", 100)


def test_sources_rejects_more_sectors_than_limit() -> None:
    """Intenção: max_sectors limita o número de setores (proteção de recursos).
    Se falhar, uma base com milhares de colunas de peso estouraria as tabelas setor-banda."""
    data = make_portfolio(PortfolioSpec(n_sectors=4))

    with pytest.raises(InputValidationError, match="max_sectors"):
        normalize_source(data, ColumnMap(), "float64", 3)


def test_sources_accepts_string_obligor_ids_and_reports_kind() -> None:
    """Intenção: ids string são aceitos e marcados para a estimativa de memória.
    Se falhar, ids string seriam rejeitados ou subestimados no orçamento."""
    data = make_portfolio().with_columns(pl.col("obligor_id").cast(pl.String))

    assert normalize_source(data, ColumnMap(), "float64", 100).id_kind == "str"


@given(st.integers(min_value=1, max_value=7))
def test_partitions_cover_all_rows_once_and_keep_obligors_together(partitions: int) -> None:
    """Intenção: a partição por hash cobre todas as linhas sem duplicar e não separa devedores.
    Se falhar, operações de um devedor seriam bandadas com exposições parciais diferentes."""
    source = normalize_source(make_portfolio(), ColumnMap(), "float64", 100)
    parts = [frame.collect() for frame in iter_partitions(source, partitions)]

    combined = pl.concat(parts).sort("operation_id")
    owners = pl.concat(
        [part.select(OBLIGOR_ID).unique().with_columns(p=pl.lit(i)) for i, part in enumerate(parts)]
    )

    assert_frame_equal(combined, source.frame.collect().sort("operation_id"))
    assert owners[OBLIGOR_ID].is_unique().all()
`````

<!-- FILE: tests/unit/test_tempstore.py -->
`````python
from __future__ import annotations

import logging
import os
import stat
from pathlib import Path

import pytest

from crplus import tempstore
from crplus.exceptions import CRPlusError
from crplus.tempstore import secure_tempdir


def _fail_inside_tempdir(parent: Path, roots: list[Path]) -> None:
    with secure_tempdir(parent=parent) as store:
        roots.append(store.root)
        raise RuntimeError


def test_secure_tempdir_removes_directory_on_normal_exit(tmp_path: Path) -> None:
    """Intenção: temporários (tabelas de devedores) são apagados ao final do run.
    Se falhar, dados sensíveis da carteira ficam em disco."""
    with secure_tempdir(parent=tmp_path) as store:
        store.path_for("obligors.parquet").write_bytes(b"x")
        root = store.root

    assert not root.exists()


def test_secure_tempdir_removes_directory_when_block_raises(tmp_path: Path) -> None:
    """Intenção: a limpeza é garantida mesmo quando o cálculo falha.
    Se falhar, cada execução com erro deixa temporários com dados da carteira."""
    roots: list[Path] = []

    with pytest.raises(RuntimeError):
        _fail_inside_tempdir(tmp_path, roots)

    assert not roots[0].exists()


@pytest.mark.skipif(os.name == "nt", reason="permissões POSIX não se aplicam ao Windows")
def test_secure_tempdir_is_private_to_owner(tmp_path: Path) -> None:
    """Intenção: o diretório temporário tem permissão 0o700 (só o dono acessa).
    Se falhar, outros usuários da máquina podem ler dados da carteira."""
    with secure_tempdir(parent=tmp_path) as store:
        mode = stat.S_IMODE(store.root.stat().st_mode)

    assert mode == 0o700


@pytest.mark.parametrize("name", ["", ".", "..", "../x", "a/b", "a\\b", "C:x"])
def test_path_for_rejects_names_that_escape_the_directory(tmp_path: Path, name: str) -> None:
    """Intenção: nomes de arquivo temporário não podem conter separadores ou '..'.
    Se falhar, um nome derivado de dados poderia gravar fora do diretório temporário."""
    with secure_tempdir(parent=tmp_path) as store, pytest.raises(CRPlusError):
        store.path_for(name)


def test_secure_tempdir_logs_without_raising_when_cleanup_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """Intenção: falha na limpeza não pode mascarar o erro original nem expor caminhos.
    Se falhar, uma falha de remoção substituiria a exceção real do cálculo."""

    def failing_rmtree(_path: Path) -> None:
        raise OSError

    monkeypatch.setattr(tempstore.shutil, "rmtree", failing_rmtree)

    with caplog.at_level(logging.WARNING), secure_tempdir(parent=tmp_path) as store:
        root = store.root

    assert str(root) not in caplog.text
    assert "temporário" in caplog.text
`````

<!-- FILE: tests/unit/test_validation.py -->
`````python
from __future__ import annotations

import math

import polars as pl
import pytest

from crplus.config import ColumnMap, ValidationConfig
from crplus.exceptions import InputValidationError
from crplus.sources import PortfolioSource, normalize_source
from crplus.validation import (
    ValidationReport,
    build_rules,
    count_duplicate_ids,
    enforce,
    evaluate_rules,
    with_duplicates,
)
from tests.synthetic import PortfolioSpec, make_portfolio

SMALL = PortfolioSpec(n_obligors=20, n_sectors=2, max_ops_per_obligor=2)


def _source(data: pl.DataFrame) -> PortfolioSource:
    return normalize_source(data, ColumnMap(), "float64", 100)


def _report(data: pl.DataFrame, config: ValidationConfig | None = None) -> ValidationReport:
    source = _source(data)
    rules = build_rules(source.n_sectors, config or ValidationConfig())
    return evaluate_rules(source.frame, rules, 10)


def _with_value(column: str, value: object, row: int = 3) -> pl.DataFrame:
    data = make_portfolio(SMALL)
    values = data[column].to_list()
    values[row] = value
    return data.with_columns(pl.Series(column, values, dtype=data.schema[column]))


INVALID_CASES = [
    ("pd", -0.01, "pd_domain"),
    ("pd", 1.01, "pd_domain"),
    ("pd", math.nan, "pd_domain"),
    ("pd", None, "pd_domain"),
    ("pd_vol", -1e-9, "pd_vol_domain"),
    ("pd_vol", math.inf, "pd_vol_domain"),
    ("lgd", 1.5, "lgd_domain"),
    ("ead", -1.0, "ead_domain"),
    ("ead", math.inf, "ead_domain"),
    ("w_s1", -0.1, "weights_domain"),
    ("w_s1", math.nan, "weights_domain"),
    ("w_s1", 1.2, "weights_domain"),
    ("operation_id", None, "operation_id_null"),
    ("obligor_id", None, "obligor_id_null"),
]


@pytest.mark.parametrize(("column", "value", "rule"), INVALID_CASES)
def test_validation_rule_flags_single_invalid_row(column: str, value: object, rule: str) -> None:
    """Intenção: cada regra de domínio detecta exatamente a linha inválida injetada.
    Se falhar, valores fora do domínio (NaN, negativos, nulos) chegariam ao cálculo."""
    report = _report(_with_value(column, value))

    assert report.count(rule) == 1
    assert report.errors[0].first_rows == (3,)


@pytest.mark.parametrize(
    ("column", "value"),
    [("pd", 0.0), ("pd", 1.0), ("lgd", 1.0), ("lgd", 0.0), ("ead", 0.0), ("pd_vol", 0.0)],
)
def test_validation_accepts_domain_boundaries(column: str, value: float) -> None:
    """Intenção: limites válidos do domínio (PD=0, PD=1, LGD=1, EAD=0) não são erros.
    Se falhar, operações legítimas seriam excluídas ou bloqueariam a execução."""
    assert _report(_with_value(column, value)).errors == ()


def test_validation_accepts_zero_residual_weight() -> None:
    """Intenção: pesos somando exatamente 1 (resíduo idiossincrático 0) são válidos.
    Se falhar, carteiras totalmente sistêmicas seriam rejeitadas."""
    data = make_portfolio(SMALL).with_columns(w_s1=pl.lit(0.25), w_s2=pl.lit(0.75))

    assert _report(data).errors == ()


def test_validation_flags_weight_sum_above_one_plus_tolerance() -> None:
    """Intenção: soma de pesos > 1 + tolerância é erro.
    Se falhar, a intensidade total de default de uma operação seria inflada."""
    data = make_portfolio(SMALL).with_columns(w_s1=pl.lit(0.6), w_s2=pl.lit(0.4 + 1e-6))

    assert _report(data).count("weights_sum") == data.height


def test_validation_tolerates_weight_sum_within_tolerance() -> None:
    """Intenção: excesso de soma dentro de weights_tolerance é aceito (arredondamento).
    Se falhar, pesos gerados em ponto flutuante somando 1+1e-12 bloqueariam a execução."""
    data = make_portfolio(SMALL).with_columns(w_s1=pl.lit(0.6), w_s2=pl.lit(0.4 + 1e-12))

    assert _report(data).count("weights_sum") == 0


def test_validation_warns_on_high_pd_without_error() -> None:
    """Intenção: PD acima de pd_warn_threshold gera aviso, não erro.
    Se falhar, PDs altas mas válidas bloqueariam a execução ou passariam sem aviso."""
    report = _report(_with_value("pd", 0.5))

    assert report.errors == ()
    assert [o.name for o in report.warnings] == ["pd_above_threshold"]


def test_validation_counts_zero_exposure_operations() -> None:
    """Intenção: operações com lgd*ead = 0 são contadas no relatório.
    Se falhar, o usuário não saberia quantas operações recebem contribuição nula."""
    assert _report(_with_value("lgd", 0.0)).count("zero_exposure") == 1


def test_validation_report_counts_rows_and_estimates_obligors() -> None:
    """Intenção: o relatório informa o tamanho da base e a estimativa de devedores.
    Se falhar, o número automático de partições seria calculado sobre dados errados."""
    data = make_portfolio(SMALL)

    report = _report(data)

    assert report.n_rows == data.height
    assert report.n_obligors_estimate == pytest.approx(data["obligor_id"].n_unique(), rel=0.1)


def test_validation_strict_mode_raises_with_report_and_no_values() -> None:
    """Intenção: em modo estrito, erro de validação levanta exceção com relatório, sem valores.
    Se falhar, dados inválidos seriam processados ou valores sensíveis vazariam na mensagem."""
    data = _with_value("ead", -123456.789)
    source = _source(data)
    rules = build_rules(source.n_sectors, ValidationConfig())
    report = evaluate_rules(source.frame, rules, 10)

    with pytest.raises(InputValidationError) as error:
        enforce(report, source.frame, rules, strict=True)

    assert error.value.report is report
    assert "123456" not in str(error.value)
    assert "1003" not in str(error.value)


def test_validation_non_strict_mode_removes_only_invalid_rows() -> None:
    """Intenção: strict = false exclui somente as linhas inválidas.
    Se falhar, linhas válidas seriam perdidas ou inválidas mantidas."""
    data = _with_value("pd", 2.0, row=5)
    source = _source(data)
    rules = build_rules(source.n_sectors, ValidationConfig())
    report = evaluate_rules(source.frame, rules, 10)

    kept = enforce(report, source.frame, rules, strict=False).collect()

    assert kept.height == data.height - 1
    assert data["operation_id"][5] not in kept["operation_id"].to_list()


def test_validation_passes_frame_through_when_valid() -> None:
    """Intenção: base válida passa intacta pela aplicação do relatório.
    Se falhar, a validação alteraria dados válidos."""
    source = _source(make_portfolio(SMALL))
    rules = build_rules(source.n_sectors, ValidationConfig())
    report = evaluate_rules(source.frame, rules, 10)

    kept = enforce(report, source.frame, rules, strict=True)

    assert kept.collect().equals(source.frame.collect())


@pytest.mark.parametrize("partitions", [1, 3])
def test_validation_counts_duplicate_operation_ids(partitions: int) -> None:
    """Intenção: operation_id repetido é detectado, inclusive com particionamento por hash.
    Se falhar, contribuições de operações distintas ficariam indistinguíveis na saída."""
    data = _with_value("operation_id", 1000, row=4)

    assert count_duplicate_ids(_source(data).frame, partitions) == 1


@pytest.mark.parametrize("strict", [True, False])
def test_validation_duplicate_ids_are_fatal_in_any_mode(strict: bool) -> None:
    """Intenção: ids repetidos sempre interrompem, pois não há linha 'certa' a manter.
    Se falhar, o modo não estrito escolheria arbitrariamente uma das operações."""
    source = _source(make_portfolio(SMALL))
    rules = build_rules(source.n_sectors, ValidationConfig())
    report = with_duplicates(evaluate_rules(source.frame, rules, 10), 2)

    with pytest.raises(InputValidationError, match="repetido"):
        enforce(report, source.frame, rules, strict=strict)


def test_validation_without_sectors_has_no_weight_rules() -> None:
    """Intenção: carteira só idiossincrática (sem colunas de peso) é válida.
    Se falhar, o caso K = 0 quebraria a validação."""
    data = make_portfolio(PortfolioSpec(n_obligors=5, n_sectors=0))

    assert _report(data).errors == ()


def test_validation_records_no_positions_when_disabled() -> None:
    """Intenção: max_reported_rows = 0 desliga a coleta de posições.
    Se falhar, a configuração seria ignorada e passadas extras seriam feitas."""
    source = _source(_with_value("pd", -1.0))
    rules = build_rules(source.n_sectors, ValidationConfig())

    assert evaluate_rules(source.frame, rules, 0).errors[0].first_rows == ()
`````
