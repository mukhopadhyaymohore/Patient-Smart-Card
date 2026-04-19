from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import date
from dateutil.relativedelta import relativedelta

from .models import Patient, SmartCard, CardDelivery, CardRenewal
from .forms import (
    SignUpForm, LoginForm,
    PersonalInfoForm, MedicalInfoForm, InsuranceInfoForm,
    DeliveryForm, RenewalForm,
)

from django.conf import settings
DEFAULT_FROM_EMAIL = 'MedCard <noreply@patientsmartcard.com>'

def send_email(subject, template, context, recipient_email):
    """Helper to send HTML emails."""
    message = render_to_string(template, context)
    send_mail(
        subject=subject,
        message='',
        from_email=DEFAULT_FROM_EMAIL,
        recipient_list=[recipient_email],
        html_message=message,
        fail_silently=True,
    )

# ─── AUTH ──────────────────────────────────────────────────────────────────────

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = SignUpForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Account created! Complete your registration below.')
        return redirect('register')
    return render(request, 'auth/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password'],
        )
        if user:
            login(request, user)
            return redirect(request.GET.get('next', 'home'))
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


# ─── HOME ──────────────────────────────────────────────────────────────────────

def home_view(request):
    card = None
    patient = None
    if request.user.is_authenticated:
        try:
            patient = request.user.patient
            card = patient.card
        except (Patient.DoesNotExist, SmartCard.DoesNotExist):
            pass

    FACILITIES = [
        {'slug':'identity',        'icon':'🔍','color':'#00c9b1','bg':'rgba(0,201,177,0.1)', 'title':'Unified Patient Identity',   'desc':'One card replaces all ID documents — Aadhaar-linked, biometric-enabled.','tag':'Core'},
        {'slug':'health-records',  'icon':'📁','color':'#38bdf8','bg':'rgba(56,189,248,0.1)','title':'Electronic Health Records',   'desc':'Lifetime medical history, lab reports, prescriptions — all in one place.','tag':'Records'},
        {'slug':'insurance',       'icon':'💳','color':'#f4c842','bg':'rgba(244,200,66,0.1)','title':'Cashless Insurance Claims',   'desc':'Auto pre-authorization and claim settlement with your insurer.','tag':'Financial'},
        {'slug':'emergency',       'icon':'🚨','color':'#ff6b8a','bg':'rgba(255,107,138,0.1)','title':'Emergency Medical Access',  'desc':'Critical info readable even if patient is unconscious.','tag':'Emergency'},
        {'slug':'appointments',    'icon':'📅','color':'#a78bfa','bg':'rgba(167,139,250,0.1)','title':'OPD Appointment Booking',   'desc':'Book, reschedule or cancel appointments across hospitals.','tag':'Outpatient'},
        {'slug':'hospitalization', 'icon':'🏥','color':'#fb923c','bg':'rgba(251,146,60,0.1)','title':'Cashless Hospitalization',   'desc':'Admission, surgery, ICU — cashless at 5,000+ empanelled hospitals.','tag':'Inpatient'},
        {'slug':'lab-diagnostics', 'icon':'🧪','color':'#34d399','bg':'rgba(52,211,153,0.1)','title':'Lab & Diagnostics',          'desc':'Discounted diagnostics. Results auto-synced to your EHR.','tag':'Diagnostics'},
        {'slug':'pharmacy',        'icon':'💊','color':'#f472b6','bg':'rgba(244,114,182,0.1)','title':'Pharmacy & Medication',     'desc':'E-prescriptions sent to partner pharmacies. Drug-allergy cross-checks.','tag':'Pharmacy'},
        {'slug':'telemedicine',    'icon':'🩺','color':'#60a5fa','bg':'rgba(96,165,250,0.1)','title':'Telemedicine',               'desc':'24/7 video consults with verified doctors.','tag':'Digital'},
        {'slug':'govt-schemes',    'icon':'🛡️','color':'#00c9b1','bg':'rgba(0,201,177,0.1)','title':'Government Scheme Benefits', 'desc':'Linked to PM-JAY, Ayushman Bharat — eligibility checked instantly.','tag':'Welfare'},
        {'slug':'privacy',         'icon':'🔒','color':'#a78bfa','bg':'rgba(167,139,250,0.1)','title':'Consent & Privacy',        'desc':'Control who sees what. Granular permissions per provider.','tag':'Privacy'},
        {'slug':'analytics',       'icon':'📊','color':'#38bdf8','bg':'rgba(56,189,248,0.1)','title':'Health Analytics',          'desc':'Personalized health score, trends, and predictive risk alerts.','tag':'Insights'},
    ]

    return render(request, 'index.html', {'card': card, 'patient': patient, 'facilities': FACILITIES})


