from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import date
from dateutil.relativedelta import relativedelta


def card_expiry():
    return date.today().replace(year=date.today().year + 5)


def generate_card_id():
    uid = uuid.uuid4().hex[:8].upper()
    return f"HC-{uid[:4]}-{uid[4:]}"


class Patient(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    BLOOD_CHOICES = [
        ('A+','A+'),('A-','A-'),('B+','B+'),('B-','B-'),
        ('AB+','AB+'),('AB-','AB-'),('O+','O+'),('O-','O-'),
    ]

    user          = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient')
    first_name    = models.CharField(max_length=100)
    middle_name   = models.CharField(max_length=100, blank=True)
    last_name     = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender        = models.CharField(max_length=1, choices=GENDER_CHOICES)
    mobile        = models.CharField(max_length=15)
    email         = models.EmailField(blank=True)
    aadhaar       = models.CharField(max_length=14)
    pan_passport  = models.CharField(max_length=20, blank=True)
    address       = models.TextField()
    photo         = models.ImageField(upload_to='patient_photos/', blank=True, null=True)

    # Medical
    blood_group        = models.CharField(max_length=4, choices=BLOOD_CHOICES)
    height_cm          = models.PositiveIntegerField(null=True, blank=True)
    weight_kg          = models.PositiveIntegerField(null=True, blank=True)
    disability_status  = models.CharField(max_length=50, blank=True, default='None')
    allergies          = models.TextField(blank=True)
    chronic_conditions = models.TextField(blank=True)
    current_medications= models.TextField(blank=True)
    past_surgeries     = models.TextField(blank=True)

    # Emergency contact
    emergency_name     = models.CharField(max_length=100)
    emergency_relation = models.CharField(max_length=50)
    emergency_mobile   = models.CharField(max_length=15)
    emergency_mobile2  = models.CharField(max_length=15, blank=True)

    # Insurance
    insurance_provider = models.CharField(max_length=100, blank=True)
    policy_number      = models.CharField(max_length=100, blank=True)
    sum_insured        = models.PositiveIntegerField(null=True, blank=True)
    policy_expiry      = models.DateField(null=True, blank=True)
    tpa                = models.CharField(max_length=100, blank=True)
    scheme_pmjay       = models.BooleanField(default=False)
    scheme_state       = models.BooleanField(default=False)
    scheme_bpl         = models.BooleanField(default=False)
    scheme_defence     = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def full_name(self):
        parts = [self.first_name, self.middle_name, self.last_name]
        return ' '.join(p for p in parts if p)

    def __str__(self):
        return self.full_name()


class SmartCard(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('suspended', 'Suspended'),
        ('pending', 'Pending'),
    ]

    patient    = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='card')
    card_id    = models.CharField(max_length=20, unique=True, default=generate_card_id)
    issued_on  = models.DateField(auto_now_add=True)
    valid_until= models.DateField(default=card_expiry)
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def is_expiring_soon(self):
        return (self.valid_until - date.today()).days <= 90

    def days_to_expiry(self):
        return (self.valid_until - date.today()).days

    def __str__(self):
        return f"{self.card_id} — {self.patient}"


class CardDelivery(models.Model):
    DELIVERY_STATUS = [
        ('processing', 'Processing'),
        ('dispatched', 'Dispatched'),
        ('in_transit', 'In Transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('failed', 'Delivery Failed'),
    ]
    TIME_SLOTS = [
        ('morning', 'Morning (9 AM – 1 PM)'),
        ('afternoon', 'Afternoon (1 PM – 5 PM)'),
        ('evening', 'Evening (5 PM – 8 PM)'),
        ('any', 'Any Time'),
    ]

    card             = models.ForeignKey(SmartCard, on_delete=models.CASCADE, related_name='deliveries')
    address_line1    = models.CharField(max_length=200)
    address_line2    = models.CharField(max_length=200, blank=True)
    city             = models.CharField(max_length=100)
    state            = models.CharField(max_length=100)
    pin_code         = models.CharField(max_length=6)
    delivery_mobile  = models.CharField(max_length=15)
    preferred_slot   = models.CharField(max_length=20, choices=TIME_SLOTS, default='any')
    instructions     = models.TextField(blank=True)
    status           = models.CharField(max_length=30, choices=DELIVERY_STATUS, default='processing')
    tracking_id      = models.CharField(max_length=30, blank=True)
    requested_at     = models.DateTimeField(auto_now_add=True)
    delivered_at     = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Delivery for {self.card.card_id} — {self.status}"


class CardRenewal(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    card         = models.ForeignKey(SmartCard, on_delete=models.CASCADE, related_name='renewals')
    requested_on = models.DateField(auto_now_add=True)
    new_expiry   = models.DateField()
    reason       = models.TextField(blank=True)
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    remarks      = models.TextField(blank=True)

    def __str__(self):
        return f"Renewal for {self.card.card_id} — {self.status}"