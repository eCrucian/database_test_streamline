"""Persistência e refinamento de planos de teste; toda decisão vai para a auditoria."""

from pathlib import Path

from dbts.audit.log import AuditEvent, AuditLog
from dbts.domain.models import Origin
from dbts.domain.testing import ProposalStatus, Severity, TestPlan, TestProposal, proposal_id
from dbts.mapping.graph import Graph
from dbts.mapping.guide import slugify
from dbts.testing.codegen import Language, generate
from dbts.testing.engine import load_catalog, merge_plan, propose


class PlanBook:
    def __init__(self, directory: Path, audit: AuditLog, user: str) -> None:
        self._dir = directory
        self._audit = audit
        self._user = user

    def path(self, name: str) -> Path:
        return self._dir / f"{slugify(name)}.json"

    def load(self, name: str) -> TestPlan:
        path = self.path(name)
        if not path.exists():
            return TestPlan(name=name)
        return TestPlan.model_validate_json(path.read_text(encoding="utf-8"))

    def save(self, plan: TestPlan) -> Path:
        path = self.path(plan.name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(plan.model_dump_json(indent=2), encoding="utf-8")
        return path

    def propose(
        self, name: str, graph: Graph, term: str | None, commits: dict[str, str]
    ) -> TestPlan:
        """Roda o motor de hipóteses e incorpora as propostas ao plano `name`."""
        fresh = propose(graph, load_catalog())
        plan = merge_plan(self.load(name), fresh)
        plan = plan.model_copy(update={"term": term, "commits": commits})
        self.save(plan)
        repos = " ".join(f"{repo}@{sha[:8]}" for repo, sha in sorted(commits.items()))
        self._audit.append(
            AuditEvent(
                action="propose",
                user=self._user,
                origin=Origin.PARSER,
                detail=f"plan={name} term={term} proposals={len(fresh)} repos={repos}",
            )
        )
        return plan

    def set_status(self, name: str, ids: list[str], status: ProposalStatus) -> TestPlan:
        plan = self.load(name)
        for pid in ids:
            plan.get(pid).status = status
            self._record(plan, pid, f"status={status}")
        self.save(plan)
        return plan

    def set_params(self, name: str, pid: str, params: dict[str, str]) -> TestPlan:
        plan = self.load(name)
        plan.get(pid).params.update(params)
        self._record(plan, pid, "params " + " ".join(f"{k}={v}" for k, v in sorted(params.items())))
        self.save(plan)
        return plan

    def replace_sql(self, name: str, pid: str, sql: str) -> TestPlan:
        """Fixa a versão corrigida (que executou) como o SQL da proposta."""
        plan = self.load(name)
        proposal = plan.get(pid)
        proposal.template, proposal.params = sql, {}
        self._record(plan, pid, "sql corrigido")
        self.save(plan)
        return plan

    def add_custom(self, name: str, title: str, description: str, sql: str) -> TestProposal:
        """Teste proposto pelo usuário; entra já aceito."""
        plan = self.load(name)
        proposal = TestProposal(
            id=proposal_id("custom", {"sql": sql}),
            hypothesis_id="custom",
            title=title,
            description=description,
            severity=Severity.MEDIUM,
            criterio="Definido pelo usuário.",
            template=sql,
            status=ProposalStatus.ACCEPTED,
            origin=Origin.USER,
        )
        plan.proposals.append(proposal)
        self._record(plan, proposal.id, "custom")
        self.save(plan)
        return proposal

    def generate(self, name: str, language: Language) -> dict[Path, str]:
        """Escreve o código das propostas aceitas em `<plans>/<plano>/<id>.<ext>`."""
        plan = self.load(name)
        code = generate(plan, language)
        out = self._dir / slugify(name)
        out.mkdir(parents=True, exist_ok=True)
        extension = "sql" if language is Language.SQL else "py"
        files = {out / f"{pid}.{extension}": text for pid, text in code.items()}
        for path, text in files.items():
            path.write_text(text, encoding="utf-8")
        self._audit.append(
            AuditEvent(
                action="generate",
                user=self._user,
                origin=Origin.PARSER,
                detail=f"plan={name} lang={language} proposals={' '.join(sorted(code))}",
            )
        )
        return files

    def _record(self, plan: TestPlan, pid: str, decision: str) -> None:
        event = AuditEvent(
            action="plan",
            user=self._user,
            origin=Origin.USER,
            decision=decision,
            detail=f"plan={plan.name} proposal={pid}",
        )
        self._audit.append(event)
