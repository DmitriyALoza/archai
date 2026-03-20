import streamlit as st
from models.inputs import ClarificationAnswer, ClarificationAnswers
from models.outputs import TaskBrief, FinalArchitecture, CritiqueReport


def _build_ascii_diagram(final_arch: FinalArchitecture) -> str:
    """Build a simple ASCII box-and-arrow diagram from components and data flows."""
    if not final_arch.components:
        return ""

    lines = []
    box_width = 30

    def box(name: str) -> list[str]:
        label = name[:box_width - 4]
        pad = box_width - 2 - len(label)
        return [
            "+" + "-" * box_width + "+",
            "| " + label + " " * pad + " |",
            "+" + "-" * box_width + "+",
        ]

    # Index components by name for flow lookup
    comp_names = [c.name for c in final_arch.components]

    # Draw each component box
    for comp in final_arch.components:
        for line in box(comp.name):
            lines.append(line)

        # Show outbound flows from this component
        outbound = [f for f in final_arch.data_flows if f.from_component == comp.name]
        for flow in outbound:
            proto = f" [{flow.protocol}]" if flow.protocol else ""
            desc = flow.description[:40] if flow.description else ""
            lines.append(f"  |")
            lines.append(f"  |-- {proto} {desc}")
            lines.append(f"  v")
            lines.append(f"  {flow.to_component}")
            lines.append("")

        lines.append("")

    return "\n".join(lines)


def render_input_panel() -> tuple[str, str]:
    """Renders the idea input form. Returns (raw_idea, context) or ('', '') if not submitted."""
    st.header("Describe Your System Idea")

    with st.form("idea_form"):
        raw_idea = st.text_area(
            "System Idea *",
            placeholder="e.g. Build a real-time collaborative document editor like Google Docs...",
            height=150,
        )
        context = st.text_area(
            "Additional Context (optional)",
            placeholder="e.g. Expected 10k concurrent users, must integrate with Slack, budget constraints...",
            height=100,
        )
        submitted = st.form_submit_button("Analyze & Generate Architecture", type="primary")

    if submitted and raw_idea.strip():
        return raw_idea.strip(), context.strip()
    elif submitted:
        st.error("Please describe your system idea before submitting.")
    return "", ""


def render_clarification_panel(task_brief: TaskBrief) -> ClarificationAnswers | None:
    """
    Renders clarifying questions with rationale.
    Returns ClarificationAnswers when the user submits, else None.
    """
    st.header("Clarifying Questions")
    st.markdown(f"**Summary:** {task_brief.summary}")

    if task_brief.assumptions:
        with st.expander("Assumptions made"):
            for a in task_brief.assumptions:
                st.markdown(f"- {a}")

    if not task_brief.clarifying_questions:
        st.info("No clarifying questions needed. Proceeding with design...")
        if st.button("Continue to Design", type="primary"):
            return ClarificationAnswers(answers=[])
        return None

    with st.form("clarification_form"):
        answers = []
        for i, q in enumerate(task_brief.clarifying_questions):
            st.markdown(f"**Question {i+1}:** {q.question}")
            if q.rationale:
                st.caption(f"Why this matters: {q.rationale}")
            answer = st.text_area(
                "Your answer",
                key=f"answer_{i}",
                placeholder="Enter your answer here...",
                height=80,
            )
            answers.append(ClarificationAnswer(question=q.question, answer=answer or "No answer provided."))

        submitted = st.form_submit_button("Submit Answers & Start Design", type="primary")

    if submitted:
        return ClarificationAnswers(answers=answers)
    return None


def render_status_panel(status_log: list[str]):
    """Renders the live execution log."""
    st.subheader("Execution Log")
    if not status_log:
        st.info("Waiting for execution to start...")
        return

    # Show last 20 messages
    recent = status_log[-20:]
    log_text = "\n".join(recent)
    st.text_area("Status", value=log_text, height=300, disabled=True, label_visibility="collapsed")


