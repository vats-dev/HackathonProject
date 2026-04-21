import os
import sys
import numpy as np
import pandas as pd
import joblib
import math
from typing import List, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor

# Add project root to python path dynamically
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.schemas import SimulationRequest, BenchmarkResponse, AlgoResult, FeatureImportance, ComplexityPoint
from core.scheduler_fcfs import run_fcfs
from core.scheduler_sjf import run_sjf
from core.scheduler_rr import run_rr
from core.scheduler_priority import run_priority

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
            print(f"Warning: Models not found at {model1_path} or {model2_path}. API will fail until models are trained.")
        else:
            burst_predictor = joblib.load(model1_path)
            algo_selector = joblib.load(model2_path)
            print("ML Models loaded successfully.")
    except Exception as e:
        print(f"Error loading models: {e}")
        
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_burst_prediction(job):
    features = pd.DataFrame(
        [[job.CPU_Percent, job.IO_Write_Bytes, job.Num_Ctx_Switches]], 
        columns=['CPU_Percent', 'IO_Write_Bytes', 'Num_Ctx_Switches']
    )
    
    pred_burst = burst_predictor.predict(features)[0]
    
    # Confidence Interval calculation
    all_tree_preds = np.stack([tree.predict(features) for tree in burst_predictor.estimators_])
    burst_std = np.std(all_tree_preds, axis=0)[0]
    
    predicted_burst_time = max(1, int(round(pred_burst)))
    burst_lower = max(1, int(round(pred_burst - burst_std)))
    burst_upper = max(1, int(round(pred_burst + burst_std)))
    
    return {
        "predicted": predicted_burst_time,
        "lower": burst_lower,
        "upper": burst_upper
    }

@app.post("/simulate")
async def simulate_endpoint(request: SimulationRequest):
    if burst_predictor is None or algo_selector is None:
        raise HTTPException(status_code=500, detail="Models not loaded.")
    
    if not request.jobs:
        raise HTTPException(status_code=400, detail="Job list cannot be empty.")
        
    core_jobs = []
    burst_data = []
    
    for job in request.jobs:
        prediction = get_burst_prediction(job)
        burst_data.append(prediction)
        
        core_jobs.append({
            "Process_ID": job.Process_ID,
            "Arrival_Time": job.Arrival_Time,
            "Burst_Time": prediction["predicted"],
            "Priority": job.Priority if job.Priority is not None else job.Process_ID
        })
        
    # Calculate Queue Features
    cpu_list = [j.CPU_Percent for j in request.jobs]
    io_list = [j.IO_Write_Bytes for j in request.jobs]
    burst_list = [p["predicted"] for p in burst_data]
    
    mean_cpu = float(np.mean(cpu_list))
    var_cpu = float(np.var(cpu_list, ddof=1)) if len(cpu_list) > 1 else 0.0
    mean_io = float(np.mean(io_list))
    var_burst = float(np.var(burst_list, ddof=1)) if len(burst_list) > 1 else 0.0
        
    queue_df = pd.DataFrame(
        [[mean_cpu, var_cpu, mean_io, var_burst]],
        columns=['mean_cpu_percent', 'variance_cpu_percent', 'mean_io', 'variance_burst_time']
    )
    
    algo_pred = int(algo_selector.predict(queue_df)[0])
    algo_map = {0: "FCFS", 1: "SJF", 2: "SRTF", 3: "RR"}
    selected_algo = algo_map.get(algo_pred, "FCFS")
    
    if selected_algo == "FCFS":
        result = run_fcfs(core_jobs)
    elif selected_algo == "SJF":
        result = run_sjf(core_jobs, preemptive=False)
    elif selected_algo == "SRTF":
        result = run_sjf(core_jobs, preemptive=True)
    elif selected_algo == "RR":
        result = run_rr(core_jobs, quantum=4)
    else:
        result = run_fcfs(core_jobs)
        
    return {
        "selected_algorithm": selected_algo,
        "burst_predictions": burst_data,
        **result
    }

@app.post("/benchmark", response_model=BenchmarkResponse)
async def benchmark_endpoint(request: SimulationRequest):
    if burst_predictor is None or algo_selector is None:
        raise HTTPException(status_code=500, detail="Models not loaded.")
    
    core_jobs = []
    burst_data = []
    for job in request.jobs:
        prediction = get_burst_prediction(job)
        burst_data.append(prediction)
        core_jobs.append({
            "Process_ID": job.Process_ID,
            "Arrival_Time": job.Arrival_Time,
            "Burst_Time": prediction["predicted"],
            "Priority": job.Priority if job.Priority is not None else job.Process_ID
        })

    # ML Recommendation
    cpu_list = [j.CPU_Percent for j in request.jobs]
    io_list = [j.IO_Write_Bytes for j in request.jobs]
    burst_list = [p["predicted"] for p in burst_data]
    queue_df = pd.DataFrame(
        [[np.mean(cpu_list), np.var(cpu_list, ddof=1) if len(cpu_list)>1 else 0.0, np.mean(io_list), np.var(burst_list, ddof=1) if len(burst_list)>1 else 0.0]],
        columns=['mean_cpu_percent', 'variance_cpu_percent', 'mean_io', 'variance_burst_time']
    )
    
    algo_probs = algo_selector.predict_proba(queue_df)[0]
    algo_pred = int(np.argmax(algo_probs))
    confidence = float(np.max(algo_probs))
    algo_map = {0: "FCFS", 1: "SJF", 2: "SRTF", 3: "RR"}
    ai_recommended = algo_map.get(algo_pred, "FCFS")
    
    # Feature Importances
    features_cols = ['CPU_Percent', 'IO_Write_Bytes', 'Num_Ctx_Switches']
    importances = burst_predictor.feature_importances_
    feat_imps = [FeatureImportance(feature=f, importance=float(i)) for f, i in zip(features_cols, importances)]

    # Parallel Execution
    with ThreadPoolExecutor() as executor:
        f_fcfs = executor.submit(run_fcfs, core_jobs)
        f_sjf = executor.submit(run_sjf, core_jobs, False)
        f_srtf = executor.submit(run_sjf, core_jobs, True)
        f_rr = executor.submit(run_rr, core_jobs, 4)
        
        results = [
            AlgoResult(algorithm="FCFS", **f_fcfs.result()),
            AlgoResult(algorithm="SJF", **f_sjf.result()),
            AlgoResult(algorithm="SRTF", **f_srtf.result()),
            AlgoResult(algorithm="RR", **f_rr.result())
        ]
        
    return BenchmarkResponse(
        results=results,
        ai_recommended=ai_recommended,
        ai_confidence=confidence,
        feature_importances=feat_imps
    )

@app.get("/complexity", response_model=List[ComplexityPoint])
async def complexity_endpoint():
    n_values = [1, 5, 10, 20, 50, 100, 200, 500]
    data = []
    for n in n_values:
        data.append(ComplexityPoint(
            n=n,
            fcfs=n * math.log2(n) if n > 0 else 0,
            sjf=n**2,
            srtf=n**2,
            rr=n
        ))
    return data
