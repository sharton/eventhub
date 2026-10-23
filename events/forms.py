from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from .models import Event

User = get_user_model()


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        label="Email",
        required=False,
        help_text="Можно указать любой адрес, даже несуществующий.",
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        return self.cleaned_data.get('email', '')

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Это имя уже занято.")
        return username


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