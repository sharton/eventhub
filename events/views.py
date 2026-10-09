from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, TemplateView
from .models import Event


class HomeView(TemplateView):
    template_name = "events/home.html"


class EventListView(ListView):
    model = Event
    template_name = "events/event_list.html"
    context_object_name = "events"


class EventCreateView(CreateView):
    model = Event
    template_name = "events/event_form.html"
    fields = ("title", "slug", "summary", "description", "poster", "starts_at", "is_published")
    success_url = reverse_lazy("events:event_list")


class EventDetailView(DetailView):
    model = Event
    template_name = "events/event_detail.html"
    context_object_name = "event"