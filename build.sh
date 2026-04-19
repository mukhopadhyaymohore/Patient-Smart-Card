#!/usr/bin/env bash
set -o errexit
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py shell << 'EOF'
from django.contrib.auth.models import User
if not User.objects.filter(username='mukhopadhyaymohore').exists():
    User.objects.create_superuser('mukhopadhyaymohore', 'mohore.mukhopadhyay@gmail.com', 'MedCard@2026')
    print("Superuser created")
else:
    print("Superuser already exists")
EOF