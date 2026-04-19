from django.contrib import admin
from .models import Patient, SmartCard, CardDelivery, CardRenewal

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'mobile', 'blood_group', 'created_at']
    search_fields = ['first_name', 'last_name', 'aadhaar', 'mobile']

@admin.register(SmartCard)
class SmartCardAdmin(admin.ModelAdmin):
    list_display = ['card_id', 'patient', 'status', 'issued_on', 'valid_until']
    list_filter = ['status']
    search_fields = ['card_id']

@admin.register(CardDelivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['card', 'city', 'status', 'requested_at']
    list_filter = ['status']

@admin.register(CardRenewal)
class RenewalAdmin(admin.ModelAdmin):
    list_display = ['card', 'requested_on', 'new_expiry', 'status']
    list_filter = ['status']