from django.contrib import admin
from django.utils.html import format_html
from django.core.mail import send_mail
from django.conf import settings
from .models import User, AdminUser


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'email', 'username', 'user_type', 
        'is_verified', 'verification_status', 'verified_by', 'verification_image_preview'
    )
    search_fields = ('email', 'username')
    list_filter = ('user_type', 'is_verified', 'verification_status')
    ordering = ('id',)
    readonly_fields = ('verification_image_display', 'verified_by')

    def verification_image_preview(self, obj):
        """Show image in the user list view."""
        if obj.verification_image:
            return format_html('<img src="{}" width="100" height="100" style="border-radius: 5px;" />', obj.verification_image.url)
        return "No Image"
    verification_image_preview.short_description = "Verification Image"

    def verification_image_display(self, obj):
        """Show image in the detailed user view."""
        if obj.verification_image:
            return format_html('<img src="{}" width="300" height="300" style="border-radius: 10px;" />', obj.verification_image.url)
        return "No Image"
    verification_image_display.short_description = "Verification Image"

    fieldsets = (
        ("User Information", {
            "fields": ("email", "username", "f_name", "l_name", "date_of_birth", "gender", "user_type", "is_verified")
        }),
        ("Verification Details", {
            "fields": ("verification_status", "verification_notes", "verification_image_display", "verified_by"),
        }),
    )

    def save_model(self, request, obj, form, change):
        """Send an email upon approval or rejection of doctor verification and store admin who verified."""
        if change:  # Only trigger on updates
            old_user = User.objects.get(pk=obj.pk)  # Get previous state

            if old_user.verification_status != obj.verification_status:
                obj.verified_by = request.user  # Store admin who approved/rejected

                # Determine if it's an approval or rejection
                if obj.verification_status == "approved":
                    subject = "Your Account Has Been Verified!"
                    message = (
                        f"Dear {obj.f_name},\n\n"
                        "Your account as a Doctor has been successfully verified. "
                        "You now have full access to our platform.\n\n"
                        "Thank you for using our platform!"
                    )
                elif obj.verification_status == "rejected":
                    subject = "Your Account Verification Was Rejected"
                    message = (
                        f"Dear {obj.f_name},\n\n"
                        "Unfortunately, your verification request was not approved. "
                        "Please review the following reason:\n\n"
                        f"Reason: {obj.verification_notes if obj.verification_notes else 'Not specified.'}\n\n"
                        "You can reapply or contact support for further information.\n\n"
                        f"Rejected by: {request.user.get_full_name()} ({request.user.email})"
                    )
                else:
                    super().save_model(request, obj, form, change)
                    return  # No email needed if status remains unchanged

                # Send email
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,  # Ensure this is set in settings.py
                    [obj.email],
                    fail_silently=False,
                )

        super().save_model(request, obj, form, change)


@admin.register(AdminUser)
class AdminUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'username', 'is_staff', 'is_superuser')
    search_fields = ('email', 'username')
    list_filter = ('is_staff', 'is_superuser')
    ordering = ('id',)
