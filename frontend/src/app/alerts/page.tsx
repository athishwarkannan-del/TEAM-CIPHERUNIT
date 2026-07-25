"use client";

import React, { useEffect, useState } from "react";
import { Filter, X, CheckCircle, AlertTriangle, Clock, ArrowUpCircle } from "lucide-react";
import { fetchAlerts, triageAlert } from "@/lib/api";
import type { AlertRead, PaginationMeta } from "@/lib/types";
import { formatTimeAgo, cn, getRiskBg, getStatusColor } from "@/lib/utils";

// -----------------------------------------------------------------------------
// Triage Modal
// -----------------------------------------------------------------------------
function TriageModal({
  alert,
  onClose,
  onTriage,
}: {
  alert: AlertRead;
  onClose: () => void;
  onTriage: (id: string, status: string, notes: string) => void;
}) {
  const [status, setStatus] = useState(alert.alert_status);
  const [notes, setNotes] = useState("");

  const statuses = [
    { value: "UNDER_INVESTIGATION", label: "Under Investigation", icon: Clock, color: "text-amber-400" },
    { value: "ESCALATED", label: "Escalated", icon: ArrowUpCircle, color: "text-red-400" },
    { value: "CLOSED_FALSE_POSITIVE", label: "Closed — False Positive", icon: X, color: "text-slate-400" },
    { value: "CLOSED_CONFIRMED", label: "Closed — Confirmed", icon: CheckCircle, color: "text-emerald-400" },
  ];

  return (
    <>
      <div className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <div className="fixed left-1/2 top-1/2 z-50 w-[520px] -translate-x-1/2 -translate-y-1/2 animate-slide-up">
        <div className="glass-card p-6">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h3 className="font-display text-lg font-bold text-white">Triage Alert</h3>
              <p className="mt-0.5 font-mono text-xs text-accent-glow">{alert.alert_number}</p>
            </div>
            <button onClick={onClose} className="rounded-lg p-1.5 text-slate-400 hover:bg-navy-700 hover:text-white">
              <X className="h-5 w-5" />
            </button>
          </div>

          <div className="glass-card-sm p-3 mb-4">
            <p className="text-sm text-white font-medium">{alert.title}</p>
            {alert.description && <p className="mt-1 text-xs text-slate-400">{alert.description}</p>}
          </div>

          {/* Status Selection */}
          <div className="mb-4">
            <label className="mb-2 block text-xs font-semibold uppercase tracking-wider text-slate-400">
              Update Status
            </label>
            <div className="grid grid-cols-2 gap-2">
              {statuses.map((s) => {
                const Icon = s.icon;
                return (
                  <button
                    key={s.value}
                    onClick={() => setStatus(s.value)}
                    className={cn(
                      "flex items-center gap-2 rounded-lg border p-3 text-left text-xs font-medium transition-all",
                      status === s.value
                        ? "border-accent/50 bg-accent/10 text-white"
                        : "border-navy-600 bg-navy-800 text-slate-400 hover:border-navy-500"
                    )}
                  >
                    <Icon className={cn("h-4 w-4", s.color)} />
                    {s.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Notes */}
          <div className="mb-5">
            <label className="mb-2 block text-xs font-semibold uppercase tracking-wider text-slate-400">
              Analyst Notes
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Add investigation notes..."
              rows={3}
              className="w-full rounded-lg border border-navy-600 bg-navy-800 p-3 text-sm text-white placeholder:text-slate-600 focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent resize-none"
            />
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3">
            <button
              onClick={onClose}
              className="rounded-lg border border-navy-600 px-4 py-2 text-sm text-slate-400 hover:bg-navy-700 hover:text-white"
            >
              Cancel
            </button>
            <button
              onClick={() => onTriage(alert.id, status, notes)}
              className="rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white shadow-glow hover:bg-accent/90 transition-all"
            >
              Update Triage
            </button>
          </div>
        </div>
      </div>
    </>
  );
}

// -----------------------------------------------------------------------------
// Alerts Page
// -----------------------------------------------------------------------------
export default function AlertsPage() {
  const [alerts, setAlerts] = useState<AlertRead[]>([]);
  const [pagination, setPagination] = useState<PaginationMeta | null>(null);
  const [loading, setLoading] = useState(true);
  const [triageTarget, setTriageTarget] = useState<AlertRead | null>(null);
  const [severityFilter, setSeverityFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  const loadAlerts = React.useCallback(() => {
    setLoading(true);
    fetchAlerts({
      severity: severityFilter || undefined,
      alert_status: statusFilter || undefined,
    }).then((res) => {
      setAlerts(res.data);
      setPagination(res.pagination);
      setLoading(false);
    });
  }, [severityFilter, statusFilter]);

  useEffect(() => {
    loadAlerts();
  }, [loadAlerts]);

  const handleTriage = async (id: string, status: string, notes: string) => {
    await triageAlert(id, { alert_status: status, notes });
    setTriageTarget(null);
    loadAlerts();
  };

  return (
    <div className="space-y-5 animate-fade-in">
      <div className="page-header">
        <p className="page-subtitle">
          Manage and triage suspicious activity alerts with severity-based prioritization
        </p>
      </div>

      {/* Filter Bar */}
      <div className="glass-card flex flex-wrap items-center gap-3 p-4">
        <Filter className="h-4 w-4 text-slate-500" />
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-500">Severity:</span>
          {["", "CRITICAL", "HIGH", "MEDIUM", "LOW"].map((s) => (
            <button
              key={s}
              onClick={() => setSeverityFilter(s)}
              className={cn(
                "rounded-lg px-3 py-1.5 text-xs font-medium transition-all",
                severityFilter === s
                  ? s === "CRITICAL" ? "bg-red-500/20 text-red-400 border border-red-500/30"
                    : s === "HIGH" ? "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                    : s === "MEDIUM" ? "bg-blue-500/20 text-blue-400 border border-blue-500/30"
                    : s === "LOW" ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                    : "bg-accent/20 text-accent-glow border border-accent/30"
                  : "border border-navy-600 bg-navy-800 text-slate-400 hover:text-white"
              )}
            >
              {s || "All"}
            </button>
          ))}
        </div>
        <div className="h-4 w-px bg-navy-600" />
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-500">Status:</span>
          {["", "NEW", "UNDER_INVESTIGATION", "ESCALATED"].map((s) => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              className={cn(
                "rounded-lg px-3 py-1.5 text-xs font-medium transition-all",
                statusFilter === s
                  ? "bg-accent/20 text-accent-glow border border-accent/30"
                  : "border border-navy-600 bg-navy-800 text-slate-400 hover:text-white"
              )}
            >
              {s ? s.replace(/_/g, " ") : "All"}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="glass-card overflow-hidden">
        {loading ? (
          <div className="space-y-3 p-5">
            {[...Array(8)].map((_, i) => <div key={i} className="skeleton h-10 rounded-lg" />)}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Alert ID</th>
                  <th>Title</th>
                  <th>Pattern</th>
                  <th>Severity</th>
                  <th>Risk Score</th>
                  <th>Status</th>
                  <th>Triggered</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {alerts.map((alert) => (
                  <tr key={alert.id}>
                    <td className="font-mono text-xs text-accent-glow">{alert.alert_number}</td>
                    <td className="max-w-[220px] truncate text-xs text-white">{alert.title}</td>
                    <td>
                      <span className="badge bg-navy-700 border-navy-600 text-slate-300 text-[10px]">
                        {alert.pattern_type.replace(/_/g, " ")}
                      </span>
                    </td>
                    <td>
                      <span className={cn("badge", getRiskBg(alert.severity))}>
                        {alert.severity === "CRITICAL" && <AlertTriangle className="h-3 w-3" />}
                        {alert.severity}
                      </span>
                    </td>
                    <td>
                      <div className="flex items-center gap-2">
                        <div className="h-1.5 w-16 overflow-hidden rounded-full bg-navy-700">
                          <div
                            className="h-full rounded-full"
                            style={{
                              width: `${alert.risk_score}%`,
                              backgroundColor: alert.risk_score >= 80 ? "#ef4444" : alert.risk_score >= 60 ? "#f59e0b" : "#3b82f6",
                            }}
                          />
                        </div>
                        <span className="text-xs font-medium text-slate-300">{alert.risk_score}</span>
                      </div>
                    </td>
                    <td>
                      <span className={cn("badge", getStatusColor(alert.alert_status))}>
                        {alert.alert_status.replace(/_/g, " ")}
                      </span>
                    </td>
                    <td className="text-xs text-slate-500">{formatTimeAgo(alert.triggered_at)}</td>
                    <td>
                      <button
                        onClick={() => setTriageTarget(alert)}
                        className="rounded-lg border border-navy-600 bg-navy-800 px-3 py-1 text-xs text-accent-glow hover:bg-accent/10 transition-colors"
                      >
                        Triage
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {pagination && (
          <div className="flex items-center justify-between border-t border-navy-700/50 px-4 py-3">
            <p className="text-xs text-slate-500">
              {pagination.total_items} total alerts
            </p>
          </div>
        )}
      </div>

      {/* Triage Modal */}
      {triageTarget && (
        <TriageModal
          alert={triageTarget}
          onClose={() => setTriageTarget(null)}
          onTriage={handleTriage}
        />
      )}
    </div>
  );
}
