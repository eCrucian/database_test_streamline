import time
from collections.abc import Callable
from typing import TYPE_CHECKING

from dbts.domain.execution import QueryFailedError, QueryResult

if TYPE_CHECKING:
    from mypy_boto3_athena import AthenaClient
    from mypy_boto3_athena.type_defs import GetQueryResultsOutputTypeDef

TERMINAL_FAILURES = {"FAILED", "CANCELLED"}


class AthenaExecutor:
    """Executa uma query no Athena e devolve todas as linhas (strings, como o Athena devolve)."""

    def __init__(
        self,
        client: "AthenaClient",
        database: str,
        workgroup: str,
        sleep: Callable[[float], None] = time.sleep,
        poll_seconds: float = 1.0,
        max_polls: int = 1800,
    ) -> None:
        self._client = client
        self._database = database
        self._workgroup = workgroup
        self._sleep = sleep
        self._poll_seconds = poll_seconds
        self._max_polls = max_polls

    def execute(self, sql: str) -> QueryResult:
        execution_id = self._client.start_query_execution(
            QueryString=sql,
            QueryExecutionContext={"Database": self._database},
            WorkGroup=self._workgroup,
        )["QueryExecutionId"]
        scanned = self._wait(execution_id)
        columns, rows = self._results(execution_id)
        return QueryResult(
            execution_id=execution_id, columns=columns, rows=rows, bytes_scanned=scanned
        )

    def _wait(self, execution_id: str) -> int:
        for _ in range(self._max_polls):
            execution = self._client.get_query_execution(QueryExecutionId=execution_id)
            info = execution["QueryExecution"]
            state = info["Status"]["State"]
            if state == "SUCCEEDED":
                return info.get("Statistics", {}).get("DataScannedInBytes", 0)
            if state in TERMINAL_FAILURES:
                reason = info["Status"].get("StateChangeReason", state)
                raise QueryFailedError(reason)
            self._sleep(self._poll_seconds)
        raise QueryFailedError(f"timeout aguardando a query {execution_id}")

    def _results(self, execution_id: str) -> tuple[list[str], list[list[str | None]]]:
        paginator = self._client.get_paginator("get_query_results")
        columns: list[str] = []
        rows: list[list[str | None]] = []
        for page in paginator.paginate(QueryExecutionId=execution_id):
            columns = columns or _columns(page)
            rows.extend(
                [cell.get("VarCharValue") for cell in r["Data"]] for r in page["ResultSet"]["Rows"]
            )
        if rows and rows[0] == columns:
            rows = rows[1:]
        return columns, rows


def _columns(page: "GetQueryResultsOutputTypeDef") -> list[str]:
    return [c["Name"] for c in page["ResultSet"]["ResultSetMetadata"]["ColumnInfo"]]
