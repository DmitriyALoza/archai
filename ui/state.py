import streamlit as st
from services.session_service import generate_session_id


PHASES = ["input", "running_phase1", "clarification", "running", "complete", "error"]


def init_state():
    """Initialize all session_state keys if not already present."""
    defaults = {
        "phase": "input",
        "session_id": generate_session_id(),
        "user_input": None,         # UserInput
        "task_brief": None,          # TaskBrief
        "clarification_answers": None,  # ClarificationAnswers
        "design_a": None,            # ArchitectureDesign
        "design_b": None,            # ArchitectureDesign
        "critique_history": [],      # list[CritiqueReport]
        "final_architecture": None,  # FinalArchitecture
        "status_log": [],            # list[str]
        "error_message": None,
        "workflow_thread": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_state():
    """Reset to a fresh session."""
    keys_to_clear = [
        "phase", "session_id", "user_input", "task_brief",
        "clarification_answers", "design_a", "design_b",
        "critique_history", "final_architecture", "status_log",
        "error_message", "workflow_thread", "_workflow_state",
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    init_state()


def add_status(message: str):
    """Append a status message to the log (safe to call from background thread)."""
    if "status_log" not in st.session_state:
        st.session_state["status_log"] = []
    st.session_state["status_log"].append(message)
    # Keep last 50 messages
    if len(st.session_state["status_log"]) > 50:
        st.session_state["status_log"] = st.session_state["status_log"][-50:]
