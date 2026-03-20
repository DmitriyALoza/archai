"""
ArchAI Workflow

Two-phase HITL approach:
  Phase 1: clarification_step only — fast, synchronous
  Phase 2: design loop + synthesis — runs in background thread

The workflow does NOT use Agno's Workflow/Loop primitives directly;
instead it orchestrates steps manually so that session_state (a plain dict)
serves as the single source of truth, compatible with Streamlit's threading model.
"""

from orchestration.steps import (
    clarification_step,
    design_step_a,
    design_step_b,
    critique_step,
    synthesis_step,
)

MAX_CRITIQUE_ITERATIONS = 3


def run_phase1(session_state: dict) -> None:
    """
    Phase 1: Clarification only.
    Runs synchronously. Sets session_state['task_brief'].
    """
    clarification_step(session_state)


def run_phase2(session_state: dict) -> None:
    """
    Phase 2: Design loop + synthesis.
    Intended to run in a background thread.
    Reads clarification_answers from session_state before starting.
    """
    try:
        for iteration in range(1, MAX_CRITIQUE_ITERATIONS + 1):
            session_state["status_log"].append(f"=== Design iteration {iteration}/{MAX_CRITIQUE_ITERATIONS} ===")

            design_step_a(session_state)
            design_step_b(session_state)

            result = critique_step(session_state, iteration)
            if result == "converged":
                session_state["status_log"].append("Designs converged. Moving to synthesis.")
                break
        else:
            session_state["status_log"].append("Max iterations reached. Moving to synthesis.")

        synthesis_step(session_state)
        session_state["phase"] = "complete"

    except Exception as e:
        session_state["status_log"].append(f"Workflow error: {e}")
        session_state["error_message"] = str(e)
        session_state["phase"] = "error"
