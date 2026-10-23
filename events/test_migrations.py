"""Exercise both supported starting histories in isolated SQLite databases."""
import subprocess
import sys
import tempfile
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class UpgradeTests(SimpleTestCase):
    def check_upgrade(self, upstream):
        with tempfile.TemporaryDirectory() as folder:
            script = '''
import os, sys
os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"
from django.conf import settings
settings.DATABASES["default"]["NAME"] = sys.argv[1]
import django
django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.loader import MigrationLoader
from django.utils import timezone

executor = MigrationExecutor(connection)
executor.loader = MigrationLoader(connection, replace_migrations=False)
target = [("events", "0004_alter_event_owner" if sys.argv[2] == "upstream" else "0001_initial"),
          ("auth", "0012_alter_user_first_name_max_length")]
executor.migrate(target)
apps = executor.loader.project_state(target).apps
User = apps.get_model("auth", "User")
user = User.objects.create(username="existing", password="!")
Event = apps.get_model("events", "Event")
fields = dict(title="Preserved", slug="preserved", starts_at=timezone.now())
if sys.argv[2] == "upstream":
    fields["owner_id"] = user.pk
event = Event.objects.create(**fields)

executor = MigrationExecutor(connection)
executor.loader.check_consistent_history(connection)
executor.migrate(executor.loader.graph.leaf_nodes())
from events.models import Event as CurrentEvent
from django.contrib.auth import get_user_model
saved = CurrentEvent.objects.get(pk=event.pk)
assert saved.title == "Preserved"
assert not saved.is_deleted
if sys.argv[2] == "upstream":
    assert saved.owner_id == user.pk
    assert get_user_model().objects.count() == 1
else:
    assert saved.owner_id != user.pk
    assert not saved.owner.is_active
    assert not saved.owner.has_usable_password()
    assert not saved.owner.is_staff
MigrationExecutor(connection).loader.check_consistent_history(connection)
print("Upgrade OK")
'''
            result = subprocess.run(
                [sys.executable, "-c", script, str(Path(folder) / "upgrade.sqlite3"),
                 "upstream" if upstream else "fork"],
                cwd=settings.BASE_DIR, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Upgrade OK", result.stdout)

    def test_fork_main_with_ownerless_event(self):
        self.check_upgrade(False)

    def test_upstream_with_applied_original_migrations(self):
        self.check_upgrade(True)
