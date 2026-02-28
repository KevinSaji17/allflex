#  AllFlex Project  Full Documentation

##  What is AllFlex?

**AllFlex** is a **multi-gym membership platform** (similar to ClassPass or CultFit) that allows users to:
- Buy a **single subscription** and access **multiple gyms**
- Gym owners can **register their gyms** and get approved by admins
- Admins manage the entire ecosystem

---

##  Project Architecture

```
AllFlex
 accounts/         User authentication (MongoDB-based)
 gyms/             Gym management, requests, tiers
 subscriptions/    Plans, payments, access control
 allflex/          Django settings, URLs
 templates/        Frontend HTML templates
```

### Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 5.x |
| Database | MongoDB (via MongoEngine) |
| Auth | Custom MongoDB-based user model |
| Frontend | HTML + Bootstrap + Jinja templates |

---

##  Mathematical Formulas Implemented

### 1. Gym Tier Scoring Formula

Located in `gyms/models.py`  `calculate_tier_score()`

This calculates a **weighted score** to assign a gym to Tier 1, 2, or 3:

```
Score = Σ (facility_weight  facility_present)
      + member_bonus
      + experience_bonus
```

#### Facility Weights

| Facility | Weight |
|----------|--------|
| AC | +1 |
| Pool | +3 |
| Spa | +3 |
| Trainers | +2 |
| Group Classes | +2 |
| Parking | +1 |
| Showers | +1 |
| Lockers | +1 |
| Cafeteria | +1 |
| Cardio | +1 |
| Weights | +1 |
| Machines | +1 |

#### Member Bonus

```
if total_members > 500   +3
if total_members > 200   +2
if total_members > 100   +1
```

#### Experience Bonus

```
if years_in_business > 10  +3
if years_in_business > 5   +2
if years_in_business > 2   +1
```

#### Tier Assignment

```
Score >= 15   Tier 1 (Premium)
Score >= 8    Tier 2 (Standard)
Score < 8     Tier 3 (Basic)
```

---

### 2. Subscription Pricing Model

```
Plan Price = Base_Price  Tier_Multiplier  Duration_Factor
```

| Tier | Gym Access Level |
|------|-----------------|
| Tier 1 | Premium gyms only |
| Tier 2 | Standard + Basic |
| Tier 3 | Basic only |

---

### 3. Access Control Formula

```
User Can Access Gym =
    subscription.is_active == True
    AND subscription.tier >= gym.tier
    AND current_date <= subscription.end_date
    AND daily_checkin_count < plan.daily_limit
```

---

##  AI / Recommendation System

### AI Gym Approval Recommendation

Located in `gyms/models.py`  This is a **rule-based AI system** (not ML, but logic-based scoring):

```python
ai_recommendation = f" Legitimate gym with {facility_count} facilities.
                      Recommended Tier: {tier}.
                      Risk: Low.
                      Recommendation: APPROVE"
```

#### Risk Scoring Logic

```
risk = "High"   if score < 5
risk = "Medium" if score < 10
risk = "Low"    if score >= 10
```

#### Recommendation Logic

```
if risk == "Low"     APPROVE
if risk == "Medium"  REVIEW
if risk == "High"    REJECT
```

>  **Note:** This is **NOT a real ML model**  it is a deterministic rule-based scoring system
> that mimics AI recommendations. There is no trained model (no `.pkl`, `.h5`, or API calls
> to GPT/Gemini etc.)

---

##  Full Workflow

```
[User Registration]
      
[User applies as Gym Owner]
      
[System calculates Tier Score + AI Recommendation]
      
[Admin reviews & approves/rejects]
      
[Gym created with assigned Tier]
      
[End Users browse gyms & buy subscriptions]
      
[User checks in at gym  Access verified]
```

---

##  User Roles

| Role | Permissions |
|------|------------|
| `user` | Browse gyms, buy subscriptions, check-in |
| `gym_owner` | Manage their gym, view members, reports |
| `admin` | Approve/reject gyms, manage all users |

---

##  Test Gym Owner Request Script

The file `create_test_request.py` creates a test gym owner request to verify the approval workflow.

### What it does

1. Finds or creates a test user with role `user`
2. Creates a `GymOwnerRequest` with premium facilities
3. Calculates the tier score and AI recommendation
4. Saves the request with status `pending`

### Sample Test Data Used

```
Gym Name    : FitZone Premium Gym
Address     : 123 Main Street, Downtown, Mumbai, Maharashtra 400001
Owner       : John Doe
Contact     : +91-9876543210
Years       : 5
Members     : 250
Facilities  : AC, Changing Rooms, Showers, Lockers, Parking,
              Trainers, Cardio, Weights, Machines, Group Classes,
              Spa, Cafeteria, Music, WiFi
```

### Expected Tier Calculation for Test Data

| Component | Score |
|-----------|-------|
| AC | +1 |
| Spa | +3 |
| Trainers | +2 |
| Group Classes | +2 |
| Parking | +1 |
| Showers | +1 |
| Lockers | +1 |
| Cafeteria | +1 |
| Cardio + Weights + Machines | +3 |
| Members (250 > 200) | +2 |
| Experience (5 years > 2) | +1 |
| **Total** | **~18  Tier 1** |

### How to Run the Script

```bash
cd c:\Users\Kevin\Downloads\allflex\allflex
python create_test_request.py
```

### How to Approve via Admin Panel

**Method 1  Manual:**
1. Go to: `http://127.0.0.1:8000/admin/gyms/gymownerrequest/`
2. Find the request for `FitZone Premium Gym`
3. Click to review
4. Change status to `Approved` and save

**Method 2  Bulk Action:**
1. Select the request checkbox
2. Choose `Approve selected requests` action
3. Click `Go`

### Expected Results After Approval

- User role changes from `user`  `gym_owner`
- Gym `FitZone Premium Gym` is created with **Tier 1**
- Gym is set to `active` and `verified`

---

##  Feature Summary

| Feature | Implementation |
|---------|---------------|
| Tier Calculation | Weighted scoring formula |
| AI Recommendation | Rule-based risk scoring |
| Access Control | Boolean + date + tier logic |
| Pricing | Tier-based multipliers |
| Database | MongoDB (MongoEngine ODM) |
| Real ML/AI |  Not implemented |

---

##  Running the Project

```bash
cd c:\Users\Kevin\Downloads\allflex\allflex
python manage.py runserver
```

Server runs at: **http://127.0.0.1:8000/**

| Panel | URL |
|-------|-----|
| Home | http://127.0.0.1:8000/ |
| Admin | http://127.0.0.1:8000/admin/ |
| Gyms | http://127.0.0.1:8000/gyms/ |
| Subscriptions | http://127.0.0.1:8000/subscriptions/ |

---

*Documentation generated on February 26, 2026*