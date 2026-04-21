import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Plus, Play, BarChart2, Cpu, Activity, FileText, 
  Trash2, Upload, ChevronRight, CheckCircle2, Info
} from "lucide-react";
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, 
  Tooltip, ResponsiveContainer, Legend 
} from "recharts";
import Papa from "papaparse";
import useSimulationStore from "./store/useSimulationStore";

// --- Utilities ---
const getProcessColor = (id) => `hsl(${(id * 137) % 360}, 70%, 60%)`;

const AnimatedNumber = ({ value }) => {
  const [displayValue, setDisplayValue] = useState(0);
  useEffect(() => {
    let start = null;
    const duration = 800;
    const animate = (timestamp) => {
      if (!start) start = timestamp;
      const progress = Math.min((timestamp - start) / duration, 1);
      setDisplayValue(progress * value);
      if (progress < 1) requestAnimationFrame(animate);
    };
    requestAnimationFrame(animate);
  }, [value]);
  return <span>{displayValue.toFixed(2)}</span>;
};

// --- Components ---

const GlassCard = ({ children, className = "" }) => (
  <div className={`bg-dark-card backdrop-blur-md border border-dark-border rounded-2xl ${className}`}>
    {children}
  </div>
);

const GanttChart = ({ data, aiRecommended }) => {
  if (!data) return (
    <div className="h-64 flex flex-col items-center justify-center text-slate-500 border-2 border-dashed border-dark-border rounded-2xl">
      <Activity size={48} className="mb-4 opacity-20" />
      <p>No simulation data yet. Run benchmark to visualize.</p>
    </div>
  );

  const totalTime = data.execution_timeline.length > 0 
    ? data.execution_timeline[data.execution_timeline.length - 1].end_time 
    : 100;

  return (
    <div className="space-y-6">
      <div className="relative h-20 bg-black/40 rounded-xl border border-dark-border overflow-hidden flex">
        <AnimatePresence>
          {data.execution_timeline.map((block, i) => (
            <motion.div
              key={`${block.Process_ID}-${i}`}
              initial={{ width: 0, opacity: 0 }}
              animate={{ 
                width: `${((block.end_time - block.start_time) / totalTime) * 100}%`,
                opacity: 1 
              }}
              transition={{ 
                duration: 0.8, 
                delay: i * 0.05,
                ease: [0.16, 1, 0.3, 1] 
              }}
              style={{ backgroundColor: getProcessColor(block.Process_ID) }}
              className="h-full border-r border-black/20 relative group cursor-pointer"
            >
              <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-black/20">
                <span className="text-[10px] font-bold text-white">P{block.Process_ID}</span>
              </div>
              {/* Tooltip on hover could go here */}
            </motion.div>
          ))}
        </AnimatePresence>
        
        {/* Time Cursor */}
        <motion.div 
          initial={{ left: 0 }}
          animate={{ left: '100%' }}
          transition={{ duration: 2, ease: "linear", repeat: Infinity }}
          className="absolute top-0 bottom-0 w-0.5 bg-primary/50 shadow-[0_0_10px_rgba(99,102,241,0.5)] z-10"
        />
      </div>

      <div className="flex justify-between text-[10px] text-slate-500 font-mono px-1">
        <span>0ms</span>
        <span>{totalTime}ms</span>
      </div>
    </div>
  );
};

