// =============================================================================
// MuleTrace AI — Comprehensive Mock Data Layer
// =============================================================================
// Realistic mock data matching all backend Pydantic schemas.
// Used when backend is unavailable or NEXT_PUBLIC_API_URL is not set.
// =============================================================================

import type {
  DashboardOverviewResponse,
  AlertRead,
  AccountRead,
  TransactionRead,
  AnalyticsOverviewResponse,
  GraphResponse,
  GeoIntelligenceResponse,
  InvestigationCase,
  ReportRead,
  PatternHitSummary,
  PaginationMeta,
} from "./types";

// -----------------------------------------------------------------------------
// Helpers
// -----------------------------------------------------------------------------
const uuid = (n: number) => `a0eebc99-9c0b-4ef8-bb6d-6bb9bd38${n.toString().padStart(4, "0")}`;
const hoursAgo = (h: number) => new Date(Date.now() - h * 3600000).toISOString();
const daysAgo = (d: number) => new Date(Date.now() - d * 86400000).toISOString();

// -----------------------------------------------------------------------------
// Alerts
// -----------------------------------------------------------------------------
export const mockAlerts: AlertRead[] = [
  { id: uuid(1), alert_number: "ALT-2025-0001", title: "Mule Chain Detected: 5-hop rapid transfer", pattern_type: "MULE_CHAIN", severity: "CRITICAL", risk_score: 96, description: "Sequential transfer chain A→B→C→D→E completed in under 8 minutes via UPI", account_id: uuid(101), case_id: uuid(501), alert_status: "NEW", triggered_at: hoursAgo(0.5), created_at: hoursAgo(0.5), updated_at: hoursAgo(0.5) },
  { id: uuid(2), alert_number: "ALT-2025-0002", title: "Fan-In Collector Hub: 12 inbound transfers", pattern_type: "FAN_IN_COLLECTOR", severity: "CRITICAL", risk_score: 93, description: "Account received 12 transfers from unique senders within 30 minutes", account_id: uuid(102), case_id: null, alert_status: "UNDER_INVESTIGATION", triggered_at: hoursAgo(1.2), created_at: hoursAgo(1.2), updated_at: hoursAgo(0.8) },
  { id: uuid(3), alert_number: "ALT-2025-0003", title: "Impossible Travel: Mumbai → Delhi in 15 mins", pattern_type: "IMPOSSIBLE_TRAVEL", severity: "HIGH", risk_score: 87, description: "Transaction executed from Delhi 15 minutes after Mumbai transaction. Distance: 1,400km", account_id: uuid(103), case_id: uuid(501), alert_status: "ESCALATED", triggered_at: hoursAgo(2.1), created_at: hoursAgo(2.1), updated_at: hoursAgo(1.5) },
  { id: uuid(4), alert_number: "ALT-2025-0004", title: "Shared Device Cluster: Samsung Galaxy S23", pattern_type: "SHARED_DEVICE", severity: "HIGH", risk_score: 82, description: "Single device fingerprint used by 4 different accounts for UPI transactions", account_id: uuid(104), case_id: null, alert_status: "NEW", triggered_at: hoursAgo(3), created_at: hoursAgo(3), updated_at: hoursAgo(3) },
  { id: uuid(5), alert_number: "ALT-2025-0005", title: "Structuring/Smurfing: 8 transactions just under ₹50,000", pattern_type: "SMURFING", severity: "HIGH", risk_score: 79, description: "Series of deposits ranging ₹48,500-₹49,900 within 2 hours", account_id: uuid(105), case_id: null, alert_status: "UNDER_INVESTIGATION", triggered_at: hoursAgo(4.5), created_at: hoursAgo(4.5), updated_at: hoursAgo(3.2) },
  { id: uuid(6), alert_number: "ALT-2025-0006", title: "Rapid Fund Layering via IMPS channel", pattern_type: "FUND_LAYERING", severity: "MEDIUM", risk_score: 71, description: "Funds received and immediately split to 3 accounts", account_id: uuid(106), case_id: null, alert_status: "NEW", triggered_at: hoursAgo(5.8), created_at: hoursAgo(5.8), updated_at: hoursAgo(5.8) },
  { id: uuid(7), alert_number: "ALT-2025-0007", title: "Dormant Account Activation: No activity for 340 days", pattern_type: "DORMANT_ACTIVATION", severity: "MEDIUM", risk_score: 65, description: "Account dormant for 11 months suddenly received ₹2,80,000 via NEFT", account_id: uuid(107), case_id: null, alert_status: "CLOSED_FALSE_POSITIVE", triggered_at: hoursAgo(8), created_at: hoursAgo(8), updated_at: hoursAgo(6) },
  { id: uuid(8), alert_number: "ALT-2025-0008", title: "Round-amount transfer pattern detected", pattern_type: "ROUND_AMOUNT", severity: "LOW", risk_score: 45, description: "Repeated round-number transfers: ₹50,000, ₹1,00,000, ₹25,000", account_id: uuid(108), case_id: null, alert_status: "CLOSED_CONFIRMED", triggered_at: hoursAgo(12), created_at: hoursAgo(12), updated_at: hoursAgo(9) },
  { id: uuid(9), alert_number: "ALT-2025-0009", title: "Velocity spike: 18 transactions in 1 hour", pattern_type: "VELOCITY_SPIKE", severity: "HIGH", risk_score: 85, description: "Account normally processes 2-3 daily transactions, sudden spike to 18 in 60 minutes", account_id: uuid(109), case_id: uuid(502), alert_status: "ESCALATED", triggered_at: hoursAgo(1.8), created_at: hoursAgo(1.8), updated_at: hoursAgo(1) },
  { id: uuid(10), alert_number: "ALT-2025-0010", title: "Cross-channel layering: UPI → IMPS → NEFT", pattern_type: "CROSS_CHANNEL", severity: "CRITICAL", risk_score: 91, description: "Funds moved across 3 channels within 20 minutes to obscure trail", account_id: uuid(110), case_id: null, alert_status: "NEW", triggered_at: hoursAgo(0.3), created_at: hoursAgo(0.3), updated_at: hoursAgo(0.3) },
  { id: uuid(11), alert_number: "ALT-2025-0011", title: "Nighttime burst: ₹8.4L transferred between 2-4 AM", pattern_type: "NIGHTTIME_BURST", severity: "MEDIUM", risk_score: 68, description: "Unusual high-value transactions during non-business hours", account_id: uuid(111), case_id: null, alert_status: "UNDER_INVESTIGATION", triggered_at: hoursAgo(6), created_at: hoursAgo(6), updated_at: hoursAgo(4) },
  { id: uuid(12), alert_number: "ALT-2025-0012", title: "New account rapid funding within 48h", pattern_type: "NEW_ACCOUNT_RAPID", severity: "MEDIUM", risk_score: 63, description: "Account opened 36 hours ago already received ₹3,50,000", account_id: uuid(112), case_id: null, alert_status: "NEW", triggered_at: hoursAgo(7), created_at: hoursAgo(7), updated_at: hoursAgo(7) },
];

