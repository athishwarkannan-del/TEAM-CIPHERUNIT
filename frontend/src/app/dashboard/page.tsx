"use client";

import React, { useEffect, useState } from "react";
import {
  ArrowLeftRight,
  ShieldAlert,
  Users,
  IndianRupee,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  Eye,
  ArrowUpRight,
} from "lucide-react";
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { fetchDashboard } from "@/lib/api";
import type { DashboardOverviewResponse, AlertRead } from "@/lib/types";
import { formatCurrencyCompact, formatNumber, getRiskBg, formatTimeAgo, cn } from "@/lib/utils";

// -----------------------------------------------------------------------------
// Custom Recharts Tooltip
// -----------------------------------------------------------------------------
function CustomTooltip({ active, payload, label }: { active?: boolean; payload?: Array<{ name: string; value: number; color: string }>; label?: string }) {
  if (!active || !payload) return null;
  return (
    <div className="glass-card-sm px-3 py-2">
      <p className="text-xs font-medium text-white">{label}</p>
      {payload.map((p, i) => (
        <p key={i} className="text-xs" style={{ color: p.color }}>
          {p.name}: {p.value}
        </p>
      ))}
    </div>
  );
}

// -----------------------------------------------------------------------------
// KPI Card Component
// -----------------------------------------------------------------------------
function KPICard({
  icon: Icon,
  label,
  value,
  trend,
  trendLabel,
  variant,
}: {
  icon: React.ElementType;
  label: string;
  value: string;
  trend?: "up" | "down";
  trendLabel?: string;
  variant: string;
}) {
  const cardClass =
    variant === "critical"
      ? "kpi-card-critical"
      : variant === "amber"
        ? "kpi-card-amber"
        : variant === "blue"
          ? "kpi-card-blue"
          : "kpi-card-emerald";

  const iconColor =
    variant === "critical"
      ? "text-red-400 bg-red-500/15"
      : variant === "amber"
        ? "text-amber-400 bg-amber-500/15"
        : variant === "blue"
          ? "text-blue-400 bg-blue-500/15"
          : "text-emerald-400 bg-emerald-500/15";

  return (
    <div className={cardClass}>
      <div className="flex items-start justify-between">
        <div className={cn("flex h-10 w-10 items-center justify-center rounded-lg", iconColor)}>
          <Icon className="h-5 w-5" />
        </div>
        {trend && (
          <div
            className={cn(
              "flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-semibold",
              trend === "up" ? "bg-red-500/10 text-red-400" : "bg-emerald-500/10 text-emerald-400"
            )}
          >
            {trend === "up" ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
            {trendLabel}
          </div>
        )}
      </div>
      <div className="mt-3">
        <p className="font-display text-2xl font-bold text-white">{value}</p>
        <p className="mt-0.5 text-xs text-slate-400">{label}</p>
      </div>
    </div>
  );
}

// -----------------------------------------------------------------------------
// Risk Score Bar
// -----------------------------------------------------------------------------
function RiskScoreBar({ score }: { score: number }) {
  const color = score >= 80 ? "#ef4444" : score >= 60 ? "#f59e0b" : score >= 40 ? "#3b82f6" : "#10b981";
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-20 overflow-hidden rounded-full bg-navy-700">
        <div className="h-full rounded-full transition-all duration-500" style={{ width: `${score}%`, backgroundColor: color }} />
      </div>
      <span className="text-xs font-medium" style={{ color }}>
        {score}
      </span>
    </div>
  );
}

