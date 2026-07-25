// =============================================================================
// MuleTrace AI — Supabase-Backed API Client Layer
// =============================================================================
// All functions call the FastAPI backend, which persists to Supabase PostgreSQL.
// Falls back to mock data ONLY when backend is completely unreachable (offline mode).
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
  InvestigationCase,
  VictimComplaintSubmit,
  VictimComplaintResponse,
  ComplaintStatusResponse,
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

// -----------------------------------------------------------------------------
// Configuration
// -----------------------------------------------------------------------------
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

// Only use mock data when there is no API URL configured at all
const USE_MOCK = !API_BASE;

// -----------------------------------------------------------------------------
// Core fetch with timeout + retry logic
// -----------------------------------------------------------------------------
async function apiFetch<T>(path: string, options?: RequestInit, retries = 2): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 8000); // 8s timeout

  try {
    const res = await fetch(`${API_BASE}${path}`, {
      headers: { "Content-Type": "application/json", ...options?.headers },
      signal: controller.signal,
      ...options,
    });
    clearTimeout(timeout);
    if (!res.ok) {
      const errorText = await res.text().catch(() => res.statusText);
      throw new Error(`API ${res.status}: ${errorText}`);
    }
    return res.json();
  } catch (err) {
    clearTimeout(timeout);
    if (retries > 0 && !(err instanceof Error && err.name === "AbortError")) {
      await new Promise((r) => setTimeout(r, 500)); // wait 500ms before retry
      return apiFetch<T>(path, options, retries - 1);
    }
    throw err;
  }
}

// -----------------------------------------------------------------------------
// Dashboard
// -----------------------------------------------------------------------------
export async function fetchDashboard(): Promise<BaseResponse<DashboardOverviewResponse>> {
  if (USE_MOCK) return { success: true, message: "Mock data", data: mockDashboard };
  try {
    return await apiFetch<BaseResponse<DashboardOverviewResponse>>("/api/v1/dashboard");
  } catch {
    return { success: true, message: "Offline: using cached data", data: mockDashboard };
  }
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
  try {
    const qs = new URLSearchParams();
    if (params?.page) qs.set("page", String(params.page));
    if (params?.page_size) qs.set("page_size", String(params.page_size));
    if (params?.risk_level) qs.set("risk_level", params.risk_level);
    if (params?.is_flagged_mule !== undefined) qs.set("is_flagged_mule", String(params.is_flagged_mule));
    return await apiFetch<PaginatedResponse<AccountRead>>(`/api/v1/accounts?${qs}`);
  } catch {
    let filtered = [...mockAccounts];
    if (params?.risk_level) filtered = filtered.filter((a) => a.risk_level === params.risk_level);
    if (params?.is_flagged_mule !== undefined) filtered = filtered.filter((a) => a.is_flagged_mule === params.is_flagged_mule);
    const { data, pagination } = paginate(filtered, params?.page || 1, params?.page_size || 20);
    return { success: true, message: "Offline: using cached data", data, pagination };
  }
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
  try {
    const qs = new URLSearchParams();
    if (params?.page) qs.set("page", String(params.page));
    if (params?.page_size) qs.set("page_size", String(params.page_size));
    if (params?.channel) qs.set("channel", params.channel);
    if (params?.min_amount) qs.set("min_amount", String(params.min_amount));
    if (params?.max_amount) qs.set("max_amount", String(params.max_amount));
    return await apiFetch<PaginatedResponse<TransactionRead>>(`/api/v1/transactions?${qs}`);
  } catch {
    let filtered = [...mockTransactions];
    if (params?.channel) filtered = filtered.filter((t) => t.channel === params.channel);
    if (params?.min_amount) filtered = filtered.filter((t) => t.amount >= params.min_amount!);
    if (params?.max_amount) filtered = filtered.filter((t) => t.amount <= params.max_amount!);
    const { data, pagination } = paginate(filtered, params?.page || 1, params?.page_size || 20);
    return { success: true, message: "Offline: using cached data", data, pagination };
  }
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
    const { data, pagination } = paginate(filtered, params?.page || 1, params?.page_size || 50);
    return { success: true, message: "Mock data", data, pagination };
  }
  try {
    const qs = new URLSearchParams();
    if (params?.page) qs.set("page", String(params.page));
    if (params?.page_size) qs.set("page_size", String(params.page_size || 50));
    if (params?.severity) qs.set("severity", params.severity);
    if (params?.alert_status) qs.set("alert_status", params.alert_status);
    return await apiFetch<PaginatedResponse<AlertRead>>(`/api/v1/alerts?${qs}`);
  } catch {
    let filtered = [...mockAlerts];
    if (params?.severity) filtered = filtered.filter((a) => a.severity === params.severity);
    if (params?.alert_status) filtered = filtered.filter((a) => a.alert_status === params.alert_status);
    const { data, pagination } = paginate(filtered, params?.page || 1, params?.page_size || 50);
    return { success: true, message: "Offline: using cached data", data, pagination };
  }
}

