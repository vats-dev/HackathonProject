import pandas as pd
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

def load_data(filepath):
    """Loads dataset using pandas"""
    return pd.read_csv(filepath)

def train_burst_predictor(df):
    print("Training Model 1: Burst Predictor...")
    # Features & Target
    X = df[['CPU_Percent', 'IO_Write_Bytes', 'Num_Ctx_Switches']]
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
    
    # Train on full dataset before saving
    final_model = RandomForestRegressor(n_estimators=100, random_state=42)
    final_model.fit(X, y)
    
    # Save the model
    save_path = os.path.join(os.path.dirname(__file__), 'saved_models', 'burst_predictor.joblib')
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    joblib.dump(final_model, save_path)
    print(f"-> Saved model to {save_path}\n")

def generate_queue_features(df, batch_size=10):
    print("Generating Queue-level Features for Model 2...")
    
    queues = []
    targets = []
    
    # Sort chronologically to simulate a real queue over time
    df = df.sort_values('Arrival_Time').reset_index(drop=True)
    
    for i in range(0, len(df), batch_size):
        batch = df.iloc[i:i+batch_size]
        
        # Calculate Queue-level features
        mean_cpu_percent = batch['CPU_Percent'].mean()
        
        # pandas var defaults to ddof=1, returning NaN for n=1. We handle it safely.
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
                # During this data generation step, we use the Actual_Burst_Time
                "Burst_Time": int(row['Actual_Burst_Time']) 
            })
            
        fcfs_outcome = run_fcfs(jobs)
        sjf_outcome = run_sjf(jobs)
        
        wt_fcfs = fcfs_outcome['average_waiting_time']
        wt_sjf = sjf_outcome['average_waiting_time']
        
        # Target label definition: 1 if SJF is strictly better, 0 otherwise
        target = 1 if wt_sjf < wt_fcfs else 0
        
        queues.append({
            'mean_cpu_percent': mean_cpu_percent,
            'variance_cpu_percent': variance_cpu_percent,
            'mean_io': mean_io,
            'variance_burst_time': variance_burst_time
        })
        targets.append(target)
        
    return pd.DataFrame(queues), pd.Series(targets)

def train_algo_selector(X, y):
    print("Training Model 2: Algorithm Selector...")
    
    # Check if we have enough data to split
    if len(X) > 1:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        preds = model.predict(X_test)
        acc = accuracy_score(y_test, preds)
        print(f"-> Algorithm Selector Accuracy: {acc * 100:.2f}%")
    else:
        print("-> Not enough data batches for a test split. Training on all available data.")
    
    # Train on full dataset
    final_model = RandomForestClassifier(n_estimators=100, random_state=42)
    final_model.fit(X, y)
    
    save_path = os.path.join(os.path.dirname(__file__), 'saved_models', 'algo_selector.joblib')
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    joblib.dump(final_model, save_path)
    print(f"-> Saved model to {save_path}\n")

if __name__ == "__main__":
    try:
        # Resolve dataset absolute path gracefully
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
        sys.exit(1)
