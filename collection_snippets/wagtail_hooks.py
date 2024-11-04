"""Wagtail hook implementations."""

import django
import wagtail.admin.forms.collections
import wagtail.admin.utils
import wagtail.hooks
from django.utils.translation import gettext_lazy as _, ngettext

import collection_snippets.bulk_action
import collection_snippets.models


@wagtail.hooks.register("register_group_permission_panel")
def register_snippet_permissions_panel():
    """Add collection permissions for snippets to the group permissions UI."""
    return wagtail.admin.forms.collections.collection_member_permission_formset_factory(
        collection_snippets.models.Snippet,
        [
            ("add_snippet", _("Add"), _("Add/edit snippets you own")),
            ("change_snippet", _("Edit"), _("Edit any snippet")),
            ("choose_snippet", _("Choose"), _("Select snippets in choosers")),
        ],
        "collectionsnippets/permissions_formset.html",
    )


@wagtail.hooks.register("describe_collection_contents")
def describe_collection(collection):
    """Count snippets belonging to a collection.

    Currently this happens on the confirmation before deleting a collection.
    """
    snippets_count = collection_snippets.models.Snippet.objects.filter(
        collection=collection
    ).count()
    if snippets_count:
        return {
            "count": snippets_count,
            "count_text": ngettext(
                "%(count)s snippet", "%(count)s snippets", snippets_count
            )
            % {"count": snippets_count},
            "url": wagtail.admin.utils.set_query_params(
                django.urls.reverse("wagtailsnippets:index"),
                {"collection_id": collection.id},
            ),
        }
    return None


wagtail.hooks.register(
    "register_bulk_action", collection_snippets.bulk_action.AddToCollectionBulkAction
)
