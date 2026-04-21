from pydantic import BaseModel
from typing import List

class JobInput(BaseModel):
    Process_ID: int
    Arrival_Time: int
    CPU_Percent: float
    IO_Write_Bytes: float
    Num_Ctx_Switches: int

class SimulationRequest(BaseModel):
    jobs: List[JobInput]
