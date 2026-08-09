from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (
    AttendanceForm,
    EquipmentForm,
    LoginForm,
    MemberProfileForm,
    PaymentForm,
    ProfileForm,
    ProgressForm,
    RegisterForm,
)
from .models import (
    AIPlan,
    Attendance,
    Equipment,
    MembershipPlan,
    MemberProfile,
    Payment,
    Progress,
)


DIET_OPTIONS = {
    "veg_no_egg": {
        "label": "Vegetarian without egg",
        "breakfast": [
            "Oats with milk, banana, almonds and peanut butter",
            "Vegetable poha with curd and seasonal fruit",
            "Paneer sandwich with milk and banana",
        ],
        "lunch": [
            "Roti, dal, paneer, vegetables and salad",
            "Rice, rajma, curd and mixed vegetables",
            "Roti, chole, paneer and salad",
        ],
        "dinner": [
            "Roti, paneer, mixed vegetables and curd",
            "Dal, rice, salad and curd",
            "Roti, dal, vegetables and paneer",
        ],
    },
    "veg_egg": {
        "label": "Vegetarian with egg",
        "breakfast": [
            "Boiled eggs, oats, banana and milk",
            "Vegetable omelette, whole wheat toast and fruit",
            "Egg sandwich with milk and banana",
        ],
        "lunch": [
            "Roti, dal, boiled eggs, vegetables and salad",
            "Rice, rajma, egg bhurji and curd",
            "Roti, paneer, egg curry and vegetables",
        ],
        "dinner": [
            "Roti, paneer, boiled eggs and vegetables",
            "Rice, dal, egg bhurji and salad",
            "Roti, egg curry, vegetables and curd",
        ],
    },
    "non_veg": {
        "label": "Non-vegetarian",
        "breakfast": [
            "Eggs, whole wheat toast, banana and milk",
            "Chicken sandwich with fruit and milk",
            "Omelette with oats and banana",
        ],
        "lunch": [
            "Grilled chicken, rice, vegetables and salad",
            "Chicken curry, roti, vegetables and curd",
            "Fish, rice, vegetables and salad",
        ],
        "dinner": [
            "Grilled chicken, roti and vegetables",
            "Fish, rice, salad and vegetables",
            "Chicken, vegetables, roti and curd",
        ],
    },
}

GOAL_ADVICE = {
    "muscle": {
        "label": "Muscle Gain",
        "tip": "Keep protein high, train each muscle group consistently, and increase weights gradually.",
    },
    "weightgain": {
        "label": "Weight Gain",
        "tip": "Add calorie-dense foods like milk, paneer, rice, nuts and peanut butter in controlled portions.",
    },
    "weightloss": {
        "label": "Weight Loss",
        "tip": "Prefer lean protein, vegetables, measured portions of carbs and regular walking or cardio.",
    },
    "general": {
        "label": "General Fitness",
        "tip": "Balance strength training, simple meals, hydration and steady sleep.",
    },
}

GYM_WORKOUTS = {
    "Chest": ["Bench Press", "Incline Dumbbell Press", "Cable Crossover"],
    "Back": ["Lat Pulldown", "Seated Cable Row", "Barbell Row"],
    "Shoulders": ["Shoulder Press", "Lateral Raises", "Rear Delt Fly"],
    "Legs": ["Squats", "Leg Press", "Leg Curl"],
    "Biceps": ["Barbell Curl", "Dumbbell Curl", "Hammer Curl"],
    "Triceps": ["Triceps Pushdown", "Overhead Extension", "Close Grip Bench Press"],
    "Abs": ["Cable Crunch", "Leg Raises", "Plank"],
}

HOME_WORKOUTS = {
    "Chest": ["Push Ups", "Wide Push Ups", "Diamond Push Ups"],
    "Back": ["Superman", "Reverse Snow Angels", "Bird Dog"],
    "Shoulders": ["Pike Push Ups", "Arm Circles", "Shoulder Taps"],
    "Legs": ["Bodyweight Squats", "Lunges", "Glute Bridges"],
    "Arms": ["Close Grip Push Ups", "Diamond Push Ups", "Isometric Biceps Hold"],
    "Abs": ["Crunches", "Leg Raises", "Mountain Climbers", "Plank"],
}


def _profile_for_user(user):
    if not user.is_authenticated:
        return None
    profile, _created = MemberProfile.objects.get_or_create(
        user=user,
        defaults={
            "full_name": user.get_full_name() or user.username,
            "mobile": "",
            "email": user.email,
        },
    )
    return profile


def _is_premium_user(user):
    if not user.is_authenticated:
        return False
    if user.is_staff or user.is_superuser:
        return True
    profile = _profile_for_user(user)
    return bool(
        profile
        and profile.ai_plan
        and profile.ai_plan.name.lower() == "premium"
        and profile.ai_plan.is_active
    )


