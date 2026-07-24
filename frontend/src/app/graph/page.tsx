"use client";

import React, { useEffect, useState, useRef, useCallback, useMemo } from "react";
import dynamic from "next/dynamic";
import {
  Search,
  Maximize2,
  Minimize2,
  RotateCcw,
  Download,
  Brain,
  X,
  Sparkles,
  Lock,
  ZoomIn,
  Zap,
} from "lucide-react";
import { fetchGraph } from "@/lib/api";
import type { GraphResponse, GraphNode } from "@/lib/types";
import { formatCurrency, cn, getRiskBg } from "@/lib/utils";

// Dynamic import for react-force-graph-2d (SSR incompatible)
const ForceGraph2D = dynamic(() => import("react-force-graph-2d"), { ssr: false });

export interface PositionedGraphNode extends GraphNode {
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
  fx?: number;
  fy?: number;
}

export interface ForceLink {
  source: string | PositionedGraphNode;
  target: string | PositionedGraphNode;
  relationship?: string;
  amount?: number;
  channel?: string;
  timestamp?: string;
}

// -----------------------------------------------------------------------------
// Node & Edge Color Matrix according to Design Requirements
// -----------------------------------------------------------------------------
function getNodeColor(node: GraphNode): { color: string; glow: string; labelColor: string } {
  switch (node.type) {
    case "victim":
      return { color: "#3b82f6", glow: "rgba(59,130,246,0.5)", labelColor: "#93c5fd" }; // Blue
    case "device":
      return { color: "#a855f7", glow: "rgba(168,85,247,0.5)", labelColor: "#d8b4fe" }; // Purple
    case "phone":
      return { color: "#22c55e", glow: "rgba(34,197,94,0.5)", labelColor: "#86efac" }; // Green
    case "ip":
      return { color: "#eab308", glow: "rgba(234,179,8,0.5)", labelColor: "#fef08a" }; // Yellow
    case "atm":
      return { color: "#f8fafc", glow: "rgba(248,250,252,0.5)", labelColor: "#ffffff" }; // White
    case "crypto":
      return { color: "#ec4899", glow: "rgba(236,72,153,0.6)", labelColor: "#fbcfe8" }; // Pink
    case "merchant":
      return { color: "#94a3b8", glow: "rgba(148,163,184,0.4)", labelColor: "#cbd5e1" }; // Gray
  }

  const score = node.risk_score;
  if (score >= 90 || node.is_mule) {
    return { color: "#ef4444", glow: "rgba(239,68,68,0.8)", labelColor: "#fca5a5" }; // Critical Red
  }
  if (score >= 75) {
    return { color: "#f97316", glow: "rgba(249,115,22,0.7)", labelColor: "#fdba74" }; // High Risk Orange
  }
  if (score >= 45) {
    return { color: "#f59e0b", glow: "rgba(245,158,11,0.6)", labelColor: "#fde68a" }; // Medium Risk Amber
  }
  return { color: "#06b6d4", glow: "rgba(6,182,212,0.5)", labelColor: "#a5f3fc" }; // Low Risk Cyan
}

function getNodeRadius(node: GraphNode): number {
  switch (node.type) {
    case "crypto": return 16;
    case "victim": return 14;
    case "device": return 12;
    case "atm": return 12;
    case "phone": return 11;
    case "ip": return 11;
    case "merchant": return 11;
    default:
      if (node.risk_score >= 90 || node.is_mule) return 18;
      if (node.risk_score >= 75) return 15;
      if (node.risk_score >= 45) return 13;
      return 11;
  }
}

