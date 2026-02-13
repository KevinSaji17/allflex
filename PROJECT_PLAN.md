# AllFlex — Project Plan

## Project overview

**AllFlex** is a gym and fitness membership platform: one membership for multiple gyms. Users can pay with **credits** (per visit) or choose **unlimited plans**. The project is built with Django, Tailwind CSS, and optional AI (Google Gemini) for gym discovery.

---

## MVP (Minimum Viable Product)

The MVP is the smallest version that proves the core idea:

> **A member can sign up, get credits (or pick a plan), find gyms by pincode, and use a visit (credits deducted).**

### In scope for MVP

| Area | Delivered |
|------|-----------|
| **Member** | Sign up, login, view Plans & Credits, see balance, Find Gyms by pincode, **Use 1 visit** (deduct credits) |
| **Credits** | Balance shown, deduction on “use visit”, seeded credit packs in DB |
| **Gym finder** | By pincode (Gemini API when key set; demo gyms when not) |
| **Plans page** | Credit packs + Unlimited plans tabs; clean, light design |

### Deferred (post-MVP)

- Real payment gateway and pack purchase flow  
- QR check-in, booking calendar  
- Full gym onboarding and payouts  
- Favorites, advanced recommendations  

---

## What was implemented

### 1. Project setup and runnability

- **`manage.py`** at project root using `allflex.settings`
- **`requirements.txt`** — Django, python-dotenv, django-tailwind, google-generativeai, Pillow
- **`.env`** and **`.env.example`** — SECRET_KEY, DEBUG, ALLOWED_HOSTS, optional GEMINI_API_KEY
- **ALLOWED_HOSTS** — configurable via env (default: localhost, 127.0.0.1)
- **Virtual environment** — `venv` at project root (recommended for running the app)
- **Migrations** — applied for accounts, gyms, users, admin, sessions
- **Seed** — `python manage.py seed_credit_packs` creates default credit packs

### 2. MVP “Use visit” flow

- **Endpoint:** `POST /use-visit/`  
  Body: `{ "gym_name": "...", "tier": 1 }`  
  Tier costs: 1 → 5 credits, 2 → 9, 3 → 13, 4 → 18.
- Deducts from `user.credits`, creates `CreditTransaction` (type `visit`, notes = gym name).
- **Dashboard:** Each gym from “Find Gyms” has a **“Use 1 visit (5 credits)”** button; on success, balance updates and a success message is shown.
- **New signups** receive **25 demo credits** so they can try a visit without buying.

### 3. Gym finder without API key

- If **GEMINI_API_KEY** is missing or empty, the gym finder returns **demo gyms** (no error).
- When the key is set in `.env`, Find Gyms uses the Gemini API for real results.

### 4. Plans page redesign

- **Full design revamp:** Light, warm fitness-app style (replacing the previous dark minimal design).
- **Hero:** Teal → emerald gradient, “Pick your pace” headline.
- **Tabs:** Credit Packs | Unlimited (pill on a floating white card).
- **Balance card:** White card with teal accent and tier visit counts (T1–T4).
- **Credit pack cards:** White cards with colored top stripe, teal CTAs, “Best value” badge.
- **Unlimited plans:** Same card style; “Most popular” plan has teal ring and badge.

---

## Tech stack

| Layer | Technology |
|-------|------------|
| Backend | Django 5.x |
| Database | SQLite (default) |
| Frontend | Django templates + Tailwind CSS (django-tailwind) |
| Auth | Custom user model `accounts.UserProfile` (roles: user, gym_owner, admin) |
| Optional AI | Google Gemini for gym-by-pincode (with demo fallback) |

---

## How to run

```bash
# From project root
cd c:\Users\Kevin\Downloads\wetransfer_allflex_2026-02-11_1947

# Create/activate venv (if not already)
py -3 -m venv venv
.\venv\Scripts\Activate.ps1   # Windows PowerShell

# Install dependencies
pip install -r requirements.txt

# Migrate (if needed)
python manage.py migrate

# Seed credit packs (if needed)
python manage.py seed_credit_packs

# Run server
python manage.py runserver
```

Open **http://127.0.0.1:8000/** — Sign up to get 25 credits, then use Dashboard → Find Gyms → “Use 1 visit”.

---

## Key URLs

| Path | Description |
|------|-------------|
| `/` | Home |
| `/plans/` | Plans & Credits (credit packs + unlimited tabs) |
| `/dashboard/` | User dashboard (gym finder, balance, use visit) |
| `/accounts/signup/` | Sign up |
| `/accounts/login/` | Login |
| `/fixed-plans/` | Standalone unlimited plans page |

---

## Document history

- **Defined MVP** — Member signup → credits/plan → find gyms → use visit (credits deducted).
- **Implemented MVP** — use_visit API, dashboard UI, demo credits, seed, GEMINI fallback.
- **Plans page** — Full design revamp (light, teal, fitness-app style).
