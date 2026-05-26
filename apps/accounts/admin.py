from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Address, Store


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0
    fields = ('label', 'city', 'street', 'apartment', 'postal_code', 'is_default')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [AddressInline]
    list_display = ('email', 'get_full_name', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined', 'last_login')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Личные данные', {'fields': ('first_name', 'last_name', 'phone', 'avatar')}),
        ('Роль и права', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Даты', {'fields': ('date_joined', 'last_login')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'role'),
        }),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'label', 'city', 'street', 'is_default')
    list_filter = ('city',)
    search_fields = ('user__email', 'city', 'street')


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'manager', 'employee_count', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'address', 'manager__email')
    filter_horizontal = ('employees',)
    fieldsets = (
        ('Магазин', {'fields': ('name', 'address', 'phone', 'is_active')}),
        ('Персонал', {'fields': ('manager', 'employees')}),
    )

    def employee_count(self, obj):
        return obj.employees.count()
    employee_count.short_description = 'Сотрудников'
