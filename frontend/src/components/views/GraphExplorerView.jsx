import React, { useEffect, useRef, useState } from 'react';
import { Network, ZoomIn, ZoomOut, RefreshCw, Search, ShieldAlert, X, ExternalLink, Loader2, AlertCircle } from 'lucide-react';
import cytoscape from 'cytoscape';

export default function GraphExplorerView({ activeDataset = 'synthetic', initialTargetId, onSelectTx }) {
  const containerRef = useRef(null);
  const cyRef = useRef(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [searchNode, setSearchNode] = useState(initialTargetId || 'tx_golden_001');
  const [depth, setDepth] = useState(1);
  const [limit, setLimit] = useState(50);
  const [graphStatus, setGraphStatus] = useState('loading'); // 'loading' | 'empty' | 'error' | 'success'
  const [nodeCount, setNodeCount] = useState(0);
  const [edgeCount, setEdgeCount] = useState(0);
  const [isTruncated, setIsTruncated] = useState(false);
  const [centerNode, setCenterNode] = useState('tx_golden_001');

  const fetchAndRenderGraph = (targetId = searchNode, reqDepth = depth, reqLimit = limit) => {
    setGraphStatus('loading');
    setSelectedNode(null);

    const target = targetId.trim() || 'tx_golden_001';
    const baseUrl = `http://127.0.0.1:8000/api/v1/graph?dataset=${activeDataset}&tx_id=${encodeURIComponent(target)}&depth=${reqDepth}&limit=${reqLimit}`;

    fetch(baseUrl)
      .then((res) => res.ok ? res.json() : Promise.reject('Graph API request failed'))
      .then((data) => {
        if (!data || !data.elements || data.elements.length === 0) {
          setGraphStatus('empty');
          setNodeCount(0);
          setEdgeCount(0);
          setIsTruncated(false);
          if (cyRef.current) {
            cyRef.current.elements().remove();
          }
          return;
        }

        const normalizedElements = data.elements.map((el) => {
          const rawData = el.data || {};
          const nType = rawData.node_type || rawData.type || (rawData.source ? 'edge' : 'node');
          let label = rawData.label || rawData.id || '';

          if (label.length > 22 && !label.includes(' ')) {
            label = `${label.slice(0, 8)}...${label.slice(-6)}`;
          }

          return {
            ...el,
            data: {
              ...rawData,
              node_type: nType,
              label: label
            }
          };
        });

        const nodeEls = normalizedElements.filter(e => !e.data.source);
        const edgeEls = normalizedElements.filter(e => e.data.source);

        setNodeCount(data.node_count || nodeEls.length);
        setEdgeCount(data.edge_count || edgeEls.length);
        setIsTruncated(Boolean(data.truncated));
        setCenterNode(data.center || target);
        setGraphStatus('success');

        if (!containerRef.current) return;

        if (cyRef.current) {
          cyRef.current.elements().remove();
          cyRef.current.add(normalizedElements);
          cyRef.current.layout({ name: 'breadthfirst', animate: false, padding: 40 }).run();
          cyRef.current.fit();
          return;
        }

        const cy = cytoscape({
          container: containerRef.current,
          elements: normalizedElements,
          style: [
            {
              selector: 'node',
              style: {
                'label': 'data(label)',
                'color': '#f1f5f9',
                'font-size': '10px',
                'font-family': 'JetBrains Mono, monospace',
                'text-valign': 'bottom',
                'text-margin-y': 5,
                'background-color': '#475569',
                'width': 28,
                'height': 28,
                'border-width': 2,
                'border-color': '#0f172a',
              },
            },
            {
              selector: 'node[node_type = "IP"], node[type = "IP"]',
              style: {
                'background-color': '#EF4444',
                'border-color': '#B91C1C',
                'shape': 'ellipse',
                'width': 32,
                'height': 32
              }
            },
            {
              selector: 'node[node_type = "Transaction"], node[type = "Transaction"]',
              style: {
                'background-color': '#F59E0B',
                'border-color': '#D97706',
                'shape': 'diamond',
                'width': 34,
                'height': 34
              }
            },
            {
              selector: 'node[node_type = "Address"], node[type = "Address"]',
              style: {
                'background-color': '#2196F3',
                'border-color': '#1D4ED8',
                'shape': 'rectangle',
                'width': 26,
                'height': 26
              }
            },
            {
              selector: 'node[node_type = "Entity"], node[type = "Entity"], node[node_type = "Wallet"]',
              style: {
                'background-color': '#22C55E',
                'border-color': '#15803D',
                'shape': 'hexagon',
                'width': 34,
                'height': 34
              }
            },
            {
              selector: 'edge',
              style: {
                'width': 2,
                'line-color': '#334155',
                'target-arrow-color': '#334155',
                'target-arrow-shape': 'triangle',
                'curve-style': 'bezier',
                'label': 'data(label)',
                'font-size': '8px',
                'color': '#64748B',
                'text-rotation': 'autorotate'
              },
            },
            {
              selector: 'edge[edge_type = "OBSERVED"], edge[edge_type = "OBSERVED_IN"]',
              style: {
                'line-color': '#EF4444',
                'target-arrow-color': '#EF4444',
                'line-style': 'dashed'
              }
            },
            {
              selector: 'edge[edge_type = "INPUT"], edge[edge_type = "INPUT_TO"]',
              style: {
                'line-color': '#2196F3',
                'target-arrow-color': '#2196F3'
              }
            },
            {
              selector: 'edge[edge_type = "OUTPUT"], edge[edge_type = "OUTPUTS_TO"]',
              style: {
                'line-color': '#F59E0B',
                'target-arrow-color': '#F59E0B'
              }
            },
            {
              selector: 'edge[edge_type = "ASSOCIATED_WITH"]',
              style: {
                'line-color': '#22C55E',
                'target-arrow-color': '#22C55E',
                'line-style': 'dotted'
              }
            },
            {
              selector: ':selected',
              style: {
                'border-width': 4,
                'border-color': '#22D3EE',
                'line-color': '#22D3EE'
              }
            }
          ],
          layout: {
            name: 'breadthfirst',
            animate: false,
            fit: true,
            padding: 40
          },
        });

        cy.on('tap', 'node', (evt) => {
          setSelectedNode(evt.target.data());
        });

        cy.on('tap', (evt) => {
          if (evt.target === cy) {
            setSelectedNode(null);
          }
        });

        cyRef.current = cy;
        cy.fit();
      })
      .catch((err) => {
        console.error('Graph Explorer fetch failed:', err);
        setGraphStatus('error');
      });
  };

  useEffect(() => {
    fetchAndRenderGraph(initialTargetId || searchNode, depth, limit);
    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
        cyRef.current = null;
      }
    };
  }, [activeDataset, initialTargetId, depth, limit]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchAndRenderGraph(searchNode, depth, limit);
  };

  const changeLayout = (name) => {
    if (cyRef.current) {
      cyRef.current.layout({ name, animate: true, fit: true, padding: 40 }).run();
    }
  };

  const handleZoomIn = () => cyRef.current && cyRef.current.zoom(cyRef.current.zoom() * 1.25);
  const handleZoomOut = () => cyRef.current && cyRef.current.zoom(cyRef.current.zoom() * 0.8);
  const handleReset = () => {
    if (cyRef.current) {
      cyRef.current.fit();
    }
  };

  return (
    <div className="p-6 space-y-4 max-w-[1600px] mx-auto h-[calc(100vh-80px)] flex flex-col font-mono">
      
      {/* Top Controls Bar */}
      <div className="bg-[#0B1626] border border-[#101C2E] p-3 rounded-xl flex flex-col lg:flex-row lg:items-center justify-between gap-3 shrink-0">
        
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-[#2196F3]/20 text-[#2196F3]">
            <Network className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <span>Multi-Layer Heterogeneous Cytoscape Graph</span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
                {activeDataset.toUpperCase()}
              </span>
            </h2>
            <p className="text-[10px] text-slate-400">
              {nodeCount} Nodes | {edgeCount} Edges | Provenance Topology Explorer
            </p>
          </div>
        </div>

        {/* Search Node & Subgraph Controls */}
        <form onSubmit={handleSearchSubmit} className="flex flex-wrap items-center gap-2">
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Target TXID / Node..."
              value={searchNode}
              onChange={(e) => setSearchNode(e.target.value)}
              className="bg-[#050B14] border border-[#101C2E] text-xs text-white pl-8 pr-3 py-1.5 rounded-lg focus:outline-none focus:border-[#2196F3] w-48"
            />
          </div>
          <select
            value={depth}
            onChange={(e) => setDepth(Number(e.target.value))}
            className="bg-[#050B14] border border-[#101C2E] text-xs text-slate-300 py-1.5 px-2 rounded-lg"
          >
            <option value={1}>Depth 1</option>
            <option value={2}>Depth 2</option>
          </select>
          <select
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value))}
            className="bg-[#050B14] border border-[#101C2E] text-xs text-slate-300 py-1.5 px-2 rounded-lg"
          >
            <option value={25}>Limit 25</option>
            <option value={50}>Limit 50</option>
            <option value={100}>Limit 100</option>
            <option value={200}>Limit 200</option>
          </select>
          <button
            type="submit"
            className="px-3 py-1.5 bg-[#2196F3]/20 hover:bg-[#2196F3] text-cyan-300 hover:text-white border border-[#2196F3]/40 text-xs rounded-lg transition"
          >
            Query Subgraph
          </button>
        </form>

        {/* Layout & Zoom Controls */}
        <div className="flex items-center space-x-2">
          <div className="flex items-center space-x-1 bg-[#050B14] p-1 rounded-lg border border-[#101C2E]">
            {['breadthfirst', 'cose', 'concentric', 'circle'].map((l) => (
              <button
                key={l}
                onClick={() => changeLayout(l)}
                className="px-2 py-1 text-[10px] text-slate-300 hover:text-white capitalize rounded hover:bg-[#101C2E]"
              >
                {l}
              </button>
            ))}
          </div>

          <div className="flex items-center space-x-1 bg-[#050B14] p-1 rounded-lg border border-[#101C2E]">
            <button onClick={handleZoomIn} className="p-1.5 text-slate-300 hover:text-white" title="Zoom In"><ZoomIn className="w-4 h-4" /></button>
            <button onClick={handleZoomOut} className="p-1.5 text-slate-300 hover:text-white" title="Zoom Out"><ZoomOut className="w-4 h-4" /></button>
            <button onClick={handleReset} className="p-1.5 text-slate-300 hover:text-white" title="Reset Fit"><RefreshCw className="w-4 h-4" /></button>
          </div>
        </div>
      </div>

      {/* Main Canvas + Side Inspector */}
      <div className="flex-1 bg-[#050B14] border border-[#101C2E] rounded-xl relative overflow-hidden flex">
        
        {/* State Banners */}
        {graphStatus === 'loading' && (
          <div className="absolute inset-0 z-20 bg-[#050B14]/90 backdrop-blur flex items-center justify-center space-x-3 text-cyan-400">
            <Loader2 className="w-6 h-6 animate-spin" />
            <span className="text-xs font-semibold">Loading Multi-Layer Cytoscape Graph...</span>
          </div>
        )}

        {graphStatus === 'empty' && (
          <div className="absolute inset-0 z-20 bg-[#050B14]/95 flex flex-col items-center justify-center space-y-3 text-slate-400">
            <AlertCircle className="w-8 h-8 text-amber-400" />
            <span className="text-xs font-semibold">No graph relationships available for the selected dataset.</span>
            <button
              onClick={() => fetchAndRenderGraph('')}
              className="px-3 py-1.5 bg-[#101C2E] hover:bg-[#1E293B] text-cyan-400 text-xs rounded-lg border border-[#2196F3]/40"
            >
              Reset Search & Reload
            </button>
          </div>
        )}

        {graphStatus === 'error' && (
          <div className="absolute inset-0 z-20 bg-[#050B14]/95 flex flex-col items-center justify-center space-y-3 text-rose-400">
            <ShieldAlert className="w-8 h-8 text-rose-500" />
            <span className="text-xs font-semibold">Unable to connect to graph service endpoint.</span>
            <button
              onClick={() => fetchAndRenderGraph('')}
              className="px-3 py-1.5 bg-rose-950/60 hover:bg-rose-900 text-rose-200 text-xs rounded-lg border border-rose-800"
            >
              Retry Connection
            </button>
          </div>
        )}

        {/* Cytoscape Container */}
        <div ref={containerRef} className="w-full h-full" />

        {/* Graph Scope Info Widget */}
        <div className="absolute top-4 left-4 bg-[#08111F]/90 p-2.5 rounded-xl border border-[#101C2E] text-[11px] space-y-1 backdrop-blur z-10 shadow-lg text-slate-300">
          <div className="text-[10px] text-cyan-400 font-bold uppercase tracking-wider flex items-center justify-between border-b border-[#101C2E] pb-1 gap-2">
            <span>GRAPH SCOPE</span>
            {isTruncated && (
              <span className="px-1.5 py-0.5 rounded bg-amber-950 text-amber-400 border border-amber-800 text-[9px]">
                TRUNCATED
              </span>
            )}
          </div>
          <div className="flex justify-between gap-4">
            <span className="text-slate-400">Center:</span>
            <span className="font-mono text-cyan-300 font-bold">{centerNode}</span>
          </div>
          <div className="flex justify-between gap-4">
            <span className="text-slate-400">Nodes / Edges:</span>
            <span className="font-mono text-white font-semibold">{nodeCount} / {edgeCount}</span>
          </div>
          <div className="flex justify-between gap-4">
            <span className="text-slate-400">Depth / Limit:</span>
            <span className="font-mono text-slate-300">{depth} / {limit}</span>
          </div>
        </div>

        {/* Legend */}
        <div className="absolute bottom-4 left-4 bg-[#08111F]/90 p-3 rounded-xl border border-[#101C2E] text-xs space-y-1.5 backdrop-blur z-10 shadow-lg">
          <div className="text-[10px] text-slate-400 font-bold uppercase mb-1 border-b border-[#101C2E] pb-1">
            {activeDataset === 'synthetic' ? 'SIH Synthetic Graph Legend' : 'Elliptic Benchmark Legend'}
          </div>
          
          <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-[11px]">
            <div className="flex items-center space-x-2"><span className="w-3 h-3 rounded-full bg-[#EF4444]"></span><span>IP Address</span></div>
            <div className="flex items-center space-x-2"><span className="w-3 h-3 rotate-45 bg-[#F59E0B]"></span><span>Transaction</span></div>
            <div className="flex items-center space-x-2"><span className="w-3 h-3 rounded-sm bg-[#2196F3]"></span><span>Bitcoin Address</span></div>
            <div className="flex items-center space-x-2"><span className="w-3 h-3 rounded bg-[#22C55E]"></span><span>Inferred Entity</span></div>
          </div>

          <div className="border-t border-[#101C2E] pt-1.5 mt-1 flex flex-wrap gap-2 text-[10px] text-slate-400">
            <span className="text-rose-400 font-bold">--- OBSERVED</span>
            <span className="text-cyan-400 font-bold">── INPUT</span>
            <span className="text-amber-400 font-bold">── OUTPUT</span>
            <span className="text-emerald-400 font-bold">... ENTITY</span>
          </div>
        </div>

        {/* Node Inspector Drawer */}
        {selectedNode && (
          <div className="w-80 bg-[#08111F]/95 border-l border-[#2196F3]/40 p-4 text-xs space-y-4 backdrop-blur overflow-y-auto z-20 shadow-2xl">
            <div className="flex items-center justify-between border-b border-[#101C2E] pb-2">
              <span className="text-cyan-400 font-bold uppercase">{selectedNode.node_type || selectedNode.type || 'Node'} Details</span>
              <button onClick={() => setSelectedNode(null)} className="text-slate-500 hover:text-white"><X className="w-4 h-4" /></button>
            </div>

            <div className="space-y-3">
              <div>
                <span className="text-[10px] text-slate-400 uppercase">Node Identifier:</span>
                <div className="text-white font-bold break-all">{selectedNode.id}</div>
              </div>

              {selectedNode.txid && (
                <div>
                  <span className="text-[10px] text-slate-400 uppercase">Transaction ID:</span>
                  <div className="text-amber-300 font-bold break-all">{selectedNode.txid}</div>
                </div>
              )}

              {selectedNode.address && (
                <div>
                  <span className="text-[10px] text-slate-400 uppercase">Address / IP:</span>
                  <div className="text-cyan-300 font-bold break-all">{selectedNode.address}</div>
                </div>
              )}

              {selectedNode.entity_id && (
                <div>
                  <span className="text-[10px] text-slate-400 uppercase">Entity Mapping:</span>
                  <div className="text-emerald-400 font-semibold">{selectedNode.entity_id}</div>
                </div>
              )}

              {selectedNode.total_amount !== undefined && (
                <div>
                  <span className="text-[10px] text-slate-400 uppercase">Total Volume:</span>
                  <div className="text-white font-bold">{(selectedNode.total_amount / 1e8).toFixed(4)} BTC</div>
                </div>
              )}

              {selectedNode.country && (
                <div>
                  <span className="text-[10px] text-slate-400 uppercase">GeoIP Country / ASN:</span>
                  <div className="text-slate-200">{selectedNode.country} ({selectedNode.asn})</div>
                </div>
              )}

              {/* Action Button: Open Investigation */}
              {(selectedNode.txid || selectedNode.node_type === 'Transaction' || selectedNode.id.startsWith('tx:')) && (
                <div className="pt-2">
                  <button
                    onClick={() => {
                      const cleanTxid = (selectedNode.txid || selectedNode.id.replace('tx:', '')).toLowerCase();
                      if (onSelectTx) onSelectTx(cleanTxid);
                    }}
                    className="w-full py-2 bg-[#2196F3] hover:bg-[#1D4ED8] text-white font-bold text-xs rounded-lg flex items-center justify-center space-x-2 transition shadow-md"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                    <span>Open 9-Stage Trace</span>
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