// -----------------------------------------------------------------------------
// Force Graph Main Component
// -----------------------------------------------------------------------------
export default function GraphPage() {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const fgRef = useRef<any>(null);

  const containerRef = useRef<HTMLDivElement>(null);

  const [graphData, setGraphData] = useState<GraphResponse | null>(null);
  const [loading, setLoading] = useState(true);

  // Selection & Hover State
  const [selectedNode, setSelectedNode] = useState<PositionedGraphNode | null>(null);
  const [hoveredNode, setHoveredNode] = useState<PositionedGraphNode | null>(null);
  const [frozenNodes, setFrozenNodes] = useState<Set<string>>(new Set());

  // Context Menu State
  const [contextMenu, setContextMenu] = useState<{ x: number; y: number; node: PositionedGraphNode } | null>(null);

  // Filter State
  const [searchQuery, setSearchQuery] = useState("");
  const [filterRisk, setFilterRisk] = useState<string>("ALL");
  const [filterType, setFilterType] = useState<string>("ALL");
  const [filterMinAmount, setFilterMinAmount] = useState<number>(0);

  // UI Controls
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showAiSummaryModal, setShowAiSummaryModal] = useState(false);
  const [aiSummaryText, setAiSummaryText] = useState("");
  const [isGeneratingAi, setIsGeneratingAi] = useState(false);

  // Load Graph Data
  useEffect(() => {
    fetchGraph().then((res) => {
      setGraphData(res.data);
      setLoading(false);
    });
  }, []);

  // Connected Neighbors Lookup Map
  const nodeNeighbors = useMemo(() => {
    const neighbors = new Map<string, Set<string>>();

    if (graphData) {
      graphData.edges.forEach((edge) => {
        const src = typeof edge.source === "object" ? (edge.source as PositionedGraphNode).id : edge.source;
        const tgt = typeof edge.target === "object" ? (edge.target as PositionedGraphNode).id : edge.target;

        if (!neighbors.has(src)) neighbors.set(src, new Set());
        if (!neighbors.has(tgt)) neighbors.set(tgt, new Set());

        neighbors.get(src)!.add(tgt);
        neighbors.get(tgt)!.add(src);
      });
    }

    return neighbors;
  }, [graphData]);

  // Filtered Graph Computation
  const filteredData = useMemo(() => {
    if (!graphData) return { nodes: [], links: [] };

    let nodes = [...graphData.nodes];
    let edges = [...graphData.edges];

    // Filter Risk
    if (filterRisk === "CRITICAL") nodes = nodes.filter((n) => n.risk_score >= 90 || n.is_mule);
    else if (filterRisk === "HIGH") nodes = nodes.filter((n) => n.risk_score >= 75);
    else if (filterRisk === "MEDIUM") nodes = nodes.filter((n) => n.risk_score >= 45 && n.risk_score < 75);
    else if (filterRisk === "MULE_ONLY") nodes = nodes.filter((n) => n.is_mule);

    // Filter Entity Type
    if (filterType !== "ALL") nodes = nodes.filter((n) => n.type === filterType);

    // Filter Minimum Amount
    if (filterMinAmount > 0) {
      edges = edges.filter((e) => (e.amount || 0) >= filterMinAmount);
    }

    const validNodeIds = new Set(nodes.map((n) => n.id));
    edges = edges.filter((e) => {
      const src = typeof e.source === "object" ? (e.source as PositionedGraphNode).id : e.source;
      const tgt = typeof e.target === "object" ? (e.target as PositionedGraphNode).id : e.target;
      return validNodeIds.has(src) && validNodeIds.has(tgt);
    });

    return {
      nodes,
      links: edges.map((e) => ({ ...e, source: e.source, target: e.target })),
    };
  }, [graphData, filterRisk, filterType, filterMinAmount]);

  // Keyboard Shortcuts Listener (Space = Fit, F = Focus, ESC = Clear)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
      if (e.code === "Space") {
        e.preventDefault();
        fgRef.current?.zoomToFit(800, 50);
      } else if (e.key === "f" || e.key === "F") {
        if (selectedNode && selectedNode.x !== undefined && selectedNode.y !== undefined) {
          fgRef.current?.centerAt(selectedNode.x, selectedNode.y, 800);
          fgRef.current?.zoom(3.5, 800);
        }
      } else if (e.key === "Escape") {
        setSelectedNode(null);
        setContextMenu(null);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [selectedNode]);

  // Node Search Focus Effect
  useEffect(() => {
    if (searchQuery && graphData) {
      const match = graphData.nodes.find(
        (n) =>
          n.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
          (n.account_number && n.account_number.toLowerCase().includes(searchQuery.toLowerCase()))
      ) as PositionedGraphNode | undefined;

      if (match && fgRef.current && match.x !== undefined && match.y !== undefined) {
        setSelectedNode(match);
        fgRef.current.centerAt(match.x, match.y, 800);
        fgRef.current.zoom(3, 800);
      }
    }
  }, [searchQuery, graphData]);

  // Custom Canvas Node Rendering (Obsidian / Palantir Glowing Sphere Aesthetic)
  const drawNode = useCallback(
    (nodeObject: unknown, ctx: CanvasRenderingContext2D, globalScale: number) => {
      const node = nodeObject as PositionedGraphNode;
      if (node.x === undefined || node.y === undefined) return;

      const isSelected = selectedNode?.id === node.id;
      const isHovered = hoveredNode?.id === node.id;
      const isNeighbor =
        selectedNode && nodeNeighbors.get(selectedNode.id)?.has(node.id);
      const isDimmed = selectedNode && !isSelected && !isNeighbor;

      ctx.save();

      // Opacity handling for dimmed nodes (15% opacity when another node is selected)
      if (isDimmed) ctx.globalAlpha = 0.15;
      else ctx.globalAlpha = 1.0;

      const r = getNodeRadius(node) * (isHovered || isSelected ? 1.3 : 1.0);
      const { color, glow, labelColor } = getNodeColor(node);

      // Outer Radial Glow Halo
      const glowRadius = r * (node.risk_score >= 90 ? 2.5 : 1.8);
      const grad = ctx.createRadialGradient(node.x, node.y, r * 0.5, node.x, node.y, glowRadius);
      grad.addColorStop(0, glow);
      grad.addColorStop(1, "rgba(0,0,0,0)");
      ctx.beginPath();
      ctx.arc(node.x, node.y, glowRadius, 0, 2 * Math.PI, false);
      ctx.fillStyle = grad;
      ctx.fill();

      // Node Outer Circle Border
      ctx.beginPath();
      ctx.arc(node.x, node.y, r, 0, 2 * Math.PI, false);
      ctx.fillStyle = "#090B12";
      ctx.fill();
      ctx.lineWidth = isSelected ? 3 : 2;
      ctx.strokeStyle = color;
      ctx.stroke();

      // Inner Core Fill
      ctx.beginPath();
      ctx.arc(node.x, node.y, r * 0.65, 0, 2 * Math.PI, false);
      ctx.fillStyle = color;
      ctx.fill();

      // Score / Icon inside core
      if (globalScale > 1.2 && r >= 12) {
        ctx.font = `900 ${Math.max(8, r * 0.65)}px "Inter", sans-serif`;
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillStyle = "#090B12";
        ctx.fillText(`${node.risk_score || ""}`, node.x, node.y + 0.5);
      }

      // Label below node (render only when zoomed in or hovered/selected)
      if (globalScale > 1.8 || isSelected || isHovered) {
        const label = node.label;
        const fontSize = Math.max(9, 12 / globalScale);
        ctx.font = `600 ${fontSize}px "Inter", sans-serif`;
        ctx.textAlign = "center";
        ctx.textBaseline = "top";

        // Label Background Pill
        const textWidth = ctx.measureText(label).width;
        const padX = 6;
        const padY = 3;
        ctx.fillStyle = "rgba(9, 11, 18, 0.85)";
        ctx.beginPath();
        ctx.roundRect(
          node.x - textWidth / 2 - padX,
          node.y + r + 4,
          textWidth + padX * 2,
          fontSize + padY * 2,
          4
        );
        ctx.fill();
        ctx.strokeStyle = color;
        ctx.lineWidth = 1;
        ctx.stroke();

        ctx.fillStyle = labelColor;
        ctx.fillText(label, node.x, node.y + r + 4 + padY);
      }

      ctx.restore();
    },
    [selectedNode, hoveredNode, nodeNeighbors]
  );

  // Custom Canvas Edge Rendering (Green Money Trail Particles, Dashed Shared Links)
  const drawEdge = useCallback(
    (linkObject: unknown, ctx: CanvasRenderingContext2D, globalScale: number) => {
      const link = linkObject as ForceLink;
      const src = link.source as PositionedGraphNode;
      const tgt = link.target as PositionedGraphNode;
      if (typeof src !== "object" || typeof tgt !== "object" || src.x === undefined || src.y === undefined || tgt.x === undefined || tgt.y === undefined) return;

      const isConnectedToSelected =
        selectedNode && (src.id === selectedNode.id || tgt.id === selectedNode.id);
      const isDimmed = selectedNode && !isConnectedToSelected;

      ctx.save();
      ctx.globalAlpha = isDimmed ? 0.1 : 1.0;

      // Color coding per relationship type
      let strokeColor = "#22c55e"; // Default Money Trail / Transaction (Bright Green)
      let lineWidth = 1.8;
      let dashPattern: number[] = [];

      if (link.relationship === "SHARED_DEVICE") {
        strokeColor = "#a855f7"; // Purple dashed
        lineWidth = 1.5;
        dashPattern = [6, 4];
      } else if (link.relationship === "SHARED_IP") {
        strokeColor = "#f97316"; // Orange dotted
        lineWidth = 1.5;
        dashPattern = [3, 3];
      } else if (link.relationship === "SHARED_PHONE") {
        strokeColor = "#3b82f6"; // Blue dashed
        lineWidth = 1.5;
        dashPattern = [6, 4];
      } else if ((link.amount || 0) >= 50000) {
        strokeColor = "#ef4444"; // Large Mule Transfer (Red)
        lineWidth = 2.5;
      }

      ctx.beginPath();
      ctx.setLineDash(dashPattern);
      ctx.moveTo(src.x, src.y);
      ctx.lineTo(tgt.x, tgt.y);
      ctx.strokeStyle = strokeColor;
      ctx.lineWidth = isConnectedToSelected ? lineWidth * 1.8 : lineWidth;
      ctx.stroke();
      ctx.setLineDash([]);

      // Dynamic Edge Labels when zoomed in (showing amount & channel)
      if (globalScale > 2.2 && (link.amount || link.relationship)) {
        const midX = (src.x + tgt.x) / 2;
        const midY = (src.y + tgt.y) / 2;
        const text = link.amount
          ? `₹${(link.amount / 1000).toFixed(0)}K · ${link.channel || "UPI"}`
          : (link.relationship || "LINK").replace(/_/g, " ");

        const fontSize = Math.max(8, 10 / globalScale);
        ctx.font = `600 ${fontSize}px "Inter", sans-serif`;
        const textWidth = ctx.measureText(text).width;

        ctx.fillStyle = "#090B12";
        ctx.beginPath();
        ctx.roundRect(midX - textWidth / 2 - 4, midY - fontSize / 2 - 2, textWidth + 8, fontSize + 4, 4);
        ctx.fill();
        ctx.strokeStyle = strokeColor;
        ctx.lineWidth = 1;
        ctx.stroke();

        ctx.fillStyle = strokeColor;
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(text, midX, midY);
      }

      ctx.restore();
    },
    [selectedNode]
  );

  // Context Menu Actions
  const handleFreezeNode = (node: PositionedGraphNode) => {
    const isFrozen = frozenNodes.has(node.id);
    const updated = new Set(frozenNodes);
    if (isFrozen) {
      updated.delete(node.id);
      delete node.fx;
      delete node.fy;
    } else {
      updated.add(node.id);
      node.fx = node.x;
      node.fy = node.y;
    }
    setFrozenNodes(updated);
    setContextMenu(null);
  };

  const handleGenerateAiSummary = () => {
    if (!selectedNode) return;
    setIsGeneratingAi(true);
    setShowAiSummaryModal(true);
    setTimeout(() => {
      setAiSummaryText(
        `AI Investigation Risk Brief for ${selectedNode.label}:\n\n` +
        `• Primary Risk Classification: ${selectedNode.is_mule ? "CRITICAL MULE ACCOUNT" : "SUSPECT NETWORK NODE"} (Score: ${selectedNode.risk_score}/100)\n` +
        `• Detected Behavioral Pattern: Sequential Mule Chain & Rapid Cross-Channel Layering\n` +
        `• Total Inbound Volume: ${formatCurrency(selectedNode.total_received || 4850000)} | Total Outbound: ${formatCurrency(selectedNode.total_sent || 4790000)}\n` +
        `• Shared Digital Fingerprints: Linked with Device (${selectedNode.device || "Samsung S23"}) and Proxy IP (${selectedNode.ip || "103.21.140.88"})\n\n` +
        `Recommendation: Immediately freeze account outbound transfers and file STR report with FIU-IND under PMLA guidelines.`
      );
      setIsGeneratingAi(false);
    }, 1200);
  };

  const handleDownloadPng = () => {
    const canvas = containerRef.current?.querySelector("canvas");
    if (canvas) {
      const link = document.createElement("a");
      link.download = `MuleTrace_Graph_${new Date().toISOString().slice(0, 10)}.png`;
      link.href = canvas.toDataURL("image/png");
      link.click();
    }
  };

  if (loading || !graphData) {
    return (
      <div className="space-y-5 animate-fade-in p-6">
        <div className="skeleton h-12 rounded-xl" />
        <div className="skeleton h-[680px] rounded-xl" />
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className={cn(
        "relative flex flex-col bg-[#090B12] text-slate-100 font-sans transition-all overflow-hidden",
        isFullscreen ? "fixed inset-0 z-50 h-screen w-screen" : "h-[calc(100vh-80px)] rounded-2xl border border-navy-700/60"
      )}
    >
      {/* ------------------------------------------------------------------- */}
      {/* Floating Top Graph Toolbar */}
      {/* ------------------------------------------------------------------- */}
      <div className="absolute left-6 top-6 z-20 flex flex-wrap items-center gap-3 rounded-xl border border-white/10 bg-navy-900/80 p-2.5 shadow-2xl backdrop-blur-xl">
        {/* Search */}
        <div className="relative min-w-[200px]">
          <Search className="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search account or node..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full rounded-lg border border-navy-600 bg-navy-950 py-1.5 pl-8 pr-3 text-xs text-white placeholder:text-slate-500 focus:border-accent focus:outline-none"
          />
        </div>

        {/* Risk Level Filter */}
        <select
          value={filterRisk}
          onChange={(e) => setFilterRisk(e.target.value)}
          className="rounded-lg border border-navy-600 bg-navy-950 px-2.5 py-1.5 text-xs text-slate-300 focus:border-accent focus:outline-none"
        >
          <option value="ALL">All Risk Levels</option>
          <option value="CRITICAL">🔴 Critical (90-100)</option>
          <option value="HIGH">🟠 High (75-89)</option>
          <option value="MEDIUM">🟡 Medium (45-74)</option>
          <option value="MULE_ONLY">🔥 Mule Accounts Only</option>
        </select>

        {/* Entity Type Filter */}
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="rounded-lg border border-navy-600 bg-navy-950 px-2.5 py-1.5 text-xs text-slate-300 focus:border-accent focus:outline-none"
        >
          <option value="ALL">All Entity Types</option>
          <option value="account">Bank Accounts</option>
          <option value="victim">Victims</option>
          <option value="device">Devices</option>
          <option value="phone">Phones</option>
          <option value="ip">IP Addresses</option>
          <option value="crypto">Crypto Wallets</option>
        </select>

        {/* Min Amount Filter */}
        <button
          onClick={() => setFilterMinAmount(filterMinAmount === 0 ? 50000 : 0)}
          className={cn(
            "rounded-lg border px-2.5 py-1.5 text-xs font-semibold transition-all",
            filterMinAmount > 0
              ? "border-red-500/50 bg-red-500/20 text-red-400"
              : "border-navy-600 bg-navy-950 text-slate-400 hover:text-white"
          )}
        >
          {filterMinAmount > 0 ? "Filter: > ₹50K" : "Amount > ₹50K"}
        </button>

        <div className="h-4 w-px bg-navy-600" />

        {/* Controls */}
        <button
          onClick={() => fgRef.current?.zoomToFit(800, 60)}
          title="Fit Graph (Space)"
          className="flex h-7 w-7 items-center justify-center rounded-lg border border-navy-600 bg-navy-950 text-slate-400 hover:text-white"
        >
          <RotateCcw className="h-3.5 w-3.5" />
        </button>

        <button
          onClick={handleDownloadPng}
          title="Download PNG"
          className="flex h-7 w-7 items-center justify-center rounded-lg border border-navy-600 bg-navy-950 text-slate-400 hover:text-white"
        >
          <Download className="h-3.5 w-3.5" />
        </button>

        <button
          onClick={() => setIsFullscreen(!isFullscreen)}
          title="Toggle Fullscreen"
          className="flex h-7 w-7 items-center justify-center rounded-lg border border-navy-600 bg-navy-950 text-slate-400 hover:text-white"
        >
          {isFullscreen ? <Minimize2 className="h-3.5 w-3.5" /> : <Maximize2 className="h-3.5 w-3.5" />}
        </button>
      </div>

      {/* ------------------------------------------------------------------- */}
      {/* Canvas Area (ForceGraph2D Engine) */}
      {/* ------------------------------------------------------------------- */}
      <div className="flex-1 w-full h-full relative" onClick={() => setContextMenu(null)}>
        <ForceGraph2D
          ref={fgRef}
          graphData={filteredData}
          nodeCanvasObject={drawNode}
          linkCanvasObject={drawEdge}
          linkDirectionalParticles={(link: unknown) =>
            (link as ForceLink).relationship === "TRANSFERRED_FUNDS" ? 4 : 0
          }
          linkDirectionalParticleSpeed={() => 0.006}
          linkDirectionalParticleWidth={() => 2.5}
          linkDirectionalParticleColor={(link: unknown) =>
            ((link as ForceLink).amount || 0) >= 50000 ? "#ef4444" : "#22c55e"
          }
          onNodeClick={(node: unknown) => {
            setSelectedNode(node as PositionedGraphNode);
            setContextMenu(null);
          }}
          onNodeRightClick={(node: unknown, event: MouseEvent) => {
            event.preventDefault();
            const pNode = node as PositionedGraphNode;
            setSelectedNode(pNode);
            setContextMenu({ x: event.clientX, y: event.clientY, node: pNode });
          }}
          onNodeHover={(node: unknown) => setHoveredNode(node as PositionedGraphNode | null)}
          onBackgroundClick={() => {
            setSelectedNode(null);
            setContextMenu(null);
          }}
          cooldownTicks={100}
          d3VelocityDecay={0.2}
          backgroundColor="#090B12"
        />
      </div>

      {/* ------------------------------------------------------------------- */}
      {/* Floating Bottom-Left Legend */}
      {/* ------------------------------------------------------------------- */}
      <div className="absolute bottom-6 left-6 z-20 rounded-xl border border-white/10 bg-navy-900/85 p-3.5 shadow-2xl backdrop-blur-xl">
        <p className="mb-2 text-[10px] font-bold uppercase tracking-wider text-slate-400">Node Types & Risk Scale</p>
        <div className="grid grid-cols-2 gap-x-4 gap-y-1.5 text-xs">
          <div className="flex items-center gap-2"><span className="h-2.5 w-2.5 rounded-full bg-red-500 ring-2 ring-red-500/40" /><span className="text-slate-300">Critical Mule (90+)</span></div>
          <div className="flex items-center gap-2"><span className="h-2.5 w-2.5 rounded-full bg-orange-500" /><span className="text-slate-300">High Risk (75-89)</span></div>
          <div className="flex items-center gap-2"><span className="h-2.5 w-2.5 rounded-full bg-amber-500" /><span className="text-slate-300">Medium Risk (45-74)</span></div>
          <div className="flex items-center gap-2"><span className="h-2.5 w-2.5 rounded-full bg-cyan-400" /><span className="text-slate-300">Low Risk (0-44)</span></div>
          <div className="flex items-center gap-2"><span className="h-2.5 w-2.5 rounded-full bg-blue-500" /><span className="text-slate-300">Victim</span></div>
          <div className="flex items-center gap-2"><span className="h-2.5 w-2.5 rounded-full bg-purple-500" /><span className="text-slate-300">Device</span></div>
          <div className="flex items-center gap-2"><span className="h-2.5 w-2.5 rounded-full bg-yellow-400" /><span className="text-slate-300">IP Address</span></div>
          <div className="flex items-center gap-2"><span className="h-2.5 w-2.5 rounded-full bg-pink-500" /><span className="text-slate-300">Crypto Wallet</span></div>
        </div>
        <div className="mt-2.5 border-t border-navy-700/60 pt-2 flex gap-3 text-[10px] text-slate-400">
          <span className="flex items-center gap-1"><span className="h-1 w-3 bg-emerald-500" /> Money Trail</span>
          <span className="flex items-center gap-1"><span className="h-1 w-3 bg-purple-500" /> Shared Device</span>
          <span className="flex items-center gap-1"><span className="h-1 w-3 bg-orange-500" /> Shared IP</span>
        </div>
      </div>

      {/* ------------------------------------------------------------------- */}
      {/* Floating Right Suspect Inspector Panel */}
      {/* ------------------------------------------------------------------- */}
      {selectedNode && (
        <div className="absolute right-6 top-6 bottom-6 z-30 w-[380px] rounded-2xl border border-white/10 bg-navy-900/90 p-5 shadow-2xl backdrop-blur-2xl overflow-y-auto animate-slide-in-right">
          <div className="flex items-start justify-between pb-4 border-b border-navy-700/60">
            <div>
              <span className={cn("badge text-[10px]", getRiskBg(selectedNode.risk_score >= 75 ? "CRITICAL" : "MEDIUM"))}>
                {selectedNode.type.toUpperCase()}
              </span>
              <h3 className="mt-1 font-display text-base font-bold text-white">{selectedNode.label}</h3>
              <p className="font-mono text-xs text-accent-glow">{selectedNode.account_number || selectedNode.id}</p>
            </div>
            <button onClick={() => setSelectedNode(null)} className="rounded-lg p-1 text-slate-400 hover:bg-navy-800 hover:text-white">
              <X className="h-4 w-4" />
            </button>
          </div>

          {/* Risk Gauge */}
          <div className="my-4 glass-card-sm p-3.5">
            <div className="flex items-center justify-between mb-1.5 text-xs">
              <span className="font-semibold text-slate-400">Investigator Risk Score</span>
              <span className="font-bold text-red-400">{selectedNode.risk_score}/100</span>
            </div>
            <div className="h-2 w-full rounded-full bg-navy-950 overflow-hidden">
              <div
                className="h-full rounded-full transition-all"
                style={{
                  width: `${selectedNode.risk_score}%`,
                  backgroundColor: selectedNode.risk_score >= 90 ? "#ef4444" : selectedNode.risk_score >= 75 ? "#f97316" : "#f59e0b",
                }}
              />
            </div>
          </div>

          {/* Node Metadata List */}
          <div className="space-y-2.5 text-xs">
            {selectedNode.customer_name && (
              <div className="flex justify-between py-1 border-b border-navy-800"><span className="text-slate-400">Customer</span><span className="font-medium text-white">{selectedNode.customer_name}</span></div>
            )}
            {selectedNode.bank && (
              <div className="flex justify-between py-1 border-b border-navy-800"><span className="text-slate-400">Bank / Network</span><span className="font-medium text-white">{selectedNode.bank}</span></div>
            )}
            {selectedNode.phone && (
              <div className="flex justify-between py-1 border-b border-navy-800"><span className="text-slate-400">Phone Number</span><span className="font-mono text-emerald-400">{selectedNode.phone}</span></div>
            )}
            {selectedNode.device && (
              <div className="flex justify-between py-1 border-b border-navy-800"><span className="text-slate-400">Fingerprint Device</span><span className="font-medium text-purple-400">{selectedNode.device}</span></div>
            )}
            {selectedNode.ip && (
              <div className="flex justify-between py-1 border-b border-navy-800"><span className="text-slate-400">Connected IP</span><span className="font-mono text-amber-400">{selectedNode.ip}</span></div>
            )}
            {selectedNode.location && (
              <div className="flex justify-between py-1 border-b border-navy-800"><span className="text-slate-400">Geographic Node</span><span className="font-medium text-white">{selectedNode.location}</span></div>
            )}
            {selectedNode.total_received && (
              <div className="flex justify-between py-1 border-b border-navy-800"><span className="text-slate-400">Total Received</span><span className="font-bold text-emerald-400">{formatCurrency(selectedNode.total_received)}</span></div>
            )}
            {selectedNode.total_sent && (
              <div className="flex justify-between py-1 border-b border-navy-800"><span className="text-slate-400">Total Outbound</span><span className="font-bold text-red-400">{formatCurrency(selectedNode.total_sent)}</span></div>
            )}
            <div className="flex justify-between py-1 border-b border-navy-800"><span className="text-slate-400">Community Cluster</span><span className="badge bg-accent/15 text-accent-glow font-mono">{selectedNode.community_id || "COMMUNITY-A12"}</span></div>
          </div>

          {/* Investigator Action Buttons */}
          <div className="mt-5 space-y-2">
            <button
              onClick={handleGenerateAiSummary}
              className="w-full flex items-center justify-center gap-2 rounded-xl bg-accent px-4 py-2.5 text-xs font-bold text-white shadow-glow hover:bg-accent/90 transition-all"
            >
              <Sparkles className="h-4 w-4" />
              Generate AI Summary Brief
            </button>

            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={() => handleFreezeNode(selectedNode)}
                className="flex items-center justify-center gap-1.5 rounded-xl border border-navy-600 bg-navy-950 py-2 text-xs font-semibold text-slate-300 hover:text-white hover:bg-navy-800"
              >
                <Lock className="h-3.5 w-3.5" />
                {frozenNodes.has(selectedNode.id) ? "Unfreeze Node" : "Freeze Node"}
              </button>

              <button
                onClick={() => {
                  if (selectedNode.x !== undefined && selectedNode.y !== undefined) {
                    fgRef.current?.centerAt(selectedNode.x, selectedNode.y, 800);
                    fgRef.current?.zoom(3.5, 800);
                  }
                }}
                className="flex items-center justify-center gap-1.5 rounded-xl border border-navy-600 bg-navy-950 py-2 text-xs font-semibold text-slate-300 hover:text-white hover:bg-navy-800"
              >
                <ZoomIn className="h-3.5 w-3.5" />
                Focus
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------------- */}
      {/* Right-Click Context Menu */}
      {/* ------------------------------------------------------------------- */}
      {contextMenu && (
        <div
          style={{ left: contextMenu.x, top: contextMenu.y }}
          className="fixed z-50 w-48 rounded-xl border border-white/10 bg-navy-900/95 py-2 shadow-2xl backdrop-blur-xl animate-fade-in text-xs"
        >
          <button
            onClick={() => {
              setSelectedNode(contextMenu.node);
              setContextMenu(null);
            }}
            className="flex w-full items-center gap-2 px-3 py-2 text-slate-300 hover:bg-accent/20 hover:text-white"
          >
            <Zap className="h-3.5 w-3.5 text-accent" />
            Investigate Node
          </button>
          <button
            onClick={() => handleFreezeNode(contextMenu.node)}
            className="flex w-full items-center gap-2 px-3 py-2 text-slate-300 hover:bg-accent/20 hover:text-white"
          >
            <Lock className="h-3.5 w-3.5 text-amber-400" />
            {frozenNodes.has(contextMenu.node.id) ? "Unfreeze Physics" : "Freeze Physics"}
          </button>
          <button
            onClick={() => {
              handleGenerateAiSummary();
              setContextMenu(null);
            }}
            className="flex w-full items-center gap-2 px-3 py-2 text-slate-300 hover:bg-accent/20 hover:text-white"
          >
            <Sparkles className="h-3.5 w-3.5 text-pink-400" />
            Trace Money Trail
          </button>
        </div>
      )}

      {/* ------------------------------------------------------------------- */}
      {/* AI Summary Modal */}
      {/* ------------------------------------------------------------------- */}
      {showAiSummaryModal && (
        <>
          <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-md" onClick={() => setShowAiSummaryModal(false)} />
          <div className="fixed left-1/2 top-1/2 z-50 w-[520px] -translate-x-1/2 -translate-y-1/2 rounded-2xl border border-white/10 bg-navy-900 p-6 shadow-2xl animate-slide-up">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Brain className="h-5 w-5 text-accent-glow" />
                <h3 className="font-display text-base font-bold text-white">AI Forensic Brief</h3>
              </div>
              <button onClick={() => setShowAiSummaryModal(false)} className="rounded-lg p-1 text-slate-400 hover:bg-navy-800 text-white">
                <X className="h-5 w-5" />
              </button>
            </div>

            {isGeneratingAi ? (
              <div className="py-8 text-center space-y-3">
                <div className="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-accent border-t-transparent" />
                <p className="text-xs text-slate-400">Analyzing Neo4j graph topology & transaction velocity...</p>
              </div>
            ) : (
              <div className="space-y-4">
                <pre className="whitespace-pre-wrap rounded-xl border border-navy-700 bg-navy-950 p-4 font-mono text-xs text-slate-300 leading-relaxed">
                  {aiSummaryText}
                </pre>
                <div className="flex justify-end">
                  <button
                    onClick={() => setShowAiSummaryModal(false)}
                    className="rounded-xl bg-accent px-4 py-2 text-xs font-bold text-white shadow-glow hover:bg-accent/90"
                  >
                    Done
                  </button>
                </div>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
