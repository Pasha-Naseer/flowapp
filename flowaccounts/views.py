import random
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.views import View
from .forms import UserRegistrationForm, VerifyCodeForm,  UserChangeFormUser, UserLoginForm, ChangePasswordForm
from .models import User
from datetime import datetime, date, time, timedelta
from django.utils import timezone


class UserLoginView(View):
    form = UserLoginForm

    def get(self, request):
        if request.user.is_authenticated:
            messages.error(request, 'شما قبلا وارد حساب شده اید')
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
        return redirect('flowaccounts:index')


