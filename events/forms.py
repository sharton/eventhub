from django import forms
from django.utils.text import slugify
from .models import Event


class EventForm(forms.ModelForm):

    starts_at = forms.DateTimeField(
        label="Дата и время",
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        input_formats=["%Y-%m-%dT%H:%M", "%d.%m.%YT%H:%M"],
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
            "is_published"
        ]
        # Указываем явно обычный текстовый ввод для slug
        widgets = {
            'slug': forms.TextInput(attrs={
                'placeholder': 'my-quest-slug',
                'class': 'validate'
            }),
        }