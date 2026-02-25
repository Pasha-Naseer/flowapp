import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.views import View
from .forms import *
from .models import User, OtpCode, Profile
from home.models import Category, Event, Friend, FriendItem, Story
from datetime import datetime, date, time, timedelta
from django.utils import timezone
from utils import send_otp_code
from django.db.models import Q


class UserLoginView(View):
    form = UserLoginForm

    def get(self, request):
        if request.user.is_authenticated:
            messages.error(request, 'شما قبلا وارد اکانت خود شده اید')
            return redirect('home:home')
        form = self.form
        return render(request, 'flowaccounts/login.html', {'form': form})

    def post(self, request):
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, "شما با موفقیت به حساب وارد شدید")
                return redirect("home:home")
            else:
                messages.error(request, "خطایی در حین ورود به حساب رخ داد")
                return redirect('flowaccounts:login')


def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "شما با موفقیت از حساب خارج شدید")
        return redirect("flowaccounts:login")
    else:
        messages.error(request, "برای خروج از حساب باید وارد آن شده باشید.")
        return redirect('flowaccounts:login')


class UserRegisterView(View):
    form_class = UserRegistrationForm

    def get(self, request):
        if request.user.is_authenticated:
            messages.error(request, "شما هنوز داخل اکانت خود هستید")
            return redirect("home:home")
        form = self.form_class
        return render(request, 'flowaccounts/register.html', {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            while OtpCode.objects.filter(phone_number=form.cleaned_data['phone_number']).exists():
                OtpCode.objects.get(phone_number=form.cleaned_data['phone_number']).delete()
            random_code = random.randint(1000, 9999)

            send_otp_code(form.cleaned_data['phone_number'], random_code)

            OtpCode.objects.create(phone_number=form.cleaned_data['phone_number'], code=random_code)
            request.session['user_registration_info'] = {
                'username': form.cleaned_data['my_username'],
                'phone_number': form.cleaned_data['phone_number'],
                'email': form.cleaned_data['my_email'],
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
                'password': form.cleaned_data['password'],
            }
            messages.success(request, 'کدی برای شما ارسال شد', 'success')
            return redirect('flowaccounts:verify_code')
        messages.success(request, "فرم خود را بازبینی کنید", 'success')
        return redirect('flowaccounts:register')


# is
class UserRegisterVerifyCodeView(View):
    form_class = VerifyCodeForm
    # what if someone comes here directly?

    def get(self, request):
        form = self.form_class
        return render(request, 'flowaccounts/verify.html', {'form': form})

    def post(self, request):
        scale = time(0, 3, 0, 0)
        duration = timedelta(hours=scale.hour, minutes=scale.minute, seconds=scale.second,
                             microseconds=scale.microsecond)
        for i in OtpCode.objects.all():
            if i.created + duration < timezone.now():
                i.delete()
        user_session = request.session['user_registration_info']
        code_instance = OtpCode.objects.get(phone_number=user_session['phone_number'])
        form = self.form_class(request.POST)
        if form.is_valid():
            if not code_instance.calculate_date() == datetime.now().date():
                messages.error(request, 'کد منقضی شد!', 'danger')
                return redirect('flowaccounts:register')
            substraction = datetime.combine(date.today(), datetime.now().time()) - datetime.combine(date.today(),
                                                                                                    code_instance.calculate_time())

            # print(datetime.now().time())
            # print(code_instance.calculate_time())
            # print(substraction)
            # print(duration)
            if substraction > duration:
                messages.error(request, 'کد منقضی شد!', 'danger')
                return redirect('flowaccounts:register')
            if User.objects.filter(username=user_session['username']).exists():
                messages.error(request, 'نام کاربری از قبل وجود دارد')
                return redirect('flowaccounts:register')
            if User.objects.filter(phone_number=user_session['phone_number']).exists():
                messages.error(request, 'شماره تلفن از قبل وجود دارد')
                return redirect('flowaccounts:register')
            if User.objects.filter(email=user_session['email']).exists():
                messages.error(request, 'ایمیل از قبل وجود دارد')
                return redirect('flowaccounts:register')
            cd = form.cleaned_data
            if cd['code'] == code_instance.code:
                User.objects.create_user(user_session['username'], user_session['phone_number'],
                                         user_session['email'], user_session['first_name'], user_session['last_name'],
                                         user_session['password'], )
                code_instance.delete()
                messages.success(request, 'کاربر با موفقیت ثبت شد', 'success')
                return redirect('flowaccounts:login')
            else:
                messages.error(request, "کد اشتباه!", 'danger')
                return redirect('flowaccounts:verify_code')
        return render(request, 'flowaccounts/register.html', {'form': form})


def user_update(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form = UserChangeFormUser(request.POST or None, instance=current_user)
        if user_form.is_valid():
            user_form.save()
            login(request, current_user)
            messages.success(request, 'کاربر آپدیت شد')
            return redirect("flowaccounts:update")
        return render(request, 'flowaccounts/update_user.html', {'user_form': user_form})
    else:
        messages.error(request, 'برای ورود به پیج باید وارد حساب شوید!')
        return redirect('home:home')


def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user
        # Did they fill the form?
        if request.method == 'POST':
            form = ChangePasswordForm(current_user, request.POST)
            # is the form valid
            if form.is_valid():
                form.save()
                messages.success(request, 'رمز شما آپدیت شد!')
                return redirect('flowaccounts:login')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                    return redirect('flowaccounts:update_password')
        else:
            form = ChangePasswordForm(current_user)
            return render(request, 'flowaccounts/update_password.html', {'form': form})
    else:
        messages.error(request, 'برای ورود به پیج باید وارد حساب شوید!')
        return redirect('home:home')


class UserProfileView(View):
    message = "برای دسترسی به این بخش باید وارد حساب کاربری شوید!"
    msg = "مشکلی پیش آمد، درصورت نکرار آن به پشتیبانی اطلاع دهید"

    def get(self, request, profile_id):
        if request.user.is_authenticated:


            profile = get_object_or_404(Profile, pk=profile_id)

            if request.user == profile.user:
                return redirect('flowaccounts:my_profile')

            user_story = Story.objects.filter(
                profile=profile,
                date_posted__gte=timezone.now() - timedelta(hours=24)
            ).first()

            friend, check = Friend.objects.get_or_create(user=request.user)
            try:
                friend_item = FriendItem.objects.get(friend=friend, user=profile.user)
            except(ValueError, FriendItem.DoesNotExist):
                status = "add to friends"
            else:
                status = "remove from friends"

            events = list(Event.objects.filter(promoter=profile.user))
            for event in events:
                friend, check = Friend.objects.get_or_create(user=event.promoter)
                if event.privacy == "PR":
                    try:
                        friend_item = FriendItem.objects.get(friend=friend, user=request.user)
                        # we need to check if we can del the var in the beginning
                    except (ValueError, FriendItem.DoesNotExist):
                        if request.user != event.promoter:  # checking if the promoter himself is viewing
                            events.remove(event)
                    else:
                        pass

            context = {
                "profile": profile,
                'status': status,
                'events': events,
                "user_story": user_story
            }
            return render(request, 'flowaccounts/profile.html', context)
        else:
            messages.error(request, self.message)
            return redirect('flowaccounts:login')

    def post(self, request, profile_id):
        if not request.user.is_authenticated:
            messages.error(request, self.message)
            return redirect('flowaccounts:login')

        profile = get_object_or_404(Profile, pk=profile_id)

        # Prevent adding yourself
        if request.user == profile.user:
            return redirect("flowaccounts:my_profile")

        action = request.POST.get("action")
        friend, _ = Friend.objects.get_or_create(user=request.user)

        if action == "add":
            FriendItem.objects.get_or_create(
                friend=friend,
                user=profile.user
            )

        elif action == "remove":
            FriendItem.objects.filter(
                friend=friend,
                user=profile.user
            ).delete()

        return redirect("flowaccounts:profile", profile_id=profile_id)

    # def post(self, request, profile_id):
    #     if request.user.is_authenticated:
    #         profile = get_object_or_404(Profile, pk=profile_id)
    #         if request.user == profile.user:
    #             return redirect("flowaccounts:my_profile")
    #         friend, already_there = Friend.objects.get_or_create(user=request.user)

            # if request.POST['status'] == "add to friends":
            #     try:
            #         friend_item = FriendItem.objects.get(friend=friend, user=request.user)
            #     except (ValueError, FriendItem.DoesNotExist):
            #         friend_item = FriendItem(friend=friend, user=profile.user)
            #         friend_item.save()
            #     else:
            #         messages.error(request, self.msg)
            #         return redirect("flowaccounts:profile", profile_id=profile_id)
            #
            # elif request.POST["status"] == "remove from friends":
            #     try:
            #         friend_item = FriendItem.objects.get(friend=friend, user=request.user)
            #     except (ValueError, FriendItem.DoesNotExist):
            #         messages.error(request, self.msg)
            #         return redirect("flowaccounts:profile", profile_id=profile_id)
            #     else:
            #         friend_item.delete()
            #         # do we need to display success messages?
        #
        #     friend_item = FriendItem(friend=friend, user=profile.user)
        #     # can add himself to close friend?
        #     # I will have a separate page for my_profile and force redirect
        #     friend_item.save()
        #     # add if add, del if del
        #     return redirect("flowaccounts:profile", profile_id=profile_id)
        # else:
        #     messages.error(request, self.message)
        #     return redirect('flowaccounts:login')


class ExploreView(View):
    form_class = ProfileExploreForm

    def get(self, request):
        # for now, we sort them by date, but later we need better algo
        explore_events = Event.objects.filter(privacy="event").order_by("-event_date")
        # we need to handle private events
        form = self.form_class()
        context = {
            'form': form,
            "explore_events": explore_events,
        }
        return render(request, 'flowaccounts/explore.html', context)

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            searched = cd['query']

            profiles = Profile.objects.filter(Q(bio__icontains=searched))
            users = User.objects.filter(Q(username__icontains=searched) | Q(first_name__icontains=searched) |
                                                   Q(last_name__icontains=searched))
            # very nice bug
            # if profile and one of the user params contain the same chars
            # the result shows the username twice

            for i in users:
                profiles = list(profiles) + list(Profile.objects.filter(user=i))

            profiles = list(set(profiles))  # and this is how we fix it
            categories = Category.objects.filter(Q(name__icontains=searched))

            events = Event.objects.filter(Q(name__icontains=searched) | Q(description__icontains=searched), privacy="PU")
            if request.user.is_authenticated:
                events = list(Event.objects.filter(Q(name__icontains=searched) | Q(description__icontains=searched)))
                for event in events:
                    friend, check = Friend.objects.get_or_create(user=event.promoter)
                    if event.privacy == "PR":
                        try:
                            friend_item = FriendItem.objects.get(friend=friend, user=request.user)
                            # we need to check if we can del the var in the beginning
                        except (ValueError, FriendItem.DoesNotExist):
                            if request.user != event.promoter:  # checking if the promoter himself is viewing
                                events.remove(event)
                        else:
                            pass
            context = {
                'profiles': profiles,
                'categories': categories,
                'events': events,
                'form': form,
            }
            return render(request, 'flowaccounts/explore.html', context)
        return self.get(request)

# class MyProfileView(View):
#     message = "برای دسترسی به این بخش باید وارد حساب کاربری شوید!"
#     form_class = ProfileUpdateForm
#
#     def get(self, request):
#         if request.user.is_authenticated:
#             profile = get_object_or_404(Profile, user=request.user)
#             form = self.form_class(instance=profile)
#             my_events = Event.objects.filter(promoter=request.user).order_by("-event_date")
#             context = {
#                 "my_events": my_events,
#                 "profile": profile,
#                 "form": form,
#             }
#             return render(request, "flowaccounts/my_profile.html", context)
#         else:
#             messages.error(request, self.message)
#             return redirect('flowaccounts:login')
#
#     def post(self, request):
#         if request.user.is_authenticated:
#             form = self.form_class(request.POST)
#             if form.is_valid():
#                 cd = form.cleaned_data
#                 profile = get_object_or_404(Profile, user=request.user)
#                 profile.user = request.user
#                 profile.profile_pic = request.FILES['profile_pic']
#                 profile.first_name = cd['first_name']
#                 profile.last_name = cd['last_name']
#                 profile.bio = cd['bio']
#                 profile.save()
#                 # form.save()
#                 context = {
#                     # "profile": profile,
#                     "form": form,
#                 }
#                 return redirect('flowaccounts:my_profile')
#             messages.error(request, 'فرم را پر کنید!')
#             return redirect('flowaccounts:my_profile')
#         else:
#             messages.error(request, self.message)
#             return redirect('flowaccounts:login')




class MyProfileView(View):
    message = "برای دسترسی به این بخش باید وارد حساب کاربری شوید!"
    form_class = ProfileUpdateForm

    def get(self, request):
        if request.user.is_authenticated:
            profile = get_object_or_404(Profile, user=request.user)
            form = self.form_class(instance=profile, user=request.user)
            my_events = Event.objects.filter(promoter=request.user).order_by("-event_date")
            return render(request, "flowaccounts/my_profile.html", {
                "my_events": my_events,
                "profile": profile,
                "form": form,
            })
        messages.error(request, self.message)
        return redirect('flowaccounts:login')

    def post(self, request):
        if request.user.is_authenticated:
            profile = get_object_or_404(Profile, user=request.user)
            form = self.form_class(request.POST, request.FILES, instance=profile, user=request.user)
            if form.is_valid():
                if User.objects.filter(username=form.cleaned_data['username']).exists():
                    messages.error(request, "نام کاربری از قبل وجود دارد")
                    return redirect('flowaccounts:my_profile')
                form.save()
                messages.success(request, "اطلاعات پروفایل شما با موفقیت بروزرسانی شد!")
                return redirect('flowaccounts:my_profile')
            messages.error(request, "فرم را به درستی پر کنید!")
            return redirect('flowaccounts:my_profile')
        messages.error(request, self.message)
        return redirect('flowaccounts:login')
