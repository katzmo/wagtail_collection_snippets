"""Custom views."""

import wagtail.admin.ui.tables
import wagtail.admin.utils
import wagtail.snippets.views.snippets

import collection_snippets.models


class SnippetsViewMixin:
    """Collection mixin for views."""

    @property
    def collections(self):
        """Collections matching the current user’s permissions."""
        return collection_snippets.models.permission_policy.collections_user_has_any_permission_for(
            self.request.user, ["add", "change"]
        )

    @property
    def current_collection(self):
        """Collection matching the currently active filter."""
        if collection_id := self.request.GET.get("collection_id"):
            return self.collections.filter(id=collection_id).first()
        return None


class IndexView(SnippetsViewMixin, wagtail.snippets.views.snippets.IndexView):
    """Custom snippets list view that filters by accessible collections."""

    list_display = ["__str__", "collection", wagtail.admin.ui.tables.UpdatedAtColumn()]

    def get_add_url(self):
        """Pass current GET parameters to the add url."""
        return wagtail.admin.utils.set_query_params(
            super().get_add_url(), self.request.GET
        )

    def get_context_data(self, **kwargs):
        """Filter items by collections accessible to the current user."""
        queryset = kwargs.pop("object_list", self.object_list)
        queryset = queryset.select_related("collection").filter(
            collection__in=self.collections
        )

        if collection_id := self.request.GET.get("collection_id"):
            queryset = queryset.filter(collection__id=collection_id)

        context = super().get_context_data(object_list=queryset, **kwargs)
        context["collections"] = self.collections if len(self.collections) > 1 else None
        context["current_collection"] = self.current_collection
        return context


class ModelIndexView(SnippetsViewMixin, wagtail.snippets.views.snippets.ModelIndexView):
    """Custom snippets model index view to filter count by accessible collections."""

    def _get_snippet_types(self):
        """Filter snippet count by accessible collections and current filter."""
        snippet_types = super()._get_snippet_types()
        user = self.request.user
        current_collection = self.current_collection

        if user.is_superuser and not current_collection:
            return snippet_types

        # Update counts
        collections = [current_collection] if current_collection else self.collections
        for snippet in snippet_types:
            if not hasattr(snippet["model"], "collection"):
                continue
            queryset = snippet["model"].objects.select_related("collection")
            snippet["count"] = queryset.filter(collection__in=collections).count()
        return snippet_types

    def get_list_url(self, type):
        """Pass existing GET parameters to every snippet index url in the list."""
        # pylint: disable=redefined-builtin
        return wagtail.admin.utils.set_query_params(
            super().get_list_url(type), self.request.GET
        )


class CreateView(SnippetsViewMixin, wagtail.snippets.views.snippets.CreateView):
    """Custom snippets model create view that pre-fills the current collection."""

    def _get_initial_form_instance(self):
        """Set the collection of a new instance to the current collection."""
        instance = super()._get_initial_form_instance()
        instance.collection = self.current_collection
        return instance


class BaseChooseView(wagtail.snippets.views.chooser.BaseChooseView):
    """Custom base chooser view for snippets with collection features."""

    template_name = "collectionsnippets/chooser.html"

    @property
    def collections(self):
        """Collections matching the current user’s permissions."""
        return collection_snippets.models.permission_policy.collections_user_has_permission_for(
            self.request.user, "choose"
        )

    def get_object_list(self):
        """Filter queryset by collections."""
        object_list = super().get_object_list()
        user = self.request.user
        if user.is_superuser:
            return object_list
        return object_list.select_related("collection").filter(
            collection__in=self.collections
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


class ViewSet(wagtail.snippets.views.snippets.SnippetViewSet):
    """Snippets view set with custom views."""

    add_view_class = CreateView
    index_view_class = IndexView
    index_template_name = "collectionsnippets/index.html"
    chooser_viewset_class = ChooserViewSet
