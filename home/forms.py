from django import forms
from .models import Event, Story


class EventCreateForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ("name", 'image', 'description', 'event_date', 'start_hour', 'end_hour',  'privacy',)


class CommentForm(forms.Form):
    text = forms.CharField(max_length=500, label="", widget=forms.TextInput(attrs={'class': "form-control form-control-lg",
                                                                                   'placeholder': 'comment',
                                                                                   "rows": 6,
                                                                                   'style': "resize: vertical;"}))


class StoryForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = ['image']
