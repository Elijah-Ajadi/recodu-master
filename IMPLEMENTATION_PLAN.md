# Recodu Implementation Plan

## Phase 1: Foundation & Authentication (Week 1)

### 1.1 Project Structure
- Create Django apps: `accounts`, `patients`, `vitals`, `dashboard`
- Configure `settings.py` with custom user model, timezone (Africa/Lagos), static/media paths
- Set up base HTML template with CSS variables design system
- Create navigation layout with role-aware menu rendering

### 1.2 Custom User Model & RBAC
- Extend `AbstractUser` with role field (`UNIT_HEAD`, `VOLUNTEER`)
- Build login/logout views with session management
- Implement middleware for role-based redirect (Unit Head → Dashboard, Volunteer → Intake)
- Create registration view (Unit Head only) for adding new volunteers
- Add session timeout logic (JavaScript idle timer + server-side `SESSION_COOKIE_AGE`)

### 1.3 Base Templates & CSS Design System
- Define CSS custom properties: color palette (green/amber/red flags), spacing scale, typography
- Build responsive grid/flexbox layout (mobile-first)
- Create reusable components: navbar, sidebar, cards, modals, form inputs, badges
- Implement dark-mode-ready variable structure

**Deliverables:** Working auth system, role-based navigation, responsive base UI

---

## Phase 2: Patient Management (Week 2)

### 2.1 Patient Model
- Fields: first_name, last_name, phone (unique), gender, age_range, blood_group, genotype, known_conditions (JSON/ManyToMany), created_at, updated_at
- Add model-level validation (phone format, valid blood groups/genotypes)
- Create migrations and admin registration

### 2.2 Patient Intake & Smart Search
- Build patient registration form with modal UI
- Implement AJAX search endpoint (`/api/patients/search/?q=`)
- JavaScript debounce on search input, async fetch, dropdown results rendering
- 15-second registration flow: minimal fields, instant submit, success feedback

### 2.3 Patient Profile & Baseline Display
- Profile view: patient details, emergency badge row (blood group, genotype)
- Multi-select condition tags with color coding (Hypertension=red, Diabetes=amber, etc.)
- "No Known Conditions" neutral tag fallback
- Tab-indexed form flow for rapid data entry

**Deliverables:** Full patient CRUD, instant search modal, profile with health badges

---

## Phase 3: Vitals Entry & Validation (Week 3)

### 3.1 Vitals Model
- Fields: patient (FK), systolic, diastolic, pulse, temperature, glucose_type (FBS/RBS), glucose_value, notes, recorded_by (FK to User), recorded_at, created_at
- Model validators for clinical ranges (BP: 60-250/40-180, temp: 30-45°C, glucose: 1-40 mmol/L)

### 3.2 Vitals Entry Form
- Single-page form with tabindex-ordered inputs
- Glucose toggle: styled radio group (FBS/RBS)
- Real-time JS validation on `input`/`blur` events:
  - Border color changes: green (normal), amber (elevated), red (critical)
  - Display threshold hints inline
- Server-side validation as security boundary (Django form `clean_*` methods)

### 3.3 Edit Lock Mechanism
- Track `created_at` timestamp on each vitals record
- JavaScript blocks edit UI after 5 minutes
- "Request Correction" flag field on model
- Unit Head dashboard shows flagged records queue

**Deliverables:** Vitals entry with live validation, 5-minute edit lock, correction request system

---

## Phase 4: Historical Timeline & Visualization (Week 4)

### 4.1 Sequential List Feed
- Patient history view: vitals records ordered newest-first
- Each card shows: date, all metrics, micro-indicators (↑↓ arrows vs previous reading)
- Color-coded metric values matching threshold system
- Medical notes drawer: CSS slide-out panel with timestamp, volunteer name, remarks, medications

### 4.2 Chart.js Graph View
- Toggle button switches between list and canvas view
- Line chart plotting: BP (systolic/diastolic dual lines), glucose over time, temperature
- Chart.js via CDN, initialized with Django-rendered JSON data
- Responsive chart sizing for mobile screens

### 4.3 Filtering & Date Range
- Date range picker on history view
- Filter by vitals type (BP only, glucose only, all)
- Pagination or infinite scroll for long histories

**Deliverables:** Dual-view history (list + chart), trend indicators, notes drawer

---

## Phase 5: Admin Dashboard & Reporting (Week 5)

### 5.1 Service Summary Dashboard (Unit Head)
- Real-time stats cards: Total Checked Today, High-Risk Anomalies, Referrals Issued
- Query logic: count vitals records for today, flag readings exceeding thresholds
- Recent activity feed: last 10 check-ups across all patients
- Correction requests queue with approve/reject actions

