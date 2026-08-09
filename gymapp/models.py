from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("member", "Member"),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="member"
    )

    def __str__(self):
        return f"{self.username} ({self.role})"


class MembershipPlan(models.Model):
    name = models.CharField(max_length=100)
    duration_months = models.PositiveIntegerField()
    fee = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} - {self.duration_months} months"


class Trainer(models.Model):
    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=200)
    mobile = models.CharField(max_length=15)
    shift_timing = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name} - {self.specialization}"


class AIPlan(models.Model):
    PLAN_CHOICES = [
        ("Free", "Free"),
        ("Premium", "Premium"),
    ]

    name = models.CharField(
        max_length=50,
        choices=PLAN_CHOICES
    )
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )
    description = models.TextField(blank=True)
    duration_months = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - ₹{self.price}"


class MemberProfile(models.Model):
    GENDER_CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
    ]

    GOAL_CHOICES = [
        ("Weight Gain", "Weight Gain"),
        ("Weight Loss", "Weight Loss"),
        ("Muscle Gain", "Muscle Gain"),
        ("Maintain Weight", "Maintain Weight"),
        ("General Fitness", "General Fitness"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="member_profile"
    )

    full_name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)

    email = models.EmailField(
        blank=True,
        null=True
    )

    age = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True,
        null=True
    )

    goal = models.CharField(
        max_length=30,
        choices=GOAL_CHOICES,
        blank=True
    )

    address = models.TextField(blank=True)

    joining_date = models.DateField(
        default=timezone.now
    )

    plan = models.ForeignKey(
        MembershipPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="members"
    )

    ai_plan = models.ForeignKey(
        AIPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ai_members"
    )

    trainer = models.ForeignKey(
        Trainer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="members"
    )

    membership_start = models.DateField(
        null=True,
        blank=True
    )

    membership_end_date = models.DateField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.full_name} - {self.user.username}"


class Equipment(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    units = models.PositiveIntegerField(default=1)

    purchase_date = models.DateField(
        default=timezone.now
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} (units: {self.units})"


class Payment(models.Model):
    PAYMENT_MODE_CHOICES = [
        ("Cash", "Cash"),
        ("Online", "Online"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Paid", "Paid"),
        ("Failed", "Failed"),
    ]

    member = models.ForeignKey(
        MemberProfile,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    plan = models.ForeignKey(
        MembershipPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_date = models.DateField(
        default=timezone.now
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_MODE_CHOICES
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="Pending"
    )

    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Payment of ₹{self.amount} by {self.member.full_name}"


class Attendance(models.Model):
    member = models.ForeignKey(
        MemberProfile,
        on_delete=models.CASCADE,
        related_name="attendances"
    )

    date = models.DateField(
        default=timezone.now
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ("Present", "Present"),
            ("Absent", "Absent"),
        ],
        default="Present"
    )

    check_in_time = models.TimeField(
        null=True,
        blank=True
    )

    check_out_time = models.TimeField(
        null=True,
        blank=True
    )

    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.member.full_name} - {self.date} - {self.status}"


class AttendanceReport(models.Model):
    member = models.ForeignKey(
        MemberProfile,
        on_delete=models.CASCADE,
        related_name="attendance_reports"
    )

    date = models.DateField(
        default=timezone.now
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ("Present", "Present"),
            ("Absent", "Absent"),
        ],
        default="Absent"
    )

    time_in = models.TimeField(
        null=True,
        blank=True
    )

    class Meta:
        unique_together = ("member", "date")

    def __str__(self):
        return f"{self.member.full_name} - {self.date}"


class Enquiry(models.Model):
    ENQUIRY_STATUS_CHOICES = [
        ("New", "New"),
        ("Seen", "Seen"),
        ("Resolved", "Resolved"),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    mobile = models.CharField(max_length=15)
    message = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    status = models.CharField(
        max_length=20,
        choices=ENQUIRY_STATUS_CHOICES,
        default="New"
    )

    def __str__(self):
        return f"Enquiry from {self.name}"


class WorkoutPlan(models.Model):
    member = models.ForeignKey(
        MemberProfile,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="workout_plans"
    )

    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        if self.member:
            return f"{self.title} - {self.member.full_name}"
        return self.title


class Feedback(models.Model):
    member = models.ForeignKey(
        MemberProfile,
        on_delete=models.CASCADE,
        related_name="feedbacks"
    )

    message = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Feedback from {self.member.full_name}"


class DietPlan(models.Model):
    member = models.ForeignKey(
        MemberProfile,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="diet_plans"
    )

    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    calories = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        if self.member:
            return f"{self.title} - {self.member.full_name}"
        return self.title


class Progress(models.Model):
    member = models.ForeignKey(
        MemberProfile,
        on_delete=models.CASCADE,
        related_name="progress_records"
    )

    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )

    body_fat = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )

    recorded_date = models.DateField(
        default=timezone.now
    )

    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.member.full_name} - {self.recorded_date}"


class Reminder(models.Model):
    member = models.ForeignKey(
        MemberProfile,
        on_delete=models.CASCADE,
        related_name="reminders"
    )

    title = models.CharField(max_length=100)
    message = models.TextField()
    reminder_date = models.DateTimeField()

    is_completed = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.title} - {self.member.full_name}"