import os
import sys
import numpy as np
import pandas as pd
import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Add project root to python path dynamically
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.schemas import SimulationRequest
from core.scheduler_fcfs import run_fcfs
from core.scheduler_sjf import run_sjf

# Globals for models
burst_predictor = None
algo_selector = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global burst_predictor, algo_selector
    
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    model1_path = os.path.join(project_root, 'ml', 'saved_models', 'burst_predictor.joblib')
    model2_path = os.path.join(project_root, 'ml', 'saved_models', 'algo_selector.joblib')
    
    try:
        if not os.path.exists(model1_path) or not os.path.exists(model2_path):
            raise FileNotFoundError(f"Model files not found. Ensure models are trained and saved at {model1_path} and {model2_path}")
            
        burst_predictor = joblib.load(model1_path)
        algo_selector = joblib.load(model2_path)
        print("ML Models loaded successfully.")
    except Exception as e:
        print(f"Error loading models: {e}")
        
    yield
    # Cleanup logic goes here if needed

app = FastAPI(lifespan=lifespan)

# Add CORS Middleware to allow requests from the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/simulate")
async def simulate_endpoint(request: SimulationRequest):
    if burst_predictor is None or algo_selector is None:
        raise HTTPException(
            status_code=500, 
            detail="Machine Learning models are not loaded. Please ensure models are trained and present."
        )
    
    if not request.jobs:
        raise HTTPException(status_code=400, detail="Job list cannot be empty.")
        
    cpu_list = []
    io_list = []
    burst_list = []
    core_jobs = []
    
    for job in request.jobs:
        # Create DataFrame to avoid sklearn feature name warnings
        features = pd.DataFrame(
            [[job.CPU_Percent, job.IO_Write_Bytes, job.Num_Ctx_Switches]], 
            columns=['CPU_Percent', 'IO_Write_Bytes', 'Num_Ctx_Switches']
        )
        
        # Predict the actual burst time using Model 1
        pred_burst = burst_predictor.predict(features)[0]
        predicted_burst_time = int(round(pred_burst))
        
        # Ensure predicted burst time is logically valid (minimum 1)
        if predicted_burst_time < 1:
            predicted_burst_time = 1
            
        cpu_list.append(job.CPU_Percent)
        io_list.append(job.IO_Write_Bytes)
        burst_list.append(predicted_burst_time)
        
        core_jobs.append({
            "Process_ID": job.Process_ID,
            "Arrival_Time": job.Arrival_Time,
            "Burst_Time": predicted_burst_time
        })
        
    # Calculate Queue Features for Algorithm Selector (Model 2)
    mean_cpu_percent = float(np.mean(cpu_list))
    mean_io = float(np.mean(io_list))
    
    # Handle variance calculations defensively
    if len(cpu_list) > 1:
        variance_cpu_percent = float(np.var(cpu_list, ddof=1))
        variance_burst_time = float(np.var(burst_list, ddof=1))
    else:
        variance_cpu_percent = 0.0
        variance_burst_time = 0.0
        
    queue_df = pd.DataFrame(
        [[mean_cpu_percent, variance_cpu_percent, mean_io, variance_burst_time]],
        columns=['mean_cpu_percent', 'variance_cpu_percent', 'mean_io', 'variance_burst_time']
    )
    
    # Predict Algorithm (0 = FCFS, 1 = SJF)
    algo_pred = int(algo_selector.predict(queue_df)[0])
    selected_algo_name = "SJF" if algo_pred == 1 else "FCFS"
    
    # Execute Core OS Logic based on Model 2's prediction
    if selected_algo_name == "SJF":
        result = run_sjf(core_jobs)
    else:
        result = run_fcfs(core_jobs)
        
    # Build final response
    return {
        "selected_algorithm": selected_algo_name,
        "average_waiting_time": result["average_waiting_time"],
        "execution_timeline": result["execution_timeline"]
    }