def render_critique_progress(critique_history: list[CritiqueReport]):
    """Renders collapsible critique history in sidebar."""
    if not critique_history:
        st.sidebar.info("No critique iterations yet.")
        return

    st.sidebar.subheader(f"Critique Progress ({len(critique_history)} iterations)")
    for report in critique_history:
        with st.sidebar.expander(f"Iteration {report.iteration} — {'Converged' if report.should_stop else 'Continuing'}"):
            st.markdown(f"**Assessment:** {report.convergence_assessment}")
            if report.weaknesses:
                st.markdown(f"**Weaknesses found:** {len(report.weaknesses)}")
                for w in report.weaknesses[:3]:  # show first 3
                    st.markdown(f"- [{w.severity.upper()}] Design {w.design_agent}: {w.aspect}")


def render_results_panel(final_arch: FinalArchitecture):
    """Renders the final architecture results."""
    st.header(f"Final Architecture: {final_arch.title}")
    st.markdown(f"**Executive Summary**\n\n{final_arch.executive_summary}")

    col1, col2 = st.columns(2)

    with col1:
        if final_arch.key_decisions:
            st.subheader("Key Decisions")
            for d in final_arch.key_decisions:
                st.markdown(f"- {d}")

        if final_arch.assumptions:
            st.subheader("Assumptions")
            for a in final_arch.assumptions:
                st.markdown(f"- {a}")

    with col2:
        if final_arch.implementation_phases:
            st.subheader("Implementation Phases")
            for i, phase in enumerate(final_arch.implementation_phases, 1):
                st.markdown(f"{i}. {phase}")

    if final_arch.components:
        st.subheader("Components")
        for comp in final_arch.components:
            with st.expander(f"{comp.name}" + (f" — {comp.technology}" if comp.technology else "")):
                st.markdown(comp.description)
                if comp.responsibilities:
                    st.markdown("**Responsibilities:**")
                    for r in comp.responsibilities:
                        st.markdown(f"- {r}")

    if final_arch.data_flows:
        st.subheader("Data Flows")
        for flow in final_arch.data_flows:
            proto = f" ({flow.protocol})" if flow.protocol else ""
            st.markdown(f"**{flow.from_component}** → **{flow.to_component}**{proto}: {flow.description}")

    col3, col4 = st.columns(2)

    with col3:
        if final_arch.tradeoffs:
            st.subheader("Tradeoffs")
            for t in final_arch.tradeoffs:
                with st.expander(t.aspect):
                    st.markdown(f"**Chosen:** {t.chosen}")
                    if t.alternatives:
                        st.markdown(f"**Alternatives considered:** {', '.join(t.alternatives)}")
                    st.markdown(f"**Rationale:** {t.rationale}")

    with col4:
        if final_arch.risks:
            st.subheader("Risks")
            for risk in final_arch.risks:
                severity_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(risk.severity.lower(), "⚪")
                with st.expander(f"{severity_color} {risk.title}"):
                    st.markdown(risk.description)
                    if risk.mitigation:
                        st.markdown(f"**Mitigation:** {risk.mitigation}")

    # ── Diagrams ──────────────────────────────────────────────────────────────
    st.subheader("Architecture Diagrams")
    tab_mermaid, tab_ascii = st.tabs(["Mermaid", "ASCII"])

    with tab_mermaid:
        if final_arch.mermaid_diagram:
            st.code(final_arch.mermaid_diagram, language="text")
            st.caption("Paste into https://mermaid.live to render")
        else:
            st.info("No Mermaid diagram was generated.")

    with tab_ascii:
        ascii_diagram = _build_ascii_diagram(final_arch)
        if ascii_diagram:
            st.code(ascii_diagram, language="text")
        else:
            st.info("No components available to render ASCII diagram.")

    # Download button
    st.subheader("Export")
    json_str = final_arch.model_dump_json(indent=2)
    st.download_button(
        label="Download Architecture JSON",
        data=json_str,
        file_name=f"architecture_{final_arch.title.replace(' ', '_').lower()}.json",
        mime="application/json",
    )
