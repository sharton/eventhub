import tempfile
from datetime import date
from io import BytesIO

from PIL import Image
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from events.models import Event
from .models import Profile


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class ProfileTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("alice", "alice@example.com", "secret123")
        self.other = get_user_model().objects.create_user("bob", "bob@example.com", "secret123")
        self.client.force_login(self.user)
        self.edit = reverse("accounts:profile_edit")
        self.profile = reverse("accounts:profile")
        self.data = dict(first_name="Алия", last_name="Тест", email="alice@example.com",
                         city="Бишкек", bio="Привет", birth_date="2000-02-03")

    def test_signal_and_string(self):
        self.assertEqual(str(self.user.profile), "Профиль alice")
        self.user.save()
        self.assertEqual(Profile.objects.filter(user=self.user).count(), 1)

    def test_anonymous_redirects_and_login_next(self):
        self.client.logout()
        for url in (self.profile, self.edit):
            self.assertRedirects(self.client.get(url), f"/login/?next={url}")
        self.assertRedirects(self.client.post("/login/", {
            "username": "alice", "password": "secret123", "next": self.edit,
        }), self.edit)

    def test_profile_fallback_for_old_user(self):
        for url in (self.profile, self.edit):
            Profile.objects.filter(user=self.user).delete()
            self.assertEqual(self.client.get(url).status_code, 200)
            self.assertTrue(Profile.objects.filter(user=self.user).exists())

    def test_update_own_profile_and_message(self):
        response = self.client.post(self.edit, self.data, follow=True)
        self.assertContains(response, "Профиль обновлён")
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Алия")
        self.assertEqual(self.user.profile.city, "Бишкек")
        self.assertEqual(self.user.profile.birth_date, date(2000, 2, 3))
        self.assertContains(self.client.get(self.edit), 'value="2000-02-03"')

    def test_duplicate_email_case_insensitive_and_no_partial_save(self):
        self.data["email"] = "BOB@example.com"
        response = self.client.post(self.edit, self.data)
        self.assertContains(response, "Этот email уже используется")
        self.user.refresh_from_db()
        self.assertEqual(self.user.profile.city, "")
        self.assertEqual(self.user.first_name, "")

    def test_invalid_profile_does_not_save_user(self):
        self.data["birth_date"] = "invalid"
        response = self.client.post(self.edit, self.data)
        self.assertTrue(response.context["profile_form"].errors)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "")

    def test_both_forms_show_errors(self):
        self.data.update(email="bad", birth_date="bad")
        response = self.client.post(self.edit, self.data)
        self.assertTrue(response.context["profile_form"].errors)
        self.assertTrue(response.context["user_form"].errors)

    def test_cannot_change_identity_permissions_or_other_user(self):
        self.data.update(user=self.other.pk, id=self.other.pk, username="hacked",
                         is_staff="true", is_superuser="true", password="hacked")
        self.client.post(self.edit, self.data)
        self.user.refresh_from_db()
        self.other.refresh_from_db()
        self.assertEqual(self.user.username, "alice")
        self.assertFalse(self.user.is_staff or self.user.is_superuser)
        self.assertTrue(self.user.check_password("secret123"))
        self.assertEqual(self.other.profile.city, "")
        self.assertEqual(self.other.first_name, "")
        response = self.client.get(self.profile, {"user": self.other.pk})
        self.assertEqual(response.context["profile"].user_id, self.user.pk)
        self.assertEqual(self.client.get(f"/profile/{self.other.pk}/edit/").status_code, 404)

    def test_csrf_and_methods(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        self.assertEqual(client.post(self.edit, self.data).status_code, 403)
        self.assertEqual(self.client.put(self.edit, self.data).status_code, 405)
        self.client.get(self.edit, self.data)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "")

    def test_avatar_upload_clear_and_invalid_file(self):
        with tempfile.TemporaryDirectory() as media, override_settings(MEDIA_ROOT=media):
            buffer = BytesIO()
            Image.new("RGB", (8, 8), "blue").save(buffer, format="PNG")
            self.data["avatar"] = SimpleUploadedFile("avatar.png", buffer.getvalue(), "image/png")
            self.assertRedirects(self.client.post(self.edit, self.data), self.profile)
            profile = Profile.objects.get(user=self.user)
            self.assertTrue(profile.avatar.storage.exists(profile.avatar.name))
            self.assertContains(self.client.get(self.profile), profile.avatar.url)
            self.data["avatar"] = SimpleUploadedFile("bad.png", b"not an image", "image/png")
            response = self.client.post(self.edit, self.data)
            self.assertIn("avatar", response.context["profile_form"].errors)
            del self.data["avatar"]
            self.data["avatar-clear"] = "on"
            self.client.post(self.edit, self.data)
            self.assertFalse(Profile.objects.get(user=self.user).avatar)

    def test_profile_lists_only_own_active_events_and_escapes_bio(self):
        own = Event.objects.create(owner=self.user, title="Mine", slug="mine", starts_at=timezone.now())
        Event.objects.create(owner=self.user, title="Deleted", slug="deleted", is_deleted=True, starts_at=timezone.now())
        Event.objects.create(owner=self.other, title="Others", slug="others", starts_at=timezone.now())
        Profile.objects.filter(user=self.user).update(bio="<script>alert(1)</script>")
        response = self.client.get(self.profile)
        self.assertEqual(list(response.context["events"]), [own])
        self.assertContains(response, reverse("events:event_detail", args=[own.pk]))
        self.assertNotContains(response, "<script>alert(1)</script>")

    def test_signup_login_logout_and_duplicate_email(self):
        self.client.logout()
        data = dict(username="newuser", email="new@example.com", password1="Strong-test-123", password2="Strong-test-123")
        self.assertRedirects(self.client.post("/signup/", data), "/login/")
        self.assertTrue(Profile.objects.filter(user__username="newuser").exists())
        data.update(username="another", email="NEW@example.com")
        self.assertContains(self.client.post("/signup/", data), "Этот email уже используется")
        self.assertFalse(get_user_model().objects.filter(username="another").exists())
        self.assertContains(self.client.post("/login/", {"username": "newuser", "password": "wrong"}), "errorlist")
        self.client.force_login(self.user)
        self.assertEqual(self.client.get("/logout/").status_code, 405)
        self.assertRedirects(self.client.post("/logout/"), "/")
