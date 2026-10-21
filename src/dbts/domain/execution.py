from pydantic import BaseModel, ConfigDict


class QueryFailedError(Exception):
    """A query foi rejeitada ou falhou na execução; a mensagem vai para o loop de correção."""


class QueryResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    execution_id: str
    columns: list[str]
    rows: list[list[str | None]]
    bytes_scanned: int


class Attempt(BaseModel):
    model_config = ConfigDict(frozen=True)

    sql: str
    error: str
    fixed_by: str | None = None
