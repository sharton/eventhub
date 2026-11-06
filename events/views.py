from django.db.models import Q
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Event
from .forms import EventForm


class HomeView(TemplateView):
    template_name = "events/home.html"


# class EventListView(ListView):
#     model = Event
#     template_name = "events/event_list.html"
#     context_object_name = "events"

#     def get_queryset(self):
#         return Event.objects.filter(is_deleted=False)


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



class OwnerRequiredMixin(UserPassesTestMixin):

    def test_func(self):
        return self.get_object().owner == self.request.user


class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
    success_url = "/events/"


class EventUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
    success_url = "/events/"
