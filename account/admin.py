from django.contrib import admin
from django.utils.html import format_html
from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'user_type', 'is_verified',
                    'verification_status', 'verification_image_preview')
    list_filter = ('user_type', 'is_verified', 'verification_status')
    search_fields = ('username', 'email', 'f_name', 'l_name')
    readonly_fields = ('verification_image_preview',)
    fieldsets = (
        (None, {
            'fields': ('username', 'email', 'password')
        }),
        ('Personal Info', {
            'fields': ('f_name', 'l_name', 'date_of_birth', 'gender')
        }),
        ('Professional Info', {
            'fields': ('user_type', 'specialization', 'clinic_details', 'info')
        }),
        ('Verification', {
            'fields': ('is_verified', 'verification_status', 'verification_image', 'verification_image_preview', 'verification_notes')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    actions = ['approve_doctors', 'reject_doctors']

    def verification_image_preview(self, obj):
        if obj.verification_image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.verification_image.url)
        return "No document uploaded"
    verification_image_preview.short_description = 'Verification Document Preview'

    def approve_doctors(self, request, queryset):
        updated = queryset.filter(
            verification_status__in=['pending', 'rejected'],
            is_verified=False
        ).update(
            user_type='Doctor',
            verification_status='approved',
            is_verified=True
        )
        self.message_user(
            request, f"Approved and converted {updated} users to Doctors")

    def reject_doctors(self, request, queryset):
        queryset.filter(user_type='Doctor').update(
            verification_status='rejected',
            is_verified=False
        )
        self.message_user(
            request, f"Rejected {queryset.count()} doctor applications")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(is_superuser=False)

    def get_readonly_fields(self, request, obj=None):
        if obj and not request.user.is_superuser:
            return self.readonly_fields + ('user_type', 'is_verified', 'verification_status')
        return self.readonly_fields


admin.site.register(User, UserAdmin)
