import pandas as pd
import numpy as np
import os
import sys
import joblib
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, accuracy_score

# Add root project path to Python path gracefully
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.scheduler_fcfs import run_fcfs
from core.scheduler_sjf import run_sjf
from core.scheduler_rr import run_rr

def load_data(filepath):
    """Loads dataset using pandas"""
    return pd.read_csv(filepath)

def train_burst_predictor(df):
    print("Training Model 1: Burst Predictor...")
    # Features & Target
    features_cols = ['CPU_Percent', 'IO_Write_Bytes', 'Num_Ctx_Switches']
    X = df[features_cols]
    y = df['Actual_Burst_Time']
    
    # Train-test split for evaluation
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Model init
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluation
    predictions = model.predict(X_test)
    r2 = r2_score(y_test, predictions)
    print(f"-> Burst Predictor R² Score: {r2:.4f}")
    
    # Feature Importance
    importances = model.feature_importances_
    feat_importances = sorted(zip(features_cols, importances), key=lambda x: x[1], reverse=True)
    print(f"-> Feature Importances: {feat_importances}")
    
    # Train on full dataset before saving
    final_model = RandomForestRegressor(n_estimators=100, random_state=42)
    final_model.fit(X, y)
    
    # Save the model
    save_path = os.path.join(os.path.dirname(__file__), 'saved_models', 'burst_predictor.joblib')
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    joblib.dump(final_model, save_path)
    print(f"-> Saved model to {save_path}\n")

def generate_queue_features(df, batch_size=10):
    print("Generating Queue-level Features for Model 2 (4 Algorithms)...")
    
    queues = []
    targets = []
    
    # Sort chronologically to simulate a real queue over time
    df = df.sort_values('Arrival_Time').reset_index(drop=True)
    
    for i in range(0, len(df), batch_size):
        batch = df.iloc[i:i+batch_size]
        
        # Calculate Queue-level features
        mean_cpu_percent = batch['CPU_Percent'].mean()
        variance_cpu_percent = batch['CPU_Percent'].var() if len(batch) > 1 else 0.0
        mean_io = batch['IO_Write_Bytes'].mean()
        variance_burst_time = batch['Actual_Burst_Time'].var() if len(batch) > 1 else 0.0
        
        if pd.isna(variance_cpu_percent): variance_cpu_percent = 0.0
        if pd.isna(variance_burst_time): variance_burst_time = 0.0
        
        # Prepare for core scheduling logic
        jobs = []
        for _, row in batch.iterrows():
            jobs.append({
                "Process_ID": int(row['Process_ID']),
                "Arrival_Time": int(row['Arrival_Time']),
                "Burst_Time": int(row['Actual_Burst_Time']) 
            })
            
        # Run all 4 candidates
        res_fcfs = run_fcfs(jobs)
        res_sjf = run_sjf(jobs, preemptive=False)
        res_srtf = run_sjf(jobs, preemptive=True)
        res_rr = run_rr(jobs, quantum=4)
        
        outcomes = {
            0: res_fcfs['average_waiting_time'],
            1: res_sjf['average_waiting_time'],
            2: res_srtf['average_waiting_time'],
            3: res_rr['average_waiting_time']
        }
        
        # Target is the index of the minimum waiting time
        target = min(outcomes, key=outcomes.get)
        
        queues.append({
            'mean_cpu_percent': mean_cpu_percent,
            'variance_cpu_percent': variance_cpu_percent,
            'mean_io': mean_io,
            'variance_burst_time': variance_burst_time
        })
        targets.append(target)
        
    return pd.DataFrame(queues), pd.Series(targets)

def train_algo_selector(X, y):
    print("Training Model 2: Multi-class Algorithm Selector (FCFS=0, SJF=1, SRTF=2, RR=3)...")
    
    if len(X) > 1:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        preds = model.predict(X_test)
        acc = accuracy_score(y_test, preds)
        print(f"-> Algorithm Selector Accuracy: {acc * 100:.2f}%")
        
        from sklearn.metrics import classification_report
        print(classification_report(y_test, preds, target_names=['FCFS', 'SJF', 'SRTF', 'RR'], labels=[0,1,2,3]))
    
    # Train on full dataset
    final_model = RandomForestClassifier(n_estimators=100, random_state=42)
    final_model.fit(X, y)
    
    save_path = os.path.join(os.path.dirname(__file__), 'saved_models', 'algo_selector.joblib')
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    joblib.dump(final_model, save_path)
    print(f"-> Saved model to {save_path}\n")

if __name__ == "__main__":
    try:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        dataset_path = os.path.join(project_root, 'data', 'synthetic_os_jobs.csv')
        
        print(f"Loading Dataset from {dataset_path}...")
        df = load_data(dataset_path)
        
        # 1. Train Model 1 (Burst Predictor)
        train_burst_predictor(df)
        
        # 2. Extract Data for Model 2 (Algorithm Selector)
        X_queues, y_targets = generate_queue_features(df, batch_size=10)
        
        # 3. Train Model 2
        train_algo_selector(X_queues, y_targets)
        
        print("ML Pipeline execution completed successfully!")

    except Exception as e:
        print(f"Pipeline Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
