# API REFERENCE - New Endpoints

## Check-In/Out APIs

### 1. Gym Check-In
**Endpoint:** `POST /gym-checkin/`  
**Authentication:** Required (login_required)

**Request Body:**
```json
{
  "booking_id": "507f1f77bcf86cd799439011",
  "latitude": 19.076,
  "longitude": 72.8777
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Successfully checked in to Gold's Gym",
  "checked_in_at": "2026-03-11T10:30:00Z",
  "distance": "45m"
}
```

**Error Responses:**
```json
// Not at gym location
{
  "success": false,
  "error": "You must be at the gym to check in. You are 1.5km away.",
  "distance": "1.5km"
}

// Already checked in today
{
  "success": false,
  "error": "You have already checked in to this gym today. Cooldown: 1 check-in per gym per day."
}

// Invalid GPS
{
  "success": false,
  "error": "Invalid GPS coordinates"
}

// Already checked in
{
  "success": false,
  "error": "Already checked in. Use check-out to complete session."
}
```

**Validation Rules:**
- ✅ User must be within 100 meters of gym
- ✅ Only 1 check-in per gym per day
- ✅ GPS coordinates must be valid (-90 to 90 lat, -180 to 180 lon)
- ✅ Booking must exist and belong to user
- ✅ Gym must have GPS coordinates configured

---

### 2. Gym Check-Out
**Endpoint:** `POST /gym-checkout/`  
**Authentication:** Required (login_required)

**Request Body:**
```json
{
  "booking_id": "507f1f77bcf86cd799439011"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Successfully checked out from Gold's Gym",
  "checked_out_at": "2026-03-11T12:15:00Z",
  "session_duration": "1h 45m",
  "duration_minutes": 105
}
```

**Error Responses:**
```json
// Not checked in
{
  "success": false,
  "error": "You must check in before checking out"
}

// Booking not found
{
  "success": false,
  "error": "Booking not found"
}
```

**Automatic Actions:**
- ✅ Calculates session duration
- ✅ Updates booking status to 'completed'
- ✅ Updates fitness profile stats (total_visits, total_credits_spent)
- ✅ Records checkout timestamp

---

## Fraud Prevention

### Cooldown System
- **Rule:** 1 check-in per gym per day per user
- **Enforced:** At check-in API level
- **Logic:** Checks existing check-ins for today (00:00 - 23:59)

### GPS Verification
- **Proximity:** 100 meters
- **Algorithm:** Haversine formula for great-circle distance
- **Spoofing Prevention:** Validates coordinates are within valid ranges
- **Records:** Stores user's check-in location for audit trail

### Status Flow
```
booked → checked_in → completed
   ↓
cancelled
```

- Cannot check-in if already checked-in
- Cannot check-out if not checked-in
- Cannot reuse completed bookings

---

## Frontend Integration Examples

### JavaScript Check-In
```javascript
async function checkIn(bookingId) {
    // Get user's GPS location
    const position = await new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject, {
            enableHighAccuracy: true,
            timeout: 5000,
            maximumAge: 0
        });
    });

    const response = await fetch('/gym-checkin/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            booking_id: bookingId,
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
        })
    });

    const result = await response.json();
    
    if (result.success) {
        alert(`Checked in! Distance: ${result.distance}`);
    } else {
        alert(`Error: ${result.error}`);
    }
}
```

### JavaScript Check-Out
```javascript
async function checkOut(bookingId) {
    const response = await fetch('/gym-checkout/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            booking_id: bookingId
        })
    });

    const result = await response.json();
    
    if (result.success) {
        alert(`Session completed! Duration: ${result.session_duration}`);
    } else {
        alert(`Error: ${result.error}`);
    }
}
```

### Error Handling
```javascript
function handleCheckInError(error) {
    if (error.message.includes('cooldown')) {
        // Show cooldown message
        showMessage('You can only check in once per day per gym', 'warning');
    } else if (error.distance) {
        // Show distance error
        showMessage(`You're ${error.distance} from the gym. Get closer!`, 'error');
    } else {
        // Generic error
        showMessage(error.error || 'Check-in failed', 'error');
    }
}
```

---

## Testing Endpoints

### cURL Examples

**Check-In:**
```bash
curl -X POST http://localhost:8000/gym-checkin/ \\
  -H "Content-Type: application/json" \\
  -H "Cookie: sessionid=YOUR_SESSION_ID" \\
  -d '{
    "booking_id": "507f1f77bcf86cd799439011",
    "latitude": 19.076,
    "longitude": 72.8777
  }'
```

**Check-Out:**
```bash
curl -X POST http://localhost:8000/gym-checkout/ \\
  -H "Content-Type: application/json" \\
  -H "Cookie: sessionid=YOUR_SESSION_ID" \\
  -d '{
    "booking_id": "507f1f77bcf86cd799439011"
  }'
```

---

## Database Fields

### Gym Model (New Fields)
```python
latitude = DecimalField(max_digits=9, decimal_places=6, null=True)
longitude = DecimalField(max_digits=9, decimal_places=6, null=True)
```

### GymBooking Model (New Fields)
```python
checked_in_at = DateTimeField(null=True)
checked_out_at = DateTimeField(null=True)
session_duration = DurationField(null=True)
check_in_latitude = DecimalField(max_digits=9, decimal_places=6, null=True)
check_in_longitude = DecimalField(max_digits=9, decimal_places=6, null=True)
status = CharField(choices=[..., 'completed'])  # Added 'completed' status
```

---

## GPS Utilities

### Available Functions

```python
from users.gps_utils import (
    haversine_distance,
    is_within_proximity,
    validate_gps_coordinates,
    format_distance
)

# Calculate distance between two points
distance = haversine_distance(lat1, lon1, lat2, lon2)  # Returns meters

# Check if within range
is_close, actual_distance = is_within_proximity(
    user_lat, user_lon, 
    gym_lat, gym_lon,
    max_distance_meters=100.0
)

# Validate coordinates
is_valid = validate_gps_coordinates(lat, lon)

# Format for display
formatted = format_distance(meters)  # Returns "50m" or "1.5km"
```

---

## Payment Service

### Available Functions

```python
from users.payment_service import (
    create_payment_order,
    verify_payment_signature,
    process_payment_callback,
    is_payment_gateway_enabled
)

# Check if payment gateway is configured
if is_payment_gateway_enabled():
    # Create order
    order = create_payment_order(
        amount=Decimal('499.00'),
        notes={'credits': 100}
    )
    
    # Process callback
    result = process_payment_callback({
        'razorpay_order_id': order_id,
        'razorpay_payment_id': payment_id,
        'razorpay_signature': signature
    })
```

---

## Configuration

### Environment Variables

```env
# Payment Gateway
RAZORPAY_KEY_ID=rzp_test_xxxxxx
RAZORPAY_KEY_SECRET=xxxxxxxxxxxxxx

# Maps API (future use)
GOOGLE_MAPS_API_KEY=AIzaSyxxxxxx
```

---

## Status Codes

- **200** - Success
- **400** - Bad Request (missing params, invalid data)
- **403** - Forbidden (not at gym, cooldown active)
- **404** - Not Found (booking doesn't exist)
- **500** - Server Error

---

## Security Features

1. **CSRF Protection** - All POST endpoints require CSRF token
2. **Authentication** - @login_required decorator
3. **GPS Validation** - Prevents spoofed coordinates
4. **Signature Verification** - Razorpay payment security
5. **Rate Limiting** - 1 check-in per gym per day
6. **Audit Trail** - Records GPS location at check-in
