# ArchAI PRD

## Agentic Architecture Design Team

---

## 1. Product Summary
ArchAI is a containerized multi-agent application that helps users design high-quality software/system architectures through structured agent collaboration and critique.

A user submits a rough system idea through a Streamlit UI. A Supervisor Agent interprets the request, expands requirements, asks clarifying questions, and dispatches tasks to two design agents. These agents propose architectures, which are critiqued and refined through a loop before producing a final recommendation.

---

## 2. Problem Statement
- Users provide incomplete requirements
- Single LLM responses lack critique
- Designs often miss tradeoffs

ArchAI solves this by simulating a real architecture review process.

---

## 3. Goals
### Primary
- Multi-agent architecture generation
- Critique loop for refinement
- Structured outputs

### Secondary
- Streamlit UI
- Docker deployment
- Diagram generation

---

## 4. Core Workflow

1. User inputs idea
2. Supervisor expands + asks questions
3. Task brief created
4. Two agents generate designs
5. Supervisor critiques
6. Agents revise
7. Final architecture produced

---

## 5. Agents

### Supervisor Agent
- Requirement expansion
- Critique orchestration
- Final synthesis

### Design Agent A (Architecture)
- Services
- APIs
- System decomposition

### Design Agent B (Infrastructure)
- Scaling
- Reliability
- Performance

---

## 6. Critique Loop
- Compare designs
- Identify weaknesses
- Request revisions
- Iterate until convergence or limit

---

## 7. Output

### Includes:
- Final architecture
- Assumptions
- Components
- Data flow
- Tradeoffs
- Risks
- Optional Mermaid diagram

---

## 8. UI (Streamlit)

### Sections:
- Input panel
- Clarification panel
- Execution status
- Results panel

---

## 9. Tech Stack
- Python
- Agno
- Streamlit
- Docker
- SQLite (optional)

---

## 10. System Flow

User → Supervisor → Clarification → Task Brief → Agents → Critique → Final Output

---

## 11. Repo Structure

```
ArchAI/
├── app/
├── agents/
├── orchestration/
├── services/
├── ui/
├── Dockerfile
└── README.md
```

---

## 12. MVP Criteria
- Input → clarification → dual design → critique → final output
- Runs in Docker
- Streamlit UI functional

---

## 13. Vision
“GitHub Copilot for System Design”

---

## 14. One-Line Definition
ArchAI is a Dockerized multi-agent architecture design assistant that uses critique loops to produce high-quality system designs.
