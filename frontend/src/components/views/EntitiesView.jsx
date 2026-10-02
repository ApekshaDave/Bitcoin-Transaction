import React, { useState, useEffect } from 'react';
import { Users, ShieldAlert, Wallet, Search, Tag, ExternalLink, AlertTriangle } from 'lucide-react';

export default function EntitiesView({ activeDataset = 'synthetic', onViewGraphTarget }) {
  const [wallets, setWallets] = useState([]);
  const [loadingWallets, setLoadingWallets] = useState(false);
  const [walletClassFilter, setWalletClassFilter] = useState('ALL');
  const [searchAddr, setSearchAddr] = useState('');
  const [status, setStatus] = useState('LOADING');

  useEffect(() => {
    fetchWallets();
  }, [activeDataset, walletClassFilter]);

  const fetchWallets = async () => {
    setLoadingWallets(true);
    try {
      let url = `http://127.0.0.1:8000/api/v1/wallets?dataset=${activeDataset || 'synthetic'}&limit=50`;
      if (walletClassFilter !== 'ALL') {
        url += `&class_label=${walletClassFilter}`;
      }
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        if (data.status === 'NOT_PROVIDED') {
          setStatus('NOT_PROVIDED');
          setWallets([]);
        } else {
          setStatus('AVAILABLE');
          const walletList = Array.isArray(data) ? data : (data.wallets || []);
          setWallets(walletList);
        }
      } else {
        setWallets([]);
      }
    } catch (e) {
      console.error('Failed to fetch wallets:', e);
      setWallets([]);
    } finally {
      setLoadingWallets(false);
    }
  };

  const sampleEntities = [
    { entity_id: 'ENTITY_C12', address_count: 4, detected_pattern: 'Peeling Chain Funnel', risk_score: 92.4, confidence: 0.88, related_ips: ['192.168.1.45', '10.0.4.12'], countries: ['US', 'DE'], total_txs: 28 },
    { entity_id: 'ENTITY_C08', address_count: 8, detected_pattern: 'Mixing Obfuscation Pool', risk_score: 88.1, confidence: 0.84, related_ips: ['172.16.0.8'], countries: ['NL'], total_txs: 45 },
    { entity_id: 'ENTITY_C03', address_count: 2, detected_pattern: 'Normal Multi-Sig Wallet', risk_score: 18.0, confidence: 0.95, related_ips: ['192.168.1.100'], countries: ['IN'], total_txs: 6 },
  ];

  const filteredWallets = (Array.isArray(wallets) ? wallets : []).filter(w => 
    w && w.address && w.address.toLowerCase().includes(searchAddr.toLowerCase())
  );

  const getWalletBadge = (cLabel) => {
    if (cLabel === 1) {
      return (
        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-400 border border-rose-500/40 inline-flex items-center gap-1">
          <ShieldAlert className="w-3 h-3" />
          <span>Class 1 (Illicit Wallet)</span>
        </span>
      );
    }
    if (cLabel === 2) {
      return (
        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 inline-block">
          Class 2 (Licit Wallet)
        </span>
      );
    }
    return (
      <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-500/20 text-slate-400 border border-slate-500/40 inline-block">
        Class 3 (Unknown)
      </span>
    );
  };

  if (activeDataset === 'elliptic_v1' || status === 'NOT_PROVIDED') {
    return (
      <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
        <div className="bg-[#0B1626] border border-[#101C2E] p-4 rounded-xl flex items-center justify-between">
          <div>
            <h2 className="text-sm font-mono font-bold text-white uppercase tracking-wider flex items-center space-x-2">
              <Users className="w-4 h-4 text-[#22C55E]" />
              <span>Inferred Address Entity Clusters</span>
            </h2>
            <p className="text-[11px] text-slate-400 font-mono">Dataset Scope: Elliptic v1 Benchmark</p>
          </div>
        </div>

        <div className="bg-[#0B1626] border border-amber-500/30 rounded-xl p-8 text-center space-y-3">
          <AlertTriangle className="w-10 h-10 text-amber-400 mx-auto" />
          <h3 className="text-base font-mono font-bold text-amber-300">Entity & Wallet Layer Not Provided</h3>
          <p className="text-xs font-mono text-slate-400 max-w-xl mx-auto">
            Wallet and entity datasets are not provided by the Elliptic v1 benchmark. Elliptic v1 contains transaction-level nodes without native address or entity clustering ground truth.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
      
      {/* Section 1: DBSCAN Entity Clusters */}
      <div className="bg-[#0B1626] border border-[#101C2E] p-4 rounded-xl flex items-center justify-between">
        <div>
          <h2 className="text-sm font-mono font-bold text-white uppercase tracking-wider flex items-center space-x-2">
            <Users className="w-4 h-4 text-[#22C55E]" />
            <span>Inferred Address Entity Clusters (DBSCAN Unsupervised)</span>
          </h2>
          <p className="text-[11px] text-slate-400 font-mono">Multi-input co-spending heuristic address grouping</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {sampleEntities.map((ent) => (
          <div key={ent.entity_id} className="bg-[#0B1626] border border-[#101C2E] rounded-xl p-5 shadow-md flex flex-col justify-between space-y-4">
            <div>
              <div className="flex items-center justify-between border-b border-[#101C2E] pb-3">
                <span className="text-xs font-mono font-bold text-emerald-400">{ent.entity_id}</span>
                <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold border ${
                  ent.risk_score >= 75 ? 'bg-rose-950/60 text-rose-400 border-rose-800' : 'bg-emerald-950/60 text-emerald-400 border-emerald-800'
                }`}>
                  Risk Score: {ent.risk_score.toFixed(1)}
                </span>
              </div>
              
              <div className="mt-3 space-y-2 text-xs font-mono">
                <div className="flex justify-between text-slate-400"><span className="text-[10px]">Addresses Clustered:</span><span className="text-white font-bold">{ent.address_count} Addrs</span></div>
                <div className="flex justify-between text-slate-400"><span className="text-[10px]">Pattern Detected:</span><span className="text-cyan-300 font-semibold">{ent.detected_pattern}</span></div>
                <div className="flex justify-between text-slate-400"><span className="text-[10px]">Associated IPs:</span><span className="text-slate-200">{ent.related_ips.join(', ')}</span></div>
                <div className="flex justify-between text-slate-400"><span className="text-[10px]">Total TX Volume:</span><span className="text-white">{ent.total_txs} TXs</span></div>
              </div>
            </div>

            <button
              onClick={() => onViewGraphTarget && onViewGraphTarget(ent.entity_id)}
              className="w-full py-2 bg-[#2196F3]/20 hover:bg-[#2196F3] text-[#22D3EE] hover:text-white rounded-xl border border-[#2196F3]/40 text-xs font-mono font-semibold transition"
            >
              Explore Entity Graph
            </button>
          </div>
        ))}
      </div>

      {/* Section 2: Wallet Layer */}
      <div className="bg-[#0B1626] border border-[#101C2E] p-4 rounded-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-sm font-mono font-bold text-white uppercase tracking-wider flex items-center space-x-2">
            <Wallet className="w-4 h-4 text-cyan-400" />
            <span>
              {activeDataset === 'synthetic'
                ? 'SIH Synthetic Wallet & Address Layer'
                : 'Elliptic v2 Wallet & Entity Layer Analysis'}
            </span>
          </h2>
          <p className="text-[11px] text-slate-400 font-mono">
            {activeDataset === 'synthetic'
              ? 'Derived synthetic addresses and participation metrics'
              : 'Ground-truth wallet classification & 57 graph feature metrics'}
          </p>
        </div>

        <div className="flex items-center space-x-3">
          {/* Class Filter */}
          <div className="flex items-center space-x-1.5 bg-[#050B14] px-3 py-1.5 rounded-xl border border-[#101C2E]">
            <Tag className="w-3.5 h-3.5 text-cyan-400" />
            <select
              value={walletClassFilter}
              onChange={(e) => setWalletClassFilter(e.target.value)}
              className="bg-transparent text-xs font-mono text-slate-200 focus:outline-none"
            >
              <option value="ALL" className="bg-[#08111F]">All Wallet Classes</option>
              <option value="1" className="bg-[#08111F] text-rose-400">Class 1 (Illicit)</option>
              <option value="2" className="bg-[#08111F] text-emerald-400">Class 2 (Licit)</option>
              <option value="3" className="bg-[#08111F] text-slate-400">Class 3 (Unknown)</option>
            </select>
          </div>

          {/* Search Wallet Address */}
          <div className="relative w-56">
            <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-500" />
            <input
              type="text"
              placeholder="Search wallet address..."
              value={searchAddr}
              onChange={(e) => setSearchAddr(e.target.value)}
              className="w-full bg-[#050B14] text-xs font-mono text-cyan-300 placeholder-slate-500 pl-8 pr-3 py-1.5 rounded-xl border border-[#101C2E] focus:outline-none focus:border-[#2196F3]"
            />
          </div>
        </div>
      </div>

      <div className="bg-[#0B1626] border border-[#101C2E] rounded-xl overflow-hidden shadow-md">
        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs">
            <thead className="bg-[#050B14] text-slate-400 border-b border-[#101C2E] uppercase text-[10px]">
              <tr>
                <th className="py-3 px-4">Wallet Address</th>
                <th className="py-3 px-4">Ground Truth Class</th>
                <th className="py-3 px-4">Sender TXs</th>
                <th className="py-3 px-4">Receiver TXs</th>
                <th className="py-3 px-4">Total Transacted (BTC)</th>
                <th className="py-3 px-4">Total Fees</th>
                <th className="py-3 px-4">Connected Addrs</th>
                <th className="py-3 px-4 text-right">Graph</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#101C2E]">
              {filteredWallets.map((w, idx) => (
                <tr key={w.address || idx} className="hover:bg-[#101C2E]/50 transition">
                  <td className="py-3 px-4 text-cyan-300 font-bold break-all max-w-xs">{w.address}</td>
                  <td className="py-3 px-4">{getWalletBadge(w.class_label)}</td>
                  <td className="py-3 px-4 text-slate-300">{w.num_txs_as_sender}</td>
                  <td className="py-3 px-4 text-slate-300">{w.num_txs_as_receiver}</td>
                  <td className="py-3 px-4 font-bold text-white">{(w.btc_transacted_total || 0).toFixed(4)} BTC</td>
                  <td className="py-3 px-4 text-slate-400">{(w.fees_total || 0).toFixed(5)}</td>
                  <td className="py-3 px-4 text-cyan-400">{w.transacted_w_address_total || 0}</td>
                  <td className="py-3 px-4 text-right">
                    <button
                      onClick={() => onViewGraphTarget && onViewGraphTarget(w.address)}
                      className="p-1.5 bg-[#101C2E] hover:bg-[#2196F3] text-slate-300 hover:text-white rounded-lg transition"
                      title="Inspect Wallet Graph"
                    >
                      <ExternalLink className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              ))}
              {filteredWallets.length === 0 && (
                <tr>
                  <td colSpan="8" className="py-8 text-center text-slate-500">
                    {loadingWallets ? 'Loading wallets...' : 'No wallets found for selected dataset/filter.'}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
