import React, { useState, useEffect } from 'react';
import { Search, RefreshCw, Cpu, Layers, Activity } from 'lucide-react';

export default function Header({ 
  activeDataset = 'synthetic', 
  onSelectDataset, 
  onSearch, 
  onRunGenerator, 
  onRunPipeline, 
  loading 
}) {
  const [query, setQuery] = useState('');
  const [timeStr, setTimeStr] = useState('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeStr(now.toLocaleTimeString('en-US', { hour12: false }));
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (query.trim() && onSearch) {
      onSearch(query.trim());
    }
  };

  return (
    <header className="h-14 bg-[#08111F] border-b border-[#101C2E] px-5 flex items-center justify-between sticky top-0 z-20 shrink-0 font-mono">
      
      {/* Left: Brand Title & Active Scope */}
      <div className="flex items-center space-x-3">
        <div className="w-8 h-8 rounded-lg bg-[#2196F3]/10 border border-[#2196F3]/30 flex items-center justify-center text-[#2196F3]">
          <Activity className="w-4 h-4" />
        </div>
        <div>
          <h1 className="text-xs font-bold text-white tracking-wide uppercase flex items-center space-x-2">
            <span>Bitcoin Traffic Monitor</span>
            <span className="text-[10px] text-slate-500 font-normal">| SIH26146</span>
          </h1>
        </div>
      </div>

      {/* Center: Search Bar */}
      <div className="flex items-center space-x-3">
        <form onSubmit={handleSearchSubmit} className="relative w-72">
          <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-500" />
          <input
            type="text"
            placeholder="Search TXID / Address / IP..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full bg-[#050B14] text-xs text-cyan-300 placeholder-slate-500 pl-8 pr-3 py-1.5 rounded-xl border border-[#101C2E] focus:outline-none focus:border-[#2196F3]/60 transition"
          />
        </form>
      </div>

      {/* Right Controls: Dataset Switcher, Pipeline Actions, Clock */}
      <div className="flex items-center space-x-3 text-xs">
        
        {/* Compact Dataset Selector */}
        <div className="flex items-center space-x-1.5 bg-[#050B14] px-2.5 py-1 rounded-xl border border-[#101C2E]">
          <Layers className="w-3.5 h-3.5 text-cyan-400" />
          <select 
            value={activeDataset} 
            onChange={(e) => onSelectDataset && onSelectDataset(e.target.value)}
            disabled={loading}
            className="bg-transparent text-xs font-medium text-slate-200 focus:outline-none cursor-pointer"
          >
            <option value="synthetic" className="bg-[#08111F] text-slate-200">
              SIH Synthetic Investigation
            </option>
            <option value="elliptic_v1" className="bg-[#08111F] text-slate-200">
              Elliptic v1 Benchmark
            </option>
            <option value="elliptic_v2" className="bg-[#08111F] text-slate-200">
              Elliptic++ Benchmark
            </option>
          </select>
        </div>

        {/* Dataset Generator Trigger */}
        {activeDataset === 'synthetic' && (
          <button
            onClick={onRunGenerator}
            disabled={loading}
            className="px-2.5 py-1 rounded-xl bg-[#101C2E] hover:bg-[#1A283D] text-slate-300 border border-slate-700/60 transition flex items-center space-x-1"
            title="Generate synthetic data"
          >
            <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
            <span>Gen Data</span>
          </button>
        )}

        {/* Run Pipeline Action */}
        <button
          onClick={onRunPipeline}
          disabled={loading}
          className="px-3 py-1 rounded-xl font-semibold bg-[#2196F3] hover:bg-[#1E88E5] text-white shadow-sm transition flex items-center space-x-1.5"
        >
          <Cpu className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Run AI Pipeline</span>
        </button>

        {/* Clock & Status Dot */}
        <div className="flex items-center space-x-2 pl-2 border-l border-[#101C2E]">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" title="System Active"></span>
          <span className="text-slate-400 text-[11px]">{timeStr}</span>
        </div>

      </div>

    </header>
  );
}
