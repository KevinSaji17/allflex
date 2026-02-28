"""
Gym Owner Request Models
Stores requests from users wanting to become gym owners
"""
from django.db import models
from django.conf import settings


class GymOwnerRequest(models.Model):
    """Model to store gym owner account requests for admin review"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    TIER_CHOICES = [
        (1, 'Tier 1 - Basic'),
        (2, 'Tier 2 - Standard'),
        (3, 'Tier 3 - Premium'),
        (4, 'Tier 4 - Elite'),
    ]
    
    # User Information
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='gym_requests')
    
    # Gym Information (searched via Gemini)
    gym_name = models.CharField(max_length=255, help_text="Gym name from search")
    gym_address = models.CharField(max_length=500, help_text="Full address from search")
    
    # Owner Information
    owner_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20)
    email = models.EmailField()
    
    # Business Details
    years_in_business = models.IntegerField()
    total_members = models.IntegerField()
    
    # Facilities Checklist (Boolean fields)
    has_ac = models.BooleanField(default=False, verbose_name="Air Conditioning")
    has_changing_rooms = models.BooleanField(default=False, verbose_name="Changing/Dressing Rooms")
    has_showers = models.BooleanField(default=False, verbose_name="Showers/Washrooms")
    has_lockers = models.BooleanField(default=False, verbose_name="Lockers")
    has_parking = models.BooleanField(default=False, verbose_name="Parking Facility")
    has_trainers = models.BooleanField(default=False, verbose_name="Personal Trainers")
    has_cardio = models.BooleanField(default=False, verbose_name="Cardio Equipment")
    has_weights = models.BooleanField(default=False, verbose_name="Free Weights")
    has_machines = models.BooleanField(default=False, verbose_name="Weight Machines")
    has_group_classes = models.BooleanField(default=False, verbose_name="Group Fitness Classes")
    has_spa = models.BooleanField(default=False, verbose_name="Spa/Sauna/Steam Room")
    has_pool = models.BooleanField(default=False, verbose_name="Swimming Pool")
    has_cafeteria = models.BooleanField(default=False, verbose_name="Cafeteria/Juice Bar")
    has_music = models.BooleanField(default=False, verbose_name="Music System")
    has_wifi = models.BooleanField(default=False, verbose_name="WiFi")
    
    # Documents
    business_proof = models.FileField(upload_to='gym_requests/', null=True, blank=True)
    
    # Additional Information
    additional_info = models.TextField(blank=True)
    
    # AI Assessment
    ai_recommendation = models.TextField(blank=True, help_text="AI analysis and recommendation")
    suggested_tier = models.IntegerField(choices=TIER_CHOICES, null=True, blank=True)
    
    # Admin Decision
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, help_text="Internal notes from admin review")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Gym Owner Request"
        verbose_name_plural = "Gym Owner Requests"
    
    def __str__(self):
        return f"{self.gym_name} - {self.owner_name} ({self.status})"
    
    def calculate_tier_score(self):
        """Calculate recommended tier based on facilities"""
        score = 0
        
        # Basic facilities (Tier 1)
        if self.has_cardio: score += 1
        if self.has_weights: score += 1
        if self.has_machines: score += 1
        
        # Standard facilities (Tier 2)
        if self.has_ac: score += 2
        if self.has_changing_rooms: score += 1
        if self.has_showers: score += 1
        if self.has_lockers: score += 1
        
        # Premium facilities (Tier 3)
        if self.has_trainers: score += 2
        if self.has_group_classes: score += 2
        if self.has_parking: score += 1
        if self.has_music: score += 1
        if self.has_wifi: score += 1
        
        # Elite facilities (Tier 4)
        if self.has_spa: score += 3
        if self.has_pool: score += 3
        if self.has_cafeteria: score += 2
        
        # Determine tier
        if score >= 15:
            return 4
        elif score >= 10:
            return 3
        elif score >= 5:
            return 2
        else:
            return 1
    
    def get_facilities_list(self):
        """Get list of available facilities"""
        facilities = []
        if self.has_ac: facilities.append("Air Conditioning")
        if self.has_changing_rooms: facilities.append("Changing Rooms")
        if self.has_showers: facilities.append("Showers")
        if self.has_lockers: facilities.append("Lockers")
        if self.has_parking: facilities.append("Parking")
        if self.has_trainers: facilities.append("Personal Trainers")
        if self.has_cardio: facilities.append("Cardio Equipment")
        if self.has_weights: facilities.append("Free Weights")
        if self.has_machines: facilities.append("Weight Machines")
        if self.has_group_classes: facilities.append("Group Classes")
        if self.has_spa: facilities.append("Spa/Sauna")
        if self.has_pool: facilities.append("Swimming Pool")
        if self.has_cafeteria: facilities.append("Cafeteria")
        if self.has_music: facilities.append("Music System")
        if self.has_wifi: facilities.append("WiFi")
        return facilities
