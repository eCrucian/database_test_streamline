from typing import Protocol, TypeVar

from pydantic import BaseModel

from dbts.domain.execution import QueryResult
from dbts.domain.models import Fact, FileRef
from dbts.domain.scan import RepoUpdate

T = TypeVar("T", bound=BaseModel)


class LLMResponseError(Exception):
    """O provider respondeu sem a saída estruturada pedida (recusa, corte por tokens...)."""


class LLMProvider(Protocol):
    name: str
    model: str

    def complete(self, prompt: str, schema: type[T]) -> T: ...


class QueryExecutor(Protocol):
    """Executa SQL e devolve o resultado; falhas viram QueryFailedError."""

    def execute(self, sql: str) -> QueryResult: ...


class ResultSink(Protocol):
    """Grava o resultado de uma query executada e devolve onde gravou."""

    name: str

    def write(self, digest: str, sql: str, result: QueryResult) -> str: ...


class Extractor(Protocol):
    """Extrai fatos de um arquivo. Não deve lançar exceção por sintaxe inválida."""

    extensions: frozenset[str]

    def extract(self, content: str, ref: FileRef) -> list[Fact]: ...


class MapStore(Protocol):
    def repo_commit(self, repo: str) -> str | None: ...

    def repo_blobs(self, repo: str) -> dict[str, str]: ...

    def apply(self, update: RepoUpdate) -> None: ...

    def facts(self, repo: str) -> list[Fact]: ...

    def all_facts(self) -> list[Fact]: ...

    def repo_commits(self) -> dict[str, str]: ...

    def get_meta(self, key: str) -> str | None: ...

    def set_meta(self, key: str, value: str) -> None: ...

    def get_annotation(self, key: str) -> str | None: ...

    def put_annotation(self, key: str, entity_id: str, model: str, payload: str) -> None: ...
