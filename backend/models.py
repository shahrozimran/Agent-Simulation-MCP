from typing import Literal
from pydantic import BaseModel, ConfigDict, Field
from .catalog import AGENT_IDS

AgentId = Literal['simple_reflex', 'model_based', 'goal_based', 'utility_based', 'learning', 'hierarchical']
ScenarioId = Literal['normal', 'heavy_traffic', 'rain_urgent', 'partial_visibility', 'road_closure']

class SimulationRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    agent_id: AgentId = 'goal_based'
    scenario_id: ScenarioId = 'rain_urgent'
    seed: int = Field(42, ge=0, le=2147483647)
    deadline: float | None = Field(None, ge=5, le=180)
    noise: float = Field(0.0, ge=0, le=0.4)

class ComparisonRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    agent_ids: list[AgentId] = Field(default_factory=lambda: list(AGENT_IDS), min_length=1, max_length=6)
    scenario_id: ScenarioId = 'rain_urgent'
    seed: int = Field(42, ge=0, le=2147483647)
    deadline: float | None = Field(None, ge=5, le=180)
    noise: float = Field(0.0, ge=0, le=0.4)

class CompareSavedRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    run_ids: list[str] = Field(min_length=2, max_length=100)

class TrainingRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    scenario_id: ScenarioId = 'rain_urgent'
    episodes: int = Field(150, ge=10, le=1000)
    seed: int = Field(42, ge=0, le=2147483647)
    epsilon: float = Field(0.2, ge=0.05, le=1.0)
