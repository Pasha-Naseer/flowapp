from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from .models import Category, Event, Comment, Membership, Notification, Friend, FriendItem, Story
from .forms import EventCreateForm, CommentForm, StoryForm
from django.utils import timezone
from django.contrib import messages
import datetime
from datetime import timedelta

class HomeView(View):
    form_class = StoryForm
    def get(self, request):
        form = self.form_class
        categories = Category.objects.all()
        stories = []
        user_story = None
        if request.user.is_authenticated:
            friend, check = Friend.objects.get_or_create(user=request.user)
            friends = FriendItem.objects.filter(friend=friend)

            all_friends = list(FriendItem.objects.all())
            for friend_item in all_friends:
                try:
                    if not (friend_item.user.profile.story.date_posted >= timezone.now() - datetime.timedelta(days=1)):
                        friend_item.user.profile.story.delete()
                except (ValueError, Story.DoesNotExist):
                    pass

            for f in friends:
                try:
                    story = f.user.profile.story
                except (ValueError, Story.DoesNotExist):
                    pass
                else:
                    stories.append(story)

            user_story = Story.objects.filter(
                profile=request.user.profile,
                date_posted__gte=timezone.now() - timedelta(hours=24)
            ).first()
        # show "in order to see stories --> login"
        context = {
            'form': form,
            "categories": categories,
            "stories": stories,
            'user_story': user_story,
        }
        return render(request, 'home/home.html', context)

    def post(self, request):
        if not request.user.is_authenticated:
            messages.error(request, "برای پست استوری باید حتما ثبت نام کنید")
            return redirect('flowaccounts:register')

        action = request.POST.get('action')

        if action == 'post_story':
            # Handle uploading a new story
            if 'image' in request.FILES:
                story = Story(profile=request.user.profile, image=request.FILES['image'])
                story.save()
                messages.success(request, "استوری پست شد")
            else:
                messages.error(request, "لطفا یک تصویر انتخاب کنید")

        elif action == 'delete_story':
            # Handle deleting a story
            story_id = request.POST.get('story_id')
            try:
                story = Story.objects.get(id=story_id, profile=request.user.profile)
                story.delete()
                messages.success(request, "استوری حذف شد")
            except Story.DoesNotExist:
                messages.error(request, "استوری یافت نشد یا شما اجازه حذف ندارید")

        return redirect('home:home')


class CategoryDetailView(View):

    def get(self, request, category_id):
        category = get_object_or_404(Category, pk=category_id)
        event_list = list(Event.objects.filter(category=category))

        for event in event_list:
            friend, check = Friend.objects.get_or_create(user=event.promoter)
            if event.privacy == "PR":
                try:
                    if request.user.is_authenticated:
                        friend_item = FriendItem.objects.get(friend=friend, user=request.user)
                    # we need to check if we can del the var in the beginning
                except (ValueError, FriendItem.DoesNotExist):
                    if request.user != event.promoter:  # checking if the promoter himself is viewing
                        event_list.remove(event)
                else:
                    pass

        context = {
            'category': category,
            'event_list': event_list,
        }
        return render(request, 'home/category_detail.html', context)

    def post(self, request):
        pass


