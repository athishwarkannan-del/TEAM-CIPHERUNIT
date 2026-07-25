"use client";
// =============================================================================
// useDashboard — Supabase-backed Dashboard Hook
// =============================================================================
// Fetches live KPIs, risk distribution, patterns, and recent alerts from the
// backend (which reads from Supabase). Auto-refreshes every 30 seconds.
// =============================================================================

import { useState, useEffect, useCallback, useRef } from "react";
import { fetchDashboard } from "@/lib/api";
import type { DashboardOverviewResponse } from "@/lib/types";

interface UseDashboardResult {
  data: DashboardOverviewResponse | null;
  loading: boolean;
  error: string | null;
  lastUpdated: Date | null;
  refetch: () => void;
  isLive: boolean;
}

const REFRESH_INTERVAL_MS = 30_000; // 30 seconds

export function useDashboard(): UseDashboardResult {
  const [data, setData] = useState<DashboardOverviewResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [isLive, setIsLive] = useState(false);
  const isMounted = useRef(true);

  const load = useCallback(async (silent = false) => {
    if (!silent) setLoading(true);
    setError(null);
    try {
      const res = await fetchDashboard();
      if (!isMounted.current) return;
      if (res.data) {
        setData(res.data);
        setLastUpdated(new Date());
        setIsLive(!res.message.includes("cached") && !res.message.includes("Mock"));
      }
    } catch (err) {
      if (!isMounted.current) return;
      setError(err instanceof Error ? err.message : "Failed to load dashboard");
    } finally {
      if (!isMounted.current) return;
      if (!silent) setLoading(false);
    }
  }, []);

  useEffect(() => {
    isMounted.current = true;
    load();
    const interval = setInterval(() => load(true), REFRESH_INTERVAL_MS);
    return () => {
      isMounted.current = false;
      clearInterval(interval);
    };
  }, [load]);

  return { data, loading, error, lastUpdated, refetch: () => load(false), isLive };
}
