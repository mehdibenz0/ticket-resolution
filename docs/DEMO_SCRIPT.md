# 60-second Demo Script

## Goal
Show that the project is not a toy chatbot but an operations automation that can be shipped.

## Flow

### 1. Open the Streamlit UI
Say:
> “This copilot helps B2B operations teams understand whether a client issue is already known, needs more information, or deserves a real escalation.”

### 2. Run the known gift-distribution scenario
Show:
- decision = `RESOLVE_FROM_KNOWLEDGE`
- similar prior case retrieved
- recommended steps
- draft response to the client

Say:
> “The AI is not inventing a solution. It is using an internal precedent and returning a structured recommendation.”

### 3. Run the missing-context scenario
Show:
- decision = `REQUEST_MORE_INFORMATION`
- clarifying questions generated

Say:
> “This avoids polluting internal queues with tickets that are impossible to investigate.”

### 4. Run the novel refund scenario
Show:
- decision = `ESCALATE_NEW_CASE`
- structured ticket payload created

Say:
> “When the knowledge base is weak, the system does not over-answer. It prepares a clean escalation.”

### 5. Mention n8n and MCP
Say:
> “The same logic can be triggered via an n8n webhook and also exposed as MCP tools, which matters when internal AI ecosystems grow across teams.”
