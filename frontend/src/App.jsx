import React, { useState } from "react";

export default function App() {
  const [jobs, setJobs] = useState([
    { Process_ID: 1, Arrival_Time: 0, CPU_Percent: 80.5, IO_Write_Bytes: 5000, Num_Ctx_Switches: 10 },
    { Process_ID: 2, Arrival_Time: 2, CPU_Percent: 20.0, IO_Write_Bytes: 200000, Num_Ctx_Switches: 300 },
    { Process_ID: 3, Arrival_Time: 4, CPU_Percent: 50.0, IO_Write_Bytes: 50000, Num_Ctx_Switches: 100 },
  ]);

  const [form, setForm] = useState({
    Process_ID: 4, Arrival_Time: 0, CPU_Percent: 0, IO_Write_Bytes: 0, Num_Ctx_Switches: 0,
  });

  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleInputChange = (e) => {
    setForm({ ...form, [e.target.name]: Number(e.target.value) });
  };

  const addJob = (e) => {
    e.preventDefault();
    setJobs([...jobs, form]);
    setForm({ ...form, Process_ID: form.Process_ID + 1 });
  };

  const runSimulation = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await fetch("http://127.0.0.1:8000/simulate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ jobs }),
      });
      if (!response.ok) throw new Error("API simulation failed.");
      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-200 p-8 font-sans">
      <div className="max-w-7xl mx-auto space-y-6">

        {/* Header */}
        <header className="bg-slate-800 p-6 rounded-lg shadow-lg border border-slate-700">
          <h1 className="text-3xl font-bold text-white tracking-tight">🧠 AI-Powered CPU Scheduler</h1>
          <p className="text-slate-400 mt-2">Intelligent process scheduling using Machine Learning.</p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

          {/* Left Column: Data Entry (Mimicking the repo's input UI) */}
          <div className="lg:col-span-5 space-y-6">
            <div className="bg-slate-800 p-6 rounded-lg shadow-lg border border-slate-700">
              <h2 className="text-xl font-semibold text-white mb-4 border-b border-slate-700 pb-2">Add New Process</h2>
              <form onSubmit={addJob} className="grid grid-cols-2 gap-4">
                {Object.keys(form).map((key) => (
                  <div key={key} className={key === "Process_ID" ? "col-span-2" : "col-span-1"}>
                    <label className="block text-xs font-medium text-slate-400 uppercase tracking-wider mb-1">
                      {key.replace(/_/g, " ")}
                    </label>
                    <input
                      type="number"
                      name={key}
                      value={form[key]}
                      onChange={handleInputChange}
                      className="w-full bg-slate-700 border border-slate-600 rounded p-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>
                ))}
                <button type="submit" className="col-span-2 mt-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded transition-colors">
                  + Add to Queue
                </button>
              </form>
            </div>

            {/* Process Queue Table */}
            <div className="bg-slate-800 p-6 rounded-lg shadow-lg border border-slate-700 overflow-x-auto">
              <h2 className="text-xl font-semibold text-white mb-4 border-b border-slate-700 pb-2">Ready Queue</h2>
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="text-slate-400 border-b border-slate-700">
                    <th className="pb-2">ID</th>
                    <th className="pb-2">Arrival</th>
                    <th className="pb-2">CPU %</th>
                    <th className="pb-2">I/O Bytes</th>
                    <th className="pb-2">Ctx Switch</th>
                  </tr>
                </thead>
                <tbody>
                  {jobs.map((job) => (
                    <tr key={job.Process_ID} className="border-b border-slate-700/50">
                      <td className="py-2 text-blue-400 font-medium">P{job.Process_ID}</td>
                      <td className="py-2">{job.Arrival_Time}</td>
                      <td className="py-2">{job.CPU_Percent}</td>
                      <td className="py-2">{job.IO_Write_Bytes}</td>
                      <td className="py-2">{job.Num_Ctx_Switches}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Right Column: AI Simulation & Results */}
          <div className="lg:col-span-7 space-y-6">
            <div className="bg-slate-800 p-6 rounded-lg shadow-lg border border-slate-700 flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-white">Simulation Engine</h2>
                <p className="text-slate-400 text-sm mt-1">Pass queue to Random Forest for dynamic algorithm selection.</p>
              </div>
              <button
                onClick={runSimulation}
                disabled={loading}
                className={`py-3 px-6 rounded font-bold text-white transition-colors ${loading ? "bg-slate-600 cursor-not-allowed" : "bg-emerald-600 hover:bg-emerald-700"
                  }`}
              >
                {loading ? "Simulating..." : "Run AI Simulation 🚀"}
              </button>
            </div>

            {error && (
              <div className="bg-red-900/50 border border-red-500 text-red-200 p-4 rounded">
                <strong>Error:</strong> {error}
              </div>
            )}

            {results && (
              <div className="space-y-6 animate-fade-in-up">

                {/* Metrics Highlight Cards */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-slate-800 p-6 rounded-lg shadow-lg border border-slate-700">
                    <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wider">AI Selected Algorithm</h3>
                    <p className="text-4xl font-bold text-emerald-400 mt-2">{results.selected_algorithm}</p>
                  </div>
                  <div className="bg-slate-800 p-6 rounded-lg shadow-lg border border-slate-700">
                    <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wider">Average Waiting Time</h3>
                    <p className="text-4xl font-bold text-blue-400 mt-2">{results.average_waiting_time.toFixed(2)} ms</p>
                  </div>
                </div>

                {/* Gantt Chart Implementation */}
                <div className="bg-slate-800 p-6 rounded-lg shadow-lg border border-slate-700">
                  <h2 className="text-xl font-semibold text-white mb-4 border-b border-slate-700 pb-2">Gantt Chart (Execution Timeline)</h2>

                  <div className="relative h-16 bg-slate-900 rounded border border-slate-700 flex overflow-hidden">
                    {results.execution_timeline.map((block, index) => {
                      const totalTime = results.execution_timeline[results.execution_timeline.length - 1].end_time;
                      const widthPercentage = ((block.end_time - block.start_time) / totalTime) * 100;

                      // Alternate colors for visual distinction
                      const colors = ["bg-blue-600", "bg-purple-600", "bg-emerald-600", "bg-amber-600", "bg-rose-600"];
                      const blockColor = colors[block.Process_ID % colors.length];

                      return (
                        <div
                          key={index}
                          style={{ width: `${widthPercentage}%` }}
                          className={`${blockColor} h-full flex flex-col items-center justify-center border-r border-slate-800 relative group transition-all hover:brightness-110`}
                        >
                          <span className="font-bold text-white drop-shadow-md">P{block.Process_ID}</span>
                          <span className="text-[10px] text-white/80 absolute bottom-1">{block.start_time} - {block.end_time}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>

              </div>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}