// -----------------------------------------------------------------------------
// Accounts
// -----------------------------------------------------------------------------
export const mockAccounts: AccountRead[] = [
  { id: uuid(101), account_number: "XXXX1001", customer_id: "CIF-100201", customer_name: "Rajesh Kumar Sharma", account_type: "savings", currency: "INR", balance: 1245000, risk_score: 96, risk_level: "CRITICAL", is_flagged_mule: true, branch_id: null, opened_at: daysAgo(450), created_at: daysAgo(450), updated_at: hoursAgo(1), status: "ACTIVE" },
  { id: uuid(102), account_number: "XXXX1002", customer_id: "CIF-100302", customer_name: "Priya Venkatesh Nair", account_type: "current", currency: "INR", balance: 3890000, risk_score: 93, risk_level: "CRITICAL", is_flagged_mule: true, branch_id: null, opened_at: daysAgo(200), created_at: daysAgo(200), updated_at: hoursAgo(2), status: "ACTIVE" },
  { id: uuid(103), account_number: "XXXX1003", customer_id: "CIF-100403", customer_name: "Mohammed Irfan Ali", account_type: "savings", currency: "INR", balance: 567000, risk_score: 87, risk_level: "HIGH", is_flagged_mule: true, branch_id: null, opened_at: daysAgo(180), created_at: daysAgo(180), updated_at: hoursAgo(3), status: "ACTIVE" },
  { id: uuid(104), account_number: "XXXX1004", customer_id: "CIF-100504", customer_name: "Deepa Subramaniam", account_type: "savings", currency: "INR", balance: 234000, risk_score: 82, risk_level: "HIGH", is_flagged_mule: true, branch_id: null, opened_at: daysAgo(90), created_at: daysAgo(90), updated_at: hoursAgo(4), status: "ACTIVE" },
  { id: uuid(105), account_number: "XXXX1005", customer_id: "CIF-100605", customer_name: "Arun Prakash Joshi", account_type: "current", currency: "INR", balance: 890000, risk_score: 79, risk_level: "HIGH", is_flagged_mule: false, branch_id: null, opened_at: daysAgo(365), created_at: daysAgo(365), updated_at: hoursAgo(5), status: "ACTIVE" },
  { id: uuid(106), account_number: "XXXX1006", customer_id: "CIF-100706", customer_name: "Kavitha Reddy Pillai", account_type: "savings", currency: "INR", balance: 156000, risk_score: 71, risk_level: "MEDIUM", is_flagged_mule: false, branch_id: null, opened_at: daysAgo(500), created_at: daysAgo(500), updated_at: hoursAgo(6), status: "ACTIVE" },
  { id: uuid(107), account_number: "XXXX1007", customer_id: "CIF-100807", customer_name: "Suresh Babu Iyer", account_type: "savings", currency: "INR", balance: 45000, risk_score: 65, risk_level: "MEDIUM", is_flagged_mule: false, branch_id: null, opened_at: daysAgo(730), created_at: daysAgo(730), updated_at: hoursAgo(8), status: "DORMANT" },
  { id: uuid(108), account_number: "XXXX1008", customer_id: "CIF-100908", customer_name: "Lakshmi Devi Gupta", account_type: "savings", currency: "INR", balance: 320000, risk_score: 45, risk_level: "LOW", is_flagged_mule: false, branch_id: null, opened_at: daysAgo(600), created_at: daysAgo(600), updated_at: hoursAgo(12), status: "ACTIVE" },
  { id: uuid(109), account_number: "XXXX1009", customer_id: "CIF-101009", customer_name: "Vikram Singh Chauhan", account_type: "current", currency: "INR", balance: 2150000, risk_score: 85, risk_level: "HIGH", is_flagged_mule: true, branch_id: null, opened_at: daysAgo(120), created_at: daysAgo(120), updated_at: hoursAgo(2), status: "ACTIVE" },
  { id: uuid(110), account_number: "XXXX1010", customer_id: "CIF-101110", customer_name: "Anitha Krishnamurthy", account_type: "savings", currency: "INR", balance: 780000, risk_score: 91, risk_level: "CRITICAL", is_flagged_mule: true, branch_id: null, opened_at: daysAgo(60), created_at: daysAgo(60), updated_at: hoursAgo(0.5), status: "ACTIVE" },
  { id: uuid(111), account_number: "XXXX1011", customer_id: "CIF-101211", customer_name: "Rahul Mehta", account_type: "savings", currency: "INR", balance: 95000, risk_score: 38, risk_level: "LOW", is_flagged_mule: false, branch_id: null, opened_at: daysAgo(800), created_at: daysAgo(800), updated_at: daysAgo(5), status: "ACTIVE" },
  { id: uuid(112), account_number: "XXXX1012", customer_id: "CIF-101312", customer_name: "Sneha Patil Deshmukh", account_type: "savings", currency: "INR", balance: 450000, risk_score: 63, risk_level: "MEDIUM", is_flagged_mule: false, branch_id: null, opened_at: daysAgo(2), created_at: daysAgo(2), updated_at: hoursAgo(7), status: "ACTIVE" },
];

