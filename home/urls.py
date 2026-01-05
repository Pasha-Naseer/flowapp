from django.urls import path
from . import views

app_name = 'home'
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("category/<int:category_id>/", views.CategoryDetailView.as_view(), name='category_detail'),
    path('category/<int:category_id>/<int:event_id>/', views.EventDetailView.as_view(), name='event_detail'),

]
