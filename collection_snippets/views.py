"""Custom views."""

import django
import wagtail.admin.ui.tables
import wagtail.admin.utils
import wagtail.permission_policies
import wagtail.snippets.views.chooser
import wagtail.snippets.views.snippets
from django.utils.translation import gettext_lazy as _

import collection_snippets.models


class CollectionPermissionMixin:
    """Collection mixin for views with a snippet object."""

    def user_has_permission(self, permission):
        """Check the current user can access the object."""
        if self.object:
            return self.permission_policy.user_has_permission_for_instance(
                self.request.user, permission, self.object
            )
        return super().user_has_permission(permission)

    def user_has_any_permission(self, permissions):
        """Check the current user can access the object."""
        if self.object:
            return self.permission_policy.user_has_any_permission_for_instance(
                self.request.user, permissions, self.object
            )
        return super().user_has_any_permission(permissions)


class SnippetsFormViewMixin(CollectionPermissionMixin):
    """Collection mixin for views with a snippet form."""

    @django.utils.functional.cached_property
    def collections(self):
        """Collections matching the current user’s permissions."""
        return self.permission_policy.collections_user_has_any_permission_for(
            self.request.user, ["add", "change"]
        )

    @django.utils.functional.cached_property
    def current_collection(self):
        """Collection matching the currently active filter."""
        if collection_id := self.request.GET.get("collection_id"):
            return self.collections.filter(id=collection_id).first()
        if len(self.collections) == 1:
            return self.collections.first()
        return None

    def get_form(self, form_class=None):
        """Modify the form to restrict collection options."""
        form = super().get_form(form_class)
        field = form.fields.get("collection")
        field.queryset = self.collections
        if len(field.queryset) == 1:
            field.widget = django.forms.HiddenInput()
        return form

    def get_context_data(self, **kwargs):
        """Remove panel headings for hidden fields."""
        context = super().get_context_data(**kwargs)
        for panel in context["panel"].children:
            for field in panel.panel.get_form_options()["fields"]:
                if isinstance(panel.form.fields[field].widget, django.forms.HiddenInput):
                    panel.heading = None
        return context


class IndexView(wagtail.snippets.views.snippets.IndexView):
    """Custom snippets list view that filters by accessible collections."""

    list_display = ["__str__", "collection", wagtail.admin.ui.tables.UpdatedAtColumn()]

    def get_add_url(self):
        """Pass current GET parameters to the add url."""
        return wagtail.admin.utils.set_query_params(
            super().get_add_url(), self.request.GET
        )

    def get_base_queryset(self):
        """Get snippets filtered by collection permissions."""
        return self.permission_policy.instances_user_has_any_permission_for(
            self.request.user, self.any_permission_required or [self.permission_required]
        )


class ModelIndexView(wagtail.snippets.views.snippets.ModelIndexView):
    """Custom snippets model index view to filter count by accessible collections."""

    def _get_snippet_types(self):
        """Filter snippet count by accessible collections and current filter."""
        snippet_types = super()._get_snippet_types()

        # Update counts
        for snippet in snippet_types:
            if not hasattr(snippet["model"], "collection"):
                continue
            queryset = snippet[
                "model"
            ].snippet_viewset.permission_policy.instances_user_has_any_permission_for(
                self.request.user, {"add", "change", "delete", "view"}
            )
            if collection_id := self.request.GET.get("collection_id"):
                queryset = queryset.filter(collection_id=collection_id)
            snippet["count"] = queryset.count()
        return snippet_types

    def get_list_url(self, model):
        """Pass existing GET parameters to every snippet index url in the list."""
        return wagtail.admin.utils.set_query_params(
            super().get_list_url(model), self.request.GET
        )


class CreateView(SnippetsFormViewMixin, wagtail.snippets.views.snippets.CreateView):
    """Custom snippets model create view that pre-fills the current collection."""

    def get_initial_form_instance(self):
        """Set the collection of a new instance to the current collection."""
        instance = super().get_initial_form_instance()
        instance.collection = self.current_collection
        return instance


class EditView(SnippetsFormViewMixin, wagtail.snippets.views.snippets.EditView):
    """Custom snippets model edit view."""


class CopyView(SnippetsFormViewMixin, wagtail.snippets.views.snippets.CopyView):
    """Custom snippets model copy view."""


class UsageView(CollectionPermissionMixin, wagtail.snippets.views.snippets.UsageView):
    """Custom snippets model usage view."""


class HistoryView(
    CollectionPermissionMixin, wagtail.snippets.views.snippets.HistoryView
):
    """Custom snippets model history view."""


class InspectView(
    CollectionPermissionMixin, wagtail.snippets.views.snippets.InspectView
):
    """Custom snippets model inspect view."""


class PreviewRevisionView(
    CollectionPermissionMixin, wagtail.snippets.views.snippets.PreviewRevisionView
):
    """Custom snippets model preview revision view."""


