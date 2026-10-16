from django.db import models
<<<<<<< HEAD
from django.urls import reverse
from django.conf import settings


class Event(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="events",
        null=True,
        blank=True,
    )
=======

class Event(models.Model):
>>>>>>> dbf18ed12d19fc28141df157b68bed74edf33b35
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    summary = models.CharField(max_length=240)
    description = models.TextField()
    poster = models.ImageField(upload_to="events/posters/", blank=True)
    starts_at = models.DateTimeField()
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
<<<<<<< HEAD
        return self.title

    # <--- Добавили метод ссылки на детальную страницу
    def get_absolute_url(self):
        return reverse('events:event_detail', kwargs={'pk': self.pk})
=======
        return self.title
>>>>>>> dbf18ed12d19fc28141df157b68bed74edf33b35
