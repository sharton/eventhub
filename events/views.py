from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import (
    TemplateView, ListView, DetailView, CreateView, UpdateView, View
)
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages

from .forms import EventForm
from .models import Event


class HomeView(TemplateView):
    template_name = "events/home.html"


class EventListView(ListView):
    model = Event
    template_name = "events/event_list.html"
    context_object_name = "events"

    def get_queryset(self):
        return Event.objects.alive().filter(is_published=True)


class EventDetailView(DetailView):
    model = Event
    template_name = "events/event_detail.html"
    context_object_name = "event"

    def get_queryset(self):
        return Event.objects.alive()


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


class MyEventsView(LoginRequiredMixin, ListView):
    model = Event
    template_name = "events/event_list.html"
    context_object_name = "events"

    def get_queryset(self):
        return Event.objects.alive().filter(owner=self.request.user)