class RevisionsCompareView(
    CollectionPermissionMixin, wagtail.snippets.views.snippets.RevisionsCompareView
):
    """Custom snippets model revisions compare view."""


class UnpublishView(
    CollectionPermissionMixin, wagtail.snippets.views.snippets.UnpublishView
):
    """Custom snippets model unpublish view."""


class RevisionsUnscheduleView(
    CollectionPermissionMixin, wagtail.snippets.views.snippets.RevisionsUnscheduleView
):
    """Custom snippets model unschedule view."""


class LockView(CollectionPermissionMixin, wagtail.snippets.views.snippets.LockView):
    """Custom snippets model lock view."""

    def user_has_permission(self, permission):
        """Check the current user can access the object."""
        has_collection_permission = CollectionPermissionMixin.user_has_permission(
            self, permission
        )
        has_permission = wagtail.snippets.views.snippets.LockView.user_has_permission(
            self, permission
        )
        return has_collection_permission and has_permission


class UnlockView(CollectionPermissionMixin, wagtail.snippets.views.snippets.UnlockView):
    """Custom snippets model unlock view."""

    def user_has_permission(self, permission):
        """Check the current user can access the object."""
        has_collection_permission = CollectionPermissionMixin.user_has_permission(
            self, permission
        )
        has_permission = wagtail.snippets.views.snippets.UnlockView.user_has_permission(
            self, permission
        )
        return has_collection_permission and has_permission


class BaseChooseView(wagtail.snippets.views.chooser.BaseChooseView):
    """Custom base chooser view for snippets with collection features."""

    permission_policy = None

    @property
    def collections(self):
        """Collections matching the current user’s permissions."""
        return self.permission_policy.collections_user_has_permission_for(
            self.request.user, "choose"
        )

    def get_object_list(self):
        """Get snippets filtered by collection permissions."""
        return self.permission_policy.instances_user_has_any_permission_for(
            self.request.user, ["choose"]
        )

    def get_filter_form(self):
        """Pass collection options to filter form."""
        filter_form_cls = self.get_filter_form_class()
        return filter_form_cls(
            self.request.GET,
            collections=self.collections if len(self.collections) > 1 else None,
        )

    def get_context_data(self, **kwargs):
        """Add collection filter options to context."""
        context = super().get_context_data(**kwargs)
        context["collections"] = self.collections if len(self.collections) > 1 else None
        return context

    def render_to_response(self):
        """Implementing abstract parent method."""


class ChooseView(
    wagtail.admin.views.generic.chooser.ChooseViewMixin,
    wagtail.admin.views.generic.chooser.CreationFormMixin,
    BaseChooseView,
):
    """Choose view for snippets using custom mixin."""


class ChooseResultsView(
    wagtail.admin.views.generic.chooser.ChooseResultsViewMixin,
    wagtail.admin.views.generic.chooser.CreationFormMixin,
    BaseChooseView,
):
    """Choose results view for snippets using custom mixin."""


class ChooserViewSet(wagtail.snippets.views.chooser.SnippetChooserViewSet):
    """Chooser view set for snippets using custom views."""

    choose_view_class = ChooseView
    choose_results_view_class = ChooseResultsView

    @property
    def permission_policy(self):
        """Set permission policy."""
        return wagtail.permission_policies.collections.CollectionPermissionPolicy(
            self.model, auth_model="collectionsnippets.Snippet"
        )


class SnippetFilter(wagtail.admin.filters.WagtailFilterSet):
    """Custom snippets model filter set."""

    permission_policy = collection_snippets.models.permission_policy

    class Meta:
        model = collection_snippets.models.Snippet
        fields = []

    def __init__(self, *args, **kwargs):
        """Add collection filter if there are multiple collections."""
        super().__init__(*args, **kwargs)
        collections = self.permission_policy.collections_user_has_any_permission_for(
            self.request.user, {"change", "delete"}
        )
        if collections.count() > 1:
            self.filters["collection_id"] = wagtail.admin.filters.CollectionFilter(
                field_name="collection_id",
                label=_("Collection"),
                queryset=collections,
            )


class ViewSet(wagtail.snippets.views.snippets.SnippetViewSet):
    """Snippets view set with custom views."""

    index_view_class = IndexView
    add_view_class = CreateView
    edit_view_class = EditView
    copy_view_class = CopyView
    usage_view_class = UsageView
    history_view_class = HistoryView
    inspect_view_class = InspectView
    revisions_view_class = PreviewRevisionView
    revisions_compare_view_class = RevisionsCompareView
    revisions_unschedule_view_class = RevisionsUnscheduleView
    unpublish_view_class = UnpublishView
    lock_view_class = LockView
    unlock_view_class = UnlockView
    chooser_viewset_class = ChooserViewSet
    filterset_class = SnippetFilter

    @property
    def permission_policy(self):
        """Set permission policy."""
        return wagtail.permission_policies.collections.CollectionPermissionPolicy(
            self.model, auth_model="collectionsnippets.Snippet"
        )