# ─── REGISTRATION (multi-step via session) ─────────────────────────────────────

@login_required
def register_view(request):
    # If patient already has a card, skip to dashboard
    try:
        _ = request.user.patient.card
        messages.info(request, 'You already have a registered Smart Card.')
        return redirect('home')
    except (Patient.DoesNotExist, SmartCard.DoesNotExist):
        pass

    step = int(request.session.get('reg_step', 1))

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'back':
            request.session['reg_step'] = max(1, step - 1)
            return redirect('register')

        if step == 1:
            form = PersonalInfoForm(request.POST, request.FILES)
            if form.is_valid():
                request.session['reg_personal'] = {
                    k: str(v) for k, v in form.cleaned_data.items()
                    if k != 'photo'
                }
                # Handle photo separately
                if 'photo' in request.FILES:
                    request.session['reg_has_photo'] = True
                request.session['reg_step'] = 2
                return redirect('register')

        elif step == 2:
            form = MedicalInfoForm(request.POST)
            if form.is_valid():
                request.session['reg_medical'] = {
                    k: str(v) for k, v in form.cleaned_data.items()
                }
                request.session['reg_step'] = 3
                return redirect('register')

        elif step == 3:
            form = InsuranceInfoForm(request.POST)
            if form.is_valid():
                request.session['reg_insurance'] = {
                    k: str(v) for k, v in form.cleaned_data.items()
                }
                request.session['reg_step'] = 4
                return redirect('register')

        elif step == 4:
            form = DeliveryForm(request.POST)
            if form.is_valid():
                request.session['reg_delivery'] = {
                    k: str(v) for k, v in form.cleaned_data.items()
                }
                request.session['reg_step'] = 5
                return redirect('register')

        elif step == 5:
            # Consent check
            consents = [
                request.POST.get('consent_accuracy'),
                request.POST.get('consent_data'),
                request.POST.get('consent_aadhaar'),
                request.POST.get('consent_terms'),
                request.POST.get('consent_notify'),
            ]
            if not all(consents):
                messages.error(request, 'Please accept all consent declarations.')
                return redirect('register')

            # Build patient from session data
            personal  = request.session.get('reg_personal', {})
            medical   = request.session.get('reg_medical', {})
            insurance = request.session.get('reg_insurance', {})
            delivery  = request.session.get('reg_delivery', {})

            def boolval(v): return v in ('True', 'true', '1', 'on')

            patient = Patient(
                user=request.user,
                first_name=personal.get('first_name',''),
                middle_name=personal.get('middle_name',''),
                last_name=personal.get('last_name',''),
                date_of_birth=personal.get('date_of_birth'),
                gender=personal.get('gender',''),
                mobile=personal.get('mobile',''),
                email=personal.get('email',''),
                aadhaar=personal.get('aadhaar',''),
                pan_passport=personal.get('pan_passport',''),
                address=personal.get('address',''),
                blood_group=medical.get('blood_group','O+'),
                height_cm=int(medical.get('height_cm',0) or 0) or None,
                weight_kg=int(medical.get('weight_kg',0) or 0) or None,
                disability_status=medical.get('disability_status','None'),
                allergies=medical.get('allergies',''),
                chronic_conditions=medical.get('chronic_conditions',''),
                current_medications=medical.get('current_medications',''),
                past_surgeries=medical.get('past_surgeries',''),
                emergency_name=medical.get('emergency_name',''),
                emergency_relation=medical.get('emergency_relation',''),
                emergency_mobile=medical.get('emergency_mobile',''),
                emergency_mobile2=medical.get('emergency_mobile2',''),
                insurance_provider=insurance.get('insurance_provider',''),
                policy_number=insurance.get('policy_number',''),
                sum_insured=int(insurance.get('sum_insured',0) or 0) or None,
                policy_expiry=insurance.get('policy_expiry') or None,
                tpa=insurance.get('tpa',''),
                scheme_pmjay=boolval(insurance.get('scheme_pmjay','')),
                scheme_state=boolval(insurance.get('scheme_state','')),
                scheme_bpl=boolval(insurance.get('scheme_bpl','')),
                scheme_defence=boolval(insurance.get('scheme_defence','')),
            )
            # Photo
            if request.session.get('reg_has_photo') and 'photo' in request.FILES:
                patient.photo = request.FILES['photo']
            patient.save()

            card = SmartCard.objects.create(patient=patient, status='pending')

            # Send registration confirmation email
            if patient.email:
                send_email(
                    subject='Your MedCard Registration is Confirmed!',
                    template='emails/registration_confirm.html',
                    context={'patient': patient, 'card': card},
                    recipient_email=patient.email,
                )

            CardDelivery.objects.create(
                card=card,
                address_line1=delivery.get('address_line1',''),
                address_line2=delivery.get('address_line2',''),
                city=delivery.get('city',''),
                state=delivery.get('state',''),
                pin_code=delivery.get('pin_code',''),
                delivery_mobile=delivery.get('delivery_mobile',''),
                preferred_slot=delivery.get('preferred_slot','any'),
                instructions=delivery.get('instructions',''),
            )

            # Clear session
            for key in ['reg_step','reg_personal','reg_medical','reg_insurance','reg_delivery','reg_has_photo']:
                request.session.pop(key, None)

            messages.success(request, f'Registration complete! Your card ID is {card.card_id}.')
            return redirect('delivery')

    else:
        # GET — show blank form for current step
        forms_map = {
            1: PersonalInfoForm(),
            2: MedicalInfoForm(),
            3: InsuranceInfoForm(),
            4: DeliveryForm(),
            5: None,
        }
        form = forms_map.get(step)

    steps_meta = [('Personal',1),('Medical',2),('Insurance',3),('Delivery',4),('Consent',5)]
    return render(request, 'registration.html', {'form': form, 'step': step, 'steps_meta': steps_meta})


