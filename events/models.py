from django.db import models
from django.urls import reverse

class Event(models.Model):
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
        return self.title

    # <--- Добавили метод ссылки на детальную страницу
    def get_absolute_url(self):
        return reverse('events:event_detail', kwargs={'pk': self.pk})