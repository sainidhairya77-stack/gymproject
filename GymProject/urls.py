from django.contrib import admin
from django.urls import path

from gymapp import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", views.login_view, name="login"),
    path("register/", views.register, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),
    path("membership-plans/", views.membership_plans, name="membership_plans"),
    path("members/", views.members, name="members"),
    path("members/add/", views.member_form, name="member_add"),
    path("members/<int:pk>/", views.member_detail, name="member_detail"),
    path("members/<int:pk>/edit/", views.member_form, name="member_edit"),
    path("members/<int:pk>/delete/", views.member_delete, name="member_delete"),
    path("attendance/", views.attendance, name="attendance"),
    path("attendance/add/", views.attendance_form, name="attendance_add"),
    path("attendance/<int:pk>/edit/", views.attendance_form, name="attendance_edit"),
    path("attendance/<int:pk>/delete/", views.attendance_delete, name="attendance_delete"),
    path("payments/", views.payments, name="payments"),
    path("payments/add/", views.payment_form, name="payment_add"),
    path("payments/<int:pk>/edit/", views.payment_form, name="payment_edit"),
    path("payments/<int:pk>/delete/", views.payment_delete, name="payment_delete"),
    path("equipment/", views.equipment, name="equipment"),
    path("equipment/add/", views.equipment_form, name="equipment_add"),
    path("equipment/<int:pk>/edit/", views.equipment_form, name="equipment_edit"),
    path("equipment/<int:pk>/delete/", views.equipment_delete, name="equipment_delete"),
    path("workout/", views.workout, name="workout"),
    path("home-workout/", views.home_workout, name="home_workout"),
    path("diet/", views.diet_plans, name="diet"),
    path("progress/", views.progress, name="progress"),
    path("progress/add/", views.progress_form, name="progress_add"),
    path("progress/<int:pk>/edit/", views.progress_form, name="progress_edit"),
    path("progress/<int:pk>/delete/", views.progress_delete, name="progress_delete"),
    path("ai-assistant/", views.ai_assistant, name="ai_assistant"),
]
