"""Backend i18n for API response messages.

Resolves the user's locale from the `Accept-Language` header on each
request and translates message keys into the chosen language. GPT-generated
content (story bodies, character descriptions, etc.) is NOT translated --
this layer only covers backend system messages (errors, success notices,
admin actions).

Usage:
    from utils.i18n import t

    return success_response(world_data, t('world.created'))
    raise ResourceNotFoundError('World', world_id)  # uses i18n internally
"""

import json
import os
from threading import Lock

from flask import has_request_context, request

SUPPORTED_LOCALES = ('vi', 'en')
DEFAULT_LOCALE = 'vi'

_catalogs = {}
_lock = Lock()


def _locale_dir():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'i18n')


def _load_catalog(locale):
    """Load and cache a locale catalog. Thread-safe."""
    if locale in _catalogs:
        return _catalogs[locale]
    with _lock:
        if locale in _catalogs:
            return _catalogs[locale]
        path = os.path.join(_locale_dir(), f'{locale}.json')
        try:
            with open(path, 'r', encoding='utf-8') as f:
                _catalogs[locale] = json.load(f)
        except (OSError, json.JSONDecodeError):
            _catalogs[locale] = {}
        return _catalogs[locale]


def _resolve(catalog, key):
    """Look up a dotted key in a nested dict. Returns None if not found."""
    node = catalog
    for part in key.split('.'):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node if isinstance(node, str) else None


def get_locale():
    """Resolve the current request's locale.

    Priority:
        1. `Accept-Language` header primary tag (vi/en)
        2. DEFAULT_LOCALE
    """
    if not has_request_context():
        return DEFAULT_LOCALE
    header = request.headers.get('Accept-Language', '')
    if not header:
        return DEFAULT_LOCALE
    # Parse "vi,en;q=0.9" -> "vi"; also handles "vi-VN" -> "vi".
    primary = header.split(',')[0].strip().split('-')[0].lower()
    if primary in SUPPORTED_LOCALES:
        return primary
    return DEFAULT_LOCALE


def t(key, **params):
    """Translate `key` to the current request locale, interpolating params.

    Falls back to the default locale if the key is missing in the active
    catalog, then to the key string itself if also missing in default.
    """
    locale = get_locale()
    template = _resolve(_load_catalog(locale), key)
    if template is None and locale != DEFAULT_LOCALE:
        template = _resolve(_load_catalog(DEFAULT_LOCALE), key)
    if template is None:
        template = key
    if params:
        try:
            return template.format(**params)
        except (KeyError, IndexError):
            return template
    return template
