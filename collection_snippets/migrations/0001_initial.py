# Generated by Django 4.2.3 on 2023-09-04 11:07

import uuid

import django.db.models.deletion
import wagtail.models
import wagtail.models.collections
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Snippet",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "translation_key",
                    models.UUIDField(default=uuid.uuid4, editable=False),
                ),
                (
                    "live",
                    models.BooleanField(
                        default=True, editable=False, verbose_name="live"
                    ),
                ),
                (
                    "has_unpublished_changes",
                    models.BooleanField(
                        default=False,
                        editable=False,
                        verbose_name="has unpublished changes",
                    ),
                ),
                (
                    "first_published_at",
                    models.DateTimeField(
                        blank=True,
                        db_index=True,
                        null=True,
                        verbose_name="first published at",
                    ),
                ),
                (
                    "last_published_at",
                    models.DateTimeField(
                        editable=False, null=True, verbose_name="last published at"
                    ),
                ),
                (
                    "go_live_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="go live date/time"
                    ),
                ),
                (
                    "expire_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="expiry date/time"
                    ),
                ),
                (
                    "expired",
                    models.BooleanField(
                        default=False, editable=False, verbose_name="expired"
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        help_text="The internal title used in the administrative interface.",
                        max_length=255,
                        verbose_name="Admin title",
                    ),
                ),
                (
                    "collection",
                    models.ForeignKey(
                        default=wagtail.models.collections.get_root_collection_id,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="wagtailcore.collection",
                        verbose_name="collection",
                    ),
                ),
                (
                    "latest_revision",
                    models.ForeignKey(
                        blank=True,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailcore.revision",
                        verbose_name="latest revision",
                    ),
                ),
                (
                    "live_revision",
                    models.ForeignKey(
                        blank=True,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailcore.revision",
                        verbose_name="live revision",
                    ),
                ),
                (
                    "locale",
                    models.ForeignKey(
                        editable=False,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="wagtailcore.locale",
                    ),
                ),
            ],
            options={
                "permissions": [("choose_snippet", "Can choose snippet")],
                "unique_together": {("translation_key", "locale")},
            },
            bases=(wagtail.models.PreviewableMixin, models.Model),
        ),
    ]
