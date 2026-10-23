from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Profile


class UniqueEmailMixin:
    def clean_email(self):
        email = self.cleaned_data["email"].strip()
        if email and get_user_model().objects.filter(email__iexact=email).exclude(
            pk=self.instance.pk
        ).exists():
            raise forms.ValidationError("Этот email уже используется.")
        return email


class SignUpForm(UniqueEmailMixin, UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "email")


class UserUpdateForm(UniqueEmailMixin, forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ("first_name", "last_name", "email")


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("avatar", "bio", "city", "birth_date")
        widgets = {
            "birth_date": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
        }

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")
        if avatar and avatar.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Размер аватара не должен превышать 5 МБ.")
        return avatar
