"use client";
// =============================================================================
// useReports — Supabase-backed Reports Hook
// =============================================================================
// Fetches all reports (STR, CTR, VICTIM_COMPLAINT, etc.) from Supabase.
// Polls every 8 seconds so new victim complaints from the Client Portal
// appear in the Admin Dashboard automatically.
// =============================================================================

import { useState, useEffect, useCallback, useRef } from "react";
import { fetchReports, generateReport, submitVictimComplaint } from "@/lib/api";
import type { ReportRead, ReportGenerateRequest, VictimComplaintSubmit, VictimComplaintResponse } from "@/lib/types";

interface UseReportsResult {
  reports: ReportRead[];
  victimComplaints: ReportRead[];
  generatedReports: ReportRead[];
  loading: boolean;
  error: string | null;
  submitting: boolean;
  refetch: () => void;
  generate: (payload: ReportGenerateRequest) => Promise<ReportRead | null>;
  submitComplaint: (payload: VictimComplaintSubmit) => Promise<VictimComplaintResponse | null>;
  isLive: boolean;
  newComplaintCount: number; // badge for new items since last seen
}

const POLL_INTERVAL_MS = 8_000; // 8 seconds for near-realtime feel

export function useReports(typeFilter?: string): UseReportsResult {
  const [reports, setReports] = useState<ReportRead[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [isLive, setIsLive] = useState(false);
  const [newComplaintCount, setNewComplaintCount] = useState(0);
  const prevComplaintCount = useRef(0);
  const isMounted = useRef(true);

  const load = useCallback(async (silent = false) => {
    if (!silent) setLoading(true);
    setError(null);
    try {
      const res = await fetchReports({ report_type: typeFilter || undefined, page_size: 100 });
      if (!isMounted.current) return;
      const items = res.data || [];
      setReports(items);
      setIsLive(!res.message.includes("cached") && !res.message.includes("Mock"));

      // Track new victim complaints
      const complaints = items.filter((r) => r.report_type === "VICTIM_COMPLAINT");
      if (prevComplaintCount.current > 0 && complaints.length > prevComplaintCount.current) {
        setNewComplaintCount(complaints.length - prevComplaintCount.current);
      }
      prevComplaintCount.current = complaints.length;
    } catch (err) {
      if (!isMounted.current) return;
      setError(err instanceof Error ? err.message : "Failed to load reports");
    } finally {
      if (!isMounted.current) return;
      if (!silent) setLoading(false);
    }
  }, [typeFilter]);

  useEffect(() => {
    isMounted.current = true;
    load();
    const interval = setInterval(() => load(true), POLL_INTERVAL_MS);
    return () => {
      isMounted.current = false;
      clearInterval(interval);
    };
  }, [load]);

  const generate = useCallback(async (payload: ReportGenerateRequest): Promise<ReportRead | null> => {
    setSubmitting(true);
    try {
      const res = await generateReport(payload);
      if (res.data && isMounted.current) {
        // Optimistic prepend
        setReports((prev) => [res.data!, ...prev]);
        return res.data;
      }
      return null;
    } catch (err) {
      throw err;
    } finally {
      if (isMounted.current) setSubmitting(false);
    }
  }, []);

  const submitComplaint = useCallback(
    async (payload: VictimComplaintSubmit): Promise<VictimComplaintResponse | null> => {
      setSubmitting(true);
      try {
        const res = await submitVictimComplaint(payload);
        if (res.success && isMounted.current) {
          await load(true); // Refresh list after submission
        }
        return res;
      } finally {
        if (isMounted.current) setSubmitting(false);
      }
    },
    [load]
  );

  const victimComplaints = reports.filter((r) => r.report_type === "VICTIM_COMPLAINT");
  const generatedReports = reports.filter((r) => r.report_type !== "VICTIM_COMPLAINT");

  return {
    reports,
    victimComplaints,
    generatedReports,
    loading,
    error,
    submitting,
    refetch: () => load(false),
    generate,
    submitComplaint,
    isLive,
    newComplaintCount,
  };
}
