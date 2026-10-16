<<<<<<< HEAD
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django.urls import reverse_lazy
from .models import Event
from .forms import EventForm
from django.shortcuts import get_object_or_404, redirect 


class HomeView(ListView):
    model = Event
    template_name = "events/home.html"
    context_object_name = "events"

    def get_queryset(self):
        return Event.objects.filter(is_published=True, is_deleted=False).order_by('-created_at')
=======
from django.views.generic import TemplateView, ListView, DetailView, CreateView
from .models import Event
from .forms import EventForm


class HomeView(TemplateView):
    template_name = "events/home.html"
>>>>>>> dbf18ed12d19fc28141df157b68bed74edf33b35


class EventListView(ListView):
    model = Event
    template_name = "events/event_list.html"
    context_object_name = "events"

<<<<<<< HEAD
    def get_queryset(self):
        return Event.objects.filter(is_deleted=False)

=======
>>>>>>> dbf18ed12d19fc28141df157b68bed74edf33b35

class EventDetailView(DetailView):
    model = Event
    template_name = "events/event_detail.html"
    context_object_name = "event"


class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
<<<<<<< HEAD
    success_url = reverse_lazy("events:home")
    extra_context = {"page_title": "Создание события"}

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.owner = self.request.user
        else:
            form.instance.owner = None
        return super().form_valid(form)


class EventUpdateView(UpdateView):
    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
    extra_context = {"page_title": "Редактирование события"}


class EventDeleteView(View):
    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        event.is_deleted = True
        event.save()
        return redirect('events:home')
=======
    success_url = "/events/"
>>>>>>> dbf18ed12d19fc28141df157b68bed74edf33b35
