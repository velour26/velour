from django.db import models


class SiteSettings(models.Model):
    """Глобальные настройки сайта — редактируются из админки"""
    site_name = models.CharField(max_length=100, default='Magazin Odejdi')
    site_description = models.TextField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    vk_url = models.URLField(blank=True)
    telegram_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    delivery_info = models.TextField(blank=True, verbose_name='Информация о доставке')
    return_policy = models.TextField(blank=True, verbose_name='Политика возврата')
    free_delivery_from = models.DecimalField(max_digits=10, decimal_places=2, default=5000,
                                             verbose_name='Бесплатная доставка от (руб)')

    class Meta:
        verbose_name = 'Настройки сайта'
        verbose_name_plural = 'Настройки сайта'

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        self.pk = 1  # singleton
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Page(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    meta_description = models.CharField(max_length=300, blank=True, verbose_name='Мета-описание')
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Страница'
        verbose_name_plural = 'Страницы'

    def __str__(self):
        return self.title


class PageSection(models.Model):
    """Редактируемая секция страницы"""
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='sections')
    key = models.CharField(max_length=100, verbose_name='Ключ секции')
    label = models.CharField(max_length=200, verbose_name='Описание')
    text = models.TextField(blank=True, verbose_name='Текст')
    image = models.ImageField(upload_to='pages/', blank=True, null=True, verbose_name='Изображение')
    link = models.CharField(max_length=300, blank=True, verbose_name='Ссылка')
    is_visible = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Секция страницы'
        verbose_name_plural = 'Секции страниц'
        ordering = ['sort_order']
        unique_together = [['page', 'key']]

    def __str__(self):
        return f'{self.page.title} / {self.label}'


class Banner(models.Model):
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    subtitle = models.CharField(max_length=300, blank=True, verbose_name='Подзаголовок')
    button_text = models.CharField(max_length=100, blank=True, default='Смотреть')
    button_link = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to='banners/', verbose_name='Изображение')
    image_mobile = models.ImageField(upload_to='banners/', blank=True, null=True,
                                     verbose_name='Изображение (мобильное)')
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Баннер'
        verbose_name_plural = 'Баннеры'
        ordering = ['sort_order']

    def __str__(self):
        return self.title
