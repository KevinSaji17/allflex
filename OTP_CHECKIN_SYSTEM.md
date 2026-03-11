# OTP-Based Gym Check-in System ✅

## Overview
The new OTP (One-Time Password) system replaces the GPS-based check-in with a more reliable, gym owner-controlled verification process.

---

## How It Works

### For Regular Users:

1. **Book a Gym**
   - Search for gyms on your dashboard
   - Book a time slot at your chosen gym
   - **You receive a 6-digit OTP immediately** (displayed in booking confirmation)
   - Save this OTP - you'll show it to the gym owner when you arrive

2. **Arrive at Gym**
   - Show your **6-digit OTP** to the gym staff/owner
   - They will enter it in their dashboard to check you in
   - Once verified, your session officially starts

3. **Complete Workout**
   - When finished, open your bookings
   - Click **"End Workout"** button
   - System records checkout time and calculates session duration automatically

### For Gym Owners:

1. **View Bookings**
   - Open your gym dashboard at `/gym-dashboard/`
   - See all bookings with status:
     - ⏳ **Awaiting Arrival** (booked)
     - 🔵 **Currently At Gym** (checked-in)
     - ✓ **Verified Visit** (completed)

2. **Check-in Users**
   - When user arrives, they show you their **6-digit OTP**
   - Find their booking in your dashboard
   - Enter the OTP in the "Check-in Action" column
   - Click **"✓ Verify"**
   - System validates OTP and checks them in automatically
   - Check-in timestamp recorded

3. **Monitor Sessions**
   - See who's currently at your gym (status: "Currently At Gym")
   - View checkout times when users end their workout
   - Track session durations

---

## Technical Implementation

### Database Schema (MongoDB)
```python
class GymBooking(Document):
    user = ReferenceField(UserProfile)
    gym = ReferenceField(Gym)
    status = StringField(choices=['booked', 'checked_in', 'completed', 'cancelled'])
    
    # OTP fields
    otp = StringField(max_length=6)  # 6-digit numeric code
    otp_verified = BooleanField(default=False)
    
    # Timestamps
    booked_at = DateTimeField()
    checked_in_at = DateTimeField(null=True)
    checked_out_at = DateTimeField(null=True)
    session_duration_minutes = IntField(null=True)  # Auto-calculated
```

### API Endpoints

#### 1. Create Booking (generates OTP)
**Endpoint:** `POST /book/`
**Response:**
```json
{
    "success": true,
    "booking_id": "507f1f77bcf86cd799439011",
    "gym_name": "Kevin's Fitness Hub",
    "otp": "123456",  // User's 6-digit OTP
    "booking_date": "2026-03-15",
    "time_slot": "06:00 AM – 07:00 AM"
}
```

#### 2. Verify OTP (gym owner check-in)
**Endpoint:** `POST /gym-dashboard/verify-otp/`
**Request:**
```json
{
    "booking_id": "507f1f77bcf86cd799439011",
    "otp": "123456"
}
```
**Response:**
```json
{
    "success": true,
    "message": "kevin123 checked in successfully!",
    "checked_in_at": "09:15 AM",
    "user": "kevin123",
    "gym": "Kevin's Fitness Hub"
}
```

#### 3. End Workout (user checkout)
**Endpoint:** `POST /end-workout/`
**Request:**
```json
{
    "booking_id": "507f1f77bcf86cd799439011"
}
```
**Response:**
```json
{
    "success": true,
    "message": "Workout completed at Kevin's Fitness Hub!",
    "checked_out_at": "10:45 AM",
    "session_duration": 90,  // minutes
    "gym": "Kevin's Fitness Hub"
}
```

---

## Files Modified

### Backend
1. **[accounts/mongo_models.py](accounts/mongo_models.py)** (Lines 369-370)
   - Added `otp` and `otp_verified` fields to `GymBooking` model

2. **[users/otp_utils.py](users/otp_utils.py)** (NEW FILE)
   - `generate_otp()`: Creates random 6-digit numeric OTP
   - `validate_otp()`: Compares entered OTP with stored OTP

3. **[users/views.py](users/views.py)**
   - Line ~428: Generate OTP when booking created
   - Line ~485: Return OTP in booking response
   - Bottom: Added `end_workout()` function