class EventCreateView(View):
    form_class = EventCreateForm

    def get(self, request, category_id):
        category = get_object_or_404(Category, pk=category_id)
        form = self.form_class
        context = {
            'category': category,
            'form': form,
        }
        return render(request, 'home/create_event.html', context)

    def post(self, request, category_id):
        category = get_object_or_404(Category, pk=category_id)
        form = self.form_class(request.POST)
        if form.is_valid():
            # image form does not submit
            # we need to check time and date before submitting
            cd = form.cleaned_data
            start_hour = int(cd["start_hour"].hour)
            end_hour = int(cd["end_hour"].hour)
            start_minute = int(cd["start_hour"].minute)
            end_minute = int(cd["end_hour"].minute)
            message = 'در زمانبندی خود دقت کنید'
            if start_hour == end_hour:
                if start_minute + 10 >= end_minute:
                    messages.error(request, message)
                    return redirect('home:create_event', category_id=category_id)
            elif start_hour > end_hour:
                messages.error(request, message)
                return redirect('home:create_event', category_id=category_id)
            # must be checked
            if cd['event_date'] <= datetime.datetime.now().date():
                if cd['start_hour'] <= timezone.now().time():
                    messages.error(request, message)
                    return redirect('home:create_event', category_id=category_id)
                    # a bit concerned about this 00:00
                    # return get

            event = Event(name= cd['name'], promoter=request.user, image=request.FILES['image'], description=cd['description'],
                          start_hour=cd['start_hour'], end_hour=cd['end_hour'], event_date=cd['event_date'],
                          privacy=cd['privacy'], category=category)
            event.save()
            return redirect('home:category_detail', category_id=category_id)

        # return to get


# show the list of subscribers too
class EventDetailView(View):
    form_class = CommentForm

    def get(self, request, category_id, event_id):
        form = self.form_class
        category = get_object_or_404(Category, pk=category_id)
        event = get_object_or_404(Event, category=category, pk=event_id)
        friend, check = Friend.objects.get_or_create(user=event.promoter)
        if event.privacy == "PR":
            try:
                friend_item = FriendItem.objects.get(friend=friend, user=request.user)
                # we need to check if we can del the var in the beginning
            except Exception:
                    messages.error(request, "وارد اکانت شوید")
                    return redirect('flowaccounts:login')
            else:
                pass

        comments = Comment.objects.filter(
            event=event,
            confirmed=True,
            parent__isnull=True
        ).select_related('profile__user').prefetch_related('replies')
        try:
            membership_status = Membership.objects.get(event=event, profile=request.user.profile, to_whom=event.promoter.profile)
        except (ValueError, Membership.DoesNotExist, Exception):  # check this from polls
            status = "request membership"
        else:
            if membership_status.accepted == False:
                status = "requested"
            else:
                status = "cancel membership"
        context = {
            'category': category,
            'event': event,
            'form': form,
            'comments': comments,
            'status': status,
        }
        return render(request, 'home/event_detail.html', context)

    def post(self, request, category_id, event_id):
        form = self.form_class(request.POST)

        if form.is_valid():
            if request.user.is_authenticated:

                category = get_object_or_404(Category, pk=category_id)
                event = get_object_or_404(Event, category=category, pk=event_id)

                parent_id = request.POST.get("parent_id")
                parent = None

                if parent_id:
                    parent = Comment.objects.get(id=parent_id)

                comment = Comment.objects.create(
                    profile=request.user.profile,
                    text=form.cleaned_data['text'],
                    event=event,
                    parent=parent,
                    confirmed=True
                )

                Notification.objects.create(
                    profile=event.promoter.profile,
                    notif_text=f"{request.user.username} commented on {event.name}!",
                    date_submitted=datetime.datetime.now()
                )

                messages.success(request, "کامنت شما ثبت شد")
                return redirect('home:event_detail', category_id=category_id, event_id=event_id)

            else:
                messages.error(request, 'برای ثبت کامنت باید وارد حساب شوید')
                return redirect("flowaccounts:login")
            # for the owner it should show a button to delete the comment


