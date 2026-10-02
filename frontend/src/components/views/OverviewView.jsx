import React, { useState, useEffect, useRef } from 'react';
import { 
  ArrowLeftRight, Wallet, Wifi, Users, AlertTriangle, ShieldAlert, 
  TrendingUp, Globe, Filter, Maximize2, RefreshCw, ChevronRight, Activity, Zap, Database, Tag
} from 'lucide-react';
import { 
  ResponsiveContainer, BarChart, Bar, LineChart, Line, XAxis, YAxis, Tooltip, Legend, PieChart, Pie, Cell 
} from 'recharts';
import cytoscape from 'cytoscape';

export default function OverviewView({ kpiData, alerts, transactions, onSelectAlert, onSelectTx, onViewGraphTarget }) {
  const [timeRange, setTimeRange] = useState('24H');
  const [selectedNode, setSelectedNode] = useState(null);
  const graphContainerRef = useRef(null);
  const cyRef = useRef(null);

  const activeDataset = kpiData?.dataset_source || 'synthetic';
  const hasGT = kpiData?.has_ground_truth_labels ?? (activeDataset !== 'synthetic');

  // Scoped class distribution chart data without hardcoded fallbacks
  const classDistData = activeDataset === 'synthetic' ? [
    { name: 'Synthetic Anomalous', value: kpiData?.class_1_count ?? 0, color: '#EF4444' },
    { name: 'Synthetic Normal', value: kpiData?.class_2_count ?? 0, color: '#22C55E' },
  ] : [
    { name: 'Class 1 (Illicit)', value: kpiData?.class_1_count ?? 0, color: '#EF4444' },
    { name: 'Class 2 (Licit)', value: kpiData?.class_2_count ?? 0, color: '#22C55E' },
    { name: 'Class 3 (Unknown)', value: kpiData?.class_3_count ?? 0, color: '#64748B' },
  ];

  // Fetch dynamic bounded Cytoscape Graph for active dataset
  useEffect(() => {
    if (!graphContainerRef.current) return;

    let isMounted = true;
    fetch(`http://127.0.0.1:8000/api/v1/graph?dataset=${activeDataset}&limit=25`)
      .then((res) => res.ok ? res.json() : Promise.reject('Graph API error'))
      .then((data) => {
        if (!isMounted || !data.elements) return;

        if (cyRef.current) {
          cyRef.current.elements().remove();
          cyRef.current.add(data.elements);
          cyRef.current.layout({ name: 'breadthfirst', animate: false, padding: 20 }).run();
          cyRef.current.fit();
          return;
        }

        const cy = cytoscape({
          container: graphContainerRef.current,
          elements: data.elements,
          style: [
            {
              selector: 'node',
              style: {
                'label': 'data(label)',
                'color': '#f1f5f9',
                'font-size': '9px',
                'font-family': 'JetBrains Mono',
                'text-valign': 'bottom',
                'text-margin-y': 4,
                'background-color': (ele) => {
                  const type = ele.data('node_type') || ele.data('type');
                  const cLabel = ele.data('classLabel');
                  if (type === 'IP') return '#EF4444';
                  if (type === 'Transaction') return '#F59E0B';
                  if (type === 'Address') return '#2196F3';
                  if (type === 'Entity' || type === 'Wallet') return '#22C55E';
                  if (cLabel === 1) return '#EF4444';
                  if (cLabel === 2) return '#22C55E';
                  return '#94A3B8';
                },
                'width': 24,
                'height': 24,
                'border-width': 2,
                'border-color': '#ffffff',
              },
            },
            {
              selector: 'edge',
              style: {
                'width': 1.5,
                'line-color': '#334155',
                'target-arrow-color': '#334155',
                'target-arrow-shape': 'triangle',
                'curve-style': 'bezier',
              },
            },
          ],
          layout: { name: 'breadthfirst', animate: false, fit: true, padding: 20 },
        });

        cy.on('tap', 'node', (evt) => {
          setSelectedNode(evt.target.data());
        });

        cyRef.current = cy;
        cy.fit();
      })
      .catch((err) => {
        console.warn('Using fallback graph rendering:', err);
      });

    return () => {
      isMounted = false;
    };
  }, [activeDataset]);

  const runLayout = (layoutName) => {
    if (cyRef.current) {
      cyRef.current.layout({ name: layoutName, animate: true }).run();
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
      
      {/* Active Dataset Overview Banner */}
      <div className="bg-[#0B1626] border border-[#101C2E] p-4 rounded-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-[#2196F3]/20 text-[#2196F3] border border-[#2196F3]/40">
            <Database className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-mono font-bold text-white uppercase tracking-wider flex items-center space-x-2">
              <span>Active Dataset:</span>
              <span className="text-cyan-400 font-extrabold">{activeDataset.toUpperCase()}</span>
            </h2>
            <p className="text-[11px] text-slate-400 font-mono">
              {activeDataset === 'synthetic' ? 'SIH Cross-Layer Synthetic Network & Blockchain Dataset' :
               activeDataset === 'elliptic_v1' ? 'Elliptic v1 Transaction Benchmark Dataset (203k TXs, 167 features)' :
               'Elliptic v2 Heterogeneous Wallet & Address Graph Dataset (1.2M Wallets, 184 Features)'}
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-4 text-xs font-mono">
          <div className="bg-[#050B14] px-3 py-1.5 rounded-xl border border-[#101C2E]">
            {activeDataset === 'synthetic' ? (
              <>
                <span className="text-slate-400">Synthetic Labels: </span>
                <span className="text-rose-400 font-bold">Anomalous</span>
                <span className="text-slate-400"> | </span>
                <span className="text-emerald-400 font-bold">Normal</span>
              </>
            ) : (
              <>
                <span className="text-slate-400">Ground Truth Labels: </span>
                <span className="text-emerald-400 font-bold">Class 1: Illicit | Class 2: Licit | Class 3: Unknown</span>
              </>
            )}
          </div>
        </div>
      </div>

      {/* 1. TOP KPI CARDS */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
        
        {/* Total Transactions */}
        <div className="bg-[#0B1626] border border-[#101C2E] rounded-xl p-4 flex flex-col justify-between shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono font-medium text-slate-400 uppercase">Transactions</span>
            <div className="p-1.5 rounded-lg bg-[#2196F3]/10 text-[#2196F3]">
              <ArrowLeftRight className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-white font-mono">{(kpiData?.total_transactions ?? 0).toLocaleString()}</div>
            <div className="text-[10px] text-emerald-400 font-mono mt-1">Blockchain Ledger</div>
          </div>
        </div>

        {/* Class 1 / Anomalous */}
        <div className="bg-[#0B1626] border border-[#101C2E] rounded-xl p-4 flex flex-col justify-between shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono font-medium text-slate-400 uppercase">
              {activeDataset === 'synthetic' ? 'Anomalous Txs' : 'Class 1 (Illicit)'}
            </span>
            <div className="p-1.5 rounded-lg bg-rose-500/10 text-rose-400">
              <ShieldAlert className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-rose-400 font-mono">{(kpiData?.class_1_count ?? 0).toLocaleString()}</div>
            <div className="text-[10px] text-rose-400/80 font-mono mt-1">
              {activeDataset === 'synthetic' ? 'Synthetic Anomalies' : 'Ground Truth Illicit'}
            </div>
          </div>
        </div>

        {/* Class 2 / Normal */}
        <div className="bg-[#0B1626] border border-[#101C2E] rounded-xl p-4 flex flex-col justify-between shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono font-medium text-slate-400 uppercase">
              {activeDataset === 'synthetic' ? 'Normal Txs' : 'Class 2 (Licit)'}
            </span>
            <div className="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-400">
              <Tag className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-emerald-400 font-mono">{(kpiData?.class_2_count ?? 0).toLocaleString()}</div>
            <div className="text-[10px] text-emerald-400/80 font-mono mt-1">
              {activeDataset === 'synthetic' ? 'Synthetic Normal' : 'Ground Truth Licit'}
            </div>
          </div>
        </div>

        {/* Wallets / Entities */}
        <div className="bg-[#0B1626] border border-[#101C2E] rounded-xl p-4 flex flex-col justify-between shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono font-medium text-slate-400 uppercase">Wallets / Entities</span>
            <div className="p-1.5 rounded-lg bg-purple-500/10 text-purple-400">
              <Wallet className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-white font-mono">{(kpiData?.total_wallets ?? 0).toLocaleString()}</div>
            <div className="text-[10px] text-purple-400 font-mono mt-1">Entity Layer</div>
          </div>
        </div>

        {/* Active Alerts */}
        <div className="bg-[#0B1626] border border-[#101C2E] rounded-xl p-4 flex flex-col justify-between shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono font-medium text-slate-400 uppercase">Active Alerts</span>
            <div className="p-1.5 rounded-lg bg-[#F59E0B]/10 text-[#F59E0B]">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-[#F59E0B] font-mono">{(alerts?.length ?? 0).toLocaleString()}</div>
            <div className="text-[10px] text-amber-400 font-mono mt-1">Risk &gt; 45 Score</div>
          </div>
        </div>

        {/* High-Risk Leads */}
        <div className="bg-[#0B1626] border border-[#101C2E] rounded-xl p-4 flex flex-col justify-between shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono font-medium text-slate-400 uppercase">High Risk Leads</span>
            <div className="p-1.5 rounded-lg bg-[#EF4444]/10 text-[#EF4444]">
              <ShieldAlert className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-[#EF4444] font-mono">{(kpiData?.high_risk_alerts_count ?? 0).toLocaleString()}</div>
            <div className="text-[10px] text-rose-400 font-mono mt-1">Prioritization Score</div>
          </div>
        </div>

      </div>

      {/* 2. CLASS DISTRIBUTION & GRAPH VISUALIZATION */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Ground Truth Class Breakdown (1 Column) */}
        <div className="bg-[#0B1626] border border-[#101C2E] rounded-xl p-5 shadow-md flex flex-col justify-between">
          <div>
            <h3 className="text-xs font-mono font-bold text-white uppercase tracking-wider mb-1">
              {activeDataset === 'synthetic' ? 'Synthetic Scenario Breakdown' : 'Ground-Truth Class Breakdown'}
            </h3>
            <p className="text-[11px] text-slate-400 font-mono mb-4">
              {activeDataset === 'synthetic' 
                ? 'Ground Truth Labels: Not Available for Synthetic Dataset' 
                : 'Elliptic benchmark ground-truth labels'}
            </p>

            <div className="h-48 relative flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={classDistData}
                    innerRadius={50}
                    outerRadius={75}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {classDistData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="space-y-2 text-xs font-mono pt-3 border-t border-[#101C2E]">
            {classDistData.map((item) => (
              <div key={item.name} className="flex justify-between items-center">
                <div className="flex items-center space-x-2">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: item.color }}></span>
                  <span className="text-slate-300">{item.name}</span>
                </div>
                <span className="font-bold text-white">{item.value.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Cytoscape Entity Graph View (2 Columns) */}
        <div className="lg:col-span-2 bg-[#0B1626] border border-[#101C2E] rounded-xl p-5 shadow-md flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h3 className="text-xs font-mono font-bold text-white uppercase tracking-wider flex items-center space-x-2">
                <Zap className="w-4 h-4 text-[#F59E0B]" />
                <span>Multi-Layer Cytoscape Graph Explorer</span>
              </h3>
              <p className="text-[11px] text-slate-400 font-mono">Heterogeneous nodes (TX, Address, Wallet, IP) & bipartite edges</p>
            </div>
            
            <div className="flex items-center space-x-2">
              <button onClick={() => runLayout('cose')} className="px-2 py-1 text-[10px] font-mono bg-[#050B14] text-slate-300 hover:text-white rounded border border-[#101C2E]">Force</button>
              <button onClick={() => runLayout('breadthfirst')} className="px-2 py-1 text-[10px] font-mono bg-[#050B14] text-slate-300 hover:text-white rounded border border-[#101C2E]">Hierarchical</button>
              <button onClick={() => runLayout('circle')} className="px-2 py-1 text-[10px] font-mono bg-[#050B14] text-slate-300 hover:text-white rounded border border-[#101C2E]">Circle</button>
            </div>
          </div>

          <div className="h-80 w-full bg-[#050B14] rounded-xl border border-[#101C2E] relative overflow-hidden">
            <div ref={graphContainerRef} className="w-full h-full"></div>
            
            <div className="absolute bottom-3 left-3 bg-[#08111F]/90 p-2 rounded-lg border border-[#101C2E] text-[10px] font-mono space-y-1 backdrop-blur">
              {activeDataset === 'synthetic' ? (
                <>
                  <div className="flex items-center space-x-1.5"><span className="w-2.5 h-2.5 rounded-full bg-[#EF4444]"></span><span>IP Address</span></div>
                  <div className="flex items-center space-x-1.5"><span className="w-2.5 h-2.5 rotate-45 bg-[#F59E0B]"></span><span>Transaction</span></div>
                  <div className="flex items-center space-x-1.5"><span className="w-2.5 h-2.5 bg-[#2196F3]"></span><span>Bitcoin Address</span></div>
                  <div className="flex items-center space-x-1.5"><span className="w-2.5 h-2.5 rounded bg-[#22C55E]"></span><span>Inferred Entity</span></div>
                </>
              ) : (
                <>
                  <div className="flex items-center space-x-1.5"><span className="w-2.5 h-2.5 rounded-full bg-[#EF4444]"></span><span>Class 1 (Illicit)</span></div>
                  <div className="flex items-center space-x-1.5"><span className="w-2.5 h-2.5 rounded-full bg-[#22C55E]"></span><span>Class 2 (Licit)</span></div>
                  <div className="flex items-center space-x-1.5"><span className="w-2.5 h-2.5 rounded-full bg-[#A855F7]"></span><span>Wallet Node</span></div>
                  <div className="flex items-center space-x-1.5"><span className="w-2.5 h-2.5 rounded-full bg-[#38BDF8]"></span><span>IP (Synthetic Only)</span></div>
                </>
              )}
            </div>

            {selectedNode && (
              <div className="absolute top-3 right-3 bg-[#08111F]/95 p-3 rounded-xl border border-[#2196F3]/40 text-xs font-mono max-w-xs space-y-1 shadow-lg backdrop-blur">
                <div className="flex items-center justify-between text-cyan-400 font-bold border-b border-[#101C2E] pb-1">
                  <span>{selectedNode.type} Details</span>
                  <button onClick={() => setSelectedNode(null)} className="text-slate-500 hover:text-white">✕</button>
                </div>
                <div className="text-slate-300 break-all">{selectedNode.label}</div>
                <div className="text-slate-400 text-[10px]">Risk Score: <span className="font-bold text-amber-400">{selectedNode.risk} / 100</span></div>
                <button
                  onClick={() => onViewGraphTarget && onViewGraphTarget(selectedNode.id)}
                  className="mt-2 w-full py-1 text-[10px] bg-[#2196F3] text-white rounded hover:bg-[#1E88E5] transition"
                >
                  Explore Subgraph
                </button>
              </div>
            )}
          </div>
        </div>

      </div>

    </div>
  );
}
