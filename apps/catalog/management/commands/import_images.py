"""
Bulk image import for existing products.

Folder structure:
    seed_data/images/
        VL-01372/
            01.jpg    ← becomes main image (first file alphabetically)
            02.jpg
            03.jpg
        VL-01366/
            01.jpg
            02.png
        ...

Supported formats: jpg, jpeg, png, webp, gif

Usage:
    python manage.py import_images
    python manage.py import_images --dir path/to/images
    python manage.py import_images --dir path/to/images --replace
    python manage.py import_images --dry-run

Options:
    --dir       Path to root folder with article subfolders
                Default: seed_data/images (relative to manage.py)
    --replace   Delete existing images for a product before importing
    --dry-run   Show what would be done, make no changes
"""
import os
import shutil
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from django.conf import settings

SUPPORTED = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}


class Command(BaseCommand):
    help = 'Import product images from a folder tree keyed by article number'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dir',
            default=os.path.join(settings.BASE_DIR, 'seed_data', 'images'),
            help='Root directory containing article-named subfolders',
        )
        parser.add_argument(
            '--replace',
            action='store_true',
            help='Delete existing images for each product before importing',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            help='Preview only — no database or file changes',
        )

    def handle(self, *args, **options):
        from apps.catalog.models import Product, ProductImage

        root = Path(options['dir'])
        replace = options['replace']
        dry_run = options['dry_run']

        if not root.exists():
            raise CommandError(
                f'Directory not found: {root}\n'
                f'Create it and add subfolders named after article numbers.'
            )

        article_dirs = sorted(
            d for d in root.iterdir()
            if d.is_dir() and not d.name.startswith('.')
        )

        if not article_dirs:
            raise CommandError(f'No subfolders found in {root}')

        self.stdout.write(f'Scanning {root} — {len(article_dirs)} folder(s)\n')
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN — no changes will be made\n'))

        total_imported = 0
        total_skipped = 0
        not_found = []

        for article_dir in article_dirs:
            article = article_dir.name

            # Find matching product
            try:
                product = Product.objects.get(article=article)
            except Product.DoesNotExist:
                not_found.append(article)
                self.stdout.write(
                    self.style.WARNING(f'  SKIP  {article:15s}  — product not found in DB')
                )
                continue

            # Collect image files sorted alphabetically
            image_files = sorted(
                f for f in article_dir.iterdir()
                if f.is_file() and f.suffix.lower() in SUPPORTED
            )

            if not image_files:
                self.stdout.write(
                    self.style.WARNING(f'  SKIP  {article:15s}  — no images in folder')
                )
                continue

            # Existing image count
            existing = ProductImage.objects.filter(product=product).count()

            if replace and existing and not dry_run:
                # Remove old images from disk + DB
                for img_obj in ProductImage.objects.filter(product=product):
                    try:
                        img_obj.image.delete(save=False)
                    except Exception:
                        pass
                ProductImage.objects.filter(product=product).delete()
                existing = 0

            action = 'replace' if replace and existing == 0 else 'add'
            self.stdout.write(
                f'  {"[DRY]" if dry_run else "OK":5s} {article:15s}  '
                f'{product.name[:40]:40s}  '
                f'{len(image_files)} file(s)  [{action}]'
            )

            if dry_run:
                total_imported += len(image_files)
                continue

            for idx, img_path in enumerate(image_files):
                is_main = (idx == 0) and (existing == 0)
                dest_name = f'{article}_{img_path.name}'
                dest_path = os.path.join(settings.MEDIA_ROOT, 'products', dest_name)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)

                # Copy file to MEDIA_ROOT/products/
                shutil.copy2(img_path, dest_path)

                # Create DB record
                relative_path = os.path.join('products', dest_name)
                img_obj = ProductImage(
                    product=product,
                    alt=product.name,
                    is_main=is_main,
                    sort_order=existing + idx,
                )
                img_obj.image.name = relative_path
                img_obj.save()

            total_imported += len(image_files)

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Done.  Imported: {total_imported} image(s)  |  '
            f'Skipped: {total_skipped} product(s)'
        ))
        if not_found:
            self.stdout.write(
                self.style.WARNING(
                    f'Articles not found in DB ({len(not_found)}): '
                    + ', '.join(not_found[:10])
                    + (f' ... and {len(not_found)-10} more' if len(not_found) > 10 else '')
                )
            )