// -----------------------------------------------------------------------------
// Transactions
// -----------------------------------------------------------------------------
const channels = ["UPI", "NEFT", "IMPS", "RTGS"] as const;
const cities = ["Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Chennai", "Kolkata", "Pune", "Jaipur"];
const patterns = ["MULE_CHAIN", "FAN_IN_COLLECTOR", "SMURFING", "SHARED_DEVICE", "VELOCITY_SPIKE", null, null, null];

export const mockTransactions: TransactionRead[] = Array.from({ length: 30 }, (_, i) => ({
  id: uuid(200 + i),
  transaction_ref: `UTR${(900000000 + i * 7919).toString()}`,
  channel: channels[i % 4],
  amount: Math.round((5000 + Math.random() * 495000) * 100) / 100,
  currency: "INR",
  timestamp: hoursAgo(i * 0.8),
  location_city: cities[i % cities.length],
  location_state: ["Maharashtra", "Delhi", "Karnataka", "Telangana", "Tamil Nadu", "West Bengal", "Maharashtra", "Rajasthan"][i % 8],
  ip_address_str: `${103 + (i % 4)}.${21 + (i % 10)}.${140 + i}.${10 + i}`,
  device_fingerprint: i % 3 === 0 ? `fp-samsung-s23-${Math.floor(i / 3)}` : i % 5 === 0 ? `fp-iphone-15-${Math.floor(i / 5)}` : null,
  sender_account_id: uuid(101 + (i % 6)),
  receiver_account_id: uuid(107 + (i % 6)),
  risk_score: Math.min(99, Math.max(10, Math.round(40 + Math.random() * 55))),
  flagged_pattern: patterns[i % patterns.length],
  narrative: i % 4 === 0 ? "Fund transfer - personal" : null,
  created_at: hoursAgo(i * 0.8),
  status: "COMPLETED",
}));

