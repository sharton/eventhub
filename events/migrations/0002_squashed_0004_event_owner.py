"""Preserve ownerless events when upgrading from the original fork.

Replaces upstream's owner migrations only when none have been applied.
Databases already at upstream 0004 retain their migration history and owners.
"""
import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def preserve_legacy_events(apps, schema_editor):
    Event = apps.get_model("events", "Event")
    alias = schema_editor.connection.alias
    events = Event.objects.using(alias).filter(owner__isnull=True)
    if events.exists():
        User = apps.get_model(settings.AUTH_USER_MODEL)
        # Never assign historical events to an arbitrary real user (e.g. pk=1).
        legacy_owner = User.objects.using(alias).create(
            username=f"legacy-events-{uuid.uuid4().hex}",
            password="!", is_active=False,
        )
        events.update(owner_id=legacy_owner.pk)


class Migration(migrations.Migration):
    replaces = [
        ("events", "0002_event_owner"),
        ("events", "0003_alter_event_owner"),
        ("events", "0004_alter_event_owner"),
    ]
    dependencies = [
        ("events", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.AddField(
            model_name="event", name="owner",
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE,
                                    related_name="events", to=settings.AUTH_USER_MODEL),
        ),
        migrations.RunPython(preserve_legacy_events, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="event", name="owner",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name="events", to=settings.AUTH_USER_MODEL),
        ),
    ]