# ─── RENEWAL ──────────────────────────────────────────────────────────────────

@login_required
def renewal_view(request):
    try:
        patient = request.user.patient
        card = patient.card
    except (Patient.DoesNotExist, SmartCard.DoesNotExist):
        messages.warning(request, 'No Smart Card found. Please register first.')
        return redirect('register')

    existing_renewal = card.renewals.filter(status__in=['submitted','under_review']).first()
    form = RenewalForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        if existing_renewal:
            messages.warning(request, 'A renewal request is already under review.')
        else:
            new_expiry = card.valid_until + relativedelta(years=5)
            CardRenewal.objects.create(
                card=card,
                new_expiry=new_expiry,
                reason=form.cleaned_data['reason'],
            )
            messages.success(request, 'Renewal request submitted successfully!')
            return redirect('renewal')

    return render(request, 'renewal.html', {
        'card': card,
        'patient': patient,
        'form': form,
        'existing_renewal': existing_renewal,
        'is_expiring_soon': card.is_expiring_soon(),
        'days_to_expiry': card.days_to_expiry(),
        'renewals': card.renewals.order_by('-requested_on')[:5],
    })


# ─── DELIVERY ─────────────────────────────────────────────────────────────────

@login_required
def delivery_view(request):
    try:
        patient = request.user.patient
        card = patient.card
        delivery = card.deliveries.order_by('-requested_at').first()
    except (Patient.DoesNotExist, SmartCard.DoesNotExist):
        messages.warning(request, 'No Smart Card found. Please register first.')
        return redirect('register')

    STEPS = [
        ('processing', 'Processing', '⚙️', 'Application verified, card being printed'),
        ('dispatched', 'Dispatched', '📦', 'Card packed and handed to courier'),
        ('in_transit', 'In Transit', '🚚', 'Card on its way to your city'),
        ('out_for_delivery', 'Out for Delivery', '🛵', 'Delivery agent on the way'),
        ('delivered', 'Delivered', '✅', 'Card delivered successfully'),
    ]

    step_names = [s[0] for s in STEPS]
    current_idx = step_names.index(delivery.status) if delivery and delivery.status in step_names else 0

    return render(request, 'delivery.html', {
        'card': card,
        'patient': patient,
        'delivery': delivery,
        'steps': STEPS,
        'current_idx': current_idx,
    })


# ─── FACILITIES ───────────────────────────────────────────────────────────────