// -----------------------------------------------------------------------------
// Dashboard
// -----------------------------------------------------------------------------
export const mockPatterns: PatternHitSummary[] = [
  { pattern_name: "Mule Chain", hit_count: 47, severity: "CRITICAL" },
  { pattern_name: "Fan-In Collector", hit_count: 38, severity: "CRITICAL" },
  { pattern_name: "Velocity Spike", hit_count: 34, severity: "HIGH" },
  { pattern_name: "Shared Device", hit_count: 29, severity: "HIGH" },
  { pattern_name: "Impossible Travel", hit_count: 23, severity: "HIGH" },
  { pattern_name: "Smurfing/Structuring", hit_count: 21, severity: "HIGH" },
  { pattern_name: "Cross-Channel Layering", hit_count: 18, severity: "CRITICAL" },
  { pattern_name: "Dormant Activation", hit_count: 15, severity: "MEDIUM" },
  { pattern_name: "Round Amount", hit_count: 12, severity: "LOW" },
  { pattern_name: "Nighttime Burst", hit_count: 11, severity: "MEDIUM" },
  { pattern_name: "New Account Rapid", hit_count: 9, severity: "MEDIUM" },
  { pattern_name: "Fund Layering", hit_count: 8, severity: "HIGH" },
  { pattern_name: "Beneficiary Sprawl", hit_count: 6, severity: "MEDIUM" },
  { pattern_name: "Reverse Mule", hit_count: 4, severity: "CRITICAL" },
];

export const mockDashboard: DashboardOverviewResponse = {
  kpis: {
    total_transactions_24h: 14832,
    flagged_mule_accounts: 67,
    active_alerts_count: 23,
    total_volume_at_risk_inr: 48750000,
  },
  risk_distribution: { low: 1245, medium: 387, high: 156, critical: 67 },
  top_patterns: mockPatterns,
  recent_alerts: mockAlerts.slice(0, 8),
};

// -----------------------------------------------------------------------------
// Analytics
// -----------------------------------------------------------------------------
export const mockAnalytics: AnalyticsOverviewResponse = {
  time_series: Array.from({ length: 14 }, (_, i) => ({
    timestamp: new Date(Date.now() - (13 - i) * 86400000).toISOString().split("T")[0],
    total_volume: Math.round(80000000 + Math.random() * 40000000),
    flagged_volume: Math.round(3000000 + Math.random() * 5000000),
    alert_count: Math.round(8 + Math.random() * 20),
  })),
  channel_breakdown: [
    { channel: "UPI", transaction_count: 8934, total_amount_inr: 45670000, mule_percentage: 4.2 },
    { channel: "NEFT", transaction_count: 3210, total_amount_inr: 89450000, mule_percentage: 2.8 },
    { channel: "IMPS", transaction_count: 2145, total_amount_inr: 23400000, mule_percentage: 5.1 },
    { channel: "RTGS", transaction_count: 543, total_amount_inr: 156000000, mule_percentage: 1.3 },
  ],
  geo_clusters: [
    { city: "Mumbai", state: "Maharashtra", latitude: 19.076, longitude: 72.8777, active_mules_count: 34, total_alert_count: 89 },
    { city: "Delhi", state: "Delhi", latitude: 28.7041, longitude: 77.1025, active_mules_count: 28, total_alert_count: 72 },
    { city: "Bengaluru", state: "Karnataka", latitude: 12.9716, longitude: 77.5946, active_mules_count: 19, total_alert_count: 45 },
    { city: "Hyderabad", state: "Telangana", latitude: 17.385, longitude: 78.4867, active_mules_count: 15, total_alert_count: 38 },
    { city: "Chennai", state: "Tamil Nadu", latitude: 13.0827, longitude: 80.2707, active_mules_count: 12, total_alert_count: 31 },
  ],
};

