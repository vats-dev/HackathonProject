# Smart CPU Job Scheduling System (AI-Augmented)

An intelligent, machine-learning-powered Operating System scheduling simulator that predicts process burst times and dynamically selects the mathematically optimal scheduling algorithm in real-time.

## 🧠 The Problem
Traditional OS scheduling algorithms (FCFS, SJF, RR) rely on static logic. SJF is optimal but impossible in practice because future CPU burst times are unknown.

## 🚀 The Solution
This system uses a **Random Forest Regressor** to predict unknown burst times based on CPU usage, I/O activity, and context switches. A second **Random Forest Classifier** then evaluates the entire queue and routes jobs to the most efficient algorithm (FCFS, SJF, SRTF, or Round Robin).

## 🛠️ Tech Stack
- **Core Logic:** Pure Python (Zero-dependency OS simulations)
- **Machine Learning:** Scikit-Learn (Random Forest), Pandas, NumPy
- **Backend:** FastAPI, Uvicorn, Pydantic
- **Frontend:** React.js, Vite, Tailwind CSS, Framer Motion, Recharts

## 📊 Features
- **Dynamic Algo Selection:** AI picks the best scheduler for your specific workload.
- **Parallel Benchmarking:** Compare all algorithms side-by-side on the same queue.
- **Complexity Visualization:** Real-time Big-O growth curves for algorithm analysis.
- **Apple-Level UI:** Minimalist dark mode dashboard with animated Gantt charts and glassmorphism.

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js & npm

### Backend Setup
1. `cd api`
2. `pip install -r ../requirements.txt`
3. `uvicorn main:app --reload`

### Frontend Setup
1. `cd frontend`
2. `npm install`
3. `npm run dev`

---
*Developed for Hackathon 2026. Built with focus on algorithmic depth and UI/UX excellence.*
