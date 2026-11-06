from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import (
    TemplateView,
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)

from .forms import EventForm
from .models import Event


class OwnerRequiredMixin(UserPassesTestMixin):
    """Доступ только владельцу события."""

    def test_func(self):
        return self.get_object().owner == self.request.user


class HomeView(TemplateView):
    template_name = "events/home.html"


class EventListView(ListView):
    model = Event
    template_name = "events/event_list.html"
    context_object_name = "events"

    def get_queryset(self):
        queryset = Event.objects.filter(is_deleted=False)
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(summary__icontains=query)
                | Q(description__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()
        return context


class EventDetailView(DetailView):
    model = Event
    template_name = "events/event_detail.html"
    context_object_name = "event"

    def get_queryset(self):
        return Event.objects.filter(is_deleted=False)


class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
    success_url = reverse_lazy("events:event_list")
    extra_context = {"page_title": "Создать событие"}

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class EventUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
    success_url = reverse_lazy("events:event_list")
    extra_context = {"page_title": "Редактировать событие"}

    def get_queryset(self):
        return Event.objects.filter(is_deleted=False)


class EventDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Event
    template_name = "events/event_confirm_delete.html"
    context_object_name = "event"
    success_url = reverse_lazy("events:event_list")

    def get_queryset(self):
        return Event.objects.filter(is_deleted=False)

    def form_valid(self, form):
        # soft delete: запись остаётся в базе, но скрывается из каталога
        self.object.is_deleted = True
        self.object.save(update_fields=["is_deleted", "updated_at"])
        return HttpResponseRedirect(self.get_success_url())
