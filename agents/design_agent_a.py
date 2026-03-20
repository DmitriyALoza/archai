from agno.agent import Agent
from agents.base import get_model
from models.outputs import ArchitectureDesign
from orchestration.prompts import DESIGN_A_FOCUS


def get_design_agent_a() -> Agent:
    """Design Agent A: Application architecture specialist."""
    return Agent(
        model=get_model(temperature=0.8),
        description=DESIGN_A_FOCUS,
        output_schema=ArchitectureDesign,
        structured_outputs=True,
    )