class EventRequestView(View):
    msg = "مشکلی پیش آمد، درصورت نکرار آن به پشتیبانی اطلاع دهید"

    def get(self, request):
        pass

    def post(self, request, category_id, event_id):
        if request.user.is_authenticated:
            category = get_object_or_404(Category, pk=category_id)
            event = get_object_or_404(Event, category=category, pk=event_id)
            profile = request.user.profile
            if profile == event.promoter.profile:
                messages.error(request, "پروموتر ایونت و درخواست دهند یکی است!")
                return redirect("home:event_detail", event_id=event_id, category_id=category_id)
            action = request.POST["action"]
            if action == "request":
                try:
                     membership_req = Membership.objects.get(event=event, profile=profile,
                                                             to_whom=event.promoter.profile)
                except (ValueError, Membership.DoesNotExist):
                    membership_req = Membership(event=event, profile=profile, to_whom=event.promoter.profile)
                    membership_req.save()
                    messages.success(request, "درخواست با موفقیت ثبت شد")
                    return redirect("home:event_detail", category_id=category_id, event_id=event_id)
                else:
                    messages.error(request, self.msg)
                    return redirect("home:event_detail", category_id=category_id, event_id=event_id)

            elif action == "cancel_request":
                try:
                    membership = Membership.objects.get(event=event, profile=profile, to_whom=event.promoter.profile,
                                                        accepted=False)
                except (ValueError, Membership.DoesNotExist):
                    messages.error(request, self.msg)
                    return redirect("home:event_detail", category_id=category_id, event_id=event_id)
                else:
                    membership.delete()
                    messages.success(request, "درخواست با موفقیت ثبت شد")
                    return redirect("home:event_detail", category_id=category_id, event_id=event_id)

            elif action == "cancel_membership":
                try:
                    membership = Membership.objects.get(event=event, profile=profile, to_whom=event.promoter.profile,
                                                        accepted=True)
                except (ValueError, Membership.DoesNotExist):
                    messages.error(request, self.msg)
                    return redirect("home:event_detail", category_id=category_id, event_id=event_id)
                else:
                    membership.delete()
                    messages.success(request, "درخواست با موفقیت ثبت شد")
                    return redirect("home:event_detail", category_id=category_id, event_id=event_id)
            else:
                 messages.error(request, self.msg)
                 return redirect("home:event_detail", category_id=category_id, event_id=event_id)
            #     # Maybe in the future we send hacking warnings to the server!

            # membership_req = Membership(event=event, profile=profile, to_whom=event.promoter.profile)
            # membership_req.save()
            # messages.success(request, "درخواست با موفقیت ثبت شد")
            # return redirect("home:event_detail", category_id=category_id, event_id=event_id)
        messages.error(request, "برای ثبت درخواست باید وارد حساب کاربری شوید!")
        return redirect('flowaccounts:login')


class NotificationsView(View):
    def get(self, request):
        if request.user.is_authenticated:
            # requests
            # comments
            membership_reqs = Membership.objects.filter(to_whom=request.user.profile, accepted=False)
            notifs = Notification.objects.filter(profile=request.user.profile).order_by('-date_submitted')
            # there must be an expiration time for the comments to be displayed
            context = {
                'membership_reqs': membership_reqs,
                'notifs': notifs,
            }
            return render(request, 'home/notifications.html', context)
        # one can't req his own event
        messages.error(request, "برای بازدید از نوتیف ها باید وارد حساب کاربری شوید!")
        return redirect('flowaccounts:login')
        # can I add comment to notifs using signals?

    def post(self, request):
        if request.user.is_authenticated:
            # print(request.POST["action"])
            action = request.POST['action']
            membership = get_object_or_404(Membership, pk=request.POST["request_id"])
            # print(membership)
            event = membership.event
            if action == "accept":
                membership.accepted = True
                event.participants.add(membership.profile.user)
                membership.save()
                event.save()
            if action == "reject":
                membership.delete()
            return redirect("home:notifications")
        messages.error(request, "برای بازدید از نوتیف ها باید وارد حساب کاربری شوید!")
        return redirect('flowaccounts:login')

    # def post(self, request):
    #     # if accept, accepted=True
    #     # if reject, delete req
    #     # else should be handled as well
    #     pass
    #

# class MyEventsView(View):
#     def get(self, request):
#         if request.user.is_authenticated:
#             events = Event.objects.filter(promoter=request.user).order_by("-event_date")
#             context = {
#                 "events": events
#             }
#             return render(request, "home/my_events.html", context)
#
#         messages.error(request, "برای دسترسی به این بخش باید وارد اکانت شوید")
#         return redirect("home:home")
#
#     def post(self, request):
#         pass
