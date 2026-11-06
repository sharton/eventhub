from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
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
        user = self.request.user
        if user.is_authenticated:
            context["favorite_ids"] = set(
                user.favorite_events.values_list("pk", flat=True)
            )
        else:
            context["favorite_ids"] = set()
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


class EventFavoriteToggleView(LoginRequiredMixin, View):
    """Добавляет событие в избранное или убирает, если оно уже там. Только POST."""

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk, is_deleted=False)
        if event.favorited_by.filter(pk=request.user.pk).exists():
            event.favorited_by.remove(request.user)
        else:
            event.favorited_by.add(request.user)

        next_url = request.POST.get("next", "")
        if next_url and url_has_allowed_host_and_scheme(
            next_url, allowed_hosts={request.get_host()}
        ):
            return redirect(next_url)
        return redirect("events:event_list")
