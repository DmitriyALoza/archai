from pydantic import BaseModel, Field
from typing import Optional


# Shared primitives

class Component(BaseModel):
    name: str
    description: str
    technology: Optional[str] = None
    responsibilities: list[str] = Field(default_factory=list)


class DataFlow(BaseModel):
    from_component: str
    to_component: str
    description: str
    protocol: Optional[str] = None


class Tradeoff(BaseModel):
    aspect: str
    chosen: str
    alternatives: list[str] = Field(default_factory=list)
    rationale: str


class Risk(BaseModel):
    title: str
    description: str
    severity: str  # low, medium, high
    mitigation: Optional[str] = None


# Supervisor Phase 1 output

class ClarifyingQuestion(BaseModel):
    question: str
    rationale: str
    category: Optional[str] = None  # e.g. "scale", "security", "data"


class TaskBrief(BaseModel):
    summary: str = Field(..., description="Expanded understanding of the system requirements")
    assumptions: list[str] = Field(default_factory=list)
    clarifying_questions: list[ClarifyingQuestion] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    success_criteria: list[str] = Field(default_factory=list)


# Design Agent output

class ArchitectureDesign(BaseModel):
    agent_id: str = Field(..., description="Identifier for the design agent (A or B)")
    summary: str
    components: list[Component] = Field(default_factory=list)
    data_flows: list[DataFlow] = Field(default_factory=list)
    tradeoffs: list[Tradeoff] = Field(default_factory=list)
    risks: list[Risk] = Field(default_factory=list)
    mermaid_diagram: Optional[str] = Field(None, description="Mermaid diagram code")
    revision_notes: Optional[str] = Field(None, description="Notes from revision instructions")


# Supervisor Phase 2 output

class DesignWeakness(BaseModel):
    design_agent: str  # "A" or "B"
    aspect: str
    description: str
    severity: str  # low, medium, high


class CritiqueReport(BaseModel):
    iteration: int
    weaknesses: list[DesignWeakness] = Field(default_factory=list)
    convergence_assessment: str
    revision_instructions_a: str = Field(..., description="Specific revision instructions for Design Agent A")
    revision_instructions_b: str = Field(..., description="Specific revision instructions for Design Agent B")
    should_stop: bool = Field(False, description="True if designs have converged and no further iteration is needed")


# Supervisor Phase 3 output

class FinalArchitecture(BaseModel):
    title: str
    executive_summary: str
    key_decisions: list[str] = Field(default_factory=list)
    components: list[Component] = Field(default_factory=list)
    data_flows: list[DataFlow] = Field(default_factory=list)
    tradeoffs: list[Tradeoff] = Field(default_factory=list)
    risks: list[Risk] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    mermaid_diagram: Optional[str] = Field(None)
    implementation_phases: list[str] = Field(default_factory=list)
