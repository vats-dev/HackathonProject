import { create } from 'zustand';

const useSimulationStore = create((set, get) => ({
  jobs: [],
  benchmarkResults: null,
  complexityData: [],
  loading: false,
  error: null,
  selectedAlgo: 'FCFS', 
  
  setJobs: (jobs) => set({ jobs }),
  addJob: (job) => set((state) => ({ jobs: [...state.jobs, job] })),
  removeJob: (pid) => set((state) => {
    // Filter out the job and then re-index all remaining jobs
    const filtered = state.jobs.filter(j => j.Process_ID !== pid);
    const reindexed = filtered.map((job, index) => ({
      ...job,
      Process_ID: index + 1
    }));
    return { jobs: reindexed };
  }),
  setSelectedAlgo: (algo) => set({ selectedAlgo: algo }),

  fetchComplexity: async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/complexity');
      const data = await res.json();
      set({ complexityData: data });
    } catch (err) {
      console.error("Failed to fetch complexity data", err);
    }
  },

  runBenchmark: async () => {
    set({ loading: true, error: null });
    try {
      const response = await fetch("http://127.0.0.1:8000/benchmark", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ jobs: get().jobs }),
      });
      if (!response.ok) throw new Error("Benchmark failed.");
      const data = await response.json();
      set({ benchmarkResults: data, selectedAlgo: data.ai_recommended });
    } catch (err) {
      set({ error: err.message });
    } finally {
      set({ loading: false });
    }
  }
}));

export default useSimulationStore;