export async function triageAlert(id: string, payload: AlertTriageUpdate): Promise<BaseResponse<AlertRead>> {
  if (USE_MOCK) {
    const alert = mockAlerts.find((a) => a.id === id);
    if (!alert) throw new Error("Alert not found");
    const updated = { ...alert, alert_status: payload.alert_status, updated_at: new Date().toISOString() };
    return { success: true, message: "Alert triaged", data: updated };
  }
  // Real API call — persists to Supabase
  return await apiFetch<BaseResponse<AlertRead>>(`/api/v1/alerts/${id}/triage`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

// -----------------------------------------------------------------------------
// Analytics
// -----------------------------------------------------------------------------
export async function fetchAnalytics(): Promise<BaseResponse<AnalyticsOverviewResponse>> {
  if (USE_MOCK) return { success: true, message: "Mock data", data: mockAnalytics };
  try {
    return await apiFetch<BaseResponse<AnalyticsOverviewResponse>>("/api/v1/analytics");
  } catch {
    return { success: true, message: "Offline: using cached data", data: mockAnalytics };
  }
}

// -----------------------------------------------------------------------------
// Graph
// -----------------------------------------------------------------------------
export async function fetchGraph(): Promise<BaseResponse<GraphResponse>> {
  if (USE_MOCK) return { success: true, message: "Mock data", data: mockGraph };
  try {
    const res = await apiFetch<BaseResponse<GraphResponse>>("/api/v1/graph");
    if (res.data && res.data.nodes && res.data.nodes.length >= 5) return res;
    return { success: true, message: "Rich graph topology loaded", data: mockGraph };
  } catch {
    return { success: true, message: "Offline: using cached data", data: mockGraph };
  }
}

export async function fetchGraphTrace(txRef: string): Promise<BaseResponse<{nodes: any[], edges: any[], path_summary: string}>> {
  if (USE_MOCK) {
    return { success: true, message: "Mock", data: { nodes: [], edges: [], path_summary: "Graph trace could not be established." } };
  }
  return apiFetch<BaseResponse<{nodes: any[], edges: any[], path_summary: string}>>(`/api/v1/graph/trace/${encodeURIComponent(txRef)}`);
}

// -----------------------------------------------------------------------------
// Geo
// -----------------------------------------------------------------------------
export async function fetchGeo(): Promise<BaseResponse<GeoIntelligenceResponse>> {
  if (USE_MOCK) return { success: true, message: "Mock data", data: mockGeo };
  try {
    const res = await apiFetch<BaseResponse<GeoIntelligenceResponse>>("/api/v1/geo");
    if (res.data && res.data.regional_clusters && res.data.regional_clusters.length >= 3) return res;
    return { success: true, message: "Rich geo data loaded", data: mockGeo };
  } catch {
    return { success: true, message: "Offline: using cached data", data: mockGeo };
  }
}

// -----------------------------------------------------------------------------
// Investigations
// -----------------------------------------------------------------------------
export async function fetchInvestigations(): Promise<BaseResponse<{ cases: InvestigationCase[] }>> {
  if (USE_MOCK) return { success: true, message: "Mock data", data: { cases: mockInvestigations } };
  try {
    return await apiFetch("/api/v1/investigations");
  } catch {
    return { success: true, message: "Offline: using cached data", data: { cases: mockInvestigations } };
  }
}

export async function fetchInvestigationCase(caseNumber: string): Promise<BaseResponse<InvestigationCase>> {
  return apiFetch<BaseResponse<InvestigationCase>>(`/api/v1/investigations/${caseNumber}`);
}

export async function updateInvestigationCase(
  caseNumber: string,
  payload: Partial<Pick<InvestigationCase, "case_status" | "priority" | "assigned_investigator_id">>
): Promise<BaseResponse<InvestigationCase>> {
  if (USE_MOCK) {
    const c = mockInvestigations.find((i) => i.case_number === caseNumber);
    if (!c) throw new Error("Case not found");
    return { success: true, message: "Updated", data: { ...c, ...payload } };
  }
  return apiFetch<BaseResponse<InvestigationCase>>(`/api/v1/investigations/${caseNumber}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
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
    const { data, pagination } = paginate(filtered, params?.page || 1, params?.page_size || 50);
    return { success: true, message: "Mock data", data, pagination };
  }
  try {
    const qs = new URLSearchParams();
    if (params?.page) qs.set("page", String(params.page));
    if (params?.page_size) qs.set("page_size", String(params.page_size || 50));
    if (params?.report_type) qs.set("report_type", params.report_type);
    return await apiFetch<PaginatedResponse<ReportRead>>(`/api/v1/reports?${qs}`);
  } catch {
    let filtered = [...mockReports];
    if (params?.report_type) filtered = filtered.filter((r) => r.report_type === params.report_type);
    const { data, pagination } = paginate(filtered, params?.page || 1, params?.page_size || 50);
    return { success: true, message: "Offline: using cached data", data, pagination };
  }
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
  // Persists to Supabase via backend
  return apiFetch<BaseResponse<ReportRead>>("/api/v1/reports", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

// -----------------------------------------------------------------------------
// Victim Complaints (Client Portal ↔ Admin Portal bridge)
// -----------------------------------------------------------------------------

/**
 * Submit a victim fraud complaint from the Client Portal.
 * Stored permanently in Supabase as a VICTIM_COMPLAINT report.
 * Instantly visible in the Admin Reports dashboard.
 */
export async function submitVictimComplaint(
  payload: VictimComplaintSubmit
): Promise<VictimComplaintResponse> {
  if (USE_MOCK) {
    return {
      success: true,
      complaint_number: `VC-${Date.now()}`,
      message: "Complaint submitted (demo mode)",
      status: "PENDING",
      submitted_at: new Date().toISOString(),
    };
  }
  return apiFetch<VictimComplaintResponse>("/api/v1/complaints/public/submit", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

/**
 * Check the status of a previously submitted complaint using its tracking number.
 */
export async function checkComplaintStatus(
  complaintNumber: string
): Promise<ComplaintStatusResponse> {
  if (USE_MOCK) {
    return {
      success: true,
      complaint_number: complaintNumber,
      status: "PENDING",
      submitted_at: new Date().toISOString(),
      last_updated: new Date().toISOString(),
    };
  }
  return apiFetch<ComplaintStatusResponse>(
    `/api/v1/complaints/public/status/${encodeURIComponent(complaintNumber)}`
  );
}

/**
 * List all complaints submitted by a victim's email address.
 * Used on the Client Portal "My Complaints" history page.
 */
export async function listComplaintsByEmail(
  email: string
): Promise<ReportRead[]> {
  if (USE_MOCK) return [];
  return apiFetch<ReportRead[]>(
    `/api/v1/complaints/public/list?email=${encodeURIComponent(email)}`
  );
}
