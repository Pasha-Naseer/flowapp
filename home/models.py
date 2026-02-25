import datetime

from django.db import models
from flowaccounts.models import User, Profile
from django.db.models.signals import post_save
#null=True set for CATEGORY.USER

class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    image = models.ImageField(default='fallback.png')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name


# currently happening
class Event(models.Model):
    privacy_choices = [
        ("PR", 'Private'),
        ("PU", "Public"),
    ]
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    image = models.ImageField(default='fallback.png')
    promoter = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()
    start_hour = models.TimeField()
    end_hour = models.TimeField()
    event_date = models.DateField()
    participants = models.ManyToManyField(
        User,
        related_name="events_joined",
        blank=True,
    )
    privacy = models.CharField(max_length=2, choices=privacy_choices, default="PU")
    # if in close friends can see else not
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


class Friend(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class FriendItem(models.Model):
    friend = models.ForeignKey(Friend, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('friend', 'user')

    def __str__(self):
        return self.user.username
        # handle this?


class Comment(models.Model):
    # with foreignkey to self so we can add replies
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    text = models.TextField(max_length=400)
    date_submitted = models.DateTimeField(auto_now=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)  # null = True should be off on server
    confirmed = models.BooleanField(default=False)

    # comment.replies.all()

    def __str__(self):
        return self.profile.user.username
    # one should be able to delete his own event's comments


class Membership(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    # when pushing on server null is not True
    to_whom = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="event_owner", null=True)  # can there be collision
    date_submitted = models.DateTimeField(auto_now_add=True)  # auto_now_add?
    accepted = models.BooleanField(default=False)
    # delete the rejected ones

    def __str__(self):
        return f"{self.profile} - {self.event} - {self.date_submitted}"


# test
class Notification(models.Model):
    notif_text = models.CharField(max_length=225)
    date_submitted = models.DateTimeField()
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)


class Story(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    image = models.ImageField(default="fallback.png")
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.profile.user.username}'s story"

# hide event from someone
# search for close friends
# adding reply class for comments
