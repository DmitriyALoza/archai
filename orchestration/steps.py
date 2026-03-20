import json
from typing import Any

from models.inputs import ClarificationAnswers
from models.outputs import TaskBrief, ArchitectureDesign, CritiqueReport, FinalArchitecture
from orchestration.prompts import (
    CLARIFICATION_TASK_PROMPT,
    DESIGN_BRIEF_PROMPT,
    CRITIQUE_PROMPT,
    SYNTHESIS_PROMPT,
)


def _format_design(design: ArchitectureDesign | None) -> str:
    if design is None:
        return "No design available."
    return design.model_dump_json(indent=2)


def _format_task_brief(brief: TaskBrief | None) -> str:
    if brief is None:
        return "No task brief available."
    return brief.model_dump_json(indent=2)


def _format_clarification_answers(answers: ClarificationAnswers | None) -> str:
    if answers is None or not answers.answers:
        return "No clarification answers provided."
    lines = []
    for qa in answers.answers:
        lines.append(f"Q: {qa.question}\nA: {qa.answer}")
    return "\n\n".join(lines)


def _format_critique_history(history: list[CritiqueReport]) -> str:
    if not history:
        return "No previous critique iterations."
    parts = []
    for report in history:
        parts.append(f"--- Iteration {report.iteration} ---\n{report.model_dump_json(indent=2)}")
    return "\n\n".join(parts)


def clarification_step(session_state: dict) -> str:
    """
    Reads: user_input
    Writes: task_brief
    Returns: 'awaiting_clarification'
    """
    from agents.supervisor_agent import get_clarification_agent

    user_input = session_state["user_input"]
    session_state["status_log"].append("Running clarification step...")

    prompt = CLARIFICATION_TASK_PROMPT.format(
        raw_idea=user_input.raw_idea,
        context=user_input.context or "None provided",
    )

    agent = get_clarification_agent()
    try:
        response = agent.run(prompt)
        task_brief: TaskBrief = response.content
    except Exception as e:
        session_state["status_log"].append(f"Clarification agent error: {e}. Retrying with reformat request...")
        response = agent.run(prompt + "\n\nIMPORTANT: Respond ONLY with valid JSON matching the TaskBrief schema.")
        task_brief: TaskBrief = response.content

    session_state["task_brief"] = task_brief
    session_state["status_log"].append(f"Task brief created with {len(task_brief.clarifying_questions)} clarifying questions.")
    return "awaiting_clarification"


def design_step_a(session_state: dict) -> str:
    """
    Reads: task_brief, clarification_answers, revision_instructions_a
    Writes: design_a
    """
    from agents.design_agent_a import get_design_agent_a

    session_state["status_log"].append("Design Agent A generating architecture...")

    revision = session_state.get("revision_instructions_a", "")
    revision_block = f"\nREVISION INSTRUCTIONS FROM CRITIQUE:\n{revision}" if revision else ""

    prompt = DESIGN_BRIEF_PROMPT.format(
        task_brief=_format_task_brief(session_state.get("task_brief")),
        clarification_answers=_format_clarification_answers(session_state.get("clarification_answers")),
        revision_instructions=revision_block,
    )

    agent = get_design_agent_a()
    try:
        response = agent.run(prompt)
        design: ArchitectureDesign = response.content
    except Exception as e:
        session_state["status_log"].append(f"Design Agent A error: {e}. Retrying...")
        response = agent.run(prompt + "\n\nIMPORTANT: Respond ONLY with valid JSON matching the ArchitectureDesign schema.")
        design: ArchitectureDesign = response.content

    design.agent_id = "A"
    session_state["design_a"] = design
    session_state["status_log"].append("Design Agent A complete.")
    return "design_a_complete"


def design_step_b(session_state: dict) -> str:
    """
    Reads: task_brief, clarification_answers, revision_instructions_b
    Writes: design_b
    """
    from agents.design_agent_b import get_design_agent_b

    session_state["status_log"].append("Design Agent B generating architecture...")

    revision = session_state.get("revision_instructions_b", "")
    revision_block = f"\nREVISION INSTRUCTIONS FROM CRITIQUE:\n{revision}" if revision else ""

    prompt = DESIGN_BRIEF_PROMPT.format(
        task_brief=_format_task_brief(session_state.get("task_brief")),
        clarification_answers=_format_clarification_answers(session_state.get("clarification_answers")),
        revision_instructions=revision_block,
    )

    agent = get_design_agent_b()
    try:
        response = agent.run(prompt)
        design: ArchitectureDesign = response.content
    except Exception as e:
        session_state["status_log"].append(f"Design Agent B error: {e}. Retrying...")
        response = agent.run(prompt + "\n\nIMPORTANT: Respond ONLY with valid JSON matching the ArchitectureDesign schema.")
        design: ArchitectureDesign = response.content

    design.agent_id = "B"
    session_state["design_b"] = design
    session_state["status_log"].append("Design Agent B complete.")
    return "design_b_complete"


def critique_step(session_state: dict, iteration: int) -> str:
    """
    Reads: design_a, design_b, critique_history
    Writes: critique_history, revision_instructions_a, revision_instructions_b
    Returns: 'converged' if should_stop else 'continue'
    """
    from agents.supervisor_agent import get_critique_agent

    session_state["status_log"].append(f"Critique step — iteration {iteration}...")

    prompt = CRITIQUE_PROMPT.format(
        iteration=iteration,
        design_a=_format_design(session_state.get("design_a")),
        design_b=_format_design(session_state.get("design_b")),
        critique_history=_format_critique_history(session_state.get("critique_history", [])),
    )

    agent = get_critique_agent()
    try:
        response = agent.run(prompt)
        report: CritiqueReport = response.content
    except Exception as e:
        session_state["status_log"].append(f"Critique agent error: {e}. Retrying...")
        response = agent.run(prompt + "\n\nIMPORTANT: Respond ONLY with valid JSON matching the CritiqueReport schema.")
        report: CritiqueReport = response.content

    report.iteration = iteration
    if "critique_history" not in session_state:
        session_state["critique_history"] = []
    session_state["critique_history"].append(report)
    session_state["revision_instructions_a"] = report.revision_instructions_a
    session_state["revision_instructions_b"] = report.revision_instructions_b

    weakness_count = len(report.weaknesses)
    session_state["status_log"].append(
        f"Critique iteration {iteration} complete. {weakness_count} weaknesses found. "
        f"{'Converged.' if report.should_stop else 'Continuing...'}"
    )

    return "converged" if report.should_stop else "continue"


def synthesis_step(session_state: dict) -> str:
    """
    Reads: task_brief, design_a, design_b, critique_history
    Writes: final_architecture
    """
    from agents.supervisor_agent import get_synthesis_agent

    session_state["status_log"].append("Synthesizing final architecture...")

    prompt = SYNTHESIS_PROMPT.format(
        task_brief=_format_task_brief(session_state.get("task_brief")),
        design_a=_format_design(session_state.get("design_a")),
        design_b=_format_design(session_state.get("design_b")),
        critique_history=_format_critique_history(session_state.get("critique_history", [])),
    )

    agent = get_synthesis_agent()
    try:
        response = agent.run(prompt)
        final: FinalArchitecture = response.content
    except Exception as e:
        session_state["status_log"].append(f"Synthesis agent error: {e}. Retrying...")
        response = agent.run(prompt + "\n\nIMPORTANT: Respond ONLY with valid JSON matching the FinalArchitecture schema.")
        final: FinalArchitecture = response.content

    session_state["final_architecture"] = final
    session_state["status_log"].append("Final architecture synthesis complete.")
    return "complete"
