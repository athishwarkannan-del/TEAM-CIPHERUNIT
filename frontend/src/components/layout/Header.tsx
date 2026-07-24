"use client";

import React from "react";
import { usePathname } from "next/navigation";
import { Bell, Search, Activity } from "lucide-react";

const pageTitles: Record<string, string> = {
  "/dashboard": "Executive SOC Dashboard",
  "/transactions": "Transaction Intelligence Ledger",
  "/graph": "Graph Intelligence Workspace",
  "/geo": "Geospatial Intelligence Map",
  "/alerts": "Suspicious Alert Triage Queue",
  "/investigations": "Investigation Case Workspace",
  "/reports": "Regulatory Compliance Reports",
};

export default function Header() {
  const pathname = usePathname();
  const title = pageTitles[pathname] || "MuleTrace AI";

  return (
    <header className="sticky top-0 z-20 flex h-14 items-center justify-between border-b border-navy-600/50 bg-navy-950/80 px-6"
      style={{ backdropFilter: "blur(16px)" }}
    >
      {/* Left: Page title */}
      <div className="flex items-center gap-3">
        <h2 className="font-display text-base font-semibold text-white">{title}</h2>
      </div>

      {/* Right: Status & Actions */}
      <div className="flex items-center gap-4">
        {/* System Status */}
        <div className="hidden md:flex items-center gap-2 rounded-full border border-navy-600/50 bg-navy-800/60 px-3 py-1.5">
          <span className="pulse-dot" />
          <span className="text-xs font-medium text-emerald-400">System Operational</span>
        </div>

        {/* Search */}
        <button className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 transition-colors hover:bg-navy-700/50 hover:text-white">
          <Search className="h-4 w-4" />
        </button>

        {/* Alerts Bell */}
        <button className="relative flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 transition-colors hover:bg-navy-700/50 hover:text-white">
          <Bell className="h-4 w-4" />
          <span className="absolute -right-0.5 -top-0.5 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[9px] font-bold text-white">
            23
          </span>
        </button>

        {/* Live Activity */}
        <div className="hidden lg:flex items-center gap-2 rounded-full border border-navy-600/50 bg-navy-800/60 px-3 py-1.5">
          <Activity className="h-3 w-3 text-accent-glow animate-pulse" />
          <span className="text-xs text-slate-400">
            <span className="font-semibold text-white">14,832</span> txns/24h
          </span>
        </div>

        {/* Avatar */}
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-accent/20 text-xs font-bold text-accent-glow ring-2 ring-accent/30">
          SP
        </div>
      </div>
    </header>
  );
}
