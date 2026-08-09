from django.contrib import admin
from .models import (
    CustomUser,
    MembershipPlan,
    Trainer,
    AIPlan,
    MemberProfile,
    Equipment,
    Payment,
    Attendance,
    AttendanceReport,
    Enquiry,
    WorkoutPlan,
    Feedback,
    DietPlan,
    Progress,
    Reminder,
)

admin.site.register(CustomUser)
admin.site.register(MembershipPlan)
admin.site.register(Trainer)
admin.site.register(AIPlan)
admin.site.register(MemberProfile)
admin.site.register(Equipment)
admin.site.register(Payment)
admin.site.register(Attendance)
admin.site.register(AttendanceReport)
admin.site.register(Enquiry)
admin.site.register(WorkoutPlan)
admin.site.register(Feedback)
admin.site.register(DietPlan)
admin.site.register(Progress)
admin.site.register(Reminder)