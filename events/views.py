from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView
from .models import Event
from .forms import EventForm


class HomeView(TemplateView):
    template_name = "events/home.html"


class EventListView(ListView):
    model = Event
    template_name = "events/event_list.html"
    context_object_name = "events"

   
    def get_queryset(self):
        return Event.objects.filter(
            is_deleted=False,
            is_published=True,
        )




class EventDetailView(DetailView):
    model = Event
    template_name = "events/event_detail.html"
    context_object_name = "event"



class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
    success_url = "/events/"

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.owner = self.request.user
            return super().form_valid(form)

        form.add_error(
            None,
            "Чтобы создать событие, необходимо войти в аккаунт."
        )
        return self.form_invalid(form)



class EventUpdateView(UpdateView):
    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
    success_url = "/events/"