def _workout_recommendation(workout_type, is_premium, goal):
    workouts = GYM_WORKOUTS if workout_type == "gym" else HOME_WORKOUTS
    title = "Detailed Gym Workout" if workout_type == "gym" else "Detailed Home Workout"
    if not is_premium:
        title = "Basic Gym Workout" if workout_type == "gym" else "Basic Home Workout"

    limit = 3 if is_premium else 2
    sets = "4 sets x 8-12 reps" if is_premium else "3 sets x 10 reps"
    recommendation = []
    for section, exercises in workouts.items():
        recommendation.append(
            {
                "section": section,
                "items": [f"{exercise} - {sets}" for exercise in exercises[:limit]],
            }
        )
    notes = [
        "Warm up for 5-10 minutes before training.",
        "Keep form controlled and rest 60-90 seconds between sets.",
    ]
    if is_premium:
        notes.extend(
            [
                "Train 4-5 days per week and rotate heavy, moderate and light sessions.",
                GOAL_ADVICE.get(goal, GOAL_ADVICE["general"])["tip"],
            ]
        )
    return {"title": title, "sections": recommendation, "notes": notes}


def _diet_recommendation(diet_key, goal_key, is_premium):
    diet = DIET_OPTIONS.get(diet_key, DIET_OPTIONS["veg_no_egg"])
    goal = GOAL_ADVICE.get(goal_key, GOAL_ADVICE["general"])
    option_count = 3 if is_premium else 1
    return {
        "title": "Detailed Diet Plan" if is_premium else "Basic Diet Plan",
        "diet_label": diet["label"],
        "goal_label": goal["label"],
        "goal_tip": goal["tip"],
        "meals": [
            {"name": "Breakfast", "options": diet["breakfast"][:option_count]},
            {"name": "Lunch", "options": diet["lunch"][:option_count]},
            {"name": "Dinner", "options": diet["dinner"][:option_count]},
        ],
        "notes": [
            "Drink enough water through the day.",
            "Adjust portions based on hunger, training level and progress.",
        ],
    }


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("dashboard")
    return render(request, "login.html", {"form": form})


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)
        user.email = form.cleaned_data.get("email", "")
        user.save()
        free_plan = AIPlan.objects.filter(name="Free", is_active=True).first()
        MemberProfile.objects.create(
            user=user,
            full_name=form.cleaned_data["full_name"],
            mobile=form.cleaned_data["mobile"],
            email=form.cleaned_data.get("email", ""),
            goal=form.cleaned_data.get("goal", ""),
            ai_plan=free_plan,
        )
        login(request, user)
        return redirect("dashboard")
    return render(request, "register.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def dashboard(request):
    today = timezone.localdate()
    total_members = MemberProfile.objects.count()
    total_attendance = Attendance.objects.count()
    present_today = Attendance.objects.filter(date=today, status="Present").count()
    total_payments = Payment.objects.count()
    paid_amount = Payment.objects.filter(payment_status="Paid").aggregate(
        total=Sum("amount")
    )["total"] or 0
    total_equipment = Equipment.objects.count()
    active_equipment = Equipment.objects.filter(is_active=True).count()

    return render(
        request,
        "dashboard.html",
        {
            "total_members": total_members,
            "total_attendance": total_attendance,
            "present_today": present_today,
            "total_payments": total_payments,
            "paid_amount": paid_amount,
            "total_equipment": total_equipment,
            "active_equipment": active_equipment,
        },
    )


@login_required
def profile(request):
    member_profile = _profile_for_user(request.user)
    form = ProfileForm(request.POST or None, instance=member_profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        request.user.email = form.cleaned_data.get("email") or ""
        request.user.save(update_fields=["email"])
        messages.success(request, "Profile updated successfully.")
        return redirect("profile")
    return render(request, "profile.html", {"profile": member_profile, "form": form})


@login_required
def membership_plans(request):
    return render(
        request,
        "membership_plans.html",
        {
            "plans": MembershipPlan.objects.all().order_by("duration_months", "fee"),
            "ai_plans": AIPlan.objects.filter(is_active=True).order_by("price"),
        },
    )


@login_required
def members(request):
    members_list = MemberProfile.objects.select_related("plan", "ai_plan", "trainer").all()
    return render(
        request,
        "members.html",
        {
            "members": members_list,
            "active_members": members_list.filter(
                Q(membership_end_date__isnull=True)
                | Q(membership_end_date__gte=timezone.localdate())
            ).count(),
            "today": timezone.localdate(),
        },
    )


@login_required
def member_detail(request, pk):
    member = get_object_or_404(
        MemberProfile.objects.select_related("user", "plan", "ai_plan", "trainer"), pk=pk
    )
    payments = member.payments.select_related("plan").order_by("-payment_date")
    attendance_records = member.attendances.order_by("-date")[:10]
    progress_records = member.progress_records.order_by("-recorded_date")[:10]
    return render(
        request,
        "member_detail.html",
        {
            "member": member,
            "payments": payments,
            "attendance_records": attendance_records,
            "progress_records": progress_records,
        },
    )


@login_required
def member_form(request, pk=None):
    member = get_object_or_404(MemberProfile, pk=pk) if pk else None
    form = MemberProfileForm(request.POST or None, instance=member)
    if request.method == "POST" and form.is_valid():
        saved_member = form.save()
        messages.success(request, "Member saved successfully.")
        return redirect("member_detail", pk=saved_member.pk)
    return render(
        request,
        "form_page.html",
        {
            "title": "Edit Member" if member else "Add Member",
            "form": form,
            "cancel_url": "members",
        },
    )


@login_required
def member_delete(request, pk):
    member = get_object_or_404(MemberProfile, pk=pk)
    if request.method == "POST":
        member.delete()
        messages.success(request, "Member deleted successfully.")
        return redirect("members")
    return render(
        request,
        "confirm_delete.html",
        {"title": "Delete Member", "object_name": member.full_name, "cancel_url": "members"},
    )


@login_required
def attendance(request):
    attendance_list = Attendance.objects.select_related("member").all().order_by("-date")
    total = attendance_list.count()
    present = attendance_list.filter(status="Present").count()
    absent = attendance_list.filter(status="Absent").count()
    attendance_percentage = round((present / total) * 100) if total else 0

    return render(
        request,
        "attendance.html",
        {
            "attendance": attendance_list,
            "present": present,
            "absent": absent,
            "attendance_percentage": attendance_percentage,
        },
    )


@login_required
def attendance_form(request, pk=None):
    record = get_object_or_404(Attendance, pk=pk) if pk else None
    form = AttendanceForm(request.POST or None, instance=record)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Attendance saved successfully.")
        return redirect("attendance")
    return render(
        request,
        "form_page.html",
        {
            "title": "Edit Attendance" if record else "Add Attendance",
            "form": form,
            "cancel_url": "attendance",
        },
    )


@login_required
def attendance_delete(request, pk):
    record = get_object_or_404(Attendance, pk=pk)
    if request.method == "POST":
        record.delete()
        messages.success(request, "Attendance deleted successfully.")
        return redirect("attendance")
    return render(
        request,
        "confirm_delete.html",
        {"title": "Delete Attendance", "object_name": str(record), "cancel_url": "attendance"},
    )


@login_required
def payments(request):
    payment_list = Payment.objects.select_related("member", "plan").all().order_by(
        "-payment_date"
    )
    paid_total = payment_list.filter(payment_status="Paid").aggregate(total=Sum("amount"))[
        "total"
    ] or 0
    pending_count = payment_list.filter(payment_status="Pending").count()
    return render(
        request,
        "payments.html",
        {
            "payments": payment_list,
            "paid_total": paid_total,
            "pending_count": pending_count,
        },
    )


@login_required
def payment_form(request, pk=None):
    payment = get_object_or_404(Payment, pk=pk) if pk else None
    form = PaymentForm(request.POST or None, instance=payment)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Payment saved successfully.")
        return redirect("payments")
    return render(
        request,
        "form_page.html",
        {
            "title": "Edit Payment" if payment else "Add Payment",
            "form": form,
            "cancel_url": "payments",
        },
    )


@login_required
def payment_delete(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    if request.method == "POST":
        payment.delete()
        messages.success(request, "Payment deleted successfully.")
        return redirect("payments")
    return render(
        request,
        "confirm_delete.html",
        {"title": "Delete Payment", "object_name": str(payment), "cancel_url": "payments"},
    )


@login_required
def equipment(request):
    equipment_list = Equipment.objects.all().order_by("name")
    return render(
        request,
        "equipment.html",
        {
            "equipment": equipment_list,
            "active_equipment": equipment_list.filter(is_active=True).count(),
            "total_units": sum(item.units for item in equipment_list),
        },
    )


@login_required
def equipment_form(request, pk=None):
    item = get_object_or_404(Equipment, pk=pk) if pk else None
    form = EquipmentForm(request.POST or None, instance=item)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Equipment saved successfully.")
        return redirect("equipment")
    return render(
        request,
        "form_page.html",
        {
            "title": "Edit Equipment" if item else "Add Equipment",
            "form": form,
            "cancel_url": "equipment",
        },
    )


@login_required
def equipment_delete(request, pk):
    item = get_object_or_404(Equipment, pk=pk)
    if request.method == "POST":
        item.delete()
        messages.success(request, "Equipment deleted successfully.")
        return redirect("equipment")
    return render(
        request,
        "confirm_delete.html",
        {"title": "Delete Equipment", "object_name": item.name, "cancel_url": "equipment"},
    )


@login_required
def workout(request):
    return render(request, "workout.html", {"workouts": GYM_WORKOUTS})


@login_required
def home_workout(request):
    return render(request, "home_workout.html", {"workouts": HOME_WORKOUTS})


@login_required
def diet_plans(request):
    selected_diet = request.GET.get("diet", "veg_no_egg")
    selected_goal = request.GET.get("goal", "general")
    recommendation = _diet_recommendation(selected_diet, selected_goal, True)
    return render(
        request,
        "diet_plans.html",
        {
            "diet_options": DIET_OPTIONS,
            "goal_options": GOAL_ADVICE,
            "selected_diet": selected_diet,
            "selected_goal": selected_goal,
            "recommendation": recommendation,
        },
    )


@login_required
def progress(request):
    member_profile = _profile_for_user(request.user)
    if request.user.is_staff or request.user.is_superuser:
        progress_records = Progress.objects.select_related("member").order_by("-recorded_date")
        attendance_qs = Attendance.objects.all()
    else:
        progress_records = member_profile.progress_records.order_by("-recorded_date")
        attendance_qs = member_profile.attendances.all()

    total_attendance = attendance_qs.count()
    present_attendance = attendance_qs.filter(status="Present").count()
    attendance_percentage = (
        round((present_attendance / total_attendance) * 100) if total_attendance else 0
    )
    latest_progress = progress_records.first()
    first_progress = progress_records.order_by("recorded_date").first()
    weight_change = None
    if latest_progress and first_progress and latest_progress.weight and first_progress.weight:
        weight_change = latest_progress.weight - first_progress.weight
    progress_percentage = min(attendance_percentage, 100)
    goal = member_profile.goal or "General Fitness"
    recommendation = "Stay consistent with workouts, attendance and meal timing."
    if attendance_percentage < 50:
        recommendation = "Focus on improving attendance first with 3 fixed workout days per week."
    elif latest_progress and latest_progress.weight:
        recommendation = "Track weight weekly and adjust diet portions based on your goal."

    return render(
        request,
        "progress.html",
        {
            "member_profile": member_profile,
            "progress_records": progress_records[:20],
            "latest_progress": latest_progress,
            "weight_change": weight_change,
            "attendance_percentage": attendance_percentage,
            "goal": goal,
            "progress_percentage": progress_percentage,
            "recommendation": recommendation,
        },
    )


@login_required
def progress_form(request, pk=None):
    record = get_object_or_404(Progress, pk=pk) if pk else None
    form = ProgressForm(request.POST or None, instance=record)
    if not (request.user.is_staff or request.user.is_superuser):
        form.fields["member"].queryset = MemberProfile.objects.filter(user=request.user)
        form.fields["member"].initial = _profile_for_user(request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Progress saved successfully.")
        return redirect("progress")
    return render(
        request,
        "form_page.html",
        {
            "title": "Edit Progress" if record else "Add Progress",
            "form": form,
            "cancel_url": "progress",
        },
    )


@login_required
def progress_delete(request, pk):
    record = get_object_or_404(Progress, pk=pk)
    if request.method == "POST":
        record.delete()
        messages.success(request, "Progress deleted successfully.")
        return redirect("progress")
    return render(
        request,
        "confirm_delete.html",
        {"title": "Delete Progress", "object_name": str(record), "cancel_url": "progress"},
    )


@login_required
def ai_assistant(request):
    selected_plan = request.POST.get("plan") or "free"
    feature = request.POST.get("feature") or ""
    selected_diet = request.POST.get("diet") or "veg_no_egg"
    selected_goal = request.POST.get("goal") or "general"
    user_has_premium = _is_premium_user(request.user)
    requested_premium = selected_plan == "premium"
    active_premium = requested_premium and user_has_premium
    upgrade_required = requested_premium and not user_has_premium
    recommendation = None

    if feature == "gym":
        recommendation = _workout_recommendation("gym", active_premium, selected_goal)
    elif feature == "home":
        recommendation = _workout_recommendation("home", active_premium, selected_goal)
    elif feature == "diet":
        recommendation = _diet_recommendation(selected_diet, selected_goal, active_premium)

    return render(
        request,
        "ai_assistant.html",
        {
            "selected_plan": selected_plan,
            "feature": feature,
            "selected_diet": selected_diet,
            "selected_goal": selected_goal,
            "diet_options": DIET_OPTIONS,
            "goal_options": GOAL_ADVICE,
            "recommendation": recommendation,
            "user_has_premium": user_has_premium,
            "active_premium": active_premium,
            "upgrade_required": upgrade_required,
        },
    )
