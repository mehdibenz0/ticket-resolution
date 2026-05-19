from __future__ import annotations
import json
from mcp.server.fastmcp import FastMCP
from resolution_copilot.retrieval import CaseRetriever
from resolution_copilot.ticketing import build_ticket_payload, persist_ticket
from resolution_copilot.schemas import ClientIssue

mcp = FastMCP('b2b-resolution-copilot')
retriever = CaseRetriever()


@mcp.tool()
def search_similar_cases(query: str, top_k: int = 3) -> str:
    """Search documented internal support cases by semantic similarity."""
    return json.dumps(retriever.search(query, top_k=top_k), indent=2)


@mcp.tool()
def create_escalation_ticket(client_company: str, requester_role: str, subject: str, message: str) -> str:
    """Create and persist a structured escalation ticket from a novel client issue."""
    issue = ClientIssue(
        client_company=client_company,
        requester_role=requester_role,
        channel='internal',
        subject=subject,
        message=message,
    )
    ticket = build_ticket_payload(issue, evidence=['Created via MCP tool'], missing_information=[])
    path = persist_ticket(ticket)
    return json.dumps({'ticket_path': str(path), 'ticket': ticket.model_dump()}, indent=2)


if __name__ == '__main__':
    mcp.run()
