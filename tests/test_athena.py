from typing import Any

import boto3
import pytest
from botocore.stub import Stubber

from dbts.adapters.athena import AthenaExecutor
from dbts.domain.execution import QueryFailedError


def _client() -> Any:
    return boto3.client(
        "athena", region_name="us-east-1", aws_access_key_id="x", aws_secret_access_key="x"
    )


def _status(state: str, **extra: Any) -> dict[str, Any]:
    status: dict[str, Any] = {"State": state, **extra}
    return {
        "QueryExecution": {
            "QueryExecutionId": "q1",
            "Status": status,
            "Statistics": {"DataScannedInBytes": 2048},
        }
    }


def _rows(*rows: list[str]) -> dict[str, Any]:
    return {
        "ResultSet": {
            "Rows": [{"Data": [{"VarCharValue": v} if v else {} for v in row]} for row in rows],
            "ResultSetMetadata": {
                "ColumnInfo": [{"Name": "a", "Type": "varchar"}, {"Name": "b", "Type": "varchar"}]
            },
        }
    }


def _start(stub: Stubber) -> None:
    stub.add_response(
        "start_query_execution",
        {"QueryExecutionId": "q1"},
        {"QueryString": "select 1", "QueryExecutionContext": {"Database": "db"}, "WorkGroup": "wg"},
    )


def test_execute_polls_and_paginates_skipping_header() -> None:
    client = _client()
    sleeps: list[float] = []
    with Stubber(client) as stub:
        _start(stub)
        stub.add_response("get_query_execution", _status("RUNNING"), {"QueryExecutionId": "q1"})
        stub.add_response("get_query_execution", _status("SUCCEEDED"), {"QueryExecutionId": "q1"})
        first = _rows(["a", "b"], ["1", ""]) | {"NextToken": "t"}
        stub.add_response("get_query_results", first, {"QueryExecutionId": "q1"})
        stub.add_response(
            "get_query_results", _rows(["2", "y"]), {"QueryExecutionId": "q1", "NextToken": "t"}
        )
        result = AthenaExecutor(client, "db", "wg", sleep=sleeps.append).execute("select 1")
    assert result.columns == ["a", "b"]
    assert result.rows == [["1", None], ["2", "y"]]
    assert result.bytes_scanned == 2048
    assert result.execution_id == "q1"
    assert sleeps == [1.0]


def test_execute_without_header_row_or_statistics() -> None:
    client = _client()
    with Stubber(client) as stub:
        _start(stub)
        status = {"QueryExecution": {"QueryExecutionId": "q1", "Status": {"State": "SUCCEEDED"}}}
        stub.add_response("get_query_execution", status, {"QueryExecutionId": "q1"})
        stub.add_response("get_query_results", _rows(["1", "x"]), {"QueryExecutionId": "q1"})
        result = AthenaExecutor(client, "db", "wg").execute("select 1")
    assert result.rows == [["1", "x"]]
    assert result.bytes_scanned == 0


def test_failed_query_raises_with_reason() -> None:
    client = _client()
    with Stubber(client) as stub:
        _start(stub)
        failed = _status("FAILED", StateChangeReason="COLUMN_NOT_FOUND: x")
        stub.add_response("get_query_execution", failed, {"QueryExecutionId": "q1"})
        with pytest.raises(QueryFailedError, match="COLUMN_NOT_FOUND"):
            AthenaExecutor(client, "db", "wg").execute("select 1")


def test_timeout() -> None:
    client = _client()
    with Stubber(client) as stub:
        _start(stub)
        stub.add_response("get_query_execution", _status("QUEUED"), {"QueryExecutionId": "q1"})
        executor = AthenaExecutor(client, "db", "wg", sleep=lambda _: None, max_polls=1)
        with pytest.raises(QueryFailedError, match="timeout"):
            executor.execute("select 1")
