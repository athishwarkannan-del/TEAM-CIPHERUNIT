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
  {
    "id": "acc-SB6200630",
    "label": "SB6200630 \u2014 Deepa Krishnan",
    "type": "account",
    "risk_score": 18,
    "account_number": "SB6200630",
    "customer_name": "Deepa Krishnan",
    "bank": "State Bank of India",
    "phone": "+91 9566163810",
    "device": "Oppo A78",
    "ip": "199.43.199.225",
    "location": "Pincode 641001",
    "last_transaction": "\u20b91,517.46 via IMPS",
    "total_received": 1821,
    "total_sent": 1517,
    "is_mule": false,
    "community_id": "COMMUNITY-B04"
  },
  {
    "id": "acc-SB12127354",
    "label": "SB12127354 \u2014 Deepa Krishnan",
    "type": "account",
    "risk_score": 18,
    "account_number": "SB12127354",
    "customer_name": "Deepa Krishnan",
    "bank": "State Bank of India",
    "location": "Pincode 641001",
    "is_mule": false,
    "community_id": "COMMUNITY-B04"
  },
  {
    "id": "dev-7018",
    "label": "Oppo A78",
    "type": "device",
    "risk_score": 19,
    "device": "Oppo A78",
    "community_id": "COMMUNITY-A12"
  },
  {
    "id": "ip-199_43_199_225",
    "label": "199.43.199.225 (Network)",
    "type": "ip",
    "risk_score": 17,
    "ip": "199.43.199.225",
    "community_id": "COMMUNITY-A12"
  },
  {
    "id": "acc-SB00009100",
    "label": "SB00009100 \u2014 Sanjay",
    "type": "account",
    "risk_score": 90,
    "account_number": "SB00009100",
    "customer_name": "Sanjay",
    "bank": "State Bank of India",
    "phone": "+91 9786579303",
    "device": "iPhone 14",
    "ip": "130.247.90.178",
    "location": "Pincode 560001",
    "last_transaction": "\u20b944,794.35 via UPI",
    "total_received": 53753,
    "total_sent": 44794,
    "is_mule": true,
    "community_id": "COMMUNITY-A12"
  },
  {
    "id": "acc-YS00056296",
    "label": "YS00056296 \u2014 Mukesh Joshi",
    "type": "account",
    "risk_score": 72,
    "account_number": "YS00056296",
    "customer_name": "Mukesh Joshi",
    "bank": "YES Bank",
    "location": "Pincode 302001",
    "is_mule": false,
    "community_id": "COMMUNITY-A12"
  },
  {
    "id": "dev-2866",
    "label": "iPhone 14",
    "type": "device",
    "risk_score": 74,
    "device": "iPhone 14",
    "community_id": "COMMUNITY-A12"
  },
  {
    "id": "ip-130_247_90_178",
    "label": "130.247.90.178 (Network)",
    "type": "ip",
    "risk_score": 65,
    "ip": "130.247.90.178",
    "community_id": "COMMUNITY-A12"
  },
  {
    "id": "acc-SB00009199",
    "label": "SB00009199 \u2014 Sakthi Prakash",
    "type": "account",
    "risk_score": 91,
    "account_number": "SB00009199",
    "customer_name": "Sakthi Prakash",
    "bank": "State Bank of India",
    "phone": "+91 9797801251",
    "device": "iPhone 14",
    "ip": "103.42.240.225",
    "location": "Pincode 600001",
    "last_transaction": "\u20b944,532.52 via UPI",
    "total_received": 53439,
    "total_sent": 44533,
    "is_mule": true,
    "community_id": "COMMUNITY-A12"
  },
  {
    "id": "acc-SB41222178",
    "label": "SB41222178 \u2014 Rakesh Agarwal",
    "type": "account",
    "risk_score": 73,
    "account_number": "SB41222178",
    "customer_name": "Rakesh Agarwal",
    "bank": "State Bank of India",
    "location": "Pincode 380001",
    "is_mule": false,
    "community_id": "COMMUNITY-A12"
  },
  {
    "id": "ip-103_42_240_225",
    "label": "103.42.240.225 (Network)",
    "type": "ip",
    "risk_score": 85,
    "ip": "103.42.240.225",
    "community_id": "COMMUNITY-A12"
  },
  {
    "id": "acc-SB00009834",
    "label": "SB00009834 \u2014 Yogesh Nair",
    "type": "account",
    "risk_score": 85,
    "account_number": "SB00009834",
    "customer_name": "Yogesh Nair",
    "bank": "State Bank of India",
    "phone": "+91 9133729406",
    "device": "Xiaomi Redmi Note 13",
    "ip": "151.121.142.172",
    "location": "Pincode 462001",
    "last_transaction": "\u20b944,228.82 via NEFT",
    "total_received": 53075,
    "total_sent": 44229,
    "is_mule": true,
    "community_id": "COMMUNITY-A12"
  },
  {
    "id": "acc-YS00071678",
    "label": "YS00071678 \u2014 Ramesh Babu",
    "type": "account",
    "risk_score": 68,
    "account_number": "YS00071678",
    "customer_name": "Ramesh Babu",
    "bank": "YES Bank",
    "location": "Pincode 530001",
    "is_mule": false,
    "community_id": "COMMUNITY-A12"
  },
  {
    "id": "dev-9493",
    "label": "Xiaomi Redmi Note 13",
    "type": "device",
    "risk_score": 65,
    "device": "Xiaomi Redmi Note 13",
    "community_id": "COMMUNITY-A12"
  },
  {
    "id": "ip-151_121_142_172",
    "label": "151.121.142.172 (Network)",
    "type": "ip",
    "risk_score": 69,
    "ip": "151.121.142.172",
    "community_id": "COMMUNITY-A12"
  },
  {
    "id": "acc-SB3629445",
    "label": "SB3629445 \u2014 Arjun Sharma",
    "type": "account",
    "risk_score": 7,
    "account_number": "SB3629445",
    "customer_name": "Arjun Sharma",
    "bank": "State Bank of India",
    "phone": "+91 9460065542",
    "device": "Samsung Galaxy A54",
    "ip": "208.37.161.229",
    "location": "Pincode 462001",
    "last_transaction": "\u20b92,278.25 via NEFT",
    "total_received": 2734,
    "total_sent": 2278,
    "is_mule": false,
    "community_id": "COMMUNITY-B04"
  },
  {
    "id": "acc-SB68166960",
    "label": "SB68166960 \u2014 Deepa Krishnan",
    "type": "account",
    "risk_score": 7,
    "account_number": "SB68166960",
    "customer_name": "Deepa Krishnan",
    "bank": "State Bank of India",
    "location": "Pincode 462001",
    "is_mule": false,
    "community_id": "COMMUNITY-B04"
  },
  {
    "id": "dev-7622",
    "label": "Samsung Galaxy A54",
    "type": "device",
    "risk_score": 12,
    "device": "Samsung Galaxy A54",
    "community_id": "COMMUNITY-A12"
  },
  {
    "id": "ip-208_37_161_229",
    "label": "208.37.161.229 (Network)",
    "type": "ip",
    "risk_score": 9,
    "ip": "208.37.161.229",
    "community_id": "COMMUNITY-A12"
  },
  {
    "id": "acc-AX00035760",
    "label": "AX00035760 \u2014 Amit Khanna",
    "type": "account",
    "risk_score": 89,
    "account_number": "AX00035760",
    "customer_name": "Amit Khanna",
    "bank": "Axis Bank",
    "phone": "+91 9242224154",
    "device": "Xiaomi Mi 11X",
    "ip": "82.189.145.41",
    "location": "Pincode 641001",
    "last_transaction": "\u20b947,290.44 via UPI",
    "total_received": 56749,
    "total_sent": 47290,
    "is_mule": true,
    "community_id": "COMMUNITY-A12"
  },
  {
    "id": "dev-6259",
    "label": "Xiaomi Mi 11X",
    "type": "device",
    "risk_score": 89,
    "device": "Xiaomi Mi 11X",
    "community_id": "COMMUNITY-A12"
  },
  {
    "id": "ip-82_189_145_41",
    "label": "82.189.145.41 (Network)",
    "type": "ip",
    "risk_score": 66,
    "ip": "82.189.145.41",
    "community_id": "COMMUNITY-A12"
  },
  {
    "id": "dev-3327",
    "label": "MacBook Pro",
    "type": "device",
    "risk_score": 90,
    "device": "MacBook Pro",
    "community_id": "COMMUNITY-A12"
  },
  {
    "id": "ip-141_124_242_207",
    "label": "141.124.242.207 (Network)",
    "type": "ip",
    "risk_score": 70,
    "ip": "141.124.242.207",
    "community_id": "COMMUNITY-A12"
  },
  {
    "id": "acc-SB3373320",
    "label": "SB3373320 \u2014 Arjun Sharma",
    "type": "account",
    "risk_score": 12,
    "account_number": "SB3373320",
    "customer_name": "Arjun Sharma",
    "bank": "State Bank of India",
    "phone": "+91 9592539893",
    "device": "iPhone 13",
    "ip": "20.75.102.227",
    "location": "Pincode 226001",
    "last_transaction": "\u20b9843.40 via NEFT",
    "total_received": 1012,
    "total_sent": 843,
    "is_mule": false,
    "community_id": "COMMUNITY-B04"
  },
  {
    "id": "acc-SB50437430",
    "label": "SB50437430 \u2014 Arjun Sharma",
    "type": "account",
    "risk_score": 12,
    "account_number": "SB50437430",
    "customer_name": "Arjun Sharma",
    "bank": "State Bank of India",
    "location": "Pincode 226001",
    "is_mule": false,
    "community_id": "COMMUNITY-B04"
  },
  {
    "id": "dev-3197",
    "label": "iPhone 13",
    "type": "device",
    "risk_score": 22,
    "device": "iPhone 13",
    "community_id": "COMMUNITY-A12"
  },
  {
    "id": "ip-20_75_102_227",
    "label": "20.75.102.227 (Network)",
    "type": "ip",
    "risk_score": 10,
    "ip": "20.75.102.227",
    "community_id": "COMMUNITY-A12"
  },
  {
    "id": "acc-YS00037463",
    "label": "YS00037463 \u2014 Sandeep Jain",
    "type": "account",
    "risk_score": 94,
    "account_number": "YS00037463",
    "customer_name": "Sandeep Jain",
    "bank": "YES Bank",
    "phone": "+91 9969119330",
    "device": "iPhone 13",
    "ip": "212.251.52.224",
    "location": "Pincode 400001",
    "last_transaction": "\u20b944,268.54 via NEFT",
    "total_received": 53122,
    "total_sent": 44269,
    "is_mule": true,
    "community_id": "COMMUNITY-A12"
  },
  {
    "id": "ip-212_251_52_224",
    "label": "212.251.52.224 (Network)",
    "type": "ip",
    "risk_score": 65,
    "ip": "212.251.52.224",
    "community_id": "COMMUNITY-A12"
  },
  {
    "id": "acc-SB00053581",
    "label": "SB00053581 \u2014 Umesh Chandra",
    "type": "account",
    "risk_score": 90,
    "account_number": "SB00053581",
    "customer_name": "Umesh Chandra",
    "bank": "State Bank of India",
    "phone": "+91 9387484583",
    "device": "OnePlus 12",
    "ip": "53.221.28.213",
    "location": "Pincode 560001",
    "last_transaction": "\u20b946,032.64 via NEFT",
    "total_received": 55239,
    "total_sent": 46033,
    "is_mule": true,
    "community_id": "COMMUNITY-A12"
  },
  {
    "id": "acc-YS00085259",
    "label": "YS00085259 \u2014 Kailash Borah",
    "type": "account",
    "risk_score": 72,
    "account_number": "YS00085259",
    "customer_name": "Kailash Borah",
    "bank": "YES Bank",
    "location": "Pincode 500001",
    "is_mule": false,
    "community_id": "COMMUNITY-A12"
  },
  {
    "id": "dev-1390",
    "label": "OnePlus 12",
    "type": "device",
    "risk_score": 69,
    "device": "OnePlus 12",
    "community_id": "COMMUNITY-A12"
  },
  {
    "id": "ip-53_221_28_213",
    "label": "53.221.28.213 (Network)",
    "type": "ip",
    "risk_score": 82,
    "ip": "53.221.28.213",
    "community_id": "COMMUNITY-A12"
  },
  {
    "id": "acc-SB4153336",
    "label": "SB4153336 \u2014 Rekha Singh",
    "type": "account",
    "risk_score": 12,
    "account_number": "SB4153336",
    "customer_name": "Rekha Singh",
    "bank": "State Bank of India",
    "phone": "+91 9398326747",
    "device": "iPhone 15",
    "ip": "98.52.75.119",
    "location": "Pincode 682001",
    "last_transaction": "\u20b9837.70 via NEFT",
    "total_received": 1005,
    "total_sent": 838,
    "is_mule": false,
    "community_id": "COMMUNITY-B04"
  },
  {
    "id": "acc-SB24790683",
    "label": "SB24790683 \u2014 Priya Nair",
    "type": "account",
    "risk_score": 12,
    "account_number": "SB24790683",
    "customer_name": "Priya Nair",
    "bank": "State Bank of India",
    "location": "Pincode 682001",
    "is_mule": false,
    "community_id": "COMMUNITY-B04"
  },
  {
    "id": "dev-2955",
    "label": "iPhone 15",
    "type": "device",
    "risk_score": 24,
    "device": "iPhone 15",
    "community_id": "COMMUNITY-A12"
  },
  {
    "id": "ip-98_52_75_119",
    "label": "98.52.75.119 (Network)",
    "type": "ip",
    "risk_score": 7,
    "ip": "98.52.75.119",
    "community_id": "COMMUNITY-A12"
  },
  {
    "id": "acc-SB7005668",
    "label": "SB7005668 \u2014 Deepa Krishnan",
    "type": "account",
    "risk_score": 20,
    "account_number": "SB7005668",
    "customer_name": "Deepa Krishnan",
    "bank": "State Bank of India",
    "phone": "+91 9290252696",
    "device": "OnePlus 12",
    "ip": "51.236.189.240",
    "location": "Pincode 682001",
    "last_transaction": "\u20b94,919.30 via IMPS",
    "total_received": 5903,
    "total_sent": 4919,
    "is_mule": false,
    "community_id": "COMMUNITY-B04"
  },
  {
    "id": "acc-SB69670203",
    "label": "SB69670203 \u2014 Rekha Singh",
    "type": "account",
    "risk_score": 20,
    "account_number": "SB69670203",
    "customer_name": "Rekha Singh",
    "bank": "State Bank of India",
    "location": "Pincode 682001",
    "is_mule": false,
    "community_id": "COMMUNITY-B04"
  },
  {
    "id": "ip-51_236_189_240",
    "label": "51.236.189.240 (Network)",
    "type": "ip",
    "risk_score": 20,
    "ip": "51.236.189.240",
    "community_id": "COMMUNITY-A12"
  },
  {
    "id": "acc-YS00022643",
    "label": "YS00022643 \u2014 Puneet Arora",
    "type": "account",
    "risk_score": 93,
    "account_number": "YS00022643",
    "customer_name": "Puneet Arora",
    "bank": "YES Bank",
    "phone": "+91 9384602384",
    "device": "Windows 11 PC",
    "ip": "20.192.157.27",
    "location": "Pincode 800001",
    "last_transaction": "\u20b947,195.12 via UPI",
    "total_received": 56634,
    "total_sent": 47195,
    "is_mule": true,
    "community_id": "COMMUNITY-A12"
  },
  {
    "id": "dev-9932",
    "label": "Windows 11 PC",
    "type": "device",
    "risk_score": 91,
    "device": "Windows 11 PC",
    "community_id": "COMMUNITY-A12"
  },
  {
    "id": "ip-20_192_157_27",
    "label": "20.192.157.27 (Network)",
    "type": "ip",
    "risk_score": 76,
    "ip": "20.192.157.27",
    "community_id": "COMMUNITY-A12"
  },
  {
    "id": "acc-ID00070352",
    "label": "ID00070352 \u2014 Nirav Modi",
    "type": "account",
    "risk_score": 75,
    "account_number": "ID00070352",
    "customer_name": "Nirav Modi",
    "bank": "IDFC FIRST Bank",
    "phone": "+91 9369953851",
    "device": "Samsung Galaxy A54",
    "ip": "158.30.17.215",
    "location": "Pincode 160001",
    "last_transaction": "\u20b944,998.67 via NEFT",
    "total_received": 53998,
    "total_sent": 44999,
    "is_mule": true,
    "community_id": "COMMUNITY-A12"
  }
],
  edges: [
  {
    "source": "acc-SB6200630",
    "target": "acc-SB12127354",
    "relationship": "TRANSFERRED_FUNDS",
    "amount": 1517,
    "channel": "IMPS",
    "timestamp": "2025-07-01 15:20:38"
  },
  {
    "source": "acc-SB00009100",
    "target": "acc-YS00056296",
    "relationship": "TRANSFERRED_FUNDS",
    "amount": 44794,
    "channel": "UPI",
    "timestamp": "2025-07-01 11:06:41"
  },
  {
    "source": "acc-SB00009100",
    "target": "dev-2866",
    "relationship": "SHARED_DEVICE"
  },
  {
    "source": "acc-SB00009199",
    "target": "acc-SB41222178",
    "relationship": "TRANSFERRED_FUNDS",
    "amount": 44533,
    "channel": "UPI",
    "timestamp": "2025-07-01 10:40:36"
  },
  {
    "source": "acc-SB00009199",
    "target": "ip-103_42_240_225",
    "relationship": "SHARED_IP"
  },
  {
    "source": "acc-SB00009834",
    "target": "acc-YS00071678",
    "relationship": "TRANSFERRED_FUNDS",
    "amount": 44229,
    "channel": "NEFT",
    "timestamp": "2025-07-01 10:49:27"
  },
  {
    "source": "acc-SB00009834",
    "target": "ip-151_121_142_172",
    "relationship": "SHARED_IP"
  },
  {
    "source": "acc-SB3629445",
    "target": "acc-SB68166960",
    "relationship": "TRANSFERRED_FUNDS",
    "amount": 2278,
    "channel": "NEFT",
    "timestamp": "2025-07-01 14:45:10"
  },
  {
    "source": "acc-AX00035760",
    "target": "acc-SB00009199",
    "relationship": "TRANSFERRED_FUNDS",
    "amount": 47290,
    "channel": "UPI",
    "timestamp": "2025-07-01 11:56:39"
  },
  {
    "source": "acc-AX00035760",
    "target": "dev-6259",
    "relationship": "SHARED_DEVICE"
  },
  {
    "source": "acc-YS00071678",
    "target": "acc-SB00009199",
    "relationship": "TRANSFERRED_FUNDS",
    "amount": 49885,
    "channel": "RTGS",
    "timestamp": "2025-07-01 10:54:41"
  },
  {
    "source": "acc-YS00071678",
    "target": "dev-3327",
    "relationship": "SHARED_DEVICE"
  },
  {
    "source": "acc-SB3373320",
    "target": "acc-SB50437430",
    "relationship": "TRANSFERRED_FUNDS",
    "amount": 843,
    "channel": "NEFT",
    "timestamp": "2025-07-01 15:00:09"
  },
  {
    "source": "acc-YS00037463",
    "target": "acc-SB00009199",
    "relationship": "TRANSFERRED_FUNDS",
    "amount": 44269,
    "channel": "NEFT",
    "timestamp": "2025-07-01 09:16:52"
  },
  {
    "source": "acc-SB00053581",
    "target": "acc-YS00085259",
    "relationship": "TRANSFERRED_FUNDS",
    "amount": 46033,
    "channel": "NEFT",
    "timestamp": "2025-07-01 09:49:32"
  },
  {
    "source": "acc-SB4153336",
    "target": "acc-SB24790683",
    "relationship": "TRANSFERRED_FUNDS",
    "amount": 838,
    "channel": "NEFT",
    "timestamp": "2025-07-01 14:23:37"
  },
  {
    "source": "acc-SB7005668",
    "target": "acc-SB69670203",
    "relationship": "TRANSFERRED_FUNDS",
    "amount": 4919,
    "channel": "IMPS",
    "timestamp": "2025-07-01 13:23:42"
  },
  {
    "source": "acc-YS00022643",
    "target": "acc-SB00009199",
    "relationship": "TRANSFERRED_FUNDS",
    "amount": 47195,
    "channel": "UPI",
    "timestamp": "2025-07-01 10:34:48"
  },
  {
    "source": "acc-YS00022643",
    "target": "ip-20_192_157_27",
    "relationship": "SHARED_IP"
  },
  {
    "source": "acc-ID00070352",
    "target": "acc-PN00039469",
    "relationship": "TRANSFERRED_FUNDS",
    "amount": 44999,
    "channel": "NEFT",
    "timestamp": "2025-07-01 10:09:38"
  },
  {
    "source": "acc-ID00070352",
    "target": "dev-7622",
    "relationship": "SHARED_DEVICE"
  },
  {
    "source": "acc-ID00070352",
    "target": "ip-158_30_17_215",
    "relationship": "SHARED_IP"
  },
  {
    "source": "acc-SB7572195",
    "target": "acc-SB87666600",
    "relationship": "TRANSFERRED_FUNDS",
    "amount": 531,
    "channel": "UPI",
    "timestamp": "2025-07-01 13:12:02"
  },
  {
    "source": "acc-SB7786479",
    "target": "acc-SB48108152",
    "relationship": "TRANSFERRED_FUNDS",
    "amount": 204,
    "channel": "UPI",
    "timestamp": "2025-07-01 13:16:54"
  },
  {
    "source": "acc-ID00070352",
    "target": "acc-SB45884163",
    "relationship": "TRANSFERRED_FUNDS",
    "amount": 46046,
    "channel": "IMPS",
    "timestamp": "2025-07-01 12:32:46"
  },
  {
    "source": "acc-ID00070352",
    "target": "dev-9493",
    "relationship": "SHARED_DEVICE"
  },
  {
    "source": "acc-ID00070352",
    "target": "ip-103_27_145_232",
    "relationship": "SHARED_IP"
  },
  {
    "source": "acc-SB4181393",
    "target": "acc-SB62968985",
    "relationship": "TRANSFERRED_FUNDS",
    "amount": 3657,
    "channel": "IMPS",
    "timestamp": "2025-07-01 13:39:35"
  },
  {
    "source": "acc-SB7777424",
    "target": "acc-SB10447935",
    "relationship": "TRANSFERRED_FUNDS",
    "amount": 1446,
    "channel": "NEFT",
    "timestamp": "2025-07-01 15:08:12"
  },
  {
    "source": "acc-CN00007630",
    "target": "acc-SB00009199",
    "relationship": "TRANSFERRED_FUNDS",
    "amount": 48406,
    "channel": "IMPS",
    "timestamp": "2025-07-01 11:15:46"
  },
  {
    "source": "acc-CN00007630",
    "target": "dev-6115",
    "relationship": "SHARED_DEVICE"
  },
  {
    "source": "acc-SB00009199",
    "target": "acc-SB47207440",
    "relationship": "TRANSFERRED_FUNDS",
    "amount": 44165,
    "channel": "UPI",
    "timestamp": "2025-07-01 12:38:27"
  },
  {
    "source": "acc-SB00009199",
    "target": "dev-9493",
    "relationship": "SHARED_DEVICE"
  },
  {
    "source": "acc-SB00009199",
    "target": "ip-103_27_145_232",
    "relationship": "SHARED_IP"
  },
  {
    "source": "acc-YS00037463",
    "target": "acc-SB00009199",
    "relationship": "TRANSFERRED_FUNDS",
    "amount": 48698,
    "channel": "IMPS",
    "timestamp": "2025-07-01 09:12:39"
  },
  {
    "source": "acc-YS00037463",
    "target": "ip-198_216_174_72",
    "relationship": "SHARED_IP"
  },
  {
    "source": "acc-SB5314727",
    "target": "acc-SB30700047",
    "relationship": "TRANSFERRED_FUNDS",
    "amount": 2718,
    "channel": "UPI",
    "timestamp": "2025-07-01 13:21:13"
  },
  {
    "source": "acc-SB3718341",
    "target": "acc-SB30980122",
    "relationship": "TRANSFERRED_FUNDS",
    "amount": 3460,
    "channel": "NEFT",
    "timestamp": "2025-07-01 13:13:32"
  },
  {
    "source": "acc-SB2305411",
    "target": "acc-SB90142849",
    "relationship": "TRANSFERRED_FUNDS",
    "amount": 160,
    "channel": "NEFT",
    "timestamp": "2025-07-01 14:05:59"
  },
  {
    "source": "acc-YS00056296",
    "target": "acc-CN00007630",
    "relationship": "TRANSFERRED_FUNDS",
    "amount": 46250,
    "channel": "RTGS",
    "timestamp": "2025-07-01 11:13:11"
  },
  {
    "source": "acc-YS00056296",
    "target": "dev-3513",
    "relationship": "SHARED_DEVICE"
  },
  {
    "source": "acc-SB00009199",
    "target": "acc-SB67985905",
    "relationship": "TRANSFERRED_FUNDS",
    "amount": 47528,
    "channel": "UPI",
    "timestamp": "2025-07-01 09:19:12"
  },
  {
    "source": "acc-SB00009199",
    "target": "dev-7018",
    "relationship": "SHARED_DEVICE"
  },
  {
    "source": "acc-SB3140306",
    "target": "acc-SB45885781",
    "relationship": "TRANSFERRED_FUNDS",
    "amount": 2578,
    "channel": "IMPS",
    "timestamp": "2025-07-01 13:51:55"
  },
  {
    "source": "acc-SB2260713",
    "target": "acc-SB24030412",
    "relationship": "TRANSFERRED_FUNDS",
    "amount": 85,
    "channel": "UPI",
    "timestamp": "2025-07-01 14:22:54"
  },
  {
    "source": "acc-SB4783105",
    "target": "acc-SB86178952",
    "relationship": "TRANSFERRED_FUNDS",
    "amount": 3768,
    "channel": "IMPS",
    "timestamp": "2025-07-01 13:31:59"
  },
  {
    "source": "acc-CN00008455",
    "target": "acc-SB00009199",
    "relationship": "TRANSFERRED_FUNDS",
    "amount": 44651,
    "channel": "IMPS",
    "timestamp": "2025-07-01 11:36:50"
  },
  {
    "source": "acc-CN00008455",
    "target": "ip-145_96_164_5",
    "relationship": "SHARED_IP"
  },
  {
    "source": "acc-SB5483468",
    "target": "acc-SB89964091",
    "relationship": "TRANSFERRED_FUNDS",
    "amount": 2097,
    "channel": "NEFT",
    "timestamp": "2025-07-01 15:04:06"
  },
  {
    "source": "acc-SB9413034",
    "target": "acc-SB15938855",
    "relationship": "TRANSFERRED_FUNDS",
    "amount": 3763,
    "channel": "IMPS",
    "timestamp": "2025-07-01 15:01:45"
  },
  {
    "source": "acc-YS00037463",
    "target": "acc-SB00009199",
    "relationship": "TRANSFERRED_FUNDS",
    "amount": 46076,
    "channel": "IMPS",
    "timestamp": "2025-07-01 09:15:57"
  },
  {
    "source": "acc-YS00037463",
    "target": "ip-198_216_174_72",
    "relationship": "SHARED_IP"
  },
  {
    "source": "acc-SB00009199",
    "target": "acc-SB11243818",
    "relationship": "TRANSFERRED_FUNDS",
    "amount": 49173,
    "channel": "IMPS",
    "timestamp": "2025-07-01 10:00:02"
  },
  {
    "source": "acc-SB00009199",
    "target": "dev-1478",
    "relationship": "SHARED_DEVICE"
  },
  {
    "source": "acc-SB00009199",
    "target": "ip-103_42_240_225",
    "relationship": "SHARED_IP"
  },
  {
    "source": "acc-SB00009199",
    "target": "acc-SB36809908",
    "relationship": "TRANSFERRED_FUNDS",
    "amount": 45172,
    "channel": "RTGS",
    "timestamp": "2025-07-01 10:59:41"
  },
  {
    "source": "acc-SB00009199",
    "target": "dev-2955",
    "relationship": "SHARED_DEVICE"
  },
  {
    "source": "acc-SB1577888",
    "target": "acc-SB69590884",
    "relationship": "TRANSFERRED_FUNDS",
    "amount": 2221,
    "channel": "UPI",
    "timestamp": "2025-07-01 13:35:40"
  },
  {
    "source": "acc-SB00009199",
    "target": "acc-SB67881875",
    "relationship": "TRANSFERRED_FUNDS",
    "amount": 47190,
    "channel": "IMPS",
    "timestamp": "2025-07-01 12:22:06"
  },
  {
    "source": "acc-SB00009199",
    "target": "dev-2955",
    "relationship": "SHARED_DEVICE"
  }
],
  community_id: "COMMUNITY-A12",
};

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
