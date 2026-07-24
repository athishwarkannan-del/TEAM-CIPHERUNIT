"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  ArrowLeftRight,
  Network,
  MapPin,
  ShieldAlert,
  Search as SearchIcon,
  FileText,
  ChevronLeft,
  ChevronRight,
  Shield,
  Fingerprint,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/transactions", label: "Transactions", icon: ArrowLeftRight },
  { href: "/graph", label: "Graph Intelligence", icon: Network },
  { href: "/geo", label: "Geo Intelligence", icon: MapPin },
  { href: "/alerts", label: "Alert Triage", icon: ShieldAlert },
  { href: "/investigations", label: "Investigations", icon: SearchIcon },
  { href: "/reports", label: "Reports", icon: FileText },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={cn(
        "fixed left-0 top-0 z-30 flex h-screen flex-col border-r border-navy-600/50 bg-navy-900/95 transition-all duration-300",
        collapsed ? "w-[68px]" : "w-[260px]"
      )}
      style={{ backdropFilter: "blur(20px)" }}
    >
      {/* Brand */}
      <div className="flex h-16 items-center gap-3 border-b border-navy-600/50 px-4">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-accent/15 text-accent">
          <Shield className="h-5 w-5" />
        </div>
        {!collapsed && (
          <div className="animate-fade-in overflow-hidden">
            <h1 className="font-display text-base font-bold text-white tracking-tight">
              MuleTrace
              <span className="ml-1 text-accent-glow">AI</span>
            </h1>
            <p className="text-[10px] font-medium uppercase tracking-widest text-slate-500">
              Financial Crime Intel
            </p>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-3 py-4">
        <div className="space-y-1">
          {navItems.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "group relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200",
                  isActive
                    ? "bg-accent/10 text-white"
                    : "text-slate-400 hover:bg-navy-700/50 hover:text-white"
                )}
              >
                {/* Active indicator glow bar */}
                {isActive && (
                  <div className="absolute left-0 top-1/2 h-6 w-[3px] -translate-y-1/2 rounded-r-full bg-accent shadow-glow" />
                )}
                <Icon
                  className={cn(
                    "h-[18px] w-[18px] shrink-0 transition-colors",
                    isActive ? "text-accent-glow" : "text-slate-500 group-hover:text-slate-300"
                  )}
                />
                {!collapsed && (
                  <span className="truncate">{item.label}</span>
                )}
              </Link>
            );
          })}
        </div>
      </nav>

      {/* System Status */}
      {!collapsed && (
        <div className="border-t border-navy-600/50 p-4 animate-fade-in">
          <div className="glass-card-sm flex items-center gap-3 p-3">
            <Fingerprint className="h-4 w-4 text-accent-glow" />
            <div className="min-w-0">
              <p className="text-xs font-medium text-slate-300">ML Engine</p>
              <p className="text-[10px] text-emerald-400 flex items-center gap-1">
                <span className="pulse-dot" />
                <span className="ml-2">Active — v2.1.3</span>
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Collapse Toggle */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="flex h-10 items-center justify-center border-t border-navy-600/50 text-slate-500 transition-colors hover:bg-navy-700/50 hover:text-white"
      >
        {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
      </button>
    </aside>
  );
}
