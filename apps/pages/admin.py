from django.contrib import admin
from .models import SiteSettings, Page, PageSection, Banner


class PageSectionInline(admin.StackedInline):
    model = PageSection
    extra = 0
    fields = ('key', 'label', 'text', 'image', 'link', 'is_visible', 'sort_order')


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Общее', {'fields': ('site_name', 'site_description')}),
        ('Контакты', {'fields': ('phone', 'email', 'address')}),
        ('Социальные сети', {'fields': ('vk_url', 'telegram_url', 'instagram_url')}),
        ('Контент', {'fields': ('delivery_info', 'return_policy', 'free_delivery_from')}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    inlines = [PageSectionInline]
    list_display = ('title', 'slug', 'is_active', 'updated_at')
    list_editable = ('is_active',)
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'slug')


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'sort_order', 'is_active')
    list_editable = ('sort_order', 'is_active')
    fields = ('title', 'subtitle', 'button_text', 'button_link', 'image', 'image_mobile', 'sort_order', 'is_active')
