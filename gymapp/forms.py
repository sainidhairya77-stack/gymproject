from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import (
    Attendance,
    CustomUser,
    Equipment,
    MemberProfile,
    Payment,
    Progress,
)


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"autofocus": True}))


class RegisterForm(UserCreationForm):
    full_name = forms.CharField(max_length=100)
    mobile = forms.CharField(max_length=15)
    email = forms.EmailField(required=False)
    goal = forms.ChoiceField(
        choices=[("", "Select goal")] + MemberProfile.GOAL_CHOICES,
        required=False,
    )

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2")


class ProfileForm(forms.ModelForm):
    class Meta:
        model = MemberProfile
        fields = (
            "full_name",
            "mobile",
            "email",
            "age",
            "gender",
            "goal",
            "address",
            "plan",
            "ai_plan",
            "trainer",
            "membership_start",
            "membership_end_date",
        )
        widgets = {
            "membership_start": forms.DateInput(attrs={"type": "date"}),
            "membership_end_date": forms.DateInput(attrs={"type": "date"}),
            "address": forms.Textarea(attrs={"rows": 3}),
        }


class MemberProfileForm(forms.ModelForm):
    class Meta:
        model = MemberProfile
        fields = (
            "user",
            "full_name",
            "mobile",
            "email",
            "age",
            "gender",
            "goal",
            "address",
            "plan",
            "ai_plan",
            "trainer",
            "membership_start",
            "membership_end_date",
        )
        widgets = {
            "membership_start": forms.DateInput(attrs={"type": "date"}),
            "membership_end_date": forms.DateInput(attrs={"type": "date"}),
            "address": forms.Textarea(attrs={"rows": 3}),
        }


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = (
            "member",
            "date",
            "status",
            "check_in_time",
            "check_out_time",
            "notes",
        )
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "check_in_time": forms.TimeInput(attrs={"type": "time"}),
            "check_out_time": forms.TimeInput(attrs={"type": "time"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = (
            "member",
            "plan",
            "amount",
            "payment_date",
            "payment_method",
            "payment_status",
            "notes",
        )
        widgets = {
            "payment_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = (
            "name",
            "description",
            "units",
            "purchase_date",
            "price",
            "is_active",
        )
        widgets = {
            "purchase_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class ProgressForm(forms.ModelForm):
    class Meta:
        model = Progress
        fields = (
            "member",
            "weight",
            "body_fat",
            "recorded_date",
            "notes",
        )
        widgets = {
            "recorded_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
