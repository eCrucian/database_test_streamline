from pydantic import BaseModel, Field

from dbts.audit.log import AuditEvent, AuditLog
from dbts.domain.models import Origin
from dbts.ports import LLMProvider

PROMPT = """Você corrige queries SQL para AWS Athena (dialeto Presto/Trino).
A query abaixo falhou. Corrija APENAS o necessário para ela executar, mantendo a intenção,
as tabelas e as colunas. Use somente SELECT (nada de INSERT, DELETE, DROP ou escrita).

ERRO:
{error}

QUERY:
{sql}

Responda em JSON com sql (a query corrigida) e explicacao (uma frase sobre a correção).
"""


class SqlFix(BaseModel):
    sql: str = Field(description="Query corrigida, completa.")
    explicacao: str = Field(description="Uma frase sobre o que foi corrigido.")


class SqlFixer:
    def __init__(self, llm: LLMProvider, audit: AuditLog, user: str) -> None:
        self._llm = llm
        self._audit = audit
        self._user = user

    def fix(self, sql: str, error: str) -> SqlFix:
        fix = self._llm.complete(PROMPT.format(error=error, sql=sql), SqlFix)
        self._audit.append(
            AuditEvent(
                action="fix",
                user=self._user,
                origin=Origin.LLM,
                llm_provider=self._llm.name,
                llm_model=self._llm.model,
                detail=fix.explicacao,
            )
        )
        return fix
