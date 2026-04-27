#!/usr/bin/env python
"""Unit tests for the backend i18n layer.

Verifies the Accept-Language header drives translation of API response
messages and that exception messages respect the request locale.
"""

import os
import sys
import unittest

os.environ.setdefault('TEST_MODE', '1')
os.environ.setdefault('JWT_SECRET_KEY', 'test-secret-do-not-use-in-prod')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask  # noqa: E402

from utils.i18n import t, get_locale  # noqa: E402
from core.exceptions import ResourceNotFoundError, PermissionDeniedError  # noqa: E402


class I18nTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)

    def test_default_locale_is_vietnamese(self):
        with self.app.test_request_context('/'):
            self.assertEqual(get_locale(), 'vi')
            self.assertEqual(t('world.created'), 'Đã tạo thế giới')

    def test_english_locale_via_header(self):
        with self.app.test_request_context('/', headers={'Accept-Language': 'en'}):
            self.assertEqual(get_locale(), 'en')
            self.assertEqual(t('world.created'), 'World created successfully')

    def test_region_tag_normalises_to_primary(self):
        with self.app.test_request_context('/', headers={'Accept-Language': 'en-US'}):
            self.assertEqual(get_locale(), 'en')

    def test_unsupported_locale_falls_back_to_default(self):
        with self.app.test_request_context('/', headers={'Accept-Language': 'fr'}):
            self.assertEqual(get_locale(), 'vi')
            self.assertEqual(t('world.created'), 'Đã tạo thế giới')

    def test_quality_value_uses_first_tag(self):
        with self.app.test_request_context(
            '/', headers={'Accept-Language': 'en,vi;q=0.9'}
        ):
            self.assertEqual(get_locale(), 'en')

    def test_template_interpolation(self):
        with self.app.test_request_context('/', headers={'Accept-Language': 'en'}):
            self.assertEqual(
                t('errors.resource_not_found', type='Foo', id='42'),
                'Foo not found: 42',
            )

    def test_missing_key_falls_back_to_default_locale_then_key(self):
        with self.app.test_request_context('/', headers={'Accept-Language': 'en'}):
            self.assertEqual(t('does.not.exist'), 'does.not.exist')

    def test_resource_not_found_uses_translated_resource_label(self):
        with self.app.test_request_context('/', headers={'Accept-Language': 'vi'}):
            err = ResourceNotFoundError('World', 'abc-123')
            self.assertIn('thế giới', err.message)
            self.assertIn('abc-123', err.message)

        with self.app.test_request_context('/', headers={'Accept-Language': 'en'}):
            err = ResourceNotFoundError('World', 'abc-123')
            self.assertIn('World', err.message)
            self.assertIn('abc-123', err.message)

    def test_permission_denied_translates_action_and_resource(self):
        with self.app.test_request_context('/', headers={'Accept-Language': 'vi'}):
            err = PermissionDeniedError('edit', 'World')
            self.assertIn('chỉnh sửa', err.message)
            self.assertIn('thế giới', err.message)

        with self.app.test_request_context('/', headers={'Accept-Language': 'en'}):
            err = PermissionDeniedError('edit', 'World')
            self.assertIn('edit', err.message)
            self.assertIn('World', err.message)

    def test_permission_denied_with_unknown_action_falls_back_gracefully(self):
        with self.app.test_request_context('/', headers={'Accept-Language': 'en'}):
            err = PermissionDeniedError('publish_to_facebook', 'Story')
            self.assertIn('publish_to_facebook', err.message)
            self.assertIn('Story', err.message)


if __name__ == '__main__':
    unittest.main(verbosity=2)
