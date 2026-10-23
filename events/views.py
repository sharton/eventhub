from django.views.generic import TemplateView, ListView, DetailView, CreateView
from .models import Event
from .forms import EventForm


class HomeView(TemplateView):
    template_name = "events/home.html"


class EventListView(ListView):
    model = Event
    template_name = "events/event_list.html"
    context_object_name = "events"


class EventDetailView(DetailView):
    model = Event
    template_name = "events/event_detail.html"
    context_object_name = "event"


class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
    success_url = "/events/"