from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from .forms import EventForm
from .models import Event


class HomeView(TemplateView):
    template_name = "events/home.html"


class EventListView(ListView):
    model = Event
    template_name = "events/event_list.html"
    context_object_name = "events"

    def get_queryset(self):
        return Event.objects.filter(is_deleted=False).prefetch_related("favorited_by")


class EventCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
    success_message = "Событие «%(title)s» создано."

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("events:event_detail", kwargs={"pk": self.object.pk})


class EventUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
    success_message = "Событие «%(title)s» обновлено."

    def get_queryset(self):
        return Event.objects.filter(is_deleted=False)

    def get_success_url(self):
        return reverse("events:event_detail", kwargs={"pk": self.object.pk})


class EventDeleteView(LoginRequiredMixin, DeleteView):
    model = Event
    template_name = "events/event_confirm_delete.html"
    success_url = reverse_lazy("events:event_list")

    def get_queryset(self):
        return Event.objects.filter(is_deleted=False)

    def form_valid(self, form):
        self.object.is_deleted = True
        self.object.save(update_fields=["is_deleted"])
        messages.success(self.request, f"Событие «{self.object.title}» удалено.")
        return HttpResponseRedirect(self.get_success_url())


class EventDetailView(DetailView):
    model = Event
    template_name = "events/event_detail.html"
    context_object_name = "event"

    def get_queryset(self):
        return Event.objects.filter(is_deleted=False)


@login_required
@require_POST
def toggle_favorite(request, pk):
    event = get_object_or_404(Event, pk=pk, is_deleted=False)
    if event.favorited_by.filter(pk=request.user.pk).exists():
        event.favorited_by.remove(request.user)
    else:
        event.favorited_by.add(request.user)
    next_url = request.POST.get("next")
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return redirect(next_url)
    return redirect("events:event_list")


class FavoriteListView(LoginRequiredMixin, ListView):
    template_name = "events/favorite_list.html"
    context_object_name = "events"

    def get_queryset(self):
        return self.request.user.favorite_events.filter(is_deleted=False)
