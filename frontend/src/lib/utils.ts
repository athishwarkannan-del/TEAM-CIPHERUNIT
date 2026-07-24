import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatCurrencyCompact(amount: number): string {
  if (amount >= 10000000) return `₹${(amount / 10000000).toFixed(1)}Cr`;
  if (amount >= 100000) return `₹${(amount / 100000).toFixed(1)}L`;
  if (amount >= 1000) return `₹${(amount / 1000).toFixed(1)}K`;
  return `₹${amount}`;
}

export function formatNumber(num: number): string {
  return new Intl.NumberFormat("en-IN").format(num);
}

export function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

export function formatDateTime(dateStr: string): string {
  return new Date(dateStr).toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function formatTimeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "Just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

export function getRiskColor(level: string): string {
  switch (level.toUpperCase()) {
    case "CRITICAL": return "#ef4444";
    case "HIGH": return "#f59e0b";
    case "MEDIUM": return "#3b82f6";
    case "LOW": return "#10b981";
    default: return "#6b7280";
  }
}

export function getRiskBg(level: string): string {
  switch (level.toUpperCase()) {
    case "CRITICAL": return "bg-red-500/15 text-red-400 border-red-500/30";
    case "HIGH": return "bg-amber-500/15 text-amber-400 border-amber-500/30";
    case "MEDIUM": return "bg-blue-500/15 text-blue-400 border-blue-500/30";
    case "LOW": return "bg-emerald-500/15 text-emerald-400 border-emerald-500/30";
    default: return "bg-slate-500/15 text-slate-400 border-slate-500/30";
  }
}

export function getChannelColor(channel: string): string {
  switch (channel.toUpperCase()) {
    case "UPI": return "bg-violet-500/15 text-violet-400 border-violet-500/30";
    case "NEFT": return "bg-cyan-500/15 text-cyan-400 border-cyan-500/30";
    case "IMPS": return "bg-orange-500/15 text-orange-400 border-orange-500/30";
    case "RTGS": return "bg-pink-500/15 text-pink-400 border-pink-500/30";
    default: return "bg-slate-500/15 text-slate-400 border-slate-500/30";
  }
}

export function getStatusColor(status: string): string {
  switch (status.toUpperCase()) {
    case "NEW": return "bg-blue-500/15 text-blue-400 border-blue-500/30";
    case "UNDER_INVESTIGATION": return "bg-amber-500/15 text-amber-400 border-amber-500/30";
    case "ESCALATED": return "bg-red-500/15 text-red-400 border-red-500/30";
    case "CLOSED_FALSE_POSITIVE": return "bg-slate-500/15 text-slate-400 border-slate-500/30";
    case "CLOSED_CONFIRMED": return "bg-emerald-500/15 text-emerald-400 border-emerald-500/30";
    case "IN_PROGRESS": return "bg-amber-500/15 text-amber-400 border-amber-500/30";
    case "OPEN": return "bg-blue-500/15 text-blue-400 border-blue-500/30";
    case "CLOSED": return "bg-slate-500/15 text-slate-400 border-slate-500/30";
    case "DRAFT": return "bg-slate-500/15 text-slate-400 border-slate-500/30";
    case "GENERATED": return "bg-emerald-500/15 text-emerald-400 border-emerald-500/30";
    case "SUBMITTED": return "bg-blue-500/15 text-blue-400 border-blue-500/30";
    default: return "bg-slate-500/15 text-slate-400 border-slate-500/30";
  }
}

export function truncate(str: string, len: number): string {
  return str.length > len ? str.slice(0, len) + "…" : str;
}