// -----------------------------------------------------------------------------
// Graph Intelligence
// -----------------------------------------------------------------------------
export const mockGraph: GraphResponse = {
  nodes: [
    // Critical Risk Accounts (90-100) — Red Glow
    {
      id: "acc-101",
      label: "XXXX1001 — R. Sharma",
      type: "account",
      risk_score: 96,
      account_number: "XXXX1001",
      customer_name: "Rajesh Kumar Sharma",
      bank: "State Bank of India",
      phone: "+91 98765 11001",
      device: "Samsung Galaxy S23",
      ip: "103.21.140.88",
      location: "Mumbai, MH",
      last_transaction: "₹49,000 via UPI (12m ago)",
      total_received: 4850000,
      total_sent: 4790000,
      is_mule: true,
      community_id: "COMMUNITY-A12",
    },
    {
      id: "acc-102",
      label: "XXXX1002 — P. Nair (Mule Hub)",
      type: "account",
      risk_score: 93,
      account_number: "XXXX1002",
      customer_name: "Priya Venkatesh Nair",
      bank: "HDFC Bank",
      phone: "+91 98765 22002",
      device: "iPhone 15 Pro",
      ip: "104.22.155.12",
      location: "Mumbai, MH",
      last_transaction: "₹88,000 via UPI (25m ago)",
      total_received: 8900000,
      total_sent: 8850000,
      is_mule: true,
      community_id: "COMMUNITY-A12",
    },
    {
      id: "acc-103",
      label: "XXXX1003 — M. Ali",
      type: "account",
      risk_score: 87,
      account_number: "XXXX1003",
      customer_name: "Mohammed Irfan Ali",
      bank: "ICICI Bank",
      phone: "+91 98765 33003",
      device: "OnePlus 11",
      ip: "103.21.140.88",
      location: "Delhi, DL",
      last_transaction: "₹47,800 via IMPS (45m ago)",
      total_received: 1250000,
      total_sent: 1240000,
      is_mule: true,
      community_id: "COMMUNITY-A12",
    },
    {
      id: "acc-110",
      label: "XXXX1010 — A. Krishnamurthy",
      type: "account",
      risk_score: 91,
      account_number: "XXXX1010",
      customer_name: "Anitha Krishnamurthy",
      bank: "Axis Bank",
      phone: "+91 98765 00010",
      device: "Xiaomi 13 Pro",
      ip: "104.22.155.12",
      location: "Bengaluru, KA",
      last_transaction: "₹88,000 via UPI (18m ago)",
      total_received: 3400000,
      total_sent: 3380000,
      is_mule: true,
      community_id: "COMMUNITY-A12",
    },

    // High & Medium Risk Accounts (45-89) — Orange/Amber Glow
    {
      id: "acc-104",
      label: "XXXX1004 — D. Subramaniam",
      type: "account",
      risk_score: 82,
      account_number: "XXXX1004",
      customer_name: "Deepa Subramaniam",
      bank: "Kotak Mahindra Bank",
      phone: "+91 98765 44004",
      device: "Samsung Galaxy S23",
      ip: "103.21.140.90",
      location: "Chennai, TN",
      last_transaction: "₹35,000 via UPI (1h ago)",
      total_received: 980000,
      total_sent: 950000,
      is_mule: false,
      community_id: "COMMUNITY-A12",
    },
    {
      id: "acc-105",
      label: "XXXX1005 — A. Joshi",
      type: "account",
      risk_score: 71,
      account_number: "XXXX1005",
      customer_name: "Arun Prakash Joshi",
      bank: "Punjab National Bank",
      phone: "+91 98765 55005",
      device: "Realme GT 3",
      ip: "103.21.140.91",
      location: "Pune, MH",
      last_transaction: "₹28,000 via IMPS (2h ago)",
      total_received: 450000,
      total_sent: 440000,
      is_mule: false,
      community_id: "COMMUNITY-B04",
    },
    {
      id: "acc-106",
      label: "XXXX1006 — K. Reddy",
      type: "account",
      risk_score: 65,
      account_number: "XXXX1006",
      customer_name: "Kavitha Reddy Pillai",
      bank: "Canara Bank",
      phone: "+91 98765 66006",
      device: "Vivo X90",
      ip: "103.21.140.92",
      location: "Hyderabad, TS",
      last_transaction: "₹52,000 via NEFT (3h ago)",
      total_received: 620000,
      total_sent: 610000,
      is_mule: false,
      community_id: "COMMUNITY-B04",
    },
    {
      id: "acc-109",
      label: "XXXX1009 — V. Chauhan",
      type: "account",
      risk_score: 62,
      account_number: "XXXX1009",
      customer_name: "Vikram Singh Chauhan",
      bank: "Bank of Baroda",
      phone: "+91 98765 99009",
      device: "iQOO 11",
      ip: "104.22.155.12",
      location: "Jaipur, RJ",
      last_transaction: "₹52,000 via NEFT (3h ago)",
      total_received: 890000,
      total_sent: 870000,
      is_mule: false,
      community_id: "COMMUNITY-B04",
    },

    // Victim (Blue)
    {
      id: "vic-701",
      label: "Smt. Sunita Rao (Victim)",
      type: "victim",
      risk_score: 10,
      account_number: "XXXX7001",
      customer_name: "Sunita Rao",
      bank: "Union Bank of India",
      phone: "+91 98765 77001",
      device: "Redmi Note 12",
      ip: "49.207.54.12",
      location: "Nagpur, MH",
      last_transaction: "₹1,50,000 (Phishing Fraud Victim)",
      total_received: 50000,
      total_sent: 150000,
      is_mule: false,
      community_id: "COMMUNITY-A12",
    },

    // Devices (Purple)
    {
      id: "dev-501",
      label: "Samsung Galaxy S23 Ultra",
      type: "device",
      risk_score: 85,
      device: "Samsung S23 Ultra (IMEI: 359128...)",
      location: "Mumbai, MH",
      community_id: "COMMUNITY-A12",
    },

    // Phone (Green)
    {
      id: "phn-801",
      label: "+91 98765 00000 (Shared)",
      type: "phone",
      risk_score: 78,
      phone: "+91 98765 00000",
      location: "Delhi, DL",
      community_id: "COMMUNITY-A12",
    },

    // IP Address (Yellow)
    {
      id: "ip-601",
      label: "103.21.140.88 (Proxy IP)",
      type: "ip",
      risk_score: 82,
      ip: "103.21.140.88",
      location: "VPN Gateway — Mumbai",
      community_id: "COMMUNITY-A12",
    },

    // ATM (White)
    {
      id: "atm-901",
      label: "ATM Andheri West",
      type: "atm",
      risk_score: 65,
      location: "Andheri West, Mumbai",
      community_id: "COMMUNITY-A12",
    },

    // Crypto Wallet (Pink)
    {
      id: "crp-301",
      label: "0x71C...39F (USDT Wallet)",
      type: "crypto",
      risk_score: 95,
      account_number: "0x71C8a9f...39F",
      bank: "TRON / TRC-20 USDT",
      total_received: 12500000,
      total_sent: 12450000,
      is_mule: true,
      community_id: "COMMUNITY-A12",
    },

    // Merchant (Gray)
    {
      id: "mch-401",
      label: "FastPay Online Retail",
      type: "merchant",
      risk_score: 20,
      customer_name: "FastPay Payment Gateway",
      bank: "Razorpay Merchant",
      location: "Bengaluru, KA",
      community_id: "COMMUNITY-[#C4]",
    },

    // Clean Original Accounts (Green)
    {
      id: "acc-108",
      label: "XXXX1008 — L. Gupta",
      type: "account",
      risk_score: 18,
      account_number: "XXXX1008",
      customer_name: "Lakshmi Devi Gupta",
      bank: "State Bank of India",
      phone: "+91 98765 88008",
      location: "Lucknow, UP",
      last_transaction: "₹15,000 via UPI (5h ago)",
      total_received: 240000,
      total_sent: 180000,
      is_mule: false,
      community_id: "COMMUNITY-C01",
    },
    {
      id: "acc-111",
      label: "XXXX1011 — R. Mehta",
      type: "account",
      risk_score: 15,
      account_number: "XXXX1011",
      customer_name: "Rahul Mehta",
      bank: "HDFC Bank",
      phone: "+91 98765 11011",
      location: "Ahmedabad, GJ",
      last_transaction: "₹12,000 via NEFT (6h ago)",
      total_received: 310000,
      total_sent: 290000,
      is_mule: false,
      community_id: "COMMUNITY-C01",
    },
  ],
  edges: [
    // Victim → Mule Hub
    { source: "vic-701", target: "acc-101", relationship: "TRANSFERRED_FUNDS", amount: 150000, channel: "IMPS", timestamp: "10m ago" },

    // Mule Chain Transfers (Red)
    { source: "acc-101", target: "acc-102", relationship: "TRANSFERRED_FUNDS", amount: 49000, channel: "UPI", timestamp: "12m ago" },
    { source: "acc-102", target: "acc-103", relationship: "TRANSFERRED_FUNDS", amount: 48500, channel: "UPI", timestamp: "15m ago" },
    { source: "acc-103", target: "acc-104", relationship: "TRANSFERRED_FUNDS", amount: 47800, channel: "IMPS", timestamp: "22m ago" },
    { source: "acc-110", target: "acc-102", relationship: "TRANSFERRED_FUNDS", amount: 88000, channel: "UPI", timestamp: "18m ago" },
    { source: "acc-102", target: "crp-301", relationship: "TRANSFERRED_FUNDS", amount: 250000, channel: "CRYPTO_CASHOUT", timestamp: "30m ago" },

    // Shared Links
    { source: "acc-101", target: "dev-501", relationship: "SHARED_DEVICE" },
    { source: "acc-104", target: "dev-501", relationship: "SHARED_DEVICE" },
    { source: "acc-101", target: "ip-601", relationship: "SHARED_IP" },
    { source: "acc-103", target: "ip-601", relationship: "SHARED_IP" },
    { source: "acc-102", target: "phn-801", relationship: "SHARED_PHONE" },
    { source: "acc-110", target: "phn-801", relationship: "SHARED_PHONE" },

    // Medium Risk Transfers (Orange/Amber)
    { source: "acc-104", target: "acc-105", relationship: "TRANSFERRED_FUNDS", amount: 35000, channel: "UPI", timestamp: "1h ago" },
    { source: "acc-106", target: "acc-109", relationship: "TRANSFERRED_FUNDS", amount: 52000, channel: "NEFT", timestamp: "3h ago" },
    { source: "acc-105", target: "acc-107", relationship: "TRANSFERRED_FUNDS", amount: 28000, channel: "IMPS", timestamp: "2h ago" },
    { source: "acc-105", target: "atm-901", relationship: "WITHDREW_FUNDS", amount: 40000, channel: "ATM_CASH", timestamp: "4h ago" },

    // Clean Transactions (Green)
    { source: "acc-111", target: "acc-108", relationship: "TRANSFERRED_FUNDS", amount: 15000, channel: "UPI", timestamp: "5h ago" },
    { source: "acc-108", target: "mch-401", relationship: "TRANSFERRED_FUNDS", amount: 3200, channel: "UPI_MERCHANT", timestamp: "6h ago" },
  ],
  community_id: "COMMUNITY-A12",
};

