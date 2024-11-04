"""Bulk actions for snippets."""

import django
import wagtail.snippets.bulk_actions.snippet_bulk_action
from django.utils.translation import gettext_lazy as _, ngettext

import collection_snippets.models


class CollectionForm(django.forms.Form):
    """Collection bulk action form."""

    def __init__(self, *args, **kwargs):
        """Initialize form with collection field."""
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["collection"] = django.forms.ModelChoiceField(
            label=_("Collection"),
            queryset=collection_snippets.models.permission_policy.collections_user_has_permission_for(
                user, "add"
            ),
        )


class AddToCollectionBulkAction(
    wagtail.snippets.bulk_actions.snippet_bulk_action.SnippetBulkAction
):
    """Bulk action for adding snippets to collections."""

    display_name = _("Add to collection")
    action_type = "add_to_collection"
    aria_label = _("Add selected snippets to collection")
    template_name = "collectionsnippets/confirm_bulk_add_to_collection.html"
    action_priority = 30
    form_class = CollectionForm
    collection = None

    def check_perm(self, obj):
        """Check permissions for the request user."""
        return collection_snippets.models.permission_policy.user_has_permission_for_instance(
            self.request.user, "change", obj
        )

    def get_form_kwargs(self):
        """Add request user to form kwargs."""
        return {**super().get_form_kwargs(), "user": self.request.user}

    def get_execution_context(self):
        """Pass collection from form to execution context."""
        return {"collection": self.cleaned_form.cleaned_data["collection"]}

    @classmethod
    def execute_action(cls, objects, collection=None, **kwargs):
        """Update selected snippets."""
        if collection is None:
            return None
        num_parent_objects = collection_snippets.models.Snippet.objects.filter(
            pk__in=[obj.pk for obj in objects]
        ).update(collection=collection)
        return num_parent_objects, 0

    def get_success_message(self, num_parent_objects, num_child_objects):
        """Display a success message."""
        collection = self.cleaned_form.cleaned_data["collection"]
        return ngettext(
            "%(num_parent_objects)d snippet has been added to %(collection)s",
            "%(num_parent_objects)d snippets have been added to %(collection)s",
            num_parent_objects,
        ) % {"num_parent_objects": num_parent_objects, "collection": collection.name}
