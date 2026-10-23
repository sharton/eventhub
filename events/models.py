from django.conf import settings
from django.db import models
from django.urls import reverse


class EventQuerySet(models.QuerySet):
    def alive(self):
        return self.filter(is_deleted=False)


class Event(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='events',
        null=True,
        blank=True,
    )
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

    objects = EventQuerySet.as_manager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('events:event_detail', kwargs={'pk': self.pk})

    def soft_delete(self):
        self.is_deleted = True
        self.save(update_fields=['is_deleted'])