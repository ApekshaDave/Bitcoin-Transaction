import React, { useState, useEffect } from 'react';
import { Wallet, ShieldAlert, AlertTriangle, CheckCircle2, ArrowRightLeft } from 'lucide-react';

export default function AddressesView({ activeDataset, onViewGraphTarget }) {
  const [wallets, setWallets] = useState([]);
  const [status, setStatus] = useState('LOADING');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    fetch(`http://localhost:8000/api/v1/wallets?dataset=${activeDataset || 'synthetic'}`)
      .then((res) => res.json())
      .then((data) => {
        if (!isMounted) return;
        if (data.status === 'NOT_PROVIDED') {
          setStatus('NOT_PROVIDED');
          setMessage(data.message || 'N/A — wallet dataset not provided by Elliptic v1 benchmark');
          setWallets([]);
        } else {
          setStatus('AVAILABLE');
          setWallets(data.wallets || []);
        }
        setLoading(false);
      })
      .catch((err) => {
        if (!isMounted) return;
        console.error('Error fetching wallets:', err);
        setStatus(activeDataset === 'elliptic_v1' ? 'NOT_PROVIDED' : 'ERROR');
        setMessage(activeDataset === 'elliptic_v1' ? 'N/A — wallet dataset not provided by Elliptic v1 benchmark' : 'Error loading wallet data');
        setWallets([]);
        setLoading(false);
      });

    return () => { isMounted = false; };
  }, [activeDataset]);

  if (activeDataset === 'elliptic_v1' || status === 'NOT_PROVIDED') {
    return (
      <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
        <div className="bg-[#0B1626] border border-[#101C2E] p-4 rounded-xl flex items-center justify-between">
          <div>
            <h2 className="text-sm font-mono font-bold text-white uppercase tracking-wider flex items-center space-x-2">
              <Wallet className="w-4 h-4 text-[#8B5CF6]" />
              <span>Bitcoin Address Ledger & Clustering</span>
            </h2>
            <p className="text-[11px] text-slate-400 font-mono">Dataset Scope: Elliptic v1 Benchmark</p>
          </div>
        </div>

        <div className="bg-[#0B1626] border border-amber-500/30 rounded-xl p-8 text-center space-y-3">
          <AlertTriangle className="w-10 h-10 text-amber-400 mx-auto" />
          <h3 className="text-base font-mono font-bold text-amber-300">Wallet Dataset Not Provided</h3>
          <p className="text-xs font-mono text-slate-400 max-w-xl mx-auto">
            Wallet/address dataset not provided by Elliptic v1 benchmark. Elliptic v1 is a transaction-level benchmark dataset without native address or wallet mappings.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
      <div className="bg-[#0B1626] border border-[#101C2E] p-4 rounded-xl flex items-center justify-between">
        <div>
          <h2 className="text-sm font-mono font-bold text-white uppercase tracking-wider flex items-center space-x-2">
            <Wallet className="w-4 h-4 text-[#8B5CF6]" />
            <span>Bitcoin Address Ledger & Clustering</span>
          </h2>
          <p className="text-[11px] text-slate-400 font-mono">
            {activeDataset === 'synthetic'
              ? 'Derived synthetic addresses from blockchain transaction inputs & outputs'
              : 'Elliptic++ v2 Heterogeneous Wallet & Address Dataset'}
          </p>
        </div>
        <div className="text-xs font-mono text-purple-400 bg-purple-500/10 px-3 py-1.5 rounded-lg border border-purple-500/20">
          Total Records: {loading ? '...' : wallets.length}
        </div>
      </div>

      <div className="bg-[#0B1626] border border-[#101C2E] rounded-xl overflow-hidden shadow-md">
        {loading ? (
          <div className="p-8 text-center text-slate-400 font-mono text-xs">Loading address records...</div>
        ) : wallets.length === 0 ? (
          <div className="p-8 text-center text-slate-400 font-mono text-xs">No address records available.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left font-mono text-xs">
              <thead className="bg-[#050B14] text-slate-400 border-b border-[#101C2E] uppercase text-[10px]">
                <tr>
                  <th className="py-3 px-4">Address</th>
                  <th className="py-3 px-4">Dataset</th>
                  <th className="py-3 px-4">Class Label</th>
                  <th className="py-3 px-4">Sender TXs</th>
                  <th className="py-3 px-4">Receiver TXs</th>
                  <th className="py-3 px-4">Total BTC Transacted</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#101C2E]">
                {wallets.map((w, idx) => (
                  <tr key={w.address || idx} className="hover:bg-[#101C2E]/50 transition">
                    <td className="py-3 px-4 text-cyan-300 font-bold break-all max-w-xs">{w.address}</td>
                    <td className="py-3 px-4 text-slate-400 uppercase text-[10px]">{w.dataset_source || activeDataset}</td>
                    <td className="py-3 px-4">
                      {w.class_label === 1 ? (
                        <span className="text-rose-400 font-bold bg-rose-500/10 px-2 py-0.5 rounded text-[10px]">Class 1 (Illicit)</span>
                      ) : w.class_label === 2 ? (
                        <span className="text-emerald-400 font-bold bg-emerald-500/10 px-2 py-0.5 rounded text-[10px]">Class 2 (Licit)</span>
                      ) : (
                        <span className="text-slate-400 bg-slate-500/10 px-2 py-0.5 rounded text-[10px]">Class 3 (Unknown)</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-slate-300">{w.num_txs_as_sender}</td>
                    <td className="py-3 px-4 text-slate-300">{w.num_txs_as_receiver}</td>
                    <td className="py-3 px-4 text-white font-bold">{typeof w.btc_transacted_total === 'number' ? w.btc_transacted_total.toFixed(4) : w.btc_transacted_total} BTC</td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => onViewGraphTarget && onViewGraphTarget(w.address)}
                        className="px-2.5 py-1 bg-[#2196F3]/20 text-[#22D3EE] hover:bg-[#2196F3] hover:text-white rounded-lg border border-[#2196F3]/40 text-[10px] transition"
                      >
                        Graph Subgraph
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
