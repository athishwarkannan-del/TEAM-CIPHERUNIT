"use client";
// =============================================================================
// useInvestigations — Supabase-backed Investigations Hook
// =============================================================================
// Fetches real investigation cases from backend (Supabase PostgreSQL).
// Supports case status updates that persist to the database.
// =============================================================================

import { useState, useEffect, useCallback, useRef } from "react";
import { fetchInvestigations, updateInvestigationCase } from "@/lib/api";
import type { InvestigationCase } from "@/lib/types";

interface UseInvestigationsResult {
  cases: InvestigationCase[];
  loading: boolean;
  error: string | null;
  refetch: () => void;
  updateCase: (
    caseNumber: string,
    updates: Partial<Pick<InvestigationCase, "case_status" | "priority" | "assigned_investigator_id">>
  ) => Promise<void>;
  isLive: boolean;
}

const POLL_INTERVAL_MS = 20_000; // 20 seconds

export function useInvestigations(): UseInvestigationsResult {
  const [cases, setCases] = useState<InvestigationCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isLive, setIsLive] = useState(false);
  const isMounted = useRef(true);

  const load = useCallback(async (silent = false) => {
    if (!silent) setLoading(true);
    setError(null);
    try {
      const res = await fetchInvestigations();
      if (!isMounted.current) return;
      if (res.data) {
        setCases(res.data.cases || []);
        setIsLive(!res.message.includes("cached") && !res.message.includes("Mock"));
      }
    } catch (err) {
      if (!isMounted.current) return;
      setError(err instanceof Error ? err.message : "Failed to load investigations");
    } finally {
      if (!isMounted.current) return;
      if (!silent) setLoading(false);
    }
  }, []);

  useEffect(() => {
    isMounted.current = true;
    load();
    const interval = setInterval(() => load(true), POLL_INTERVAL_MS);
    return () => {
      isMounted.current = false;
      clearInterval(interval);
    };
  }, [load]);

  const updateCase = useCallback(
    async (
      caseNumber: string,
      updates: Partial<Pick<InvestigationCase, "case_status" | "priority" | "assigned_investigator_id">>
    ) => {
      // Optimistic update
      setCases((prev) =>
        prev.map((c) => (c.case_number === caseNumber ? { ...c, ...updates } : c))
      );
      try {
        await updateInvestigationCase(caseNumber, updates);
      } catch (err) {
        // Rollback
        await load(true);
        throw err;
      }
    },
    [load]
  );

  return { cases, loading, error, refetch: () => load(false), updateCase, isLive };
}
