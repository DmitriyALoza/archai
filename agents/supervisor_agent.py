from agno.agent import Agent
from agents.base import get_model
from models.outputs import TaskBrief, CritiqueReport, FinalArchitecture
from orchestration.prompts import SUPERVISOR_SYSTEM_INSTRUCTIONS


def get_clarification_agent() -> Agent:
    """Phase 1: Interprets requirements and generates clarifying questions."""
    return Agent(
        model=get_model(temperature=0.3),
        description=SUPERVISOR_SYSTEM_INSTRUCTIONS,
        output_schema=TaskBrief,
        structured_outputs=True,
    )


def get_critique_agent() -> Agent:
    """Phase 2: Critiques designs and produces revision instructions."""
    return Agent(
        model=get_model(temperature=0.4),
        description=SUPERVISOR_SYSTEM_INSTRUCTIONS,
        output_schema=CritiqueReport,
        structured_outputs=True,
    )


def get_synthesis_agent() -> Agent:
    """Phase 3: Synthesizes final architecture from both designs."""
    return Agent(
        model=get_model(temperature=0.5),
        description=SUPERVISOR_SYSTEM_INSTRUCTIONS,
        output_schema=FinalArchitecture,
        structured_outputs=True,
    )
