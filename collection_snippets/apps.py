"""Collection Snippets app."""

import django
from django.utils.translation import gettext_lazy as _


class CollectionSnippetsAppConfig(django.apps.AppConfig):
    """App config."""

    name = "collection_snippets"
    label = "collectionsnippets"
    verbose_name = _("Collection Snippets")
