import hashlib

from dbts.audit.log import AuditEvent, AuditLog
from dbts.domain.enrichment import TableSummary
from dbts.domain.models import EntityKind, Origin
from dbts.mapping.graph import Graph
from dbts.mapping.render import table_card
from dbts.ports import LLMProvider, MapStore

PROMPT_VERSION = "table-summary-v1"
PROMPT = """Você é um validador de modelos analisando uma esteira de dados.
Com base APENAS no cartão abaixo, extraído automaticamente do código, descreva a tabela.
Não invente tabelas, colunas ou regras que não aparecem no cartão.

Responda em JSON com:
- resumo: até duas frases sobre o que a tabela contém e para que serve;
- papel: um de fonte, intermediaria, feature, saida, desconhecido;
- pontos_de_atencao: riscos curtos para validação (chaves de junção com nomes diferentes,
  possível duplicação, filtros, vazamento temporal); lista vazia se nada se destaca.

CARTÃO:
{card}
"""


class TableEnricher:
    """Resume tabelas com LLM, com cache pelo hash do prompt e do modelo."""

    def __init__(self, llm: LLMProvider, store: MapStore, audit: AuditLog, user: str) -> None:
        self._llm = llm
        self._store = store
        self._audit = audit
        self._user = user

    def summarize(self, graph: Graph) -> dict[str, TableSummary]:
        return {
            table.id: self._summary(table.id, PROMPT.format(card=table_card(graph, table)))
            for table in graph.of_kind(EntityKind.TABLE)
        }

    def _summary(self, entity_id: str, prompt: str) -> TableSummary:
        key = self._key(prompt)
        cached = self._store.get_annotation(key)
        if cached is not None:
            return TableSummary.model_validate_json(cached)
        summary = self._llm.complete(prompt, TableSummary)
        self._store.put_annotation(key, entity_id, self._llm.model, summary.model_dump_json())
        self._audit.append(
            AuditEvent(
                action="enrich",
                user=self._user,
                origin=Origin.LLM,
                llm_provider=self._llm.name,
                llm_model=self._llm.model,
                detail=f"entity={entity_id} key={key[:12]}",
            )
        )
        return summary

    def _key(self, prompt: str) -> str:
        material = f"{PROMPT_VERSION}\n{self._llm.name}\n{self._llm.model}\n{prompt}"
        return hashlib.sha256(material.encode()).hexdigest()
