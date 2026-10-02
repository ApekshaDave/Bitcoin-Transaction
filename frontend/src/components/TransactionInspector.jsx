import React, { useEffect, useState } from 'react';
import { FileSearch, ArrowRight, CornerDownRight, Wifi, ShieldCheck, Tag } from 'lucide-react';

export default function TransactionInspector({ selectedTxid }) {
  const [txDetails, setTxDetails] = useState(null);
  const [loading, setLoading] = useState(false);
  const [inputTxid, setInputTxid] = useState(selectedTxid || '');

  useEffect(() => {
    if (selectedTxid) {
      setInputTxid(selectedTxid);
      fetchTxDetails(selectedTxid);
    }
  }, [selectedTxid]);

  const fetchTxDetails = async (txidToFetch) => {
    if (!txidToFetch) return;
    setLoading(true);
    try {
      const res = await fetch(`/api/v1/transactions/${txidToFetch}`);
      if (res.ok) {
        const data = await res.json();
        setTxDetails(data);
      } else {
        setTxDetails(null);
      }
    } catch (e) {
      setTxDetails(null);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    fetchTxDetails(inputTxid);
  };

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-6">
      
      {/* Header & Search Bar */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <FileSearch className="w-5 h-5 text-indigo-400" />
            Blockchain & Network Transaction Inspector
          </h2>
          <p className="text-xs text-slate-400 font-mono mt-0.5">
            Inspect transaction lineage, prev_txid outputs, script types, and P2P observations
          </p>
        </div>

        <form onSubmit={handleSearch} className="flex items-center space-x-2 w-full sm:w-auto">
          <input
            type="text"
            placeholder="Enter 64-char TXID..."
            value={inputTxid}
            onChange={(e) => setInputTxid(e.target.value)}
            className="w-full sm:w-80 bg-slate-900 text-xs font-mono text-cyan-300 px-3 py-2 rounded-xl border border-slate-800 focus:outline-none focus:border-cyan-500/50"
          />
          <button
            type="submit"
            className="px-3.5 py-2 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white transition"
          >
            Inspect
          </button>
        </form>
      </div>

      {!txDetails ? (
        <div className="py-12 text-center text-slate-500 font-mono text-xs">
          {loading ? 'Fetching transaction lineage...' : 'Enter a TXID above or click any alert in the queue to inspect details.'}
        </div>
      ) : (
        <div className="space-y-6">
          
          {/* Metadata Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="text-slate-500">TXID</span>
              <p className="text-cyan-300 font-bold truncate mt-0.5" title={txDetails.txid}>{txDetails.txid}</p>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="text-slate-500">Fee / Size</span>
              <p className="text-slate-200 mt-0.5">{txDetails.fee} Sats / {txDetails.size} Bytes</p>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="text-slate-500">Total Input Amount</span>
              <p className="text-emerald-400 font-bold mt-0.5">{(txDetails.total_input_amount / 1e8).toFixed(4)} BTC</p>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="text-slate-500">Scenario Label (Eval)</span>
              <p className="text-purple-400 font-bold mt-0.5">{txDetails.synthetic_scenario_label || 'normal'}</p>
            </div>
          </div>

          {/* Inputs & Outputs Breakdown */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            
            {/* Inputs Column */}
            <div className="space-y-3">
              <h3 className="text-xs font-mono font-bold text-slate-400 uppercase tracking-wider">
                Inputs ({txDetails.inputs?.length || 0})
              </h3>
              <div className="space-y-2">
                {(txDetails.inputs || []).map((inp, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-slate-900/40 border border-slate-800 text-xs font-mono space-y-1">
                    <div className="flex justify-between text-slate-300 font-medium">
                      <span>{inp.address}</span>
                      <span className="text-emerald-400">{(inp.amount / 1e8).toFixed(4)} BTC</span>
                    </div>
                    {inp.prev_txid && (
                      <div className="flex items-center space-x-1 text-[11px] text-slate-500 pt-1 border-t border-slate-800/60">
                        <CornerDownRight className="w-3 h-3 text-cyan-500" />
                        <span>Spent Output from TX: {inp.prev_txid.slice(0, 12)}... (vout #{inp.prev_vout_index})</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Outputs Column */}
            <div className="space-y-3">
              <h3 className="text-xs font-mono font-bold text-slate-400 uppercase tracking-wider">
                Outputs ({txDetails.outputs?.length || 0})
              </h3>
              <div className="space-y-2">
                {(txDetails.outputs || []).map((out, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-slate-900/40 border border-slate-800 text-xs font-mono space-y-1">
                    <div className="flex justify-between text-slate-300 font-medium">
                      <span>{out.address}</span>
                      <span className="text-emerald-400">{(out.amount / 1e8).toFixed(4)} BTC</span>
                    </div>
                    <div className="flex items-center justify-between text-[11px] pt-1 border-t border-slate-800/60">
                      <span className="text-slate-500 font-mono">Script: {out.script_type}</span>
                      {out.is_change_ground_truth === 1 && (
                        <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] bg-purple-950 text-purple-300 border border-purple-800">
                          <Tag className="w-2.5 h-2.5 mr-1" />
                          Change Output (Ground Truth)
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>

          {/* Network Observations List */}
          <div className="space-y-3 pt-4 border-t border-slate-800">
            <h3 className="text-xs font-mono font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <Wifi className="w-4 h-4 text-cyan-400" />
              Correlated Network Layer Observations ({txDetails.network_observations?.length || 0})
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {(txDetails.network_observations || []).map((obs, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-xs font-mono space-y-1">
                  <div className="flex justify-between text-slate-200 font-bold">
                    <span>IP: {obs.src_ip}:{obs.src_port}</span>
                    <span className="text-cyan-400">{obs.geo_country}</span>
                  </div>
                  <div className="text-[11px] text-slate-400">
                    ASN: {obs.asn}
                  </div>
                  <div className="text-[11px] text-slate-500">
                    Propagation Delay: {obs.time_delta}s
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>
      )}

    </div>
  );
}