FACILITY_META = {
    'identity':         {'title': 'Unified Patient Identity',    'icon': '🔍', 'tag': 'Core'},
    'health-records':   {'title': 'Electronic Health Records',   'icon': '📁', 'tag': 'Records'},
    'insurance':        {'title': 'Cashless Insurance Claims',   'icon': '💳', 'tag': 'Financial'},
    'emergency':        {'title': 'Emergency Medical Access',    'icon': '🚨', 'tag': 'Emergency'},
    'appointments':     {'title': 'OPD Appointment Booking',     'icon': '📅', 'tag': 'Outpatient'},
    'hospitalization':  {'title': 'Cashless Hospitalization',    'icon': '🏥', 'tag': 'Inpatient'},
    'lab-diagnostics':  {'title': 'Lab & Diagnostics',           'icon': '🧪', 'tag': 'Diagnostics'},
    'pharmacy':         {'title': 'Pharmacy & Medication',       'icon': '💊', 'tag': 'Pharmacy'},
    'telemedicine':     {'title': 'Telemedicine',                'icon': '🩺', 'tag': 'Digital'},
    'govt-schemes':     {'title': 'Government Scheme Benefits',  'icon': '🛡️', 'tag': 'Welfare'},
    'privacy':          {'title': 'Consent & Privacy',           'icon': '🔒', 'tag': 'Privacy'},
    'analytics':        {'title': 'Health Analytics',            'icon': '📊', 'tag': 'Insights'},
}


def facility_view(request, slug):
    meta = FACILITY_META.get(slug)
    if not meta:
        from django.http import Http404
        raise Http404
    return render(request, f'facilities/{slug}.html', {'meta': meta, 'slug': slug})

# ─── ADMIN PANEL ──────────────────────────────────────────────────────────────

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q, Count

def superuser_required(view_func):
    """Decorator — only superusers can access admin panel views."""
    from functools import wraps
    from django.http import HttpResponseForbidden
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return redirect('/login/?next=' + request.path)
        return view_func(request, *args, **kwargs)
    return wrapper


@superuser_required
def admin_dashboard(request):
    from django.utils import timezone
    from datetime import timedelta

    total_patients  = Patient.objects.count()
    total_cards     = SmartCard.objects.count()
    active_cards    = SmartCard.objects.filter(status='active').count()
    pending_cards   = SmartCard.objects.filter(status='pending').count()
    total_renewals  = CardRenewal.objects.count()
    pending_renewals= CardRenewal.objects.filter(status='submitted').count()
    total_deliveries= CardDelivery.objects.count()
    delivered       = CardDelivery.objects.filter(status='delivered').count()
    expiring_soon   = SmartCard.objects.filter(
        valid_until__lte=date.today() + relativedelta(days=90),
        status='active'
    ).count()

    recent_patients = Patient.objects.order_by('-created_at')[:5]
    recent_renewals = CardRenewal.objects.order_by('-requested_on')[:5]

    return render(request, 'admin_panel/dashboard.html', {
        'total_patients':   total_patients,
        'total_cards':      total_cards,
        'active_cards':     active_cards,
        'pending_cards':    pending_cards,
        'total_renewals':   total_renewals,
        'pending_renewals': pending_renewals,
        'total_deliveries': total_deliveries,
        'delivered':        delivered,
        'expiring_soon':    expiring_soon,
        'recent_patients':  recent_patients,
        'recent_renewals':  recent_renewals,
    })


@superuser_required
def admin_patients(request):
    q      = request.GET.get('q', '').strip()
    blood  = request.GET.get('blood', '')
    gender = request.GET.get('gender', '')

    patients = Patient.objects.all().order_by('-created_at')

    if q:
        patients = patients.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q)  |
            Q(mobile__icontains=q)     |
            Q(aadhaar__icontains=q)    |
            Q(card__card_id__icontains=q)
        )
    if blood:
        patients = patients.filter(blood_group=blood)
    if gender:
        patients = patients.filter(gender=gender)

    return render(request, 'admin_panel/patients.html', {
        'patients': patients,
        'q': q, 'blood': blood, 'gender': gender,
        'blood_choices': Patient.BLOOD_CHOICES,
        'gender_choices': Patient.GENDER_CHOICES,
        'total': patients.count(),
    })


@superuser_required
def admin_patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    card = None
    delivery = None
    renewals = []
    try:
        card     = patient.card
        delivery = card.deliveries.order_by('-requested_at').first()
        renewals = card.renewals.order_by('-requested_on')
    except SmartCard.DoesNotExist:
        pass
    return render(request, 'admin_panel/patient_detail.html', {
        'patient': patient,
        'card': card,
        'delivery': delivery,
        'renewals': renewals,
    })


