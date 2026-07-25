# Victim Complaint Intake: User Portal → Admin Reports Integration

## Problem Statement

A **separate User Portal** (developed on another team member's machine as a standalone web app) needs to send victim complaint data to our **MuleTrace AI Backend API**. When a victim submits a complaint on that portal, it should automatically appear under the **Reports** menu in our Admin Platform (`frontend/`).

---

## Data Requirements: What To Fetch From User Portal

The User Portal form collects these fields from victims:

| # | Field | Type | Required | Example |
|:--|:------|:-----|:---------|:--------|
| 1 | `transaction_id` | String (max 100) | Yes | `UTR2025MULE001` or `UPI/123456/789` |
| 2 | `victim_name` | String (max 200) | Yes | `Rahul Sharma` |
| 3 | `victim_email` | String (email) | Yes | `rahul.sharma@gmail.com` |
| 4 | `victim_phone` | String (max 15) | No | `+919876543210` |
| 5 | `incident_type` | Enum String | Yes | One of: `PHISHING`, `DIGITAL_ARREST`, `UPI_FRAUD`, `INVESTMENT_SCAM`, `JOB_FRAUD`, `LOAN_FRAUD`, `OTHER` |
| 6 | `amount_lost` | Float | No | `150000.00` |
| 7 | `incident_date` | DateTime | No | `2025-07-20T14:30:00Z` |
| 8 | `description` | Text (max 2000) | Yes | `"I received a call claiming to be from CBI..."` |

> [!IMPORTANT]
> The User Portal team needs to make **one single API call** to submit a complaint. Our backend handles everything else — storage, report generation, and admin visibility.

---

## How To Connect Both Systems

### Connection Architecture

```
 USER PORTAL                         MULETRACE AI BACKEND              ADMIN PLATFORM
 (Another System)                    (Your FastAPI on port 8000)        (Your Next.js on port 3000)
 ┌──────────────────┐               ┌───────────────────────┐          ┌────────────────────┐
 │                  │  HTTP POST    │                       │          │                    │
 │ Victim fills     ├──────────────►│ POST /api/v1/         │          │ Reports Menu       │
 │ complaint form   │               │ complaints/public/    │          │ shows complaints   │
 │                  │◄──────────────┤ submit                │          │ as VICTIM_COMPLAINT │
 │ Gets tracking ID │  JSON response│                       │          │ report type        │
 └──────────────────┘               │ Validates → Stores    │          └─────────┬──────────┘
                                    │ in `reports` table    │                    │
                                    │ as report_type =      │                    │
                                    │ "VICTIM_COMPLAINT"    │◄───────────────────┘
                                    │                       │  GET /api/v1/reports
                                    └───────────────────────┘  ?report_type=VICTIM_COMPLAINT
```

### The Connection Method: Simple REST API Call

The User Portal team makes **one `fetch()` / `axios.post()` call** from their frontend:

```javascript
// User Portal team adds this to their form submit handler:
const response = await fetch("http://<YOUR_BACKEND_IP>:8000/api/v1/complaints/public/submit", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
        transaction_id: "UTR2025MULE001",
        victim_name: "Rahul Sharma",
        victim_email: "rahul@gmail.com",
        incident_type: "DIGITAL_ARREST",
        amount_lost: 150000.00,
        description: "I was called by someone claiming to be CBI officer..."
    })
});

const data = await response.json();
// Response: { success: true, complaint_number: "CMP-2025-00042", status: "RECEIVED" }
```

> [!IMPORTANT]
> **Network Connection**: Both systems must be on the **same network** (e.g., same WiFi, same LAN, or same college network). The User Portal calls your backend using your machine's **local IP address** (e.g., `192.168.1.105:8000`) instead of `localhost:8000`. You find your IP by running `ipconfig` in terminal.

### CORS Configuration

Your backend `.env` file needs the User Portal's URL added to the allowed origins:

```
CORS_ORIGINS=["http://localhost:3000", "http://localhost:3001", "http://<USER_PORTAL_IP>:3002"]
```

---

## How Data Stores & Appears In Reports Menu

### Strategy: Store As A Report Row (Zero New Tables Needed)

Instead of creating a new `victim_complaints` table, we store each complaint directly as a row in the **existing `reports` table** with `report_type = "VICTIM_COMPLAINT"`. This means:

- The existing `GET /api/v1/reports?report_type=VICTIM_COMPLAINT` endpoint **already works** to list them.
- The existing Admin frontend Reports page **already fetches and displays** them.
- No database migration needed. No new table. No new frontend page.

### How The Data Maps To Existing Report Table Columns

| Report Column | Complaint Data Stored |
|:---|:---|
| `report_number` | `CMP-2025-00042` (auto-generated) |
| `report_type` | `"VICTIM_COMPLAINT"` |
| `title` | `"Victim Complaint: DIGITAL_ARREST — Rahul Sharma"` |
| `generated_at` | Timestamp of complaint submission |
| `file_path` | `null` (no file, just metadata) |
| `summary_text` | Full complaint details as structured JSON/text: transaction_id, victim_name, email, phone, incident_type, amount_lost, description |
| `case_id` | `null` initially (admin can link to a case later) |
| `status` | `"active"` (from TimestampMixin) |

---

## Proposed Changes

### Backend Changes (3 new files, 2 modified files)

---

#### [NEW] [victim_complaint.py](file:///c:/Users/athis/OneDrive/Desktop/Cipher/backend/app/schemas/victim_complaint.py)

Pydantic schemas for the public complaint submission endpoint:
- `VictimComplaintSubmit` — Input validation (transaction_id, victim_name, victim_email, incident_type, description, amount_lost, incident_date)
- `VictimComplaintResponse` — Returns complaint_number + status to the victim

---

#### [NEW] [victim_complaints.py](file:///c:/Users/athis/OneDrive/Desktop/Cipher/backend/app/api/v1/victim_complaints.py)

New API route file with 2 public endpoints:
- `POST /api/v1/complaints/public/submit` — Receives complaint from User Portal, validates, stores as report row, returns tracking ID
- `GET /api/v1/complaints/public/status/{complaint_number}` — Victim checks complaint status using their tracking ID

---

#### [NEW] [victim_complaint_service.py](file:///c:/Users/athis/OneDrive/Desktop/Cipher/backend/app/services/victim_complaint_service.py)

Business logic service that:
1. Validates the complaint payload
2. Generates a unique complaint number (`CMP-2025-XXXXX`)
3. Builds a `Report` object with `report_type="VICTIM_COMPLAINT"` and `summary_text` containing the full structured complaint details as JSON
4. Saves via existing `ReportRepository.create()`
5. Returns the complaint number

---

#### [MODIFY] [router.py](file:///c:/Users/athis/OneDrive/Desktop/Cipher/backend/app/api/v1/router.py)

Add the victim complaints router:
```python
from app.api.v1.victim_complaints import router as victim_complaints_router
api_v1_router.include_router(victim_complaints_router)
```

---

#### [MODIFY] [settings.py](file:///c:/Users/athis/OneDrive/Desktop/Cipher/backend/app/config/settings.py)

Update CORS to allow the User Portal origin:
```python
CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"]
```

---

### What The User Portal Team Needs To Do (On Their Side)

1. Add a form submit handler that POSTs JSON to `http://<YOUR_IP>:8000/api/v1/complaints/public/submit`
2. Display the returned `complaint_number` as a confirmation receipt to the victim
3. Optionally call `GET /api/v1/complaints/public/status/{complaint_number}` to show status updates

That is the **only integration point**. No shared database, no shared code, no complex setup.

---

### Admin Side: How Reports Menu Shows Complaints

The Admin Reports page already calls `GET /api/v1/reports`. When victim complaints are stored as `report_type = "VICTIM_COMPLAINT"`, they appear automatically in the Reports list. The admin can:

1. **Filter by type**: `GET /api/v1/reports?report_type=VICTIM_COMPLAINT` to see only victim complaints
2. **Click to view details**: The `summary_text` field contains the full structured complaint (transaction_id, victim_name, incident_type, description, amount_lost)
3. **Link to a case**: Admin can later associate the complaint with a `case_id` for further investigation

---

## Open Questions

> [!IMPORTANT]
> **Q1: Same Network or Internet?**
> Are both systems on the **same local network** (e.g., same WiFi / college LAN)? If yes, the User Portal calls `http://192.168.x.x:8000`. If the User Portal is deployed to the internet (e.g., Vercel/Netlify), then your backend also needs to be publicly accessible (e.g., deployed on Render).

> [!IMPORTANT]
> **Q2: Does the User Portal team need a specific API contract/documentation?**
> I can generate a simple API specification document that you can share with the other team, containing exact URL, JSON payload format, and expected responses.

> [!IMPORTANT]
> **Q3: Should victims be able to track complaint status?**
> If yes, we add the `GET /status/{complaint_number}` endpoint. If not, we skip it and only implement the submit endpoint.

---

## Verification Plan

### Automated Tests
- Direct test script calling `POST /api/v1/complaints/public/submit` and verifying the complaint appears in `GET /api/v1/reports?report_type=VICTIM_COMPLAINT`

### Manual Verification
- Submit a complaint via the test script → Check the Admin Reports page → Confirm the complaint appears as a `VICTIM_COMPLAINT` report type