### 5.2 Data Export Engine
- CSV export view: filtered patient data + vitals history
- Streaming `HttpResponse` with `csv` module
- Export filters: date range, specific patients, specific metrics
- One-click download button on dashboard

### 5.3 User Management (Unit Head)
- List all volunteers with status (active/inactive)
- Deactivate/reactivate accounts
- View system activity logs (login times, records created)

**Deliverables:** Unit Head dashboard, CSV export, user management panel

---

## Phase 6: Polish, Security & Deployment Prep (Week 6)

### 6.1 Security Hardening
- CSRF protection on all forms (Django default)
- Rate limiting on search API endpoint
- Input sanitization on all user-facing fields
- Session security: `SESSION_COOKIE_HTTPONLY`, `SESSION_COOKIE_SECURE` (production)
- Password reset flow for volunteers

### 6.2 Performance & UX Polish
- Database indexing on frequently queried fields (phone, recorded_at, patient FK)
- Pagination on all list views
- Loading states on AJAX calls
- Error toast notifications for failed submissions
- Accessibility audit: keyboard navigation, ARIA labels, contrast ratios

### 6.3 Deployment Preparation
- `requirements.txt` with pinned versions
- `.env` configuration for SECRET_KEY, DEBUG, DATABASE_URL
- SQLite → PostgreSQL migration guide
- `gunicorn` + `whitenoise` configuration
- Dockerfile and `docker-compose.yml` (optional)
- Production `settings.py` split (base.py, production.py)

**Deliverables:** Production-ready codebase, deployment docs, security audit complete

---

## Technical Reference

### Database Schema Overview

```
User (Custom)
├── id, email, role, is_active, date_joined

Patient
├── id, first_name, last_name, phone (unique), gender, age_range
├── blood_group, genotype
├── known_conditions (JSONField)
├── created_at, updated_at

VitalsRecord
├── id, patient (FK), recorded_by (FK to User)
├── systolic, diastolic, pulse, temperature
├── glucose_type (FBS/RBS), glucose_value
├── notes, medications
├── correction_requested (bool), correction_approved (bool)
├── recorded_at, created_at

CorrectionRequest (optional separate model)
├── id, vitals_record (FK), requested_by (FK), reason, status, reviewed_by (FK), reviewed_at
```

### URL Structure

```
/accounts/login/
/accounts/logout/
/accounts/register/        (Unit Head only)

/patients/search/          (AJAX endpoint)
/patients/create/
/patients/<id>/
/patients/<id>/history/

/vitals/create/
/vitals/<id>/edit/         (Unit Head or within 5-min window)
/vitals/<id>/request-correction/

/dashboard/                (role-aware: volunteer sees intake, unit head sees stats)
/dashboard/export/         (Unit Head only)
/dashboard/users/          (Unit Head only)
```

### Clinical Threshold Reference (for JS + Django validation)

| Metric | Normal | Elevated (Amber) | Critical (Red) |
|--------|--------|------------------|----------------|
| Systolic BP | < 120 | 120-139 | ≥ 140 |
| Diastolic BP | < 80 | 80-89 | ≥ 90 |
| Pulse | 60-100 | 100-120 | > 120 or < 60 |
| Temperature | 36.1-37.2°C | 37.3-38.0°C | > 38.0°C or < 36.1°C |
| FBS Glucose | 3.9-5.5 mmol/L | 5.6-6.9 mmol/L | ≥ 7.0 mmol/L |
| RBS Glucose | < 7.8 mmol/L | 7.8-11.0 mmol/L | > 11.0 mmol/L |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| High-volume queue slowdown | AJAX search with debounce, minimal form fields, tabindex flow |
| Data entry errors | Dual validation (JS + Django), 5-min edit lock, correction request system |
| Shared device security | Session timeout via JS idle timer, auto-logout on inactivity |
| Low-end device compatibility | No frontend framework, vanilla JS, CSS-only animations, Chart.js via CDN |
| Data loss during export | Streaming CSV response, no in-memory buffering of full dataset |

---

## Success Criteria

1. Volunteer can register a new patient in under 15 seconds
2. Search returns results in under 500ms for 1000+ patient database
3. All vitals entries validated client-side and server-side
4. Unit Head dashboard loads in under 2 seconds with full day metrics
5. CSV export handles 10,000+ records without timeout
6. Application passes Lighthouse mobile performance score > 85
7. Zero PII exposed to unauthorized roles (RBAC enforced at view and template level)
