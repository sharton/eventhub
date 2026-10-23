from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView

from .forms import ProfileUpdateForm, SignUpForm, UserUpdateForm
from .models import Profile


@require_http_methods(["GET", "POST"])
def signup(request):
    form = SignUpForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            form.save()
        return redirect("accounts:login")
    return render(request, "accounts/signup.html", {"form": form})


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"], _ = Profile.objects.get_or_create(user=self.request.user)
        context["events"] = self.request.user.events.filter(is_deleted=False).order_by("-starts_at")
        return context


@login_required
@require_http_methods(["GET", "POST"])
def profile_edit(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    data = request.POST if request.method == "POST" else None
    user_form = UserUpdateForm(data, instance=request.user)
    files = request.FILES if request.method == "POST" else None
    profile_form = ProfileUpdateForm(data, files, instance=profile)
    if request.method == "POST":
        # Validate both forms so errors from each are visible; save neither on failure.
        user_valid = user_form.is_valid()
        profile_valid = profile_form.is_valid()
        if user_valid and profile_valid:
            with transaction.atomic():
                user_form.save()
                profile_form.save()
            messages.success(request, "Профиль обновлён")
            return redirect("accounts:profile")
    return render(request, "accounts/profile_edit.html", {
        "user_form": user_form, "profile_form": profile_form,
    })
