from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import Event


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class EventTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user("owner")
        self.other = get_user_model().objects.create_user("other")
        self.event = Event.objects.create(owner=self.owner, title="Event", slug="event", starts_at=timezone.now())
        self.client.force_login(self.owner)
        self.data = dict(title="Updated", slug="updated", summary="Summary", description="Details", starts_at="2026-11-01T18:30", is_published="on")

    def url(self, action):
        return reverse(f"events:event_{action}", args=[self.event.pk])

    def test_creation_sets_owner_and_ignores_protected_fields(self):
        self.data.update(owner=self.other.pk, is_deleted="true")
        self.assertRedirects(self.client.post(reverse("events:event_create"), self.data), "/events/")
        event = Event.objects.get(slug="updated")
        self.assertEqual(event.owner_id, self.owner.pk)
        self.assertFalse(event.is_deleted)

    def test_owner_can_update_with_html_datetime(self):
        self.assertContains(self.client.get(self.url("update")), self.event.starts_at.strftime("%Y-%m-%dT%H:%M"))
        self.assertRedirects(self.client.post(self.url("update"), self.data), "/events/")
        self.event.refresh_from_db()
        self.assertEqual(self.event.title, "Updated")

    def test_soft_delete_requires_post_and_keeps_row(self):
        self.assertEqual(self.client.get(self.url("delete")).status_code, 200)
        self.event.refresh_from_db()
        self.assertFalse(self.event.is_deleted)
        self.assertRedirects(self.client.post(self.url("delete")), "/events/")
        self.event.refresh_from_db()
        self.assertTrue(self.event.is_deleted)
        for action in ("detail", "update", "delete"):
            self.assertEqual(self.client.get(self.url(action)).status_code, 404)
        self.assertEqual(self.client.post(self.url("delete")).status_code, 404)
        self.assertNotContains(self.client.get("/events/"), self.url("detail"))

    def test_other_user_cannot_update_or_delete(self):
        self.client.force_login(self.other)
        for action in ("update", "delete"):
            self.assertEqual(self.client.get(self.url(action)).status_code, 403)
            self.assertEqual(self.client.post(self.url(action), self.data).status_code, 403)
        self.event.refresh_from_db()
        self.assertEqual(self.event.title, "Event")
        self.assertFalse(self.event.is_deleted)
        self.assertNotContains(self.client.get(self.url("detail")), self.url("delete"))

    def test_anonymous_cannot_mutate(self):
        self.client.logout()
        for url in (self.url("update"), self.url("delete"), reverse("events:event_create")):
            self.assertRedirects(self.client.post(url, self.data), f"/login/?next={url}")

    def test_delete_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        self.assertEqual(client.post(self.url("delete")).status_code, 403)
        self.event.refresh_from_db()
        self.assertFalse(self.event.is_deleted)

    def test_navigation_and_detail_links(self):
        response = self.client.get("/events/")
        for url in (self.url("detail"), reverse("events:event_create"), reverse("accounts:profile")):
            self.assertContains(response, f'href="{url}"')
        self.assertContains(response, "Все события")
        self.assertContains(response, "Создать событие")
