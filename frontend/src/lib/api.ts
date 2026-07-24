// =============================================================================
// MuleTrace AI — API Client Layer
// =============================================================================
// Typed fetch functions for all backend endpoints.
// Falls back to mock data when NEXT_PUBLIC_API_URL is not set.
// =============================================================================

import type {
  BaseResponse,
  PaginatedResponse,
  DashboardOverviewResponse,
  AccountRead,
  TransactionRead,
  AlertRead,
  AlertTriageUpdate,
  AnalyticsOverviewResponse,
  GraphResponse,
  GeoIntelligenceResponse,
  ReportRead,
  ReportGenerateRequest,
} from "./types";

import {
  mockDashboard,
  mockAccounts,
  mockTransactions,
  mockAlerts,
  mockAnalytics,
  mockGraph,
  mockGeo,
  mockInvestigations,
  mockReports,
  paginate,
} from "./mock-data";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";
const USE_MOCK = !API_BASE;

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) throw new Error(`API Error ${res.status}: ${res.statusText}`);
  return res.json();
}

// -----------------------------------------------------------------------------
// Dashboard
// -----------------------------------------------------------------------------
export async function fetchDashboard(): Promise<BaseResponse<DashboardOverviewResponse>> {
  if (USE_MOCK) {
    return { success: true, message: "Mock data", data: mockDashboard };
  }
  return apiFetch<BaseResponse<DashboardOverviewResponse>>("/api/v1/dashboard");
}

// -----------------------------------------------------------------------------
// Accounts
// -----------------------------------------------------------------------------
export async function fetchAccounts(params?: {
  page?: number;
  page_size?: number;
  risk_level?: string;
  is_flagged_mule?: boolean;
}): Promise<PaginatedResponse<AccountRead>> {
  if (USE_MOCK) {
    let filtered = [...mockAccounts];
    if (params?.risk_level) filtered = filtered.filter((a) => a.risk_level === params.risk_level);
    if (params?.is_flagged_mule !== undefined) filtered = filtered.filter((a) => a.is_flagged_mule === params.is_flagged_mule);
    const { data, pagination } = paginate(filtered, params?.page || 1, params?.page_size || 20);
    return { success: true, message: "Mock data", data, pagination };
  }
  const qs = new URLSearchParams();
  if (params?.page) qs.set("page", String(params.page));
  if (params?.page_size) qs.set("page_size", String(params.page_size));
  if (params?.risk_level) qs.set("risk_level", params.risk_level);
  if (params?.is_flagged_mule !== undefined) qs.set("is_flagged_mule", String(params.is_flagged_mule));
  return apiFetch<PaginatedResponse<AccountRead>>(`/api/v1/accounts?${qs}`);
}

// -----------------------------------------------------------------------------
// Transactions
// -----------------------------------------------------------------------------
export async function fetchTransactions(params?: {
  page?: number;
  page_size?: number;
  channel?: string;
  min_amount?: number;
  max_amount?: number;
}): Promise<PaginatedResponse<TransactionRead>> {
  if (USE_MOCK) {
    let filtered = [...mockTransactions];
    if (params?.channel) filtered = filtered.filter((t) => t.channel === params.channel);
    if (params?.min_amount) filtered = filtered.filter((t) => t.amount >= params.min_amount!);
    if (params?.max_amount) filtered = filtered.filter((t) => t.amount <= params.max_amount!);
    const { data, pagination } = paginate(filtered, params?.page || 1, params?.page_size || 20);
    return { success: true, message: "Mock data", data, pagination };
  }
  const qs = new URLSearchParams();
  if (params?.page) qs.set("page", String(params.page));
  if (params?.page_size) qs.set("page_size", String(params.page_size));
  if (params?.channel) qs.set("channel", params.channel);
  if (params?.min_amount) qs.set("min_amount", String(params.min_amount));
  if (params?.max_amount) qs.set("max_amount", String(params.max_amount));
  return apiFetch<PaginatedResponse<TransactionRead>>(`/api/v1/transactions?${qs}`);
}

