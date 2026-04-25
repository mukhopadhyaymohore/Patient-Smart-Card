from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Patient, CardDelivery, CardRenewal
from datetime import date
from dateutil.relativedelta import relativedelta


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-input'


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Password'}))


class PersonalInfoForm(forms.ModelForm):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]

    class Meta:
        model = Patient
        fields = [
            'first_name', 'middle_name', 'last_name',
            'date_of_birth', 'gender', 'mobile', 'email',
            'aadhaar', 'pan_passport', 'address', 'photo',
        ]
        widgets = {
            'first_name':    forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Rahul'}),
            'middle_name':   forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Suresh'}),
            'last_name':     forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Mehta'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'gender':        forms.RadioSelect(attrs={'class': 'radio-input'}),
            'mobile':        forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+91 9876543210'}),
            'email':         forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'you@email.com'}),
            'aadhaar':       forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'XXXX XXXX XXXX', 'maxlength': '14'}),
            'pan_passport':  forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'ABCDE1234F'}),
            'address':       forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'House No., Street, City, State, PIN'}),
            'photo':         forms.ClearableFileInput(attrs={'class': 'form-input'}),
        }


class MedicalInfoForm(forms.ModelForm):
    DISABILITY_CHOICES = [
        ('None','None'), ('Visual','Visual'), ('Hearing','Hearing'),
        ('Locomotor','Locomotor'), ('Intellectual','Intellectual'), ('Other','Other'),
    ]

    class Meta:
        model = Patient
        fields = [
            'blood_group', 'height_cm', 'weight_kg', 'disability_status',
            'allergies', 'chronic_conditions', 'current_medications', 'past_surgeries',
            'emergency_name', 'emergency_relation', 'emergency_mobile', 'emergency_mobile2',
        ]
        widgets = {
            'blood_group':         forms.Select(attrs={'class': 'form-select'}),
            'height_cm':           forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '170'}),
            'weight_kg':           forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '70'}),
            'disability_status':   forms.Select(attrs={'class': 'form-select'}),
            'allergies':           forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'e.g. Penicillin, Latex...', 'rows': 3}),
            'chronic_conditions':  forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'e.g. Diabetes, Hypertension...', 'rows': 3}),
            'current_medications': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'List medications with dosage...', 'rows': 3}),
            'past_surgeries':      forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'Year, procedure, hospital name...', 'rows': 3}),
            'emergency_name':      forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Full name'}),
            'emergency_relation':  forms.Select(attrs={'class': 'form-select'}),
            'emergency_mobile':    forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+91 XXXXXXXXXX'}),
            'emergency_mobile2':   forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+91 XXXXXXXXXX'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['disability_status'].widget = forms.Select(
            choices=self.DISABILITY_CHOICES,
            attrs={'class': 'form-select'}
        )
        self.fields['emergency_relation'].widget = forms.Select(
            choices=[('Spouse','Spouse'),('Parent','Parent'),('Sibling','Sibling'),
                     ('Child','Child'),('Friend','Friend'),('Other','Other')],
            attrs={'class': 'form-select'}
        )


class InsuranceInfoForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'insurance_provider', 'policy_number', 'sum_insured',
            'policy_expiry', 'tpa',
            'scheme_pmjay', 'scheme_state', 'scheme_bpl', 'scheme_defence',
        ]
        widgets = {
            'insurance_provider': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Star Health, HDFC Ergo...'}),
            'policy_number':      forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Policy ID'}),
            'sum_insured':        forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '500000'}),
            'policy_expiry':      forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'tpa':                forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Medi Assist, Paramount...'}),
            'scheme_pmjay':       forms.CheckboxInput(attrs={'class': 'form-check'}),
            'scheme_state':       forms.CheckboxInput(attrs={'class': 'form-check'}),
            'scheme_bpl':         forms.CheckboxInput(attrs={'class': 'form-check'}),
            'scheme_defence':     forms.CheckboxInput(attrs={'class': 'form-check'}),
        }


class DeliveryForm(forms.ModelForm):
    STATES = [
        ('Andaman and Nicobar Islands', 'Andaman and Nicobar Islands'),
        ('Andhra Pradesh', 'Andhra Pradesh'),
        ('Arunachal Pradesh', 'Arunachal Pradesh'),
        ('Assam', 'Assam'),
        ('Bihar', 'Bihar'),
        ('Chandigarh', 'Chandigarh'),
        ('Chhattisgarh', 'Chhattisgarh'),
        ('Dadra and Nagar Haveli and Daman and Diu', 'Dadra and Nagar Haveli and Daman and Diu'),
        ('Delhi', 'Delhi'),
        ('Goa', 'Goa'),
        ('Gujarat', 'Gujarat'),
        ('Haryana', 'Haryana'),
        ('Himachal Pradesh', 'Himachal Pradesh'),
        ('Jammu and Kashmir', 'Jammu and Kashmir'),
        ('Jharkhand', 'Jharkhand'),
        ('Karnataka', 'Karnataka'),
        ('Kerala', 'Kerala'),
        ('Ladakh', 'Ladakh'),
        ('Lakshadweep', 'Lakshadweep'),
        ('Madhya Pradesh', 'Madhya Pradesh'),
        ('Maharashtra', 'Maharashtra'),
        ('Manipur', 'Manipur'),
        ('Meghalaya', 'Meghalaya'),
        ('Mizoram', 'Mizoram'),
        ('Nagaland', 'Nagaland'),
        ('Odisha', 'Odisha'),
        ('Puducherry', 'Puducherry'),
        ('Punjab', 'Punjab'),
        ('Rajasthan', 'Rajasthan'),
        ('Sikkim', 'Sikkim'),
        ('Tamil Nadu', 'Tamil Nadu'),
        ('Telangana', 'Telangana'),
        ('Tripura', 'Tripura'),
        ('Uttar Pradesh', 'Uttar Pradesh'),
        ('Uttarakhand', 'Uttarakhand'),
        ('West Bengal', 'West Bengal'),
        ('Other', 'Other'),
    ]

    class Meta:
        model = CardDelivery
        fields = [
            'address_line1', 'address_line2', 'city', 'state',
            'pin_code', 'delivery_mobile', 'preferred_slot', 'instructions',
        ]
        widgets = {
            'address_line1':   forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Flat No., Building Name'}),
            'address_line2':   forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Street, Area, Landmark'}),
            'city':            forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Mumbai'}),
            'state':           forms.Select(attrs={'class': 'form-select'}),
            'pin_code':        forms.TextInput(attrs={'class': 'form-input', 'placeholder': '400001', 'maxlength': '6'}),
            'delivery_mobile': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+91 XXXXXXXXXX'}),
            'preferred_slot':  forms.Select(attrs={'class': 'form-select'}),
            'instructions':    forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'e.g. Call before delivery...', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['state'].widget = forms.Select(
            choices=self.STATES,
            attrs={'class': 'form-select'}
        )


class RenewalForm(forms.ModelForm):
    class Meta:
        model = CardRenewal
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Briefly describe why you are renewing (optional)...',
                'rows': 4,
            }),
        }