4. **[gyms/views.py](gyms/views.py)**
   - Added `verify_booking_otp()`: Gym owner OTP verification
   - Added `end_workout()`: Duplicate endpoint for gym owners (if needed)

5. **[gyms/urls.py](gyms/urls.py)**
   - Added `/verify-otp/` route
   - Added `/end-workout/` route

6. **[users/urls.py](users/urls.py)**
   - Added `/end-workout/` route for users

### Frontend
7. **[gyms/templates/gyms/dashboard.html](gyms/templates/gyms/dashboard.html)**
   - Added "User's OTP" column showing 6-digit OTP
   - Added "Check-in Action" column with OTP input field and Verify button
   - Added JavaScript function `verifyOTP()` for AJAX verification
   - Enhanced legend with OTP system instructions

---

## Advantages Over GPS System

| Feature | GPS System ❌ | OTP System ✅ |
|---------|--------------|---------------|
| **Reliability** | GPS can be inaccurate indoors | Always works, independent of location |
| **Gym Owner Control** | No verification by owner | Owner directly verifies attendance |
| **User Privacy** | Requires location permission | No location data needed |
| **Fraud Prevention** | Can be spoofed with fake GPS | Owner physically sees the user |
| **Simplicity** | Complex distance calculation | Simple 6-digit code |
| **Proof of Attendance** | GPS coordinates stored | Owner-verified check-in |

---

## User Flow Diagram

```
USER SIDE:
┌─────────────┐
│ Book Gym    │
│ (Dashboard) │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Receive OTP │◄── "Your OTP: 123456"
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Arrive at   │
│ Gym         │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Show OTP to │
│ Staff/Owner │
└─────────────┘


GYM OWNER SIDE:
┌─────────────┐
│ See Booking │
│ in Dashboard│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ User Shows  │
│ OTP: 123456 │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Enter OTP   │
│ Click Verify│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│✅ User       │
│ Checked In  │
└─────────────┘


COMPLETION:
┌─────────────┐
│ User Clicks │
│ End Workout │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│✅ Session    │
│ Complete    │
│ Duration    │
│ Calculated  │
└─────────────┘
```

---

## Testing Guide

### Test Scenario 1: Happy Path

1. **Login as kevin123** (regular user)
   ```
   http://127.0.0.1:8000/login/
   Username: kevin123
   Password: kevin123
   ```

2. **Book a gym**
   - Go to Dashboard
   - Search "Mumbai" or "400001"
   - Book "Kevin's Fitness Hub"
   - **Note the OTP shown in success message** (e.g., "Your OTP: 123456")

3. **Login as kevin** (gym owner)
   ```
   http://127.0.0.1:8000/login/
   Username: kevin
   Password: kevin123
   ```

4. **Verify OTP**
   - Go to "🏢 My Dashboard"
   - Find kevin123's booking (status: "⏳ Awaiting Arrival")
   - See OTP in "User's OTP" column
   - Enter OTP in input field
   - Click "✓ Verify"
   - Should see success message
   - Status changes to "🔵 Currently At Gym"

5. **End workout as kevin123**
   - Switch back to kevin123 account
   - Go to My Bookings
   - Find checked-in booking
   - Click "End Workout" button
   - Checkout time recorded
   - Session duration calculated automatically

### Test Scenario 2: Invalid OTP

1. Follow steps 1-3 from Happy Path
2. As gym owner, enter **wrong OTP** (e.g., "999999")
3. Click "✓ Verify"
4. Should see error: "Invalid OTP. Please check and try again."

### Test Scenario 3: Already Checked In

1. Complete Happy Path test
2. Try to verify OTP again for same booking
3. Should see error: "User already checked in"

---

## Future Enhancements

1. **SMS/Email OTP Delivery**
   - Send OTP via SMS to user's phone
   - Email fallback option

2. **OTP Expiry**
   - Add timestamp to OTP generation
   - Expire OTP after 24 hours

3. **QR Code Alternative**
   - Generate QR code containing booking ID + OTP
   - Gym owner scans QR code to check in

4. **Push Notifications**
   - Notify user when checked in
   - Notify gym owner of pending arrivals

5. **Analytics Dashboard**
   - Peak hours visualization
   - Average session duration
   - No-show rate tracking

---

**Last Updated:** March 11, 2026
**Status:** ✅ Fully Implemented and Ready for Testing