// -----------------------------------------------------------------------------
// Alerts
// -----------------------------------------------------------------------------
export async function fetchAlerts(params?: {
  page?: number;
  page_size?: number;
  severity?: string;
  alert_status?: string;
}): Promise<PaginatedResponse<AlertRead>> {
  if (USE_MOCK) {
    let filtered = [...mockAlerts];
    if (params?.severity) filtered = filtered.filter((a) => a.severity === params.severity);
    if (params?.alert_status) filtered = filtered.filter((a) => a.alert_status === params.alert_status);
    const { data, pagination } = paginate(filtered, params?.page || 1, params?.page_size || 20);
    return { success: true, message: "Mock data", data, pagination };
  }
  const qs = new URLSearchParams();
  if (params?.page) qs.set("page", String(params.page));
  if (params?.page_size) qs.set("page_size", String(params.page_size));
  if (params?.severity) qs.set("severity", params.severity);
  if (params?.alert_status) qs.set("alert_status", params.alert_status);
  return apiFetch<PaginatedResponse<AlertRead>>(`/api/v1/alerts?${qs}`);
}

export async function triageAlert(id: string, payload: AlertTriageUpdate): Promise<BaseResponse<AlertRead>> {
  if (USE_MOCK) {
    const alert = mockAlerts.find((a) => a.id === id);
    if (!alert) throw new Error("Alert not found");
    const updated = { ...alert, alert_status: payload.alert_status, updated_at: new Date().toISOString() };
    return { success: true, message: "Alert triaged", data: updated };
  }
  return apiFetch<BaseResponse<AlertRead>>(`/api/v1/alerts/${id}/triage`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

// -----------------------------------------------------------------------------
// Analytics
// -----------------------------------------------------------------------------
export async function fetchAnalytics(): Promise<BaseResponse<AnalyticsOverviewResponse>> {
  if (USE_MOCK) {
    return { success: true, message: "Mock data", data: mockAnalytics };
  }
  return apiFetch<BaseResponse<AnalyticsOverviewResponse>>("/api/v1/analytics");
}

// -----------------------------------------------------------------------------
// Graph
// -----------------------------------------------------------------------------
export async function fetchGraph(): Promise<BaseResponse<GraphResponse>> {
  if (USE_MOCK) {
    return { success: true, message: "Mock data", data: mockGraph };
  }
  return apiFetch<BaseResponse<GraphResponse>>("/api/v1/graph");
}

// -----------------------------------------------------------------------------
// Geo
// -----------------------------------------------------------------------------
export async function fetchGeo(): Promise<BaseResponse<GeoIntelligenceResponse>> {
  if (USE_MOCK) {
    return { success: true, message: "Mock data", data: mockGeo };
  }
  return apiFetch<BaseResponse<GeoIntelligenceResponse>>("/api/v1/geo");
}

// -----------------------------------------------------------------------------
// Investigations
// -----------------------------------------------------------------------------
export async function fetchInvestigations(): Promise<BaseResponse<{ cases: typeof mockInvestigations }>> {
  if (USE_MOCK) {
    return { success: true, message: "Mock data", data: { cases: mockInvestigations } };
  }
  return apiFetch("/api/v1/investigations");
}

// -----------------------------------------------------------------------------
// Reports
// -----------------------------------------------------------------------------
export async function fetchReports(params?: {
  page?: number;
  page_size?: number;
  report_type?: string;
}): Promise<PaginatedResponse<ReportRead>> {
  if (USE_MOCK) {
    let filtered = [...mockReports];
    if (params?.report_type) filtered = filtered.filter((r) => r.report_type === params.report_type);
    const { data, pagination } = paginate(filtered, params?.page || 1, params?.page_size || 20);
    return { success: true, message: "Mock data", data, pagination };
  }
  const qs = new URLSearchParams();
  if (params?.page) qs.set("page", String(params.page));
  if (params?.report_type) qs.set("report_type", params.report_type);
  return apiFetch<PaginatedResponse<ReportRead>>(`/api/v1/reports?${qs}`);
}

export async function generateReport(payload: ReportGenerateRequest): Promise<BaseResponse<ReportRead>> {
  if (USE_MOCK) {
    const newReport: ReportRead = {
      id: crypto.randomUUID(),
      report_number: `STR-2025-${String(Math.floor(Math.random() * 9000 + 1000))}`,
      report_type: payload.report_type,
      title: payload.title,
      generated_at: new Date().toISOString(),
      file_path: null,
      summary_text: payload.summary_notes || "AI-generated summary pending...",
      case_id: payload.case_id || null,
      created_at: new Date().toISOString(),
      status: "DRAFT",
    };
    return { success: true, message: "Report generated", data: newReport };
  }
  return apiFetch<BaseResponse<ReportRead>>("/api/v1/reports", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
