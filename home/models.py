from django.db import models
from accounts.models import CustomUser


class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    image = models.ImageField(default='fallback.png')

    def __str__(self):
        return self.name


class Event(models.Model):
    privacy_choices = [
        ("PR", 'Private'),
        ("PU", "Public"),
    ]
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    image = models.ImageField(default='fallback.png')
    promoter = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    description = models.TextField()
    start_hour = models.TimeField()
    end_hour = models.TimeField()
    event_date = models.DateField()
    participants = models.ManyToManyField(
        CustomUser,
        related_name="events_joined",
        blank=True,
    )
    privacy = models.CharField(max_length=2, choices=privacy_choices, default="PU")


    def __str__(self):
        return self.name
    
    # Get all participants of an event
    # event.participants.all()

    # Add a participant
    # event.participants.add(user)

    # Remove a participant
    # event.participants.remove(user)

    # Get all events a user has joined
    # user.events_joined.all()

    # Get all events a user has promoted
    # user.promoted_events.all()
