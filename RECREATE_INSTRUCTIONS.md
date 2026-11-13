# Instruções para recriar o projeto `crplus` (CreditRisk+ em Python)

Você vai receber dois arquivos: este (`RECREATE_INSTRUCTIONS.md`) e `CRPLUS_BUNDLE.md`, que
contém o código-fonte completo. Coloque os dois numa pasta vazia, abra o Claude Code nessa pasta
e cole o prompt da seção 1. (A seção 2 permite fazer o mesmo sem o Claude Code.)

## 1. Prompt para o Claude Code

> Recrie o projeto descrito em `CRPLUS_BUNDLE.md` nesta pasta, **sem alterar nenhum conteúdo**:
>
> 1. O bundle tem 92 arquivos. Cada um começa com uma linha `<!-- FILE: caminho -->`,
>    seguida de um bloco de código delimitado por 5 ou mais crases. O conteúdo do arquivo é
>    exatamente o que está entre a linha de abertura (que contém as crases e a linguagem) e a
>    linha de fechamento com o mesmo número de crases. Não reformate, não "corrija" e não
>    resuma nada; preserve finais de linha LF e uma quebra de linha ao final.
> 2. Para não transcrever à mão um arquivo tão grande, salve o script da seção 2 deste arquivo
>    como `extract_bundle.py`, rode `python extract_bundle.py CRPLUS_BUNDLE.md` e depois apague
>    o script. Confira que foram criados 92 arquivos, incluindo `CLAUDE.md`,
>    `pyproject.toml`, `src/crplus/api.py` e `tests/integration/golden/end_to_end.json`.
> 3. Rode `git init` e faça um commit inicial com todos os arquivos.
> 4. Instale o ambiente: `uv sync --all-extras` (Python 3.12; o `uv` baixa o Python se
>    necessário). Isso gera um novo `uv.lock`. Se a validação do passo 5 falhar por diferença
>    de versão, fixe as versões da tabela da seção 3 no `pyproject.toml`.
> 5. Valide com os comandos do `Makefile` (alvo `check`). Se `make` não existir (Windows), rode
>    cada comando diretamente, sempre como `uv run python -m <ferramenta>`:
>    `ruff check .`, `ruff format --check .`, `mypy --strict src`,
>    `pytest -m "not slow" --cov=crplus --cov-branch --cov-fail-under=95`,
>    `pytest -m integration`, `bandit -r src -c pyproject.toml -ll`, `pip_audit`,
>    `xenon --max-absolute A --max-modules A --max-average A src` e
>    `mkdocs build --strict --site-dir <diretório temporário fora do projeto>`.
>    Resultado esperado: tudo verde, cobertura 100%, ~426 testes passando e 4 pulados.
> 6. Depois de validado, leia o `CLAUDE.md` (especificação do projeto) e `docs/` antes de
>    qualquer mudança. Não altere código a menos que eu peça.

## 2. Extrator (sem depender do Claude Code)

```python
"""Extrai os arquivos de CRPLUS_BUNDLE.md para o diretório atual."""

import re
import sys
from pathlib import Path

MARKER = re.compile(r"^<!-- FILE: (.+) -->$")
FENCE = re.compile(r"^(`{5,})[A-Za-z]*$")


def extract(bundle: Path, root: Path) -> int:
    lines = bundle.read_text(encoding="utf-8").split("\n")
    count, i = 0, 0
    while i < len(lines):
        marker = MARKER.match(lines[i])
        if not marker:
            i += 1
            continue
        fence = FENCE.match(lines[i + 1]).group(1)
        end = lines.index(fence, i + 2)
        target = (root / marker.group(1)).resolve()
        if not target.is_relative_to(root.resolve()):
            raise SystemExit(f"caminho inseguro: {marker.group(1)}")
        target.parent.mkdir(parents=True, exist_ok=True)
        content = "\n".join(lines[i + 2 : end])
        target.write_text(content + "\n" if content else "", encoding="utf-8", newline="\n")
        count += 1
        i = end + 1
    return count


if __name__ == "__main__":
    print(extract(Path(sys.argv[1]), Path.cwd()), "arquivos extraídos")
```

Uso: `python extract_bundle.py CRPLUS_BUNDLE.md` numa pasta vazia, depois os passos 3–5.

## 3. Versões usadas no desenvolvimento original

| Pacote | Versão |
|--------|--------|
| `polars` | 2.1.0 |
| `numpy` | 2.5.4 |
| `scipy` | 1.18.1 |
| `pyarrow` | 26.0.1 |
| `numba` | 0.68.1 |
| `pandas` | 3.1.1 |
| `pytest` | 9.2.0 |
| `hypothesis` | 6.170.15 |
| `mypy` | 2.4.1 |
| `ruff` | 0.17.4 |
| `bandit` | 1.9.4 |
| `xenon` | 0.9.3 |
| `mkdocs` | 1.6.1 |
| `mkdocs-material` | 9.8.1 |
| `mkdocstrings` | 1.0.8 |

Python 3.12.13, uv 0.12.3, Windows 11.

## 4. Observações

- `uv.lock` não está no bundle (≈ 500 KB); ele é regenerado no passo 4.
- Os benchmarks de escala (`pytest -m slow`) não fazem parte da validação: geram dezenas de GB.
  Veja `docs/performance.md`.
- No Windows com Controle de Aplicativo, os executáveis de `.venv/Scripts` podem ser bloqueados;
  por isso todos os comandos usam `uv run python -m <ferramenta>`.
