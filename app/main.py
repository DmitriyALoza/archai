import sys
import os
import time
import threading

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import streamlit as st

from ui.state import init_state, reset_state
from ui.components import (
    render_input_panel,
    render_clarification_panel,
    render_status_panel,
    render_critique_progress,
    render_results_panel,
)
from models.inputs import UserInput
from services.session_service import save_session_metadata, update_session_status


st.set_page_config(
    page_title="ArchAI — Multi-Agent Architecture Designer",
    page_icon="🏗️",
    layout="wide",
)

init_state()

# ── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("🏗️ ArchAI")
    st.caption("Multi-Agent Architecture Designer")
    st.divider()

    st.markdown(f"**Session:** `{st.session_state.session_id}`")
    st.markdown(f"**Phase:** `{st.session_state.phase}`")

    render_critique_progress(st.session_state.critique_history)

    st.divider()
    if st.button("New Session", use_container_width=True):
        reset_state()
        st.rerun()

# ── Phase State Machine ───────────────────────────────────────────────────────

phase = st.session_state.phase

# ── PHASE: input ─────────────────────────────────────────────────────────────
if phase == "input":
    st.title("Design Your System Architecture")
    st.markdown(
        "Describe your system idea and ArchAI will use a multi-agent critique loop "
        "to produce a production-ready architecture recommendation."
    )

    raw_idea, context = render_input_panel()

    if raw_idea:
        st.session_state.user_input = UserInput(raw_idea=raw_idea, context=context or None)
        st.session_state.phase = "running_phase1"
        save_session_metadata(st.session_state.session_id, raw_idea[:100])
        st.rerun()

# ── PHASE: running_phase1 (synchronous clarification) ───────────────────────
elif phase == "running_phase1":
    st.title("Analyzing Your Idea...")

    with st.spinner("Supervisor Agent is analyzing your requirements..."):
        from orchestration.workflow import run_phase1

        # Build a plain dict snapshot of session state for the workflow
        workflow_state = {
            "user_input": st.session_state.user_input,
            "task_brief": None,
            "status_log": st.session_state.status_log,
        }

        try:
            run_phase1(workflow_state)
            st.session_state.task_brief = workflow_state["task_brief"]
            st.session_state.status_log = workflow_state["status_log"]
            st.session_state.phase = "clarification"
            update_session_status(st.session_state.session_id, "clarification")
        except Exception as e:
            st.session_state.error_message = str(e)
            st.session_state.phase = "error"

    st.rerun()

# ── PHASE: clarification ─────────────────────────────────────────────────────
elif phase == "clarification":
    st.title("Clarification Questions")

    answers = render_clarification_panel(st.session_state.task_brief)

    if answers is not None:
        st.session_state.clarification_answers = answers
        st.session_state.phase = "running"
        update_session_status(st.session_state.session_id, "running")
        st.rerun()

# ── PHASE: running (background design loop) ──────────────────────────────────
elif phase == "running":
    st.title("Generating Architecture...")

    # Only start the thread once — keyed on _workflow_state being absent
    if st.session_state.get("_workflow_state") is None:
        from orchestration.workflow import run_phase2

        workflow_state = {
            "user_input": st.session_state.user_input,
            "task_brief": st.session_state.task_brief,
            "clarification_answers": st.session_state.clarification_answers,
            "design_a": None,
            "design_b": None,
            "critique_history": [],
            "revision_instructions_a": "",
            "revision_instructions_b": "",
            "final_architecture": None,
            "status_log": list(st.session_state.status_log),
            "phase": "running",
            "error_message": None,
        }
        st.session_state["_workflow_state"] = workflow_state

        thread = threading.Thread(target=run_phase2, args=(workflow_state,), daemon=True)
        thread.start()
        st.session_state.workflow_thread = thread

    # Pull live updates from the shared workflow_state dict
    workflow_state = st.session_state["_workflow_state"]
    st.session_state.status_log = workflow_state["status_log"]
    st.session_state.critique_history = workflow_state["critique_history"]

    render_status_panel(st.session_state.status_log)

    thread = st.session_state.workflow_thread
    if thread and not thread.is_alive():
        # Thread finished — do one final sync then transition
        for key in ["design_a", "design_b", "critique_history", "final_architecture",
                    "status_log", "phase", "error_message"]:
            st.session_state[key] = workflow_state.get(key)
        update_session_status(st.session_state.session_id, st.session_state.phase)
        st.rerun()
    else:
        time.sleep(2)
        st.rerun()

# ── PHASE: complete ───────────────────────────────────────────────────────────
elif phase == "complete":
    if st.session_state.final_architecture:
        render_results_panel(st.session_state.final_architecture)
    else:
        st.error("Workflow completed but no final architecture was produced.")

    st.divider()
    if st.button("Design Another System", type="primary"):
        reset_state()
        st.rerun()

# ── PHASE: error ─────────────────────────────────────────────────────────────
elif phase == "error":
    st.error(f"An error occurred: {st.session_state.error_message}")

    st.subheader("Execution Log")
    render_status_panel(st.session_state.status_log)

    if st.button("Try Again", type="primary"):
        reset_state()
        st.rerun()
