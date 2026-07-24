"use client";

import React, { useEffect, useState } from "react";
import {
  FileText,
  Plus,
  Download,
  X,
  FileJson,
  Sparkles,
  Send,
} from "lucide-react";
import { fetchReports, generateReport } from "@/lib/api";
import type { ReportRead } from "@/lib/types";
import { formatDate, cn, getStatusColor } from "@/lib/utils";

// -----------------------------------------------------------------------------
// Report Generator Modal
// -----------------------------------------------------------------------------
function ReportGeneratorModal({
  onClose,
  onGenerate,
}: {
  onClose: () => void;
  onGenerate: (report: ReportRead) => void;
}) {
  const [reportType, setReportType] = useState("STR");
  const [title, setTitle] = useState("");
  const [notes, setNotes] = useState("");
  const [generating, setGenerating] = useState(false);

  const reportTypes = [
    { value: "STR", label: "Suspicious Transaction Report", desc: "For FIU-IND filing under PMLA" },
    { value: "CTR", label: "Currency Transaction Report", desc: "High-value cash transaction reporting" },
    { value: "CYBERCRIME_SUMMARY", label: "Cybercrime Summary", desc: "Investigation summary for LEA" },
    { value: "EXECUTIVE_BRIEF", label: "Executive Brief", desc: "Weekly/Monthly executive overview" },
  ];

  const handleGenerate = async () => {
    if (!title.trim()) return;
    setGenerating(true);
    const res = await generateReport({
      report_type: reportType,
      title,
      summary_notes: notes || undefined,
      include_graph_visualization: true,
    });
    if (res.data) onGenerate(res.data);
    setGenerating(false);
    onClose();
  };

  return (
    <>
      <div className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <div className="fixed left-1/2 top-1/2 z-50 w-[560px] -translate-x-1/2 -translate-y-1/2 animate-slide-up">
        <div className="glass-card p-6">
          <div className="flex items-center justify-between mb-5">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent/15 text-accent">
                <FileText className="h-4 w-4" />
              </div>
              <h3 className="font-display text-lg font-bold text-white">Generate Report</h3>
            </div>
            <button onClick={onClose} className="rounded-lg p-1.5 text-slate-400 hover:bg-navy-700 hover:text-white">
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Report Type */}
          <div className="mb-4">
            <label className="mb-2 block text-xs font-semibold uppercase tracking-wider text-slate-400">
              Report Type
            </label>
            <div className="grid grid-cols-2 gap-2">
              {reportTypes.map((rt) => (
                <button
                  key={rt.value}
                  onClick={() => setReportType(rt.value)}
                  className={cn(
                    "rounded-lg border p-3 text-left transition-all",
                    reportType === rt.value
                      ? "border-accent/50 bg-accent/10"
                      : "border-navy-600 bg-navy-800 hover:border-navy-500"
                  )}
                >
                  <p className="text-xs font-semibold text-white">{rt.label}</p>
                  <p className="mt-0.5 text-[10px] text-slate-500">{rt.desc}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Title */}
          <div className="mb-4">
            <label className="mb-2 block text-xs font-semibold uppercase tracking-wider text-slate-400">
              Report Title
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g., STR — Mule Ring Western Region"
              className="w-full rounded-lg border border-navy-600 bg-navy-800 p-3 text-sm text-white placeholder:text-slate-600 focus:border-accent focus:outline-none"
            />
          </div>

          {/* AI Narrative Notes */}
          <div className="mb-5">
            <label className="mb-2 block text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1">
              <Sparkles className="h-3 w-3 text-accent-glow" />
              Executive Narrative Notes
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Add investigation summary for AI narrative generation..."
              rows={4}
              className="w-full rounded-lg border border-navy-600 bg-navy-800 p-3 text-sm text-white placeholder:text-slate-600 focus:border-accent focus:outline-none resize-none"
            />
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3">
            <button onClick={onClose} className="rounded-lg border border-navy-600 px-4 py-2 text-sm text-slate-400 hover:bg-navy-700">
              Cancel
            </button>
            <button
              onClick={handleGenerate}
              disabled={!title.trim() || generating}
              className="flex items-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white shadow-glow hover:bg-accent/90 transition-all disabled:opacity-40"
            >
              {generating ? (
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
              ) : (
                <Send className="h-4 w-4" />
              )}
              Generate Report
            </button>
          </div>
        </div>
      </div>
    </>
  );
}

// -----------------------------------------------------------------------------
// Reports Page
// -----------------------------------------------------------------------------
export default function ReportsPage() {
  const [reports, setReports] = useState<ReportRead[]>([]);
  const [loading, setLoading] = useState(true);
  const [showGenerator, setShowGenerator] = useState(false);
  const [typeFilter, setTypeFilter] = useState("");

  const loadReports = React.useCallback(() => {
    setLoading(true);
    fetchReports({ report_type: typeFilter || undefined }).then((res) => {
      setReports(res.data);
      setLoading(false);
    });
  }, [typeFilter]);

  useEffect(() => {
    loadReports();
  }, [typeFilter]);

  const handleGenerated = (newReport: ReportRead) => {
    setReports((prev) => [newReport, ...prev]);
  };

  const reportTypeColor: Record<string, string> = {
    STR: "bg-red-500/15 text-red-400 border-red-500/30",
    CTR: "bg-amber-500/15 text-amber-400 border-amber-500/30",
    CYBERCRIME_SUMMARY: "bg-violet-500/15 text-violet-400 border-violet-500/30",
    EXECUTIVE_BRIEF: "bg-blue-500/15 text-blue-400 border-blue-500/30",
  };

  return (
    <div className="space-y-5 animate-fade-in">
      <div className="page-header flex items-center justify-between">
        <div>
          <p className="page-subtitle">
            Generate and manage STR/CTR compliance reports for FIU-IND submission
          </p>
        </div>
        <button
          onClick={() => setShowGenerator(true)}
          className="flex items-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white shadow-glow hover:bg-accent/90 transition-all"
        >
          <Plus className="h-4 w-4" />
          Generate Report
        </button>
      </div>

      {/* Filter */}
      <div className="glass-card flex items-center gap-3 p-4">
        <span className="text-xs text-slate-500">Type:</span>
        {["", "STR", "CTR", "EXECUTIVE_BRIEF"].map((t) => (
          <button
            key={t}
            onClick={() => setTypeFilter(t)}
            className={cn(
              "rounded-lg px-3 py-1.5 text-xs font-medium transition-all",
              typeFilter === t
                ? "bg-accent/20 text-accent-glow border border-accent/30"
                : "border border-navy-600 bg-navy-800 text-slate-400 hover:text-white"
            )}
          >
            {t || "All"}
          </button>
        ))}
      </div>

      {/* Reports Table */}
      <div className="glass-card overflow-hidden">
        {loading ? (
          <div className="space-y-3 p-5">
            {[...Array(4)].map((_, i) => <div key={i} className="skeleton h-10 rounded-lg" />)}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Report ID</th>
                  <th>Type</th>
                  <th>Title</th>
                  <th>Status</th>
                  <th>Generated</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {reports.map((report) => (
                  <tr key={report.id}>
                    <td className="font-mono text-xs text-accent-glow">{report.report_number}</td>
                    <td>
                      <span className={cn("badge", reportTypeColor[report.report_type] || "bg-slate-500/15 text-slate-400 border-slate-500/30")}>
                        {report.report_type}
                      </span>
                    </td>
                    <td className="max-w-[280px]">
                      <p className="text-xs font-medium text-white truncate">{report.title}</p>
                      {report.summary_text && (
                        <p className="mt-0.5 text-[11px] text-slate-500 truncate max-w-[280px]">{report.summary_text}</p>
                      )}
                    </td>
                    <td>
                      <span className={cn("badge", getStatusColor(report.status))}>{report.status}</span>
                    </td>
                    <td className="text-xs text-slate-500">{formatDate(report.generated_at)}</td>
                    <td>
                      <div className="flex items-center gap-1">
                        {report.file_path && (
                          <button className="flex items-center gap-1 rounded-lg border border-navy-600 bg-navy-800 px-2 py-1 text-xs text-slate-400 hover:text-white hover:bg-navy-700">
                            <Download className="h-3 w-3" /> PDF
                          </button>
                        )}
                        <button className="flex items-center gap-1 rounded-lg border border-navy-600 bg-navy-800 px-2 py-1 text-xs text-slate-400 hover:text-white hover:bg-navy-700">
                          <FileJson className="h-3 w-3" /> JSON
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Generator Modal */}
      {showGenerator && (
        <ReportGeneratorModal
          onClose={() => setShowGenerator(false)}
          onGenerate={handleGenerated}
        />
      )}
    </div>
  );
}
