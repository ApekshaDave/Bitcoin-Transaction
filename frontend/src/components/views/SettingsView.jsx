import React, { useState } from 'react';
import { Settings, Sliders, Save, Database, ShieldCheck } from 'lucide-react';

export default function SettingsView() {
  const [weights, setWeights] = useState({
    anomaly: 0.25,
    peeling: 0.25,
    mixing: 0.20,
    network: 0.15,
    graph: 0.15,
  });

  const [savedMessage, setSavedMessage] = useState(false);

  const handleSliderChange = (key, val) => {
    setWeights((prev) => ({ ...prev, [key]: parseFloat(val) }));
  };

  const handleSave = () => {
    setSavedMessage(true);
    setTimeout(() => setSavedMessage(false), 2500);
  };

  const totalWeight = Object.values(weights).reduce((a, b) => a + b, 0);

  return (
    <div className="p-6 space-y-6 max-w-[1200px] mx-auto font-mono">
      <div className="bg-[#0B1626] border border-[#101C2E] p-4 rounded-xl flex items-center justify-between">
        <div>
          <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center space-x-2">
            <Settings className="w-4 h-4 text-[#2196F3]" />
            <span>Platform Configuration & Risk Engine Calibration</span>
          </h2>
          <p className="text-[11px] text-slate-400">Tune normalized component weights for SIH26146 scoring engine</p>
        </div>
      </div>

      {/* Risk Formula Box */}
      <div className="bg-[#0B1626] border border-[#101C2E] rounded-xl p-5 shadow-md space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center space-x-2">
            <Sliders className="w-4 h-4 text-cyan-400" />
            <span>Multi-Component Risk Scoring Weights</span>
          </h3>
          <div className="text-xs text-slate-300">
            Sum of Weights: <span className={`font-bold ${Math.abs(totalWeight - 1.0) < 0.01 ? 'text-emerald-400' : 'text-rose-400'}`}>{totalWeight.toFixed(2)}</span>
          </div>
        </div>

        <div className="bg-[#050B14] p-3 rounded-xl border border-[#101C2E] text-xs text-cyan-300 text-center font-bold">
          Risk Score = 100 × (w₁·S_anomaly + w₂·S_peeling + w₃·S_mixing + w₄·S_network + w₅·S_graph)
        </div>

        <div className="space-y-4 pt-2">
          {Object.entries(weights).map(([key, val]) => (
            <div key={key} className="space-y-1">
              <div className="flex justify-between text-xs">
                <span className="text-slate-300 capitalize">w_{key} Weight ({key}):</span>
                <span className="text-white font-bold">{val.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min="0.0"
                max="0.5"
                step="0.05"
                value={val}
                onChange={(e) => handleSliderChange(key, e.target.value)}
                className="w-full h-1.5 bg-[#050B14] rounded-lg appearance-none cursor-pointer accent-[#2196F3]"
              />
            </div>
          ))}
        </div>

        <div className="pt-3 flex justify-end">
          <button
            onClick={handleSave}
            className="flex items-center space-x-2 px-4 py-2 bg-[#2196F3] hover:bg-[#1E88E5] text-white rounded-xl font-bold text-xs shadow-md transition"
          >
            <Save className="w-4 h-4" />
            <span>Save & Recalibrate Engine</span>
          </button>
        </div>

        {savedMessage && (
          <div className="text-xs text-emerald-400 text-center font-bold">
            ✓ Risk Engine Weights updated successfully!
          </div>
        )}
      </div>

      {/* Deployment & Environment Information */}
      <div className="bg-[#0B1626] border border-[#101C2E] rounded-xl p-5 shadow-md space-y-3">
        <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center space-x-2">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span>Deployment Environment Specifications</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className="bg-[#050B14] p-3 rounded-xl border border-[#101C2E]">
            <span className="text-slate-400 text-[10px]">Dataset Mode:</span>
            <div className="text-emerald-400 font-bold mt-0.5">Synthetic Generation</div>
          </div>

          <div className="bg-[#050B14] p-3 rounded-xl border border-[#101C2E]">
            <span className="text-slate-400 text-[10px]">GeoIP Engine:</span>
            <div className="text-cyan-400 font-bold mt-0.5">Local Database / Synthetic Fallback</div>
          </div>

          <div className="bg-[#050B14] p-3 rounded-xl border border-[#101C2E]">
            <span className="text-slate-400 text-[10px]">Network Connectivity:</span>
            <div className="text-emerald-400 font-bold mt-0.5">Offline / Air-Gapped Container</div>
          </div>
        </div>
      </div>

    </div>
  );
}
