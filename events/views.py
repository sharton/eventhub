from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from .models import Event
from .forms import EventForm


class HomeView(ListView):
    model = Event
    template_name = "events/home.html"
    context_object_name = "events"

    def get_queryset(self):
        # Отображаем только опубликованные и не удаленные события
        return Event.objects.filter(is_published=True, is_deleted=False).order_by('-created_at')


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
    success_url = reverse_lazy("events:home") # Перенаправление на главную после создания



class EventUpdateView(UpdateView):
    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
    success_url = reverse_lazy("events:home") # Перенаправление на главную после обновления