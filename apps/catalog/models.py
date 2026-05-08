from django.db import models
from django.utils.text import slugify
from django.utils.crypto import get_random_string


def unique_slug(instance, value):
    slug = slugify(value, allow_unicode=True)
    Model = type(instance)
    qs = Model.objects.filter(slug=slug)
    if instance.pk:
        qs = qs.exclude(pk=instance.pk)
    if qs.exists():
        slug = f'{slug}-{get_random_string(4)}'
    return slug


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    slug = models.SlugField(max_length=120, unique=True, allow_unicode=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.name)
        super().save(*args, **kwargs)


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100, verbose_name='Название')
    slug = models.SlugField(max_length=120, unique=True, allow_unicode=True)
    description = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Подкатегория'
        verbose_name_plural = 'Подкатегории'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return f'{self.category.name} → {self.name}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.name)
        super().save(*args, **kwargs)


class SubSubCategory(models.Model):
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='subsubcategories')
    name = models.CharField(max_length=100, verbose_name='Название')
    slug = models.SlugField(max_length=120, unique=True, allow_unicode=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Подподкатегория'
        verbose_name_plural = 'Подподкатегории'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return f'{self.subcategory} → {self.name}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.name)
        super().save(*args, **kwargs)


class FilterGroup(models.Model):
    """Группа фильтров (Цвет, Размер, Материал и т.д.)"""
    name = models.CharField(max_length=100, verbose_name='Название')
    slug = models.SlugField(max_length=120, unique=True)
    categories = models.ManyToManyField(Category, blank=True, related_name='filter_groups',
                                        verbose_name='Применяется в категориях')
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    filter_type = models.CharField(
        max_length=20,
        choices=[('checkbox', 'Чекбокс'), ('range', 'Диапазон'), ('color', 'Цвет')],
        default='checkbox'
    )

    class Meta:
        verbose_name = 'Группа фильтров'
        verbose_name_plural = 'Группы фильтров'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class FilterOption(models.Model):
    """Конкретные значения фильтров (Красный, XL, Хлопок и т.д.)"""
    group = models.ForeignKey(FilterGroup, on_delete=models.CASCADE, related_name='options')
    value = models.CharField(max_length=100, verbose_name='Значение')
    slug = models.SlugField(max_length=120)
    color_code = models.CharField(max_length=10, blank=True, help_text='HEX код для цветовых фильтров')
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Опция фильтра'
        verbose_name_plural = 'Опции фильтров'
        ordering = ['sort_order', 'value']
        unique_together = [['group', 'slug']]

    def __str__(self):
        return f'{self.group.name}: {self.value}'


class Brand(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)

    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products',
                                 verbose_name='Категория')
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='products', verbose_name='Подкатегория')
    subsubcategory = models.ForeignKey(SubSubCategory, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='products', verbose_name='Подподкатегория')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='products', verbose_name='Бренд')
    name = models.CharField(max_length=255, verbose_name='Название')
    slug = models.SlugField(max_length=300, unique=True, allow_unicode=True)
    article = models.CharField(max_length=50, unique=True, verbose_name='Артикул')
    description = models.TextField(blank=True, verbose_name='Описание')
    composition = models.CharField(max_length=255, blank=True, verbose_name='Состав')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                    verbose_name='Старая цена')
    filter_options = models.ManyToManyField(FilterOption, blank=True, related_name='products',
                                            verbose_name='Фильтры')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    is_featured = models.BooleanField(default=False, verbose_name='Рекомендуемый')
    is_new = models.BooleanField(default=False, verbose_name='Новинка')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.name)
        super().save(*args, **kwargs)

    @property
    def discount_percent(self):
        if self.old_price and self.old_price > self.price:
            return int((1 - self.price / self.old_price) * 100)
        return 0

    @property
    def main_image(self):
        img = self.images.filter(is_main=True).first()
        if not img:
            img = self.images.first()
        return img

    @property
    def approved_reviews(self):
        return self.reviews.filter(is_approved=True)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt = models.CharField(max_length=200, blank=True)
    is_main = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Изображение товара'
        verbose_name_plural = 'Изображения товаров'
        ordering = ['-is_main', 'sort_order']

    def save(self, *args, **kwargs):
        if self.is_main:
            ProductImage.objects.filter(product=self.product, is_main=True).exclude(pk=self.pk).update(is_main=False)
        super().save(*args, **kwargs)


class ProductVariant(models.Model):
    """Вариант товара (размер + цвет)"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    size = models.CharField(max_length=20, blank=True, verbose_name='Размер')
    color = models.ForeignKey(FilterOption, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='variants', verbose_name='Цвет',
                              limit_choices_to={'group__slug': 'color'})
    stock = models.PositiveIntegerField(default=0, verbose_name='Остаток')
    sku = models.CharField(max_length=100, blank=True, verbose_name='SKU')

    class Meta:
        verbose_name = 'Вариант товара'
        verbose_name_plural = 'Варианты товара'

    def __str__(self):
        parts = [self.product.name]
        if self.size:
            parts.append(f'р. {self.size}')
        if self.color:
            parts.append(self.color.value)
        return ' '.join(parts)


class Favorite(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        unique_together = [['user', 'product']]

    def __str__(self):
        return f'{self.user} → {self.product}'


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        unique_together = [['product', 'user']]

    def __str__(self):
        return f'{self.user} — {self.product} ({self.rating}★)'
