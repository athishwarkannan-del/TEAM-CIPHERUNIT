import { create } from 'zustand';
import type { GraphNode } from '@/lib/types';

export type TimelineRange = '1H' | '24H' | '7D' | '30D' | '90D' | 'ALL';

interface GraphState {
  selectedNode: GraphNode | null;
  hoveredNode: GraphNode | null;
  hoverPos: { x: number; y: number } | null;
  hopLevel: number;
  timelineRange: TimelineRange;
  filterRisk: string;
  filterType: string;
  filterMinAmount: number;
  filterBank: string;
  searchQuery: string;
  pinnedNodes: Set<string>;
  hiddenNodes: Set<string>;
  expandedCommunities: Set<string>;

  setSelectedNode: (node: GraphNode | null) => void;
  setHoveredNode: (node: GraphNode | null, pos?: { x: number; y: number } | null) => void;
  setHopLevel: (hop: number) => void;
  setTimelineRange: (range: TimelineRange) => void;
  setFilterRisk: (risk: string) => void;
  setFilterType: (type: string) => void;
  setFilterMinAmount: (amount: number) => void;
  setFilterBank: (bank: string) => void;
  setSearchQuery: (query: string) => void;
  togglePinNode: (id: string) => void;
  toggleHideNode: (id: string) => void;
  toggleCommunity: (id: string) => void;
  resetFilters: () => void;
}

export const useGraphStore = create<GraphState>((set) => ({
  selectedNode: null,
  hoveredNode: null,
  hoverPos: null,
  hopLevel: 3,
  timelineRange: 'ALL',
  filterRisk: 'ALL',
  filterType: 'ALL',
  filterMinAmount: 0,
  filterBank: 'ALL',
  searchQuery: '',
  pinnedNodes: new Set(),
  hiddenNodes: new Set(),
  expandedCommunities: new Set(['COMMUNITY-A12']),

  setSelectedNode: (node) => set({ selectedNode: node }),
  setHoveredNode: (node, pos = null) => set({ hoveredNode: node, hoverPos: pos }),
  setHopLevel: (hop) => set({ hopLevel: hop }),
  setTimelineRange: (range) => set({ timelineRange: range }),
  setFilterRisk: (risk) => set({ filterRisk: risk }),
  setFilterType: (type) => set({ filterType: type }),
  setFilterMinAmount: (amount) => set({ filterMinAmount: amount }),
  setFilterBank: (bank) => set({ filterBank: bank }),
  setSearchQuery: (query) => set({ searchQuery: query }),

  togglePinNode: (id) =>
    set((state) => {
      const next = new Set(state.pinnedNodes);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return { pinnedNodes: next };
    }),

  toggleHideNode: (id) =>
    set((state) => {
      const next = new Set(state.hiddenNodes);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return { hiddenNodes: next };
    }),

  toggleCommunity: (id) =>
    set((state) => {
      const next = new Set(state.expandedCommunities);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return { expandedCommunities: next };
    }),

  resetFilters: () =>
    set({
      selectedNode: null,
      hoveredNode: null,
      hoverPos: null,
      hopLevel: 3,
      timelineRange: 'ALL',
      filterRisk: 'ALL',
      filterType: 'ALL',
      filterMinAmount: 0,
      filterBank: 'ALL',
      searchQuery: '',
      pinnedNodes: new Set(),
      hiddenNodes: new Set(),
    }),
}));
