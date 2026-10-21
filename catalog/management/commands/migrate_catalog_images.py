from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from catalog.image_migration import (
    StorageMigration,
    content_hash,
    is_valid_image,
    load_manifest,
    storage_reference,
)
from catalog.models import ChaletModel, Terrain


IMAGE_ROOTS = {
    'models': 'modeles',
    'terrains': 'terrains',
}

STORAGE_GROUPS = {
    'models': 'modeles',
    'terrains': 'terrains',
}


class Command(BaseCommand):
    help = 'Upload catalog images to private Supabase Storage and update galleries.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')
        parser.add_argument('--bucket', default=None)
        parser.add_argument('--source-root', default=None)

    def handle(self, *args, **options):
        manifest = load_manifest()
        bucket = options['bucket'] or manifest['bucket']
        source_root = Path(options['source_root'] or Path(__file__).resolve().parents[4])
        storage = StorageMigration(bucket=bucket, dry_run=options['dry_run'])

        if not options['dry_run'] and not storage.configured:
            raise CommandError(
                'SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required outside dry-run mode.'
            )
        if not options['dry_run']:
            self.stdout.write(f'BUCKET {storage.ensure_bucket()}: {bucket}')

        totals = {'discovered': 0, 'planned': 0, 'uploaded': 0, 'duplicates': 0, 'updated': 0, 'failed': 0}
        all_files = set()
        content_hashes = {}

        for group_name, records in manifest['groups'].items():
            model_class = ChaletModel if group_name == 'models' else Terrain
            for slug, filenames in records.items():
                record = model_class.objects.filter(slug=slug).first()
                if record is None:
                    raise CommandError(f'No {group_name[:-1]} record exists for slug {slug}.')

                references = []
                for index, filename in enumerate(filenames):
                    source_path = source_root / IMAGE_ROOTS[group_name] / filename
                    totals['discovered'] += 1
                    all_files.add((group_name, filename))
                    if not source_path.is_file():
                        totals['failed'] += 1
                        self.stderr.write(f'FAIL missing file: {source_path}')
                        continue
                    if not is_valid_image(source_path):
                        totals['failed'] += 1
                        self.stderr.write(f'FAIL invalid image: {source_path}')
                        continue

                    file_hash = content_hash(source_path)
                    if file_hash in content_hashes:
                        self.stdout.write(
                            f'SKIP duplicate content: {source_path.name} '
                            f'(same as {content_hashes[file_hash]})'
                        )
                        continue
                    content_hashes[file_hash] = source_path.name

                    object_path = f'{STORAGE_GROUPS[group_name]}/{filename}'
                    try:
                        result = storage.upload(source_path, object_path)
                        totals['duplicates' if result == 'duplicate' else result] += 1
                        references.append(storage_reference(bucket, object_path))
                        self.stdout.write(f'{result.upper()}: {source_path.name} -> {object_path}')
                    except Exception as error:
                        totals['failed'] += 1
                        self.stderr.write(f'FAIL upload {source_path.name}: {error}')

                if not references:
                    continue
                if options['dry_run']:
                    totals['updated'] += 1
                    continue

                with transaction.atomic():
                    record.image = references[0]
                    record.gallery = references
                    record.save(update_fields=('image', 'gallery'))
                totals['updated'] += 1

        expected = {
            (group_name, filename)
            for group_name, records in manifest['groups'].items()
            for filenames in records.values()
            for filename in filenames
        }
        if all_files != expected:
            self.stderr.write('WARNING: manifest file accounting is incomplete.')

        self.stdout.write(self.style.SUCCESS(f'SUMMARY: {totals}'))