// -----------------------------------------------------------------------------
// Geo Intelligence
// -----------------------------------------------------------------------------
export const mockGeo: GeoIntelligenceResponse = {
  impossible_travel_alerts: [
    { account_number: "XXXX1003", origin: "Mumbai", destination: "Delhi", distance_km: 1400, time_gap_minutes: 15, flagged: true },
    { account_number: "XXXX1009", origin: "Chennai", destination: "Kolkata", distance_km: 1660, time_gap_minutes: 22, flagged: true },
    { account_number: "XXXX1005", origin: "Bengaluru", destination: "Hyderabad", distance_km: 570, time_gap_minutes: 8, flagged: true },
  ],
  regional_clusters: [
    { city: "Mumbai", mule_count: 34, lat: 19.076, lng: 72.8777 },
    { city: "Delhi", mule_count: 28, lat: 28.7041, lng: 77.1025 },
    { city: "Bengaluru", mule_count: 19, lat: 12.9716, lng: 77.5946 },
    { city: "Hyderabad", mule_count: 15, lat: 17.385, lng: 78.4867 },
    { city: "Chennai", mule_count: 12, lat: 13.0827, lng: 80.2707 },
  ],
};

// -----------------------------------------------------------------------------
// Investigations
// -----------------------------------------------------------------------------
export const mockInvestigations: InvestigationCase[] = [
  { case_number: "CAS-2025-0045", title: "Mule Ring Operation — Western Region", priority: "CRITICAL", case_status: "IN_PROGRESS", assigned_investigator_id: "INV-882", alerts_count: 8 },
  { case_number: "CAS-2025-0046", title: "Fan-In Collector Network — Andheri Hub", priority: "HIGH", case_status: "IN_PROGRESS", assigned_investigator_id: "INV-445", alerts_count: 5 },
  { case_number: "CAS-2025-0047", title: "Cross-Channel Layering — South Zone", priority: "HIGH", case_status: "OPEN", assigned_investigator_id: "INV-331", alerts_count: 3 },
  { case_number: "CAS-2025-0048", title: "Shared Device Fraud Cluster — Delhi NCR", priority: "MEDIUM", case_status: "IN_PROGRESS", assigned_investigator_id: "INV-882", alerts_count: 4 },
  { case_number: "CAS-2025-0049", title: "Dormant Account Activation Series", priority: "LOW", case_status: "CLOSED", assigned_investigator_id: "INV-112", alerts_count: 2 },
];

