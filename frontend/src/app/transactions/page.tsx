"use client";

import React, { useEffect, useState } from "react";
import { Search, Filter, X, Eye, Wifi, Smartphone, MapPin as MapPinIcon } from "lucide-react";
import { fetchTransactions } from "@/lib/api";
import type { TransactionRead, PaginationMeta } from "@/lib/types";
import { formatCurrency, formatDateTime, cn, getChannelColor, getRiskBg } from "@/lib/utils";

// -----------------------------------------------------------------------------
// Slide-Over Transaction Inspector
// -----------------------------------------------------------------------------
function TransactionInspector({
  tx,
  onClose,
}: {
  tx: TransactionRead;
  onClose: () => void;
}) {
  return (
    <>
      <div className="slide-over-backdrop" onClick={onClose} />
      <div className="slide-over-panel overflow-y-auto">
        <div className="border-b border-navy-600 p-5">
          <div className="flex items-center justify-between">
            <h3 className="font-display text-lg font-bold text-white">Transaction Details</h3>
            <button onClick={onClose} className="rounded-lg p-1.5 text-slate-400 hover:bg-navy-700 hover:text-white">
              <X className="h-5 w-5" />
            </button>
          </div>
          <p className="mt-1 font-mono text-xs text-accent-glow">{tx.transaction_ref}</p>
        </div>

        <div className="space-y-5 p-5">
          {/* Amount & Channel */}
          <div className="glass-card-sm p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-slate-400">Amount</p>
                <p className="font-display text-2xl font-bold text-white">{formatCurrency(tx.amount)}</p>
              </div>
              <span className={cn("badge text-sm", getChannelColor(tx.channel))}>{tx.channel}</span>
            </div>
          </div>

          {/* Risk Assessment */}
          <div className="glass-card-sm p-4">
            <h4 className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-400">Risk Assessment</h4>
            <div className="flex items-center gap-3">
              <div className="flex-1">
                <div className="h-2.5 w-full overflow-hidden rounded-full bg-navy-700">
                  <div
                    className="h-full rounded-full transition-all"
                    style={{
                      width: `${tx.risk_score}%`,
                      backgroundColor: tx.risk_score >= 80 ? "#ef4444" : tx.risk_score >= 60 ? "#f59e0b" : tx.risk_score >= 40 ? "#3b82f6" : "#10b981",
                    }}
                  />
                </div>
              </div>
              <span className="text-lg font-bold text-white">{tx.risk_score}</span>
            </div>
            {tx.flagged_pattern && (
              <div className="mt-3">
                <span className={cn("badge", getRiskBg("HIGH"))}>
                  {tx.flagged_pattern.replace(/_/g, " ")}
                </span>
              </div>
            )}
          </div>

          {/* Accounts */}
          <div className="glass-card-sm p-4">
            <h4 className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-400">Accounts</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-400">Sender</span>
                <span className="font-mono text-xs text-white">{tx.sender_account_id.slice(0, 8)}…</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Receiver</span>
                <span className="font-mono text-xs text-white">{tx.receiver_account_id.slice(0, 8)}…</span>
              </div>
            </div>
          </div>

          {/* Device & Network */}
          <div className="glass-card-sm p-4">
            <h4 className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-400">Device & Network Intelligence</h4>
            <div className="space-y-3 text-sm">
              {tx.device_fingerprint && (
                <div className="flex items-center gap-2">
                  <Smartphone className="h-4 w-4 text-slate-500" />
                  <span className="text-slate-400">Device:</span>
                  <span className="font-mono text-xs text-white">{tx.device_fingerprint}</span>
                </div>
              )}
              {tx.ip_address_str && (
                <div className="flex items-center gap-2">
                  <Wifi className="h-4 w-4 text-slate-500" />
                  <span className="text-slate-400">IP:</span>
                  <span className="font-mono text-xs text-white">{tx.ip_address_str}</span>
                </div>
              )}
              {tx.location_city && (
                <div className="flex items-center gap-2">
                  <MapPinIcon className="h-4 w-4 text-slate-500" />
                  <span className="text-slate-400">Location:</span>
                  <span className="text-white">{tx.location_city}, {tx.location_state}</span>
                </div>
              )}
            </div>
          </div>

          {/* Timestamp */}
          <div className="glass-card-sm p-4">
            <h4 className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-400">Timeline</h4>
            <p className="text-sm text-white">{formatDateTime(tx.timestamp)}</p>
            <p className="mt-1 text-xs text-slate-500">Status: {tx.status}</p>
          </div>
        </div>
      </div>
    </>
  );
}

