from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse_lazy
from django.views.generic import (
    TemplateView, ListView, DetailView, CreateView, UpdateView, View
)
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from django.db.models import Q
from django.db.models.functions import Lower

from .forms import EventForm
from .models import Event, Favorite


# ---------- утилита: id избранных событий пользователя ----------
def _favorite_ids(user):
    if user.is_authenticated:
        return set(
            Favorite.objects.filter(user=user).values_list("event_id", flat=True)
        )
    return set()


# ---------- Главная ----------
class HomeView(TemplateView):
    template_name = "events/home.html"


# ---------- Список всех опубликованных событий ----------
class EventListView(ListView):
    model = Event
    template_name = "events/event_list.html"
    context_object_name = "events"

    def get_queryset(self):
        qs = Event.objects.alive().filter(is_published=True)
        q = self.request.GET.get("q", "").strip().lower()
        if q:
            qs = qs.annotate(
                title_lower=Lower("title"),
                summary_lower=Lower("summary"),
            ).filter(
                Q(title_lower__contains=q) | Q(summary_lower__contains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "").strip()
        ctx["user_favorite_ids"] = _favorite_ids(self.request.user)
        return ctx


# ---------- Детальная страница ----------
class EventDetailView(DetailView):
    model = Event
    template_name = "events/event_detail.html"
    context_object_name = "event"

    def get_queryset(self):
        return Event.objects.alive()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["user_favorite_ids"] = _favorite_ids(self.request.user)
        return ctx


# ---------- Создание события ----------
class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
    success_url = reverse_lazy("events:event_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Создать событие"
        return ctx


# ---------- Редактирование события ----------
class EventUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
    success_url = reverse_lazy("events:event_list")

    def get_queryset(self):
        return Event.objects.alive()

    def test_func(self):
        event = self.get_object()
        return event.owner == self.request.user

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Редактировать событие"
        return ctx


# ---------- Удаление (soft-delete) ----------
class EventDeleteView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Soft-delete: помечаем is_deleted=True, запись остаётся в БД."""

    def get_object(self):
        return get_object_or_404(Event.objects.alive(), pk=self.kwargs["pk"])

    def test_func(self):
        return self.get_object().owner == self.request.user

    def post(self, request, pk):
        event = self.get_object()
        event.soft_delete()
        messages.success(request, "Событие удалено.")
        return redirect("events:event_list")

    def get(self, request, pk):
        event = self.get_object()
        return render(request, "events/event_confirm_delete.html", {"event": event})


# ---------- Мои события ----------
class MyEventsView(LoginRequiredMixin, ListView):
    model = Event
    template_name = "events/event_list.html"
    context_object_name = "events"

    def get_queryset(self):
        qs = Event.objects.alive().filter(owner=self.request.user)
        q = self.request.GET.get("q", "").strip().lower()
        if q:
            qs = qs.annotate(
                title_lower=Lower("title"),
                summary_lower=Lower("summary"),
            ).filter(
                Q(title_lower__contains=q) | Q(summary_lower__contains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "").strip()
        ctx["user_favorite_ids"] = _favorite_ids(self.request.user)
        return ctx


# ---------- Избранное ----------
class FavoriteListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = "events/event_list.html"
    context_object_name = "events"

    def get_queryset(self):
        qs = Event.objects.alive().filter(favorited_by__user=self.request.user)
        q = self.request.GET.get("q", "").strip().lower()
        if q:
            qs = qs.annotate(
                title_lower=Lower("title"),
                summary_lower=Lower("summary"),
            ).filter(
                Q(title_lower__contains=q) | Q(summary_lower__contains=q)
            )
        return qs.distinct()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "").strip()
        ctx["is_favorites_page"] = True
        ctx["user_favorite_ids"] = _favorite_ids(self.request.user)
        return ctx


# ---------- Поставить / убрать лайк ----------
@login_required
@require_POST
def toggle_favorite(request, pk):
    event = get_object_or_404(Event.objects.alive(), pk=pk)
    fav, created = Favorite.objects.get_or_create(user=request.user, event=event)
    if not created:
        fav.delete()
        messages.success(request, "Убрано из избранного.")
    else:
        messages.success(request, "Добавлено в избранное.")
    return redirect(request.META.get("HTTP_REFERER", "events:event_list"))