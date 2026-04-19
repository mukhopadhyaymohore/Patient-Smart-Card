from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('signup/',  views.signup_view,  name='signup'),
    path('login/',   views.login_view,   name='login'),
    path('logout/',  views.logout_view,  name='logout'),

    # Core pages
    path('',           views.home_view,     name='home'),
    path('register/',  views.register_view, name='register'),
    path('renew/',     views.renewal_view,  name='renewal'),
    path('delivery/',  views.delivery_view, name='delivery'),

    # Facilities
    path('facilities/<slug:slug>/', views.facility_view, name='facility'),

    # Admin panel
    path('admin-panel/',                        views.admin_dashboard,    name='admin_dashboard'),
    path('admin-panel/patients/',               views.admin_patients,     name='admin_patients'),
    path('admin-panel/patients/<int:pk>/',      views.admin_patient_detail, name='admin_patient_detail'),
    path('admin-panel/patients/<int:pk>/delete/', views.admin_patient_delete, name='admin_patient_delete'),
    path('admin-panel/cards/',                  views.admin_cards,        name='admin_cards'),
    path('admin-panel/cards/<int:pk>/status/',  views.admin_card_status,  name='admin_card_status'),
    path('admin-panel/deliveries/',             views.admin_deliveries,   name='admin_deliveries'),
    path('admin-panel/deliveries/<int:pk>/status/', views.admin_delivery_status, name='admin_delivery_status'),
    path('admin-panel/renewals/',               views.admin_renewals,     name='admin_renewals'),
    path('admin-panel/renewals/<int:pk>/action/', views.admin_renewal_action, name='admin_renewal_action'),
]