export default function App() {
  const { 
    jobs, setJobs, addJob, removeJob, 
    benchmarkResults, complexityData, 
    loading, error, selectedAlgo, 
    setSelectedAlgo, runBenchmark, fetchComplexity 
  } = useSimulationStore();

  const [form, setForm] = useState({
    Process_ID: 1, Arrival_Time: 0, CPU_Percent: 50, IO_Write_Bytes: 1000, Num_Ctx_Switches: 5, Priority: 1
  });

  const handleInputChange = (name, value) => {
    setForm(prev => ({
      ...prev,
      [name]: value === "" ? "" : Number(value)
    }));
  };

  const handleAddJob = (e) => {
    e.preventDefault();
    // Always assign the next sequential ID based on current queue length
    const newJob = { ...form, Process_ID: jobs.length + 1 };
    addJob(newJob);
    // Prepare form for next process
    setForm({ ...form, Process_ID: jobs.length + 2 });
  };

  useEffect(() => {
    fetchComplexity();
    // ... rest of effects
    // Command+Enter listener
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
        runBenchmark();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleCsvUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      Papa.parse(file, {
        header: true,
        dynamicTyping: true,
        complete: (results) => {
          const importedJobs = results.data.filter(j => j.Process_ID).map(j => ({
            Process_ID: j.Process_ID,
            Arrival_Time: j.Arrival_Time || 0,
            CPU_Percent: j.CPU_Percent || 50,
            IO_Write_Bytes: j.IO_Write_Bytes || 0,
            Num_Ctx_Switches: j.Num_Ctx_Switches || 0,
            Priority: j.Priority || j.Process_ID
          }));
          setJobs(importedJobs);
        }
      });
    }
  };

  const selectedResult = benchmarkResults?.results.find(r => r.algorithm === selectedAlgo);

  return (
    <div className="min-h-screen bg-dark-bg text-slate-200 font-sans selection:bg-primary selection:text-white">
      <div className="flex h-screen overflow-hidden">
        
        {/* --- LEFT PANEL: INPUT & QUEUE --- */}
        <aside className="w-80 border-r border-dark-border bg-black/20 flex flex-col">
          <div className="p-6 border-b border-dark-border">
            <div className="flex items-center gap-3 mb-1">
              <div className="p-2 bg-primary rounded-lg">
                <Cpu size={20} className="text-white" />
              </div>
              <h1 className="text-lg font-bold tracking-tight">SmartScheduler</h1>
            </div>
            <p className="text-xs text-slate-500">AI-Augmented OS Kernel</p>
          </div>

          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            <section>
              <h2 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-4">Add Process</h2>
              <form className="space-y-4" onSubmit={handleAddJob}>
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <label className="text-[10px] text-slate-500 px-1">Arrival</label>
                    <input type="number" value={form.Arrival_Time} onChange={e => handleInputChange('Arrival_Time', e.target.value)} className="w-full bg-white/5 border border-dark-border rounded-lg p-2 text-sm focus:border-primary outline-none transition-colors" />
                  </div>
                  <div className="space-y-1">
                    <label className="text-[10px] text-slate-500 px-1">CPU %</label>
                    <input type="number" value={form.CPU_Percent} onChange={e => handleInputChange('CPU_Percent', e.target.value)} className="w-full bg-white/5 border border-dark-border rounded-lg p-2 text-sm focus:border-primary outline-none transition-colors" />
                  </div>
                  <div className="space-y-1">
                    <label className="text-[10px] text-slate-500 px-1">I/O Bytes</label>
                    <input type="number" value={form.IO_Write_Bytes} onChange={e => handleInputChange('IO_Write_Bytes', e.target.value)} className="w-full bg-white/5 border border-dark-border rounded-lg p-2 text-sm focus:border-primary outline-none transition-colors" />
                  </div>
                  <div className="space-y-1">
                    <label className="text-[10px] text-slate-500 px-1">Ctx Switches</label>
                    <input type="number" value={form.Num_Ctx_Switches} onChange={e => handleInputChange('Num_Ctx_Switches', e.target.value)} className="w-full bg-white/5 border border-dark-border rounded-lg p-2 text-sm focus:border-primary outline-none transition-colors" />
                  </div>
                  <div className="col-span-2 space-y-1">
                    <label className="text-[10px] text-slate-500 px-1">Priority (Lower = Higher)</label>
                    <input type="number" value={form.Priority} onChange={e => handleInputChange('Priority', e.target.value)} className="w-full bg-white/5 border border-dark-border rounded-lg p-2 text-sm focus:border-primary outline-none transition-colors" />
                  </div>
                </div>
                <button type="submit" className="w-full bg-primary hover:bg-primary/90 text-white font-medium py-2 rounded-lg text-sm transition-all flex items-center justify-center gap-2">
                  <Plus size={16} /> Add to Queue
                </button>
              </form>
            </section>

            <section>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Ready Queue ({jobs.length})</h2>
                <label className="cursor-pointer hover:text-primary transition-colors">
                  <Upload size={14} />
                  <input type="file" accept=".csv" className="hidden" onChange={handleCsvUpload} />
                </label>
              </div>
              <div className="space-y-2">
                {jobs.map((job) => (
                  <div key={job.Process_ID} className="group flex items-center justify-between p-3 bg-white/5 border border-dark-border rounded-xl hover:border-white/20 transition-all">
                    <div className="flex items-center gap-3">
                      <div className="w-1.5 h-8 rounded-full" style={{ backgroundColor: getProcessColor(job.Process_ID) }} />
                      <div>
                        <p className="text-xs font-bold">Process P{job.Process_ID}</p>
                        <p className="text-[10px] text-slate-500">Arrival: {job.Arrival_Time}ms • {job.CPU_Percent}% CPU</p>
                      </div>
                    </div>
                    <button onClick={() => removeJob(job.Process_ID)} className="opacity-0 group-hover:opacity-100 p-1.5 hover:bg-red-500/10 hover:text-red-500 rounded-lg transition-all">
                      <Trash2 size={14} />
                    </button>
                  </div>
                ))}
              </div>
            </section>
          </div>

          <div className="p-4 border-t border-dark-border">
            <button 
              onClick={runBenchmark}
              disabled={loading}
              className="w-full bg-white text-black font-bold py-3 rounded-xl flex items-center justify-center gap-2 hover:bg-white/90 disabled:opacity-50 transition-all"
            >
              {loading ? <Activity className="animate-spin" size={18} /> : <Play size={18} fill="black" />}
              {loading ? "Benchmarking..." : "Run AI Simulation"}
            </button>
          </div>
        </aside>

        {/* --- CENTER PANEL: GANTT & COMPLEXITY --- */}
        <main className="flex-1 flex flex-col bg-dark-bg p-8 overflow-y-auto space-y-8">
          
          <header className="flex justify-between items-end">
            <div>
              <h2 className="text-3xl font-bold tracking-tight mb-2">Simulation Roadmap</h2>
              <div className="flex gap-2">
                {['FCFS', 'SJF', 'SRTF', 'RR'].map(algo => (
                  <button
                    key={algo}
                    onClick={() => setSelectedAlgo(algo)}
                    className={`px-4 py-1.5 rounded-full text-xs font-medium transition-all border ${
                      selectedAlgo === algo 
                        ? 'bg-primary border-primary text-white shadow-[0_0_20px_rgba(99,102,241,0.3)]' 
                        : 'bg-white/5 border-dark-border text-slate-400 hover:border-white/20'
                    } ${benchmarkResults?.ai_recommended === algo ? 'ring-2 ring-primary ring-offset-4 ring-offset-dark-bg' : ''}`}
                  >
                    {algo}
                  </button>
                ))}
              </div>
            </div>
            {selectedResult && (
              <div className="text-right">
                <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Efficiency Factor</p>
                <p className="text-2xl font-mono text-primary font-bold">{selectedResult.algorithm_complexity}</p>
              </div>
            )}
          </header>

          <section className="space-y-6">
            <GlassCard className="p-8">
              <div className="flex items-center justify-between mb-8">
                <h3 className="text-lg font-bold flex items-center gap-2">
                  <Activity size={20} className="text-primary" /> Execution Timeline
                </h3>
                <div className="flex gap-6">
                  <div className="text-right">
                    <p className="text-[10px] text-slate-500 uppercase font-bold">Avg Waiting</p>
                    <p className="text-xl font-mono text-white">
                      {selectedResult ? <AnimatedNumber value={selectedResult.average_waiting_time} /> : '0.00'}ms
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-[10px] text-slate-500 uppercase font-bold">Ctx Switches</p>
                    <p className="text-xl font-mono text-white">{selectedResult?.context_switches || 0}</p>
                  </div>
                </div>
              </div>
              <GanttChart data={selectedResult} />
            </GlassCard>

            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
              <GlassCard className="p-8">
                <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
                  <BarChart2 size={20} className="text-primary" /> Algorithmic Growth (Big-O)
                </h3>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={complexityData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                      <XAxis dataKey="n" stroke="#475569" fontSize={10} />
                      <YAxis stroke="#475569" fontSize={10} />
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#0a0a0f', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '12px' }}
                        itemStyle={{ fontSize: '12px' }}
                      />
                      <Legend iconType="circle" />
                      <Line type="monotone" dataKey="fcfs" stroke="#6366f1" strokeWidth={2} dot={false} />
                      <Line type="monotone" dataKey="sjf" stroke="#ef4444" strokeWidth={2} dot={false} />
                      <Line type="monotone" dataKey="rr" stroke="#10b981" strokeWidth={2} dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </GlassCard>

              <GlassCard className="p-8 flex flex-col">
                <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
                  <Info size={20} className="text-primary" /> AI Insights
                </h3>
                {benchmarkResults ? (
                  <div className="flex-1 space-y-6">
                    <div className="flex items-center gap-6 p-4 bg-white/5 rounded-2xl border border-dark-border">
                      <div className="relative w-20 h-20">
                        <svg className="w-full h-full transform -rotate-90">
                          <circle cx="40" cy="40" r="36" stroke="currentColor" strokeWidth="8" fill="transparent" className="text-white/5" />
                          <motion.circle 
                            cx="40" cy="40" r="36" stroke="currentColor" strokeWidth="8" fill="transparent" 
                            strokeDasharray={226}
                            initial={{ strokeDashoffset: 226 }}
                            animate={{ strokeDashoffset: 226 - (226 * benchmarkResults.ai_confidence) }}
                            className="text-primary"
                          />
                        </svg>
                        <div className="absolute inset-0 flex items-center justify-center text-xs font-bold">
                          {Math.round(benchmarkResults.ai_confidence * 100)}%
                        </div>
                      </div>
                      <div>
                        <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Confidence Score</p>
                        <p className="text-sm text-slate-300 mt-1">
                          The model is highly confident that <span className="text-white font-bold">{benchmarkResults.ai_recommended}</span> will yield the lowest waiting time.
                        </p>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Key Feature Importance</p>
                      {benchmarkResults.feature_importances.map((feat, i) => (
                        <div key={feat.feature} className="space-y-1">
                          <div className="flex justify-between text-[10px]">
                            <span>{feat.feature}</span>
                            <span>{Math.round(feat.importance * 100)}%</span>
                          </div>
                          <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                            <motion.div 
                              initial={{ width: 0 }}
                              animate={{ width: `${feat.importance * 100}%` }}
                              className="h-full bg-primary"
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="flex-1 flex items-center justify-center text-slate-500 text-sm">
                    Awaiting simulation data...
                  </div>
                )}
              </GlassCard>
            </div>
          </section>
        </main>

        {/* --- RIGHT PANEL: METRICS OVERVIEW --- */}
        <aside className="w-80 border-l border-dark-border bg-black/20 p-6 space-y-6 overflow-y-auto">
          <h2 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Algorithm Comparison</h2>
          <div className="space-y-4">
            {benchmarkResults?.results.map(res => (
              <div 
                key={res.algorithm}
                onClick={() => setSelectedAlgo(res.algorithm)}
                className={`p-4 rounded-2xl border transition-all cursor-pointer ${
                  selectedAlgo === res.algorithm 
                    ? 'bg-primary/10 border-primary shadow-[0_0_20px_rgba(99,102,241,0.1)]' 
                    : 'bg-white/5 border-dark-border hover:border-white/10'
                }`}
              >
                <div className="flex items-center justify-between mb-3">
                  <span className="text-sm font-bold">{res.algorithm}</span>
                  {benchmarkResults.ai_recommended === res.algorithm && (
                    <span className="bg-primary/20 text-primary text-[8px] font-bold px-2 py-0.5 rounded-full uppercase tracking-widest">AI Pick</span>
                  )}
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div className="p-2 bg-black/20 rounded-lg">
                    <p className="text-[8px] text-slate-500 uppercase">Wait Time</p>
                    <p className="text-xs font-mono">{res.average_waiting_time.toFixed(1)}ms</p>
                  </div>
                  <div className="p-2 bg-black/20 rounded-lg">
                    <p className="text-[8px] text-slate-500 uppercase">Switches</p>
                    <p className="text-xs font-mono">{res.context_switches}</p>
                  </div>
                </div>
              </div>
            ))}
            {!benchmarkResults && (
              <div className="text-center py-12 text-slate-600">
                <FileText size={40} className="mx-auto mb-2 opacity-10" />
                <p className="text-xs italic">Compare algorithms side-by-side after simulation.</p>
              </div>
            )}
          </div>

          {benchmarkResults && (
            <div className="pt-6 border-t border-dark-border">
              <div className="p-4 bg-success/10 border border-success/20 rounded-2xl">
                <div className="flex items-center gap-2 mb-2 text-success">
                  <CheckCircle2 size={16} />
                  <span className="text-xs font-bold uppercase tracking-widest">Simulation Success</span>
                </div>
                <p className="text-[10px] text-slate-400 leading-relaxed">
                  The {benchmarkResults.ai_recommended} algorithm reduced waiting time by {
                    Math.round(((Math.max(...benchmarkResults.results.map(r => r.average_waiting_time)) - Math.min(...benchmarkResults.results.map(r => r.average_waiting_time))) / Math.max(...benchmarkResults.results.map(r => r.average_waiting_time))) * 100)
                  }% compared to the worst case.
                </p>
              </div>
            </div>
          )}
        </aside>

      </div>
    </div>
  );
}
