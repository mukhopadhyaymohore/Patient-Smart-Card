# 🏥 Patient Smart Card

A full-stack Django web application that digitizes and unifies patient healthcare management — from identity verification to cashless insurance claims, all through a single smart card.

🔗 **Live Demo:** [patient-smart-card-khjy.onrender.com](https://patient-smart-card-khjy.onrender.com)

---

## 📌 Overview

The Patient Smart Card system replaces fragmented health documents with a single, secure, NFC-enabled card linked to a patient's complete medical profile. It provides healthcare facilities, insurers, and patients a unified platform for managing health records, appointments, insurance claims, and more.

---

## ✨ Features

### Patient Side
- 🪪 **Unified Patient Identity** — Aadhaar-linked, biometric-enabled digital health ID
- 📁 **Electronic Health Records** — Lifetime medical history, lab reports, prescriptions
- 💳 **Cashless Insurance Claims** — Auto pre-authorization and claim settlement
- 🚨 **Emergency Medical Access** — Critical info accessible without PIN
- 📅 **OPD Appointment Booking** — Book specialists across 5,000+ hospitals
- 🏥 **Cashless Hospitalization** — Admission to discharge without upfront payment
- 🧪 **Lab & Diagnostics** — Discounted tests, results auto-synced to EHR
- 💊 **Pharmacy & Medication** — E-prescriptions, drug-allergy cross-checks
- 🩺 **Telemedicine** — 24/7 video consultations with verified doctors
- 🛡️ **Government Scheme Benefits** — PM-JAY, Ayushman Bharat auto-linked
- 🔒 **Consent & Privacy Control** — Granular permissions per provider
- 📊 **Health Analytics** — Personalized health score and risk alerts

### Admin Side
- 📊 Custom Admin Dashboard with live stats
- 👤 Patient management with search and filters
- 💳 Smart Card status management
- 📦 Delivery tracking and status updates
- 🔄 Renewal request approval/rejection workflow

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Django 4.2 |
| Frontend | HTML5, CSS3, JavaScript |
| Database | SQLite (dev) |
| Static Files | WhiteNoise |
| Deployment | Render |
| Version Control | Git, GitHub |

## 📂 Project Structure

```
Patient Smart Card/
├── cards/                  ← Main Django app
│   ├── migrations/
│   ├── admin.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── config/                 ← Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── static/css/             ← Shared stylesheet
├── templates/              ← HTML templates
│   ├── admin_panel/
│   ├── auth/
│   ├── emails/
│   └── facilities/
│   └── base.html
├── manage.py
├── requirements.txt
├── Procfile
└── build.sh
```


## 🚀 Local Setup

```bash
# Clone the repository
git clone https://github.com/mukhopadhyaymohore/Patient-Smart-Card.git
cd Patient-Smart-Card

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file with these variables
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start server
python manage.py runserver
```

---

## 🌐 Deployment

Deployed on **Render** with:
- Automatic deploys from GitHub `main` branch
- Environment variables managed via Render dashboard
- Static files served via WhiteNoise
- HTTPS provided automatically by Render

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
