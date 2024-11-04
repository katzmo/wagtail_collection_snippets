"""Custom URL endpoints."""

import django
import wagtail.admin.auth
import wagtail.utils.urlpatterns

import collection_snippets.views

# Override endpoints with custom views.
urlpatterns = wagtail.utils.urlpatterns.decorate_urlpatterns(
    wagtail.utils.urlpatterns.decorate_urlpatterns(
        [
            django.urls.path(
                "snippets/", collection_snippets.views.ModelIndexView.as_view()
            ),
        ],
        wagtail.admin.auth.require_admin_access,
    ),
    django.views.decorators.cache.never_cache,
)
