from django.urls import path
from . import views

app_name = "events"

urlpatterns = [
    path('', views.HomeView.as_view(), name="home"),
    path('events/', views.EventListView.as_view(), name="event_list"),
    path('events/<int:pk>', views.EventDetailView.as_view(), name="event_detail"),
    path('events/create/', views.EventCreateView.as_view(), name="event_create"),
    path('events/update/<int:pk>', views.EventUpdateView.as_view(), name="event_update"),

]