// -----------------------------------------------------------------------------
// Reports
// -----------------------------------------------------------------------------
export const mockReports: ReportRead[] = [
  { id: uuid(301), report_number: "STR-2025-0012", report_type: "STR", title: "Suspicious Transaction Report — Mule Ring Western Region", generated_at: daysAgo(1), file_path: "/reports/STR-2025-0012.pdf", summary_text: "Investigation revealed a 5-node mule chain operating across UPI and IMPS channels, processing approximately ₹48.7L in 72 hours. Principal beneficiary account XXXX1002 identified as fan-in collector hub.", case_id: uuid(501), created_at: daysAgo(1), status: "GENERATED" },
  { id: uuid(302), report_number: "CTR-2025-0008", report_type: "CTR", title: "Currency Transaction Report — High Value RTGS Transfers", generated_at: daysAgo(3), file_path: "/reports/CTR-2025-0008.pdf", summary_text: "Report covers 12 RTGS transfers exceeding ₹10L each, originating from accounts flagged for velocity anomalies.", case_id: null, created_at: daysAgo(3), status: "SUBMITTED" },
  { id: uuid(303), report_number: "STR-2025-0011", report_type: "STR", title: "Suspicious Activity — Impossible Travel Pattern", generated_at: daysAgo(5), file_path: "/reports/STR-2025-0011.pdf", summary_text: "Account XXXX1003 exhibited impossible travel patterns between Mumbai and Delhi with 15-minute gaps between transactions.", case_id: uuid(501), created_at: daysAgo(5), status: "SUBMITTED" },
  { id: uuid(304), report_number: "EXB-2025-0003", report_type: "EXECUTIVE_BRIEF", title: "Weekly Executive Brief — Fraud Trends", generated_at: daysAgo(7), file_path: null, summary_text: "Weekly summary of fraud detection metrics showing 23% increase in mule chain patterns and 15% decrease in smurfing attempts.", case_id: null, created_at: daysAgo(7), status: "DRAFT" },
];

// -----------------------------------------------------------------------------
// Pagination Helper
// -----------------------------------------------------------------------------
export function paginate<T>(items: T[], page: number, pageSize: number): { data: T[]; pagination: PaginationMeta } {
  const total = items.length;
  const totalPages = Math.ceil(total / pageSize);
  const start = (page - 1) * pageSize;
  const data = items.slice(start, start + pageSize);
  return {
    data,
    pagination: {
      total_items: total,
      page,
      page_size: pageSize,
      total_pages: totalPages,
      has_next: page < totalPages,
      has_prev: page > 1,
    },
  };
}
