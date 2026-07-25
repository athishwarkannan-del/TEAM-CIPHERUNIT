"use client";

import React, { useEffect, useState } from "react";
import {
  Briefcase,
  AlertTriangle,
  User,
  Clock,
  Shield,
} from "lucide-react";
import { fetchInvestigations } from "@/lib/api";
import type { InvestigationCase } from "@/lib/types";
import { cn, getRiskBg, getStatusColor } from "@/lib/utils";

// Mock evidence linked to cases
const caseEvidence: Record<string, { accounts: string[]; total_volume: string; alerts: number; timeline: { date: string; event: string }[] }> = {
  "CAS-2025-0045": {
    accounts: ["XXXX1001", "XXXX1002", "XXXX1003", "XXXX1004", "XXXX1005"],
    total_volume: "₹48.7L",
    alerts: 8,
    timeline: [
      { date: "Jul 24, 2025 14:32", event: "Alert ALT-2025-0001 triggered — Mule chain detected" },
      { date: "Jul 24, 2025 13:15", event: "Account XXXX1002 flagged as Fan-In collector" },
      { date: "Jul 23, 2025 22:40", event: "Velocity spike on XXXX1009 — 18 txns in 1 hour" },
      { date: "Jul 23, 2025 18:05", event: "Case opened by INV-882" },
    ],
  },
  "CAS-2025-0046": {
    accounts: ["XXXX1002", "XXXX1009", "XXXX1010", "XXXX1011"],
    total_volume: "₹25.8L",
    alerts: 5,
    timeline: [
      { date: "Jul 24, 2025 11:20", event: "Fan-In collector pattern confirmed" },
      { date: "Jul 23, 2025 16:45", event: "Case assigned to INV-445" },
    ],
  },
};

export default function InvestigationsPage() {
  const [cases, setCases] = useState<InvestigationCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCase, setSelectedCase] = useState<string | null>(null);

  useEffect(() => {
    fetchInvestigations()
      .then((res) => {
        if (res.data) setCases(res.data.cases);
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="space-y-5 animate-fade-in">
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(4)].map((_, i) => <div key={i} className="skeleton h-[180px] rounded-xl" />)}
        </div>
      </div>
    );
  }

  const activeCase = selectedCase ? cases.find((c) => c.case_number === selectedCase) : null;
  const evidence = selectedCase ? caseEvidence[selectedCase] : null;

  return (
    <div className="space-y-5 animate-fade-in">
      <div className="page-header">
        <p className="page-subtitle">
          Active investigation cases, evidence boards, and linked alert timelines
        </p>
      </div>

      {/* Case Cards Grid */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3 animate-stagger">
        {cases.map((c) => (
          <div
            key={c.case_number}
            onClick={() => setSelectedCase(c.case_number)}
            className={cn(
              "glass-card-hover cursor-pointer p-5",
              selectedCase === c.case_number && "ring-1 ring-accent/40"
            )}
          >
            <div className="flex items-start justify-between">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent/15 text-accent">
                <Briefcase className="h-5 w-5" />
              </div>
              <span className={cn("badge", getRiskBg(c.priority))}>{c.priority}</span>
            </div>
            <div className="mt-3">
              <p className="font-mono text-xs text-accent-glow">{c.case_number}</p>
              <p className="mt-1 text-sm font-semibold text-white">{c.title}</p>
            </div>
            <div className="mt-3 flex items-center gap-4 text-xs text-slate-400">
              <span className={cn("badge", getStatusColor(c.case_status))}>{c.case_status.replace(/_/g, " ")}</span>
              <span className="flex items-center gap-1">
                <User className="h-3 w-3" />
                {c.assigned_investigator_id}
              </span>
              <span className="flex items-center gap-1">
                <AlertTriangle className="h-3 w-3" />
                {c.alerts_count} alerts
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Case Detail / Evidence Board */}
      {activeCase && (
        <div className="grid grid-cols-1 gap-5 lg:grid-cols-2 animate-slide-up">
          {/* Case Overview */}
          <div className="glass-card p-5">
            <h3 className="mb-4 text-sm font-semibold text-white flex items-center gap-2">
              <Shield className="h-4 w-4 text-accent-glow" />
              Case Overview
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Case Number</span>
                <span className="font-mono text-accent-glow">{activeCase.case_number}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Title</span>
                <span className="text-white text-right max-w-[250px]">{activeCase.title}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Priority</span>
                <span className={cn("badge", getRiskBg(activeCase.priority))}>{activeCase.priority}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Status</span>
                <span className={cn("badge", getStatusColor(activeCase.case_status))}>{activeCase.case_status.replace(/_/g, " ")}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Assigned</span>
                <span className="text-white">{activeCase.assigned_investigator_id}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Linked Alerts</span>
                <span className="text-white font-semibold">{activeCase.alerts_count}</span>
              </div>
              {evidence && (
                <>
                  <div className="border-t border-navy-600 pt-3 flex justify-between text-sm">
                    <span className="text-slate-400">Combined Volume</span>
                    <span className="text-lg font-bold text-white">{evidence.total_volume}</span>
                  </div>
                  <div>
                    <span className="text-xs text-slate-400 mb-2 block">Linked Accounts</span>
                    <div className="flex flex-wrap gap-1.5">
                      {evidence.accounts.map((acc) => (
                        <span key={acc} className="badge bg-navy-700 border-navy-600 text-slate-300 font-mono">{acc}</span>
                      ))}
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Evidence Timeline */}
          <div className="glass-card p-5">
            <h3 className="mb-4 text-sm font-semibold text-white flex items-center gap-2">
              <Clock className="h-4 w-4 text-accent-glow" />
              Evidence Timeline
            </h3>
            {evidence?.timeline ? (
              <div className="relative space-y-0">
                <div className="absolute left-[7px] top-2 bottom-2 w-px bg-navy-600" />
                {evidence.timeline.map((event, i) => (
                  <div key={i} className="relative flex gap-4 pb-5">
                    <div className="relative z-10 mt-1.5 h-[15px] w-[15px] shrink-0 rounded-full border-2 border-accent bg-navy-900" />
                    <div>
                      <p className="text-xs text-slate-500">{event.date}</p>
                      <p className="mt-0.5 text-sm text-slate-300">{event.event}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-slate-500">Select a case to view its evidence timeline.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
