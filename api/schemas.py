from pydantic import BaseModel
from typing import List, Dict, Any

class JobInput(BaseModel):
    Process_ID: int
    Arrival_Time: int
    CPU_Percent: float
    IO_Write_Bytes: float
    Num_Ctx_Switches: int
    Priority: int = None

class SimulationRequest(BaseModel):
    jobs: List[JobInput]

class TimelineEntry(BaseModel):
    Process_ID: int
    start_time: int
    end_time: int
    state: str

class AlgoResult(BaseModel):
    algorithm: str
    average_waiting_time: float
    average_turnaround_time: float
    context_switches: int
    execution_timeline: List[TimelineEntry]
    algorithm_complexity: str

class FeatureImportance(BaseModel):
    feature: str
    importance: float

class BenchmarkResponse(BaseModel):
    results: List[AlgoResult]
    ai_recommended: str
    ai_confidence: float
    feature_importances: List[FeatureImportance]

class ComplexityPoint(BaseModel):
    n: int
    fcfs: float
    sjf: float
    srtf: float
    rr: float
