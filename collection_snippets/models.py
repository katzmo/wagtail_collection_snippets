"""Snippet models."""

import django
import wagtail.contrib.settings.context_processors
import wagtail.models
import wagtail.permission_policies.collections
import wagtail.snippets.models
from django.utils.translation import gettext_lazy as _


class Snippet(
    wagtail.models.CollectionMember,
    wagtail.models.DraftStateMixin,
    wagtail.models.RevisionMixin,
    wagtail.models.PreviewableMixin,
    wagtail.models.TranslatableMixin,
    django.db.models.Model,
):
    """Base translatable snippet class with revisions and preview, using collections."""

    class Meta(wagtail.models.TranslatableMixin.Meta):
        # noqa: D106 (skipping nested class docstring)
        permissions = [("choose_snippet", "Can choose snippet")]

    title = django.db.models.CharField(
        max_length=255,
        verbose_name=_("Admin title"),
        help_text=_("The internal title used in the administrative interface."),
    )

    panels = [
        wagtail.admin.panels.FieldPanel("collection"),
        wagtail.admin.panels.FieldPanel("title"),
    ]

    _revisions = django.contrib.contenttypes.fields.GenericRelation(
        "wagtailcore.Revision"
    )

    @property
    def revisions(self):
        """Override the revisions property to return a GenericRelation."""
        # Recommended by Wagtail to define a GenericRelation to the Revision model.
        # See https://docs.wagtail.org/en/v4.0/topics/snippets.html#saving-revisions-of-snippets
        return self._revisions

    def __str__(self):
        """Custom string representation (used in the admin UI)."""
        return self.title

    def get_preview_template(self, request, mode_name):
        """Provide a template for the preview."""
        return [
            f"{self._meta.app_label}/previews/{self._meta.model_name}.html",
            "collectionsnippets/preview.html",
        ]

    def get_preview_context(self, request, mode_name):
        """Use settings context of the first accessible site for the snippets preview."""
        context = super().get_preview_context(request, mode_name)
        site = (
            list(request.user.get_explorable_sites())[0]
            if hasattr(request, "user")
            else None
        )
        context["settings"] = wagtail.contrib.settings.context_processors.SettingProxy(
            request_or_site=site or request
        )
        return context


@django.dispatch.receiver((wagtail.signals.published, wagtail.signals.unpublished))
def snippet_changed(instance, **kwargs):
    """When a snippet changed, purge the cache for all pages displaying the snippet."""
    if isinstance(instance, Snippet) is False:
        return
    batch = wagtail.contrib.frontend_cache.utils.PurgeBatch()
    references = wagtail.models.ReferenceIndex.get_references_to(instance)
    for source, _ in references.group_by_source_object():
        if hasattr(source, "full_url"):
            batch.add_page(source)
        elif hasattr(source, "site"):
            if localized_root := source.site.root_page.get_translation_or_none(
                instance.locale
            ):
                batch.add_pages(localized_root.get_descendants(inclusive=True))
    batch.purge()


def register_snippet(model):
    """Register snippets with the collection snippets admin viewset."""
    wagtail.snippets.models.register_snippet(
        model, viewset="collection_snippets.views.ViewSet"
    )
    return model


permission_policy = wagtail.permission_policies.collections.CollectionPermissionPolicy(
    Snippet
)
