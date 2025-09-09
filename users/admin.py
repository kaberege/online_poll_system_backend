from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()

class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('first_name', 'is_staff')
    search_fields = ('email',)
    ordering = ('email',)
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('phone_number',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {
            'fields': ('phone_number',),
        }),
    )
    

admin.site.register(User, UserAdmin)
