# ArchAI

A multi-agent architecture design assistant that uses iterative critique loops to produce high-quality system designs. Give it an idea, answer a few clarifying questions, and get back a complete architecture with components, data flows, tradeoffs, risks, and an implementation plan.

## How it works

ArchAI runs three specialist agents in a structured workflow:

**Supervisor** — orchestrates the entire process. It expands your initial idea into a structured task brief, critiques competing designs, and synthesizes the final output.

**Design Agent A** — focuses on application architecture: service decomposition, APIs, data models, and business logic. Runs at higher temperature for more creative proposals.

**Design Agent B** — focuses on infrastructure and operations: scaling, reliability, observability, deployment, and security. Runs at lower temperature for grounded, conventional solutions.

### Workflow

```
User idea
    │
    ▼
[Phase 1 — Clarification]
Supervisor expands the idea, surfaces assumptions,
and generates clarifying questions for the user.
    │
    ▼
User answers questions
    │
    ▼
[Phase 2 — Design Loop] (runs in background, up to 3 iterations)
┌─────────────────────────────────────────────────┐
│  Design Agent A  ──→  application architecture  │
│  Design Agent B  ──→  infrastructure design      │
│       │                                          │
│  Supervisor critiques both designs,              │
│  identifies weaknesses, issues revision notes.  │
│  Repeats until convergence or iteration limit.  │
└─────────────────────────────────────────────────┘
    │
    ▼
[Synthesis]
Supervisor combines the best elements of both designs
into a final architecture document.
    │
    ▼
Output: components, data flows, tradeoffs, risks,
        assumptions, implementation phases, diagram
```

All agent outputs are structured via Pydantic schemas — no free-form text parsing.

---

## Setup

### Prerequisites

- Docker and Docker Compose
- An OpenAI API key

### 1. Clone and configure

```bash
git clone <repo-url>
cd archai
cp .env.example .env
```

Edit `.env`:

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL_ID=gpt-4o
DB_PATH=data/archai.db
```

### 2. Run with Docker

```bash
docker-compose up --build
```

Open [http://localhost:8501](http://localhost:8501).

The `data/` directory is mounted as a volume so the SQLite session database persists across container restarts.

### Running locally (without Docker)

Requires Python 3.12+ and [uv](https://github.com/astral-sh/uv).

```bash
uv sync
uv run streamlit run app/main.py
```

---

## Project structure

```
archai/
├── app/
│   └── main.py               # Streamlit entry point, phase state machine
├── agents/
│   ├── base.py               # LLM model factory (swap providers here)
│   ├── supervisor_agent.py   # Clarification, critique, and synthesis agents
│   ├── design_agent_a.py     # Application architecture agent
│   └── design_agent_b.py     # Infrastructure agent
├── orchestration/
│   ├── prompts.py            # All system prompts
│   ├── steps.py              # Individual workflow step functions
│   └── workflow.py           # Phase 1 / Phase 2 orchestration
├── models/
│   ├── inputs.py             # Input schemas (UserInput, ClarificationAnswers)
│   └── outputs.py            # Output schemas (TaskBrief, ArchitectureDesign, etc.)
├── ui/
│   ├── state.py              # Streamlit session state management
│   └── components.py         # UI rendering components
├── services/
│   └── session_service.py    # SQLite session tracking
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## Configuration

| Variable | Description | Default |
|---|---|---|
| `OPENAI_API_KEY` | Your OpenAI API key | — |
| `OPENAI_MODEL_ID` | Model to use | `gpt-4o` |
| `DB_PATH` | Path for SQLite session database | `data/archai.db` |

To switch to a different LLM provider, edit `agents/base.py` — it's the single point of model instantiation.

## Agent temperatures

| Agent | Temperature | Rationale |
|---|---|---|
| Design Agent A | 0.8 | Creative, divergent application proposals |
| Design Agent B | 0.2 | Grounded, conventional infrastructure solutions |
| Supervisor (all phases) | 0.2 | Deterministic requirement analysis and synthesis |

## License

MIT
