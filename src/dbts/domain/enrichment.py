from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class TableRole(StrEnum):
    SOURCE = "fonte"
    INTERMEDIATE = "intermediaria"
    FEATURE = "feature"
    OUTPUT = "saida"
    UNKNOWN = "desconhecido"


class TableSummary(BaseModel):
    """Resumo gerado por LLM: sempre hipótese, nunca fato."""

    model_config = ConfigDict(frozen=True)

    resumo: str = Field(description="Até duas frases sobre o que a tabela contém e para que serve.")
    papel: TableRole
    pontos_de_atencao: list[str] = Field(
        default_factory=list,
        description="Riscos curtos para validação; vazio se nada se destaca.",
    )
