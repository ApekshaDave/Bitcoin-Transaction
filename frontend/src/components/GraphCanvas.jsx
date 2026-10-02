import React, { useEffect, useRef, useState } from 'react';
import cytoscape from 'cytoscape';
import { ZoomIn, ZoomOut, Maximize2, Network, Info } from 'lucide-react';

export default function GraphCanvas({ graphData }) {
  const containerRef = useRef(null);
  const cyRef = useRef(null);
  const [selectedElement, setSelectedElement] = useState(null);

  useEffect(() => {
    if (!containerRef.current || !graphData || !graphData.elements) return;

    // Destroy existing instance if any
    if (cyRef.current) {
      cyRef.current.destroy();
    }

    // Initialize Cytoscape
    const cy = cytoscape({
      container: containerRef.current,
      elements: graphData.elements,
      style: [
        {
          selector: 'node',
          style: {
            'label': 'data(label)',
            'color': '#cbd5e1',
            'font-size': '10px',
            'font-family': 'JetBrains Mono, monospace',
            'text-valign': 'bottom',
            'text-margin-y': 5,
            'background-color': '#475569',
            'width': 30,
            'height': 30,
            'border-width': 2,
            'border-color': '#1e293b'
          }
        },
        {
          selector: 'node[node_type = "IP"]',
          style: {
            'background-color': '#38bdf8',
            'border-color': '#0284c7',
            'shape': 'ellipse',
            'width': 34,
            'height': 34
          }
        },
        {
          selector: 'node[node_type = "Transaction"]',
          style: {
            'background-color': '#c084fc',
            'border-color': '#9333ea',
            'shape': 'diamond',
            'width': 36,
            'height': 36
          }
        },
        {
          selector: 'node[node_type = "Address"]',
          style: {
            'background-color': '#34d399',
            'border-color': '#059669',
            'shape': 'rectangle',
            'width': 28,
            'height': 28
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 1.5,
            'line-color': '#334155',
            'target-arrow-color': '#334155',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'label': 'data(label)',
            'font-size': '8px',
            'color': '#64748b',
            'text-rotation': 'autorotate'
          }
        },
        {
          selector: 'edge[edge_type = "OBSERVED"], edge[edge_type = "OBSERVED_IN"]',
          style: {
            'line-color': '#38bdf8',
            'target-arrow-color': '#38bdf8',
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
          selector: 'edge[edge_type = "SPENDS"]',
          style: {
            'line-color': '#fb7185',
            'target-arrow-color': '#fb7185',
            'width': 2.5
          }
        },
        {
          selector: ':selected',
          style: {
            'border-width': 4,
            'border-color': '#38bdf8',
            'line-color': '#38bdf8'
          }
        }
      ],
      layout: {
        name: 'concentric',
        concentric: function(node) {
          return node.data('node_type') === 'Transaction' ? 2 : 1;
        },
        levelWidth: function() { return 1; },
        padding: 50
      }
    });

    cy.on('tap', 'node, edge', (evt) => {
      setSelectedElement(evt.target.data());
    });

    cy.on('tap', (evt) => {
      if (evt.target === cy) {
        setSelectedElement(null);
      }
    });

    cyRef.current = cy;

    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
      }
    };
  }, [graphData]);

  const handleZoomIn = () => cyRef.current && cyRef.current.zoom(cyRef.current.zoom() * 1.2);
  const handleZoomOut = () => cyRef.current && cyRef.current.zoom(cyRef.current.zoom() * 0.8);
  const handleFit = () => cyRef.current && cyRef.current.fit();

  return (
    <div className="relative w-full h-[650px] glass-panel rounded-2xl border border-slate-800 overflow-hidden">
      
      {/* Top Header */}
      <div className="absolute top-4 left-4 z-10 flex items-center space-x-3 bg-slate-900/80 px-4 py-2 rounded-xl border border-slate-800 backdrop-blur-md">
        <Network className="w-5 h-5 text-purple-400" />
        <div>
          <h3 className="text-sm font-bold text-white">Heterogeneous Network Graph</h3>
          <p className="text-[11px] font-mono text-slate-400">
            {graphData?.node_count || 0} Nodes | {graphData?.edge_count || 0} Edges
          </p>
        </div>
      </div>

      {/* Legend Overlay */}
      <div className="absolute bottom-4 left-4 z-10 flex flex-wrap gap-2 bg-slate-900/80 px-3 py-2 rounded-xl border border-slate-800 backdrop-blur-md text-xs font-mono">
        <div className="flex items-center space-x-1.5">
          <span className="w-3 h-3 rounded-full bg-cyan-400"></span>
          <span className="text-slate-300">IP</span>
        </div>
        <div className="flex items-center space-x-1.5">
          <span className="w-3 h-3 rotate-45 bg-purple-400"></span>
          <span className="text-slate-300">Transaction</span>
        </div>
        <div className="flex items-center space-x-1.5">
          <span className="w-3 h-3 rounded-sm bg-emerald-400"></span>
          <span className="text-slate-300">Address</span>
        </div>
        <div className="flex items-center space-x-1.5 pl-2 border-l border-slate-700">
          <span className="w-4 h-0.5 bg-rose-400"></span>
          <span className="text-rose-300">SPENDS Edge</span>
        </div>
      </div>

      {/* Control Buttons */}
      <div className="absolute top-4 right-4 z-10 flex flex-col space-y-1 bg-slate-900/80 p-1.5 rounded-xl border border-slate-800 backdrop-blur-md">
        <button onClick={handleZoomIn} className="p-2 text-slate-300 hover:text-white hover:bg-slate-800 rounded-lg transition" title="Zoom In">
          <ZoomIn className="w-4 h-4" />
        </button>
        <button onClick={handleZoomOut} className="p-2 text-slate-300 hover:text-white hover:bg-slate-800 rounded-lg transition" title="Zoom Out">
          <ZoomOut className="w-4 h-4" />
        </button>
        <button onClick={handleFit} className="p-2 text-slate-300 hover:text-white hover:bg-slate-800 rounded-lg transition" title="Fit Canvas">
          <Maximize2 className="w-4 h-4" />
        </button>
      </div>

      {/* Selected Node Inspector Side Drawer */}
      {selectedElement && (
        <div className="absolute bottom-4 right-4 z-10 w-72 p-4 glass-panel bg-slate-900/90 rounded-xl border border-slate-800 text-xs space-y-2">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <span className="font-bold text-cyan-400 flex items-center gap-1">
              <Info className="w-3.5 h-3.5" /> Element Details
            </span>
            <button onClick={() => setSelectedElement(null)} className="text-slate-400 hover:text-white">✕</button>
          </div>
          <pre className="font-mono text-[11px] text-slate-300 overflow-x-auto max-h-40">
            {JSON.stringify(selectedElement, null, 2)}
          </pre>
        </div>
      )}

      {/* Cytoscape Container */}
      <div ref={containerRef} className="w-full h-full" />
    </div>
  );
}
