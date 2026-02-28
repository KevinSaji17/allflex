# Admin Panel Guide - ALLFLEX

## Overview
This guide explains how to use the enhanced admin panel features for managing gym owner requests, gyms, and user roles.

## Access the Admin Panel
1. Navigate to `http://127.0.0.1:8000/admin/`
2. Login with your superuser credentials

## Key Features

### 1. Gym Owner Requests Management

#### View Requests
- Go to **GYMS → Gym Owner Requests**
- See all pending, approved, and rejected requests
- Filter by status, tier, or creation date
- Search by gym name, owner name, email, or address

#### Review Individual Request
1. Click on a request to view details
2. Review:
   - **Gym Details**: Name and address (from Google search)
   - **Owner Information**: Name, contact, email
   - **Business Details**: Years in business, total members
   - **Facilities**: Complete checklist with suggested tier
   - **AI Assessment**: Automated recommendations
   - **Documents**: Business proof uploads

3. Make a decision:
   - Change **Status** to "Approved" or "Rejected"
   - Add **Admin Notes** for internal reference
   - Click **Save**

When you approve a request:
- ✅ User is automatically promoted to "gym_owner" role
- ✅ New Gym is created with suggested tier
- ✅ Gym is activated and verified as ALLFLEX partner

#### Bulk Actions
Select multiple requests and use actions:
- **✓ Approve selected requests** - Approves all and creates gyms
- **✗ Reject selected requests** - Rejects all selected

### 2. Gym Management

#### View All Gyms
- Go to **GYMS → Gyms**
- See tier, status, active state, wallet balance
- Filter by tier, status, verification status
- Search by name, location, or owner

#### Gym Actions
Select gyms and use bulk actions:
- **✓ Approve selected gyms** - Approves and activates gyms
- **✗ Reject selected gyms** - Rejects and deactivates gyms
- **🟢 Activate selected gyms** - Makes gyms available to users
- **🔴 Deactivate selected gyms** - Temporarily disables gyms
- **✓ Mark as verified partner** - Adds ALLFLEX verified badge

#### Edit Individual Gym
1. Click on a gym to edit
2. Modify:
   - Basic info (name, logo, description, location)
   - Tier and capacity
   - Status and verification
   - View wallet balance (read-only)

### 3. Payout Requests

#### Manage Payouts
- Go to **GYMS → Payout Requests**
- View pending payout requests from gym owners
- Filter by status or date

#### Bulk Actions
- **✓ Approve selected payouts** - Approve pending requests
- **✗ Reject selected payouts** - Reject pending requests

### 4. User Management

#### For SQL Database Mode
- Go to **AUTHENTICATION AND AUTHORIZATION → Users**
- View all users with roles

#### User Actions
- **🏋️ Promote to gym owner** - Grant gym owner access
- **👤 Change to regular user** - Demote to regular user
- **✓ Activate users** - Enable user accounts
- **✗ Deactivate users** - Disable user accounts

#### For MongoDB Mode
MongoDB users cannot be managed directly through admin panel.
Use management commands instead:

```bash
# Promote user to gym owner
python manage.py promote_gym_owner <username>

# Demote user back to regular user
python manage.py promote_gym_owner <username> --demote

# List all pending gym owner requests
python manage.py list_gym_requests

# List approved/rejected requests
python manage.py list_gym_requests --status approved
python manage.py list_gym_requests --status rejected
```

### 5. Credit Management

#### Credit Packs
- Go to **USERS → Credit Packs**
- Create, edit, or deactivate credit packs
- Set tier, credits, price, and validity

#### Bulk Actions
- **✓ Activate selected packs** - Make packs available
- **✗ Deactivate selected packs** - Hide from users

#### User Credit Balances
- Go to **USERS → User Credit Balances**
- View all user credit balances
- Monitor usage and balances

#### Credit Transactions
- Go to **USERS → Credit Transactions**
- View all credit transactions
- Filter by type (credit/debit) and date

### 6. Bookings & Ratings

#### Bookings
- Go to **GYMS → Bookings**
- View all gym bookings
- Filter by gym tier or date
- Track credit usage

#### Ratings
- Go to **GYMS → Ratings**
- View all gym ratings and reviews
- Filter by star rating or gym tier
- Monitor gym quality

## Common Workflows

### Workflow 1: Approve New Gym Owner
1. Go to **GYMS → Gym Owner Requests**
2. Filter by Status: "Pending"
3. Click on a request to review
4. Verify:
   - Business details are legitimate
   - Facilities match the tier
   - Contact information is valid
   - Documents are provided
5. Change Status to "Approved"
6. Add admin notes if needed
7. Click **Save**
8. System automatically:
   - Promotes user to gym_owner
   - Creates the gym
   - Activates the gym

### Workflow 2: Bulk Approve Multiple Requests
1. Go to **GYMS → Gym Owner Requests**
2. Filter by Status: "Pending"
3. Select checkboxes for requests to approve
4. Select "✓ Approve selected requests" from Action dropdown
5. Click **Go**
6. All selected requests are approved and gyms created

### Workflow 3: Verify and Activate Gym
1. Go to **GYMS → Gyms**
2. Find the gym to verify
3. Either:
   - Click on gym → Edit details → Check "Is verified partner" → Save
   - OR select gym → Action: "✓ Mark as verified partner" → Go

### Workflow 4: Manage Payouts
1. Go to **GYMS → Payout Requests**
2. Filter by Status: "Pending"
3. Review amounts and gym owner details
4. Select requests to approve
5. Action: "✓ Approve selected payouts"
6. Click **Go**

## Tips

- **Always review facilities carefully** - They determine the tier
- **Check AI recommendations** - They provide helpful insights
- **Add admin notes** - Keep track of decisions
- **Use bulk actions** - Save time on multiple requests
- **Monitor wallet balances** - Ensure gym owners are paid fairly
- **Review ratings regularly** - Maintain quality standards

## Security Notes

- Only superusers can access the admin panel
- All actions are logged
- User promotion is permanent (requires manual demotion)
- Rejected requests can be re-reviewed later

## Support

For issues or questions:
- Check Django logs for errors
- Review MongoDB connection if users don't load
- Ensure DATABASE_MODE is set correctly in settings
- Use management commands for MongoDB user management

---

**Admin Panel Version**: 2.0  
**Last Updated**: February 2026  
**System**: ALLFLEX Gym Management Platform
