from agno.agent import Agent
from agents.base import get_model
from models.outputs import ArchitectureDesign
from orchestration.prompts import DESIGN_B_FOCUS


def get_design_agent_b() -> Agent:
    """Design Agent B: Infrastructure and operations specialist."""
    return Agent(
        model=get_model(temperature=0.7),
        description=DESIGN_B_FOCUS,
        output_schema=ArchitectureDesign,
        structured_outputs=True,
    )
