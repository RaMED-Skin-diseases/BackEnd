from django.contrib import admin
from .models import User, AdminUser


# Register your models here.


class UserAdmin(admin.ModelAdmin):
    def get_fields(self, request, obj=None):
        if obj and obj.user_type == 'Doctor':
            return [
                'f_name', 'l_name', 'date_of_birth', 'email', 'gender',
                'password', 'username', 'user_type', 'info', 'specialization',
                'clinic_details', 'is_verified'
            ]
        # Fields for Patient users (doctor-specific fields hidden)
        return [
            'f_name', 'l_name', 'date_of_birth', 'email', 'gender',
            'password', 'username', 'user_type',
            'is_verified'
        ]
    list_display = ("username", "f_name", "l_name", "user_type")


admin.site.register(User, UserAdmin)
admin.site.site_header = "Skin Diseases Admin"

class CustomUserAdmin(UserAdmin):
    model = AdminUser
    list_display = ['username', 'is_staff', 'is_active']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

admin.site.register(AdminUser, CustomUserAdmin)