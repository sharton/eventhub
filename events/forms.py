from django import forms

from .models import Event


class EventForm(forms.ModelForm):

    starts_at = forms.DateTimeField(
        label="Дата и время",
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        input_formats=["%Y-%m-%dT%H:%M", "%d.%m.%YT%H:%M", "%d.%m.%Y %H:%M"],
    )

    class Meta:
        model = Event
        fields = [
            "title",
            "slug",
            "summary",
            "description",
            "poster",
            "starts_at",
            "is_published",
        ]