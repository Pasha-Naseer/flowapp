from django.shortcuts import render, get_object_or_404
from django.views import View
from .models import Category, Event


class HomeView(View):
    def get(self, request):
        categories = Category.objects.all()
        context = {
           "categories": categories,
        }
        return render(request, 'home/home.html', context)
    
    def post(self, request):
        pass


class CategoryDetailView(View):
    def get(self, request, category_id):
        category = get_object_or_404(Category, pk=category_id)
        event_list = Event.objects.filter(category=category)
        context = {
            'category': category,
            'event_list': event_list,
        }
        return render(request, 'home/category_detail.html', context)


    def post(self, request):
        pass



class EventDetailView(View):
    def get(self, request, category_id, event_id):
        category = get_object_or_404(Category, pk=category_id)
        event = get_object_or_404(Event, category=category, pk=event_id)
        context = {
            'event': event
        }
        return render(request, 'home/event_detail.html', context)

    def post(self, request):
        pass
