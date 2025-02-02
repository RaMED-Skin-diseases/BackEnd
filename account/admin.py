from django.contrib import admin
from .models import User, AdminUser


class UserAdmin(admin.ModelAdmin):
    # Define the fields to display in the form based on user type
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
            'password', 'username', 'user_type', 'is_verified'
        ]

    # List the fields to display in the admin list view
    list_display = ("username", "f_name", "l_name", "user_type", "is_verified")
    
    # Add search capability
    search_fields = ['username', 'email', 'f_name', 'l_name']

    # Define the order of the objects listed in the admin panel
    ordering = ['username']

    # Add filtering options
    list_filter = ('user_type', 'is_verified')


admin.site.register(User, UserAdmin)
admin.site.site_header = "Skin Diseases Admin"


class CustomUserAdmin(UserAdmin):
    model = AdminUser
    list_display = ['username', 'is_staff', 'is_active', 'last_login']
    
    # Fieldsets define how fields are arranged in the form
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
        ('Important Dates', {'fields': ('last_login',)}),
    )

    # Custom add fieldsets for creating a new admin user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    
    # Add search functionality for AdminUser
    search_fields = ['username', 'email']
    
    # Add ordering option for the list
    ordering = ['username']


admin.site.register(AdminUser, CustomUserAdmin)