// -----------------------------------------------------------------------------
// Transactions Page
// -----------------------------------------------------------------------------
export default function TransactionsPage() {
  const [transactions, setTransactions] = useState<TransactionRead[]>([]);
  const [pagination, setPagination] = useState<PaginationMeta | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedTx, setSelectedTx] = useState<TransactionRead | null>(null);
  const [channelFilter, setChannelFilter] = useState("");
  const [searchRef, setSearchRef] = useState("");

  useEffect(() => {
    setLoading(true);
    fetchTransactions({
      page: 1,
      page_size: 20,
      channel: channelFilter || undefined,
    }).then((res) => {
      setTransactions(res.data);
      setPagination(res.pagination);
      setLoading(false);
    });
  }, [channelFilter]);

  const filtered = searchRef
    ? transactions.filter((t) => t.transaction_ref.toLowerCase().includes(searchRef.toLowerCase()))
    : transactions;

  return (
    <div className="space-y-5 animate-fade-in">
      <div className="page-header">
        <p className="page-subtitle">Search, filter, and inspect cross-channel transactions with risk intelligence</p>
      </div>

      {/* Filter Bar */}
      <div className="glass-card flex flex-wrap items-center gap-3 p-4">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder="Search by UTR / Reference..."
            value={searchRef}
            onChange={(e) => setSearchRef(e.target.value)}
            className="w-full rounded-lg border border-navy-600 bg-navy-800 py-2 pl-9 pr-3 text-sm text-white placeholder:text-slate-500 focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-slate-500" />
          {["", "UPI", "NEFT", "IMPS", "RTGS"].map((ch) => (
            <button
              key={ch}
              onClick={() => setChannelFilter(ch)}
              className={cn(
                "rounded-lg px-3 py-1.5 text-xs font-medium transition-all",
                channelFilter === ch
                  ? "bg-accent/20 text-accent-glow border border-accent/30"
                  : "border border-navy-600 bg-navy-800 text-slate-400 hover:text-white hover:bg-navy-700"
              )}
            >
              {ch || "All"}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="glass-card overflow-hidden">
        {loading ? (
          <div className="space-y-3 p-5">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="skeleton h-10 rounded-lg" />
            ))}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th>UTR / Reference</th>
                  <th>Channel</th>
                  <th>Amount (₹)</th>
                  <th>Location</th>
                  <th>Risk Score</th>
                  <th>Pattern</th>
                  <th>Time</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((tx) => (
                  <tr key={tx.id} className="cursor-pointer" onClick={() => setSelectedTx(tx)}>
                    <td className="font-mono text-xs text-accent-glow">{tx.transaction_ref}</td>
                    <td>
                      <span className={cn("badge", getChannelColor(tx.channel))}>{tx.channel}</span>
                    </td>
                    <td className="font-medium text-white">{formatCurrency(tx.amount)}</td>
                    <td className="text-xs">{tx.location_city || "—"}</td>
                    <td>
                      <div className="flex items-center gap-2">
                        <div className="h-1.5 w-16 overflow-hidden rounded-full bg-navy-700">
                          <div
                            className="h-full rounded-full"
                            style={{
                              width: `${tx.risk_score}%`,
                              backgroundColor:
                                tx.risk_score >= 80 ? "#ef4444" : tx.risk_score >= 60 ? "#f59e0b" : tx.risk_score >= 40 ? "#3b82f6" : "#10b981",
                            }}
                          />
                        </div>
                        <span className="text-xs font-medium text-slate-300">{tx.risk_score}</span>
                      </div>
                    </td>
                    <td>
                      {tx.flagged_pattern ? (
                        <span className={cn("badge", getRiskBg("HIGH"))}>
                          {tx.flagged_pattern.replace(/_/g, " ")}
                        </span>
                      ) : (
                        <span className="text-xs text-slate-600">—</span>
                      )}
                    </td>
                    <td className="text-xs text-slate-500">{formatDateTime(tx.timestamp)}</td>
                    <td>
                      <button className="rounded p-1 text-slate-500 hover:bg-navy-700 hover:text-white">
                        <Eye className="h-3.5 w-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {pagination && (
          <div className="flex items-center justify-between border-t border-navy-700/50 px-4 py-3">
            <p className="text-xs text-slate-500">
              Showing {filtered.length} of {pagination.total_items} transactions
            </p>
            <div className="flex gap-2">
              <button disabled={!pagination.has_prev} className="rounded-lg border border-navy-600 bg-navy-800 px-3 py-1 text-xs text-slate-400 disabled:opacity-30">
                Previous
              </button>
              <button disabled={!pagination.has_next} className="rounded-lg border border-navy-600 bg-navy-800 px-3 py-1 text-xs text-slate-400 disabled:opacity-30">
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Slide-over Inspector */}
      {selectedTx && <TransactionInspector tx={selectedTx} onClose={() => setSelectedTx(null)} />}
    </div>
  );
}
