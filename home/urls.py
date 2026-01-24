from django.urls import path
from . import views

app_name = 'home'
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("category/<int:category_id>/", views.CategoryDetailView.as_view(), name='category_detail'),
    path('category/<int:category_id>/<int:event_id>/', views.EventDetailView.as_view(), name='event_detail'),
    path('category/<int:category_id>/create_event/', views.EventCreateView.as_view(), name='create_event'),
    path('category/<int:category_id>/<int:event_id>/event_request/', views.EventRequestView.as_view(), name='event_request'),
    path("notifications/", views.NotificationsView.as_view(), name="notifications"),
    # path("my_events/", views.MyEventsView.as_view(), name='my_events'),


]
