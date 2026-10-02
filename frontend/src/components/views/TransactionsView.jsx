import React, { useState } from 'react';
import { Search, Filter, ArrowLeftRight, ExternalLink, ShieldAlert, Tag } from 'lucide-react';

export default function TransactionsView({ transactions, onSelectTx, onViewGraphTarget }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [riskFilter, setRiskFilter] = useState('ALL');
  const [classFilter, setClassFilter] = useState('ALL');
  const [inspectTx, setInspectTx] = useState(null);

  const sampleTxs = transactions && transactions.length > 0 ? transactions : [];

  const filtered = sampleTxs.filter((tx) => {
    const matchesSearch = tx.txid.toLowerCase().includes(searchTerm.toLowerCase());
    
    // Risk filter
    let matchesRisk = true;
    const rScore = tx.risk_score || 0;
    if (riskFilter === 'HIGH') matchesRisk = rScore >= 75;
    else if (riskFilter === 'MEDIUM') matchesRisk = rScore >= 25 && rScore < 75;
    else if (riskFilter === 'LOW') matchesRisk = rScore < 25;

    // Ground truth class filter (1: Illicit, 2: Licit, 3: Unknown)
    let matchesClass = true;
    const cLabel = tx.class_label !== undefined ? tx.class_label : (tx.synthetic_scenario_label !== 'normal' ? 1 : 2);
    if (classFilter === '1') matchesClass = cLabel === 1;
    else if (classFilter === '2') matchesClass = cLabel === 2;
    else if (classFilter === '3') matchesClass = cLabel === 3;

    return matchesSearch && matchesRisk && matchesClass;
  });

  const getClassBadge = (tx) => {
    const cLabel = tx.class_label !== undefined ? tx.class_label : (tx.synthetic_scenario_label !== 'normal' ? 1 : 2);
    if (cLabel === 1) {
      return (
        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-400 border border-rose-500/40 flex items-center gap-1 w-fit">
          <ShieldAlert className="w-3 h-3" />
          <span>Class 1 (Illicit)</span>
        </span>
      );
    }
    if (cLabel === 2) {
      return (
        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 w-fit inline-block">
          Class 2 (Licit)
        </span>
      );
    }
    return (
      <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-500/20 text-slate-400 border border-slate-500/40 w-fit inline-block">
        Class 3 (Unknown)
      </span>
    );
  };

  const handleOpenDetail = (tx) => {
    setInspectTx(tx);
    if (onSelectTx) onSelectTx(tx);
  };

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto relative">
      
      {/* Header Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#0B1626] border border-[#101C2E] p-4 rounded-xl">
        <div>
          <h2 className="text-sm font-mono font-bold text-white uppercase tracking-wider flex items-center space-x-2">
            <ArrowLeftRight className="w-4 h-4 text-[#2196F3]" />
            <span>Bitcoin On-Chain Transactions</span>
          </h2>
          <p className="text-[11px] text-slate-400 font-mono">Multi-dataset transaction ledger observations & ground-truth labels</p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          
          {/* Class Filter */}
          <div className="flex items-center space-x-1.5 bg-[#050B14] px-2.5 py-1.5 rounded-xl border border-[#101C2E]">
            <Tag className="w-3.5 h-3.5 text-cyan-400" />
            <select
              value={classFilter}
              onChange={(e) => setClassFilter(e.target.value)}
              className="bg-transparent text-xs font-mono text-slate-200 focus:outline-none cursor-pointer"
            >
              <option value="ALL" className="bg-[#08111F]">All Ground Truth</option>
              <option value="1" className="bg-[#08111F] text-rose-400">Class 1 (Illicit)</option>
              <option value="2" className="bg-[#08111F] text-emerald-400">Class 2 (Licit)</option>
              <option value="3" className="bg-[#08111F] text-slate-400">Class 3 (Unknown)</option>
            </select>
          </div>

          {/* Search */}
          <div className="relative w-56">
            <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-500" />
            <input
              type="text"
              placeholder="Filter by TXID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-[#050B14] text-xs font-mono text-cyan-300 placeholder-slate-500 pl-8 pr-3 py-1.5 rounded-xl border border-[#101C2E] focus:outline-none focus:border-[#2196F3]"
            />
          </div>

          {/* Risk Filter */}
          <select
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
            className="bg-[#050B14] text-xs font-mono text-slate-300 py-1.5 px-3 rounded-xl border border-[#101C2E] focus:outline-none"
          >
            <option value="ALL">All Risk Scores</option>
            <option value="HIGH">High Risk (&gt; 75)</option>
            <option value="MEDIUM">Medium Risk (25-75)</option>
            <option value="LOW">Low Risk (&lt; 25)</option>
          </select>

        </div>
      </div>

      {/* Table */}
      <div className="bg-[#0B1626] border border-[#101C2E] rounded-xl overflow-hidden shadow-md">
        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs">
            <thead className="bg-[#050B14] text-slate-400 border-b border-[#101C2E] uppercase text-[10px]">
              <tr>
                <th className="py-3 px-4">TXID</th>
                <th className="py-3 px-4">Source</th>
                <th className="py-3 px-4">Ground Truth Class</th>
                <th className="py-3 px-4">Step / Height</th>
                <th className="py-3 px-4">Total Input</th>
                <th className="py-3 px-4">Fee (Sats/BTC)</th>
                <th className="py-3 px-4">Risk Score</th>
                <th className="py-3 px-4 text-right">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#101C2E]">
              {filtered.map((tx) => {
                const totalVal = tx.total_input_amount ? (tx.total_input_amount / 1e8).toFixed(4) : (tx.total_input || 0).toFixed(4);
                const rScore = tx.risk_score || 0;

                return (
                  <tr key={tx.txid} className="hover:bg-[#101C2E]/50 transition">
                    <td className="py-3 px-4 text-cyan-300 font-bold break-all max-w-xs">{tx.txid.substring(0, 20)}...</td>
                    <td className="py-3 px-4 text-slate-400 text-[11px]">
                      <span className="px-2 py-0.5 rounded bg-[#101C2E] text-slate-300 border border-slate-700/50 uppercase text-[10px]">
                        {tx.dataset_source || 'synthetic'}
                      </span>
                    </td>
                    <td className="py-3 px-4">{getClassBadge(tx)}</td>
                    <td className="py-3 px-4 text-slate-300">
                      {tx.time_step ? `Step ${tx.time_step}` : tx.block_height}
                    </td>
                    <td className="py-3 px-4 font-bold text-white">{totalVal} BTC</td>
                    <td className="py-3 px-4 text-slate-400">{tx.fee || 0}</td>
                    <td className="py-3 px-4">
                      <span className={`font-bold ${
                        rScore >= 75 ? 'text-rose-400' :
                        rScore >= 25 ? 'text-amber-400' : 'text-emerald-400'
                      }`}>
                        {rScore.toFixed(1)} / 100
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => handleOpenDetail(tx)}
                        className="px-2.5 py-1 bg-[#2196F3]/10 hover:bg-[#2196F3] text-[#2196F3] hover:text-white border border-[#2196F3]/30 rounded-lg text-[11px] font-semibold flex items-center space-x-1.5 ml-auto transition shadow-sm"
                        title="Inspect Full Transaction Detail"
                      >
                        <ExternalLink className="w-3.5 h-3.5" />
                        <span>Detail</span>
                      </button>
                    </td>
                  </tr>
                );
              })}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan="8" className="py-8 text-center text-slate-500">
                    No transactions match the selected filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* TRANSACTION DETAIL MODAL OVERLAY */}
      {inspectTx && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#0B1626] border border-[#2196F3]/40 rounded-2xl w-full max-w-2xl max-h-[85vh] overflow-y-auto p-6 shadow-2xl space-y-5 animate-in fade-in zoom-in-95 duration-200">
            
            {/* Modal Header */}
            <div className="flex items-start justify-between border-b border-[#101C2E] pb-4">
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <span className="p-1.5 rounded-lg bg-[#2196F3]/20 text-[#2196F3] border border-[#2196F3]/40">
                    <ArrowLeftRight className="w-4 h-4" />
                  </span>
                  <h3 className="text-sm font-mono font-bold text-white uppercase tracking-wider">
                    Transaction Inspector
                  </h3>
                </div>
                <div className="text-xs font-mono text-cyan-300 font-bold break-all pt-1">
                  TXID: {inspectTx.txid}
                </div>
              </div>
              <button
                onClick={() => setInspectTx(null)}
                className="text-slate-400 hover:text-white text-lg font-mono p-1 rounded-lg hover:bg-[#101C2E]"
              >
                ✕
              </button>
            </div>

            {/* Badges & Meta */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs font-mono">
              <div className="bg-[#050B14] p-3 rounded-xl border border-[#101C2E]">
                <div className="text-[10px] text-slate-500 uppercase mb-1">Dataset Source</div>
                <div className="text-cyan-400 font-bold uppercase">{inspectTx.dataset_source || 'synthetic'}</div>
              </div>

              <div className="bg-[#050B14] p-3 rounded-xl border border-[#101C2E]">
                <div className="text-[10px] text-slate-500 uppercase mb-1">Ground Truth</div>
                <div>{getClassBadge(inspectTx)}</div>
              </div>

              <div className="bg-[#050B14] p-3 rounded-xl border border-[#101C2E]">
                <div className="text-[10px] text-slate-500 uppercase mb-1">Time Step / Block</div>
                <div className="text-slate-200 font-bold">{inspectTx.time_step ? `Step ${inspectTx.time_step}` : inspectTx.block_height || 'N/A'}</div>
              </div>

              <div className="bg-[#050B14] p-3 rounded-xl border border-[#101C2E]">
                <div className="text-[10px] text-slate-500 uppercase mb-1">Risk Score</div>
                <div className={`font-bold ${
                  (inspectTx.risk_score || 0) >= 75 ? 'text-rose-400' :
                  (inspectTx.risk_score || 0) >= 25 ? 'text-amber-400' : 'text-emerald-400'
                }`}>
                  {(inspectTx.risk_score || 0).toFixed(1)} / 100
                </div>
              </div>
            </div>

            {/* Amount & Fee */}
            <div className="bg-[#050B14] p-4 rounded-xl border border-[#101C2E] grid grid-cols-3 gap-4 text-xs font-mono">
              <div>
                <span className="text-[10px] text-slate-500 uppercase block">Total Input Amount</span>
                <span className="text-sm font-bold text-white">
                  {inspectTx.total_input_amount ? (inspectTx.total_input_amount / 1e8).toFixed(4) : (inspectTx.total_input || 0).toFixed(4)} BTC
                </span>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 uppercase block">Total Output Amount</span>
                <span className="text-sm font-bold text-emerald-400">
                  {inspectTx.total_output_amount ? (inspectTx.total_output_amount / 1e8).toFixed(4) : (inspectTx.total_output || 0).toFixed(4)} BTC
                </span>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 uppercase block">Fee</span>
                <span className="text-sm font-bold text-amber-400">{inspectTx.fee || 0} Sats</span>
              </div>
            </div>

            {/* Inputs & Outputs Details */}
            <div className="space-y-3 font-mono text-xs">
              <h4 className="text-[11px] font-bold text-slate-300 uppercase tracking-wider border-b border-[#101C2E] pb-1">
                Transaction Inputs & Outputs Structure
              </h4>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {/* Inputs */}
                <div className="bg-[#050B14] p-3 rounded-xl border border-[#101C2E] space-y-2">
                  <div className="text-[10px] text-slate-400 font-bold uppercase">Inputs ({inspectTx.inputs?.length || 1})</div>
                  {inspectTx.inputs && inspectTx.inputs.length > 0 ? (
                    inspectTx.inputs.map((inp, idx) => (
                      <div key={idx} className="text-[11px] bg-[#08111F] p-2 rounded border border-[#101C2E] text-slate-300 break-all">
                        <div>Address: <span className="text-cyan-300">{inp.address || inp.source_address || 'bc1q_input...'}</span></div>
                        <div className="text-[10px] text-slate-400">Amount: {(inp.amount / 1e8).toFixed(4)} BTC</div>
                      </div>
                    ))
                  ) : (
                    <div className="text-[11px] text-slate-400">Input Script Address: <span className="text-cyan-300">bc1q_in_{inspectTx.txid.substring(0, 8)}...</span></div>
                  )}
                </div>

                {/* Outputs */}
                <div className="bg-[#050B14] p-3 rounded-xl border border-[#101C2E] space-y-2">
                  <div className="text-[10px] text-slate-400 font-bold uppercase">Outputs ({inspectTx.outputs?.length || 1})</div>
                  {inspectTx.outputs && inspectTx.outputs.length > 0 ? (
                    inspectTx.outputs.map((out, idx) => (
                      <div key={idx} className="text-[11px] bg-[#08111F] p-2 rounded border border-[#101C2E] text-slate-300 break-all">
                        <div>Address: <span className="text-emerald-300">{out.address || out.target_address || 'bc1q_output...'}</span></div>
                        <div className="text-[10px] text-slate-400">Amount: {(out.amount / 1e8).toFixed(4)} BTC</div>
                      </div>
                    ))
                  ) : (
                    <div className="text-[11px] text-slate-400">Output Script Address: <span className="text-emerald-300">bc1q_out_{inspectTx.txid.substring(0, 8)}...</span></div>
                  )}
                </div>
              </div>
            </div>

            {/* Modal Footer Actions */}
            <div className="flex items-center justify-between pt-4 border-t border-[#101C2E]">
              {onViewGraphTarget && (
                <button
                  onClick={() => {
                    setInspectTx(null);
                    onViewGraphTarget(`TX_${inspectTx.txid}`);
                  }}
                  className="px-3.5 py-1.5 bg-[#2196F3] hover:bg-[#1E88E5] text-white rounded-xl text-xs font-mono font-bold flex items-center space-x-1.5 transition shadow-lg"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                  <span>Explore Subgraph in Graph Explorer</span>
                </button>
              )}
              
              <button
                onClick={() => setInspectTx(null)}
                className="px-4 py-1.5 bg-[#101C2E] hover:bg-slate-800 text-slate-300 rounded-xl text-xs font-mono ml-auto transition"
              >
                Close Inspector
              </button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
}