// -----------------------------------------------------------------------------
// Dashboard Page
// -----------------------------------------------------------------------------
export default function DashboardPage() {
  const [data, setData] = useState<DashboardOverviewResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboard()
      .then((res) => {
        setData(res.data);
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      });
  }, []);

  if (loading || !data) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="skeleton h-[120px] rounded-xl" />
          ))}
        </div>
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div className="skeleton h-[350px] rounded-xl" />
          <div className="skeleton h-[350px] rounded-xl" />
        </div>
        <div className="skeleton h-[400px] rounded-xl" />
      </div>
    );
  }

  const { kpis, risk_distribution, top_patterns, recent_alerts } = data;

  const riskDonutData = [
    { name: "Critical", value: risk_distribution.critical, color: "#ef4444" },
    { name: "High", value: risk_distribution.high, color: "#f59e0b" },
    { name: "Medium", value: risk_distribution.medium, color: "#3b82f6" },
    { name: "Low", value: risk_distribution.low, color: "#10b981" },
  ];

  const patternData = top_patterns.slice(0, 10).map((p) => ({
    name: p.pattern_name.length > 18 ? p.pattern_name.slice(0, 18) + "…" : p.pattern_name,
    hits: p.hit_count,
    fill:
      p.severity === "CRITICAL" ? "#ef4444" : p.severity === "HIGH" ? "#f59e0b" : p.severity === "MEDIUM" ? "#3b82f6" : "#10b981",
  }));

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Page Header */}
      <div className="page-header">
        <p className="page-subtitle">Real-time overview of mule account detection, risk intelligence, and active investigations</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4 animate-stagger">
        <KPICard
          icon={ArrowLeftRight}
          label="Total Transactions (24h)"
          value={formatNumber(kpis.total_transactions_24h)}
          trend="up"
          trendLabel="+12.4%"
          variant="blue"
        />
        <KPICard
          icon={Users}
          label="Flagged Mule Accounts"
          value={formatNumber(kpis.flagged_mule_accounts)}
          trend="up"
          trendLabel="+8"
          variant="critical"
        />
        <KPICard
          icon={ShieldAlert}
          label="Active Alert Queue"
          value={formatNumber(kpis.active_alerts_count)}
          trend="up"
          trendLabel="+5"
          variant="amber"
        />
        <KPICard
          icon={IndianRupee}
          label="Volume at Risk"
          value={formatCurrencyCompact(kpis.total_volume_at_risk_inr)}
          trend="up"
          trendLabel="+₹3.2Cr"
          variant="critical"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Risk Distribution Donut */}
        <div className="glass-card p-5">
          <h3 className="mb-4 text-sm font-semibold text-white">Account Risk Distribution</h3>
          <div className="flex items-center gap-6">
            <ResponsiveContainer width="50%" height={220}>
              <PieChart>
                <Pie
                  data={riskDonutData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={85}
                  paddingAngle={3}
                  dataKey="value"
                  stroke="none"
                >
                  {riskDonutData.map((entry, i) => (
                    <Cell key={i} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
              </PieChart>
            </ResponsiveContainer>
            <div className="space-y-3">
              {riskDonutData.map((item) => (
                <div key={item.name} className="flex items-center gap-3">
                  <div className="h-3 w-3 rounded-full" style={{ backgroundColor: item.color }} />
                  <div>
                    <p className="text-xs text-slate-400">{item.name}</p>
                    <p className="text-sm font-semibold text-white">{formatNumber(item.value)}</p>
                  </div>
                </div>
              ))}
              <div className="border-t border-navy-600 pt-2">
                <p className="text-xs text-slate-500">Total Monitored</p>
                <p className="text-lg font-bold text-white">
                  {formatNumber(riskDonutData.reduce((a, b) => a + b.value, 0))}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Top Fraud Patterns */}
        <div className="glass-card p-5">
          <h3 className="mb-4 text-sm font-semibold text-white">Top Fraud Pattern Hits</h3>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={patternData} layout="vertical" margin={{ left: 0, right: 16 }}>
              <XAxis type="number" tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false} />
              <YAxis type="category" dataKey="name" tick={{ fontSize: 11, fill: "#94a3b8" }} width={120} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="hits" radius={[0, 4, 4, 0]} barSize={14}>
                {patternData.map((entry, i) => (
                  <Cell key={i} fill={entry.fill} fillOpacity={0.8} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Live Alert Triage Feed */}
      <div className="glass-card p-5">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-white">Live Alert Triage Feed</h3>
          <a
            href="/alerts"
            className="flex items-center gap-1 text-xs font-medium text-accent-glow transition-colors hover:text-white"
          >
            View All <ArrowUpRight className="h-3 w-3" />
          </a>
        </div>
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
                <th>Time</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {recent_alerts.map((alert: AlertRead) => (
                <tr key={alert.id} className="cursor-pointer">
                  <td className="font-mono text-xs text-accent-glow">{alert.alert_number}</td>
                  <td className="max-w-[200px] truncate text-xs">{alert.title}</td>
                  <td>
                    <span className="badge bg-navy-700 border-navy-600 text-slate-300">
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
                    <RiskScoreBar score={alert.risk_score} />
                  </td>
                  <td>
                    <span
                      className={cn(
                        "badge",
                        alert.alert_status === "NEW"
                          ? "bg-blue-500/15 text-blue-400 border-blue-500/30"
                          : alert.alert_status === "ESCALATED"
                            ? "bg-red-500/15 text-red-400 border-red-500/30"
                            : alert.alert_status === "UNDER_INVESTIGATION"
                              ? "bg-amber-500/15 text-amber-400 border-amber-500/30"
                              : "bg-slate-500/15 text-slate-400 border-slate-500/30"
                      )}
                    >
                      {alert.alert_status.replace(/_/g, " ")}
                    </span>
                  </td>
                  <td className="text-xs text-slate-500">{formatTimeAgo(alert.triggered_at)}</td>
                  <td>
                    <button className="rounded p-1 text-slate-500 transition-colors hover:bg-navy-700 hover:text-white">
                      <Eye className="h-3.5 w-3.5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
