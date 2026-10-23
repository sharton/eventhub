from django.conf import settings
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    avatar = models.ImageField(upload_to="accounts/avatars/", blank=True)
    bio = models.TextField("О себе", blank=True)
    city = models.CharField("Город", max_length=100, blank=True)
    birth_date = models.DateField("Дата рождения", null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Профиль {self.user.get_username()}"