@superuser_required
def admin_patient_delete(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        user = patient.user
        patient.delete()
        user.delete()
        messages.success(request, 'Patient and associated account deleted successfully.')
        return redirect('admin_patients')
    return render(request, 'admin_panel/confirm_delete.html', {'patient': patient})


@superuser_required
def admin_cards(request):
    q      = request.GET.get('q', '').strip()
    status = request.GET.get('status', '')

    cards = SmartCard.objects.select_related('patient').order_by('-issued_on')

    if q:
        cards = cards.filter(
            Q(card_id__icontains=q) |
            Q(patient__first_name__icontains=q) |
            Q(patient__last_name__icontains=q)  |
            Q(patient__mobile__icontains=q)
        )
    if status:
        cards = cards.filter(status=status)

    return render(request, 'admin_panel/cards.html', {
        'cards': cards,
        'q': q,
        'status': status,
        'status_choices': SmartCard.STATUS_CHOICES,
        'total': cards.count(),
    })


@superuser_required
def admin_card_status(request, pk):
    card = get_object_or_404(SmartCard, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(SmartCard.STATUS_CHOICES):
            card.status = new_status
            card.save()
            messages.success(request, f'Card {card.card_id} status updated to {new_status}.')
    return redirect('admin_cards')


@superuser_required
def admin_deliveries(request):
    q      = request.GET.get('q', '').strip()
    status = request.GET.get('status', '')

    deliveries = CardDelivery.objects.select_related('card__patient').order_by('-requested_at')

    if q:
        deliveries = deliveries.filter(
            Q(card__card_id__icontains=q) |
            Q(card__patient__first_name__icontains=q) |
            Q(card__patient__last_name__icontains=q)  |
            Q(city__icontains=q) |
            Q(pin_code__icontains=q)
        )
    if status:
        deliveries = deliveries.filter(status=status)

    return render(request, 'admin_panel/deliveries.html', {
        'deliveries': deliveries,
        'q': q,
        'status': status,
        'status_choices': CardDelivery.DELIVERY_STATUS,
        'total': deliveries.count(),
    })


@superuser_required
def admin_delivery_status(request, pk):
    delivery = get_object_or_404(CardDelivery, pk=pk)
    if request.method == 'POST':
        new_status   = request.POST.get('status')
        tracking_id  = request.POST.get('tracking_id', '').strip()
        if new_status in dict(CardDelivery.DELIVERY_STATUS):
            delivery.status = new_status
            if tracking_id:
                delivery.tracking_id = tracking_id
            if new_status == 'delivered':
                from django.utils import timezone
                delivery.delivered_at = timezone.now()
            delivery.save()
            # Send delivery update email
            if delivery.card.patient.email:
                send_email(
                    subject=f'MedCard Delivery Update — {delivery.get_status_display()}',
                    template='emails/delivery_update.html',
                    context={'patient': delivery.card.patient, 'delivery': delivery},
                    recipient_email=delivery.card.patient.email,
                )
            messages.success(request, f'Delivery status updated to {new_status}.')
    return redirect('admin_deliveries')


@superuser_required
def admin_renewals(request):
    q      = request.GET.get('q', '').strip()
    status = request.GET.get('status', '')

    renewals = CardRenewal.objects.select_related('card__patient').order_by('-requested_on')

    if q:
        renewals = renewals.filter(
            Q(card__card_id__icontains=q) |
            Q(card__patient__first_name__icontains=q) |
            Q(card__patient__last_name__icontains=q)
        )
    if status:
        renewals = renewals.filter(status=status)

    return render(request, 'admin_panel/renewals.html', {
        'renewals': renewals,
        'q': q,
        'status': status,
        'status_choices': CardRenewal.STATUS_CHOICES,
        'total': renewals.count(),
    })


@superuser_required
def admin_renewal_action(request, pk):
    renewal = get_object_or_404(CardRenewal, pk=pk)
    if request.method == 'POST':
        action  = request.POST.get('action')
        remarks = request.POST.get('remarks', '').strip()
        if action == 'approve':
            renewal.status = 'approved'
            # Send renewal approval email
            if renewal.card.patient.email:
                send_email(
                    subject='Your MedCard Renewal has been Approved!',
                    template='emails/renewal_approved.html',
                    context={'patient': renewal.card.patient, 'card': renewal.card, 'renewal': renewal},
                    recipient_email=renewal.card.patient.email,
                )
            renewal.card.valid_until = renewal.new_expiry
            renewal.card.save()
            messages.success(request, 'Renewal approved. Card validity extended.')
        elif action == 'reject':
            renewal.status = 'rejected'
            # Send renewal rejection email
            if renewal.card.patient.email:
                send_email(
                    subject='Update on Your MedCard Renewal Request',
                    template='emails/renewal_rejected.html',
                    context={'patient': renewal.card.patient, 'renewal': renewal},
                    recipient_email=renewal.card.patient.email,
                )
            messages.warning(request, 'Renewal request rejected.')
        renewal.remarks = remarks
        renewal.save()
    return redirect('admin_renewals')