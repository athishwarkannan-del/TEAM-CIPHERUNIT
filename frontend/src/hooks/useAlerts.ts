"use client";
// =============================================================================
// useAlerts — Supabase-backed Alerts Hook
// =============================================================================
// Fetches alerts from backend (Supabase). Triage actions persist immediately.
// Polls every 15 seconds for new alerts and status changes.
// =============================================================================

import { useState, useEffect, useCallback, useRef } from "react";
import { fetchAlerts, triageAlert } from "@/lib/api";
import type { AlertRead, PaginationMeta, AlertTriageUpdate } from "@/lib/types";

interface UseAlertsParams {
  severity?: string;
  alert_status?: string;
  page?: number;
  page_size?: number;
}

interface UseAlertsResult {
  alerts: AlertRead[];
  pagination: PaginationMeta | null;
  loading: boolean;
  error: string | null;
  triaging: string | null; // ID of alert being triaged
  refetch: () => void;
  triage: (id: string, payload: AlertTriageUpdate) => Promise<void>;
  isLive: boolean;
}

const POLL_INTERVAL_MS = 15_000; // 15 seconds

export function useAlerts(params?: UseAlertsParams): UseAlertsResult {
  const [alerts, setAlerts] = useState<AlertRead[]>([]);
  const [pagination, setPagination] = useState<PaginationMeta | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [triaging, setTriaging] = useState<string | null>(null);
  const [isLive, setIsLive] = useState(false);
  const isMounted = useRef(true);

  const load = useCallback(async (silent = false) => {
    if (!silent) setLoading(true);
    setError(null);
    try {
      const res = await fetchAlerts(params);
      if (!isMounted.current) return;
      setAlerts(res.data || []);
      setPagination(res.pagination);
      setIsLive(!res.message.includes("cached") && !res.message.includes("Mock"));
    } catch (err) {
      if (!isMounted.current) return;
      setError(err instanceof Error ? err.message : "Failed to load alerts");
    } finally {
      if (!isMounted.current) return;
      if (!silent) setLoading(false);
    }
  }, [params?.severity, params?.alert_status, params?.page, params?.page_size]); // eslint-disable-line

  useEffect(() => {
    isMounted.current = true;
    load();
    const interval = setInterval(() => load(true), POLL_INTERVAL_MS);
    return () => {
      isMounted.current = false;
      clearInterval(interval);
    };
  }, [load]);

  const triage = useCallback(async (id: string, payload: AlertTriageUpdate) => {
    setTriaging(id);

    // Optimistic update — immediately reflect change in UI
    setAlerts((prev) =>
      prev.map((a) =>
        a.id === id
          ? { ...a, alert_status: payload.alert_status, updated_at: new Date().toISOString() }
          : a
      )
    );

    try {
      const res = await triageAlert(id, payload);
      if (res.data && isMounted.current) {
        // Confirm with server's actual data
        setAlerts((prev) => prev.map((a) => (a.id === id ? res.data! : a)));
      }
    } catch (err) {
      // Rollback optimistic update on error
      if (isMounted.current) {
        await load(true);
        throw err;
      }
    } finally {
      if (isMounted.current) setTriaging(null);
    }
  }, [load]);

  return { alerts, pagination, loading, error, triaging, refetch: () => load(false), triage, isLive };
}
