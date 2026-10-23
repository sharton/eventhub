from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView

from .models import Event
from .forms import EventForm


class HomeView(TemplateView):
    template_name = "events/home.html"


class ActiveEventsMixin:
    def get_queryset(self):
        return Event.objects.filter(is_deleted=False).select_related("owner")


class EventListView(ActiveEventsMixin, ListView):
    model = Event
    template_name = "events/event_list.html"
    context_object_name = "events"


class EventDetailView(ActiveEventsMixin, DetailView):
    model = Event
    template_name = "events/event_detail.html"
    context_object_name = "event"


class OwnerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.get_object().owner_id == self.request.user.pk


class EventCreateView(LoginRequiredMixin, CreateView):
    extra_context = {"page_title": "Создать событие"}
    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
    success_url = reverse_lazy("events:event_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class EventUpdateView(LoginRequiredMixin, OwnerRequiredMixin, ActiveEventsMixin, UpdateView):
    extra_context = {"page_title": "Редактировать событие"}
    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
    success_url = reverse_lazy("events:event_list")


class EventDeleteView(LoginRequiredMixin, OwnerRequiredMixin, ActiveEventsMixin, DetailView):
    model = Event
    template_name = "events/event_confirm_delete.html"
    context_object_name = "event"
    http_method_names = ["get", "post", "head", "options"]

    def post(self, request, *args, **kwargs):
        event = self.get_object()
        Event.objects.filter(pk=event.pk, owner=request.user, is_deleted=False).update(
            is_deleted=True, updated_at=timezone.now()
        )
        messages.success(request, "Событие удалено")
        return redirect("events:event_list")
