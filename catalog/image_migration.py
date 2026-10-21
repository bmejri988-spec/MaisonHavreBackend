from __future__ import annotations

import json
import hashlib
import mimetypes
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from django.conf import settings


MANIFEST_PATH = Path(__file__).with_name('image_migration_manifest.json')
STORAGE_PREFIX = 'storage://'


def load_manifest():
    with MANIFEST_PATH.open(encoding='utf-8') as manifest_file:
        return json.load(manifest_file)


def is_valid_image(path):
    with path.open('rb') as image_file:
        header = image_file.read(12)
    return (
        header.startswith(b'\xff\xd8\xff')
        or header.startswith(b'\x89PNG\r\n\x1a\n')
        or header.startswith(b'RIFF') and header[8:12] == b'WEBP'
    )


def content_hash(path):
    digest = hashlib.sha256()
    with path.open('rb') as image_file:
        for chunk in iter(lambda: image_file.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def storage_reference(bucket, path):
    return f'{STORAGE_PREFIX}{bucket}/{path}'


class StorageMigration:
    def __init__(self, bucket, dry_run=False):
        self.bucket = bucket
        self.dry_run = dry_run
        self.base_url = os.getenv('SUPABASE_URL', '').rstrip('/')
        self.service_role_key = (
            os.getenv('SUPABASE_SERVICE_ROLE_KEY')
            or os.getenv('SUPABASE_SECRET_KEY', '')
        )

    @property
    def configured(self):
        return bool(self.base_url and self.service_role_key)

    def _request(self, method, path, data=None, content_type=None):
        url = f'{self.base_url}/storage/v1/{path}'
        headers = {
            'Authorization': f'Bearer {self.service_role_key}',
            'apikey': self.service_role_key,
        }
        if content_type:
            headers['Content-Type'] = content_type
        if method == 'POST' and '/object/' in path:
            headers['Cache-Control'] = '3600'
            headers['x-upsert'] = 'false'
        request = Request(url, data=data, headers=headers, method=method)
        return urlopen(request, timeout=45)

    def exists(self, object_path):
        try:
            with self._request(
                'HEAD',
                f'object/{quote(self.bucket)}/{quote(object_path, safe="/")}',
            ):
                return True
        except HTTPError as error:
            if error.code == 404:
                return False
            raise

    def ensure_bucket(self):
        try:
            with self._request('GET', f'bucket/{quote(self.bucket)}'):
                return 'existing'
        except HTTPError as error:
            if error.code != 404:
                raise
        payload = json.dumps({
            'id': self.bucket,
            'name': self.bucket,
            'public': False,
        }).encode('utf-8')
        self._request('POST', 'bucket', data=payload, content_type='application/json').read()
        return 'created'

    def upload(self, source_path, object_path):
        if self.dry_run:
            return 'planned'
        content_type = mimetypes.guess_type(source_path.name)[0] or 'application/octet-stream'
        try:
            with source_path.open('rb') as image_file:
                self._request(
                    'POST',
                    f'object/{quote(self.bucket)}/{quote(object_path, safe="/")}',
                    data=image_file.read(),
                    content_type=content_type,
                ).read()
            return 'uploaded'
        except HTTPError as error:
            if error.code == 409:
                return 'duplicate'
            details = error.read().decode('utf-8', errors='replace').strip()
            raise RuntimeError(
                f'Supabase Storage upload returned HTTP {error.code}'
                + (f': {details}' if details else '')
            ) from error
        except (OSError, URLError):
            raise


def signed_url(reference, expires_in=3600):
    if not reference.startswith(STORAGE_PREFIX):
        return reference
    bucket, object_path = reference[len(STORAGE_PREFIX):].split('/', 1)
    base_url = os.getenv('SUPABASE_URL', '').rstrip('/')
    service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')
    if not service_role_key:
        service_role_key = os.getenv('SUPABASE_SECRET_KEY', '')
    if not base_url or not service_role_key:
        return reference

    payload = json.dumps({'expiresIn': expires_in}).encode('utf-8')
    url = (
        f'{base_url}/storage/v1/object/sign/{quote(bucket)}/'
        f'{quote(object_path, safe="/")}'
    )
    request = Request(
        url,
        data=payload,
        headers={
            'Authorization': f'Bearer {service_role_key}',
            'apikey': service_role_key,
            'Content-Type': 'application/json',
        },
        method='POST',
    )
    try:
        with urlopen(request, timeout=15) as response:
            result = json.loads(response.read().decode('utf-8'))
    except HTTPError as error:
        details = error.read().decode('utf-8', errors='replace').strip()
        raise RuntimeError(
            f'Supabase signed URL request returned HTTP {error.code}'
            + (f': {details}' if details else '')
        ) from error
    signed_path = result.get('signedURL') or result.get('signedUrl')
    if not signed_path:
        raise RuntimeError(f'Supabase did not return a signed URL for {object_path}')
    if signed_path.startswith('http'):
        return signed_path
    return f'{base_url}/storage/v1{signed_path}'


def resolve_image_url(value):
    return signed_url(value)


def resolve_gallery(values):
    return [resolve_image_url(value) for value in values]
