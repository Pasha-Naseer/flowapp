from django.contrib.auth.forms import SetPasswordForm
from django import forms
from .models import User, Profile
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.validators import MinLengthValidator


class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(label='password', widget=forms.PasswordInput)


class ChangePasswordForm(SetPasswordForm):
    class Meta:
        model = User
        fields = ['new_password1', 'new_password2']

    def __init__(self, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

        self.fields['new_password1'].widget.attrs['class'] = 'form-control'
        self.fields['new_password1'].widget.attrs['placeholder'] = 'رمز'
        self.fields['new_password1'].label = ''
        self.fields['new_password1'].help_text = '<ul class="form-text text-muted small"><li>رمزتان نباید با سایر اطلاعات شما مشابه باشد</li><li>رمزتان باید حداقل دارای 8 کاراکتر باشد</li><li>رمزتان نباید رمز رایجی باشد</li><li>رمزتان نباید تماما عددی باشد</li></ul>'

        self.fields['new_password2'].widget.attrs['class'] = 'form-control'
        self.fields['new_password2'].widget.attrs['placeholder'] = 'تکرار رمز'
        self.fields['new_password2'].label = ''
        self.fields['new_password2'].help_text = '<span class="form-text text-muted"><small>رمز خود را دوباره وارد کنید</small></span>'


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='confirm password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'phone_number', 'email')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password1'] and cd['password2'] and cd['password1'] != cd['password2']:
            raise ValidationError("Passwords don't match")
        return cd['password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(help_text='You can change your password using this form...<a href=\"../password/\">this form</a>')

    class Meta:
        model = User
        fields = ('username', 'phone_number', 'email', 'first_name', 'last_name', 'password', 'last_login')


class UserChangeFormUser(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'phone_number', 'email', 'first_name', 'last_name',)

    def __init__(self, *args, **kwargs):
         super(UserChangeFormUser, self).__init__(*args, **kwargs)

         self.fields['username'].widget.attrs['class'] = 'form-control'
         self.fields['username'].widget.attrs['placeholder'] = 'نام کاربری'
         self.fields['username'].label = 'نام کاربری'

         self.fields['phone_number'].widget.attrs['class'] = 'form-control'
         self.fields['phone_number'].widget.attrs['placeholder'] = 'شماره تلفن'
         self.fields['phone_number'].label = 'شماره تلفن'

         self.fields['email'].widget.attrs['class'] = 'form-control'
         self.fields['email'].widget.attrs['placeholder'] = 'ایمیل'
         self.fields['email'].label = 'ایمیل'

         self.fields['first_name'].widget.attrs['class'] = 'form-control'
         self.fields['first_name'].widget.attrs['placeholder'] = 'نام'
         self.fields['first_name'].label = 'نام'

         self.fields['last_name'].widget.attrs['class'] = 'form-control'
         self.fields['last_name'].widget.attrs['placeholder'] = 'نام خانوادگی'
         self.fields['last_name'].label = 'نام خانوادگی'


class UserRegistrationForm(forms.Form):
    my_username = forms.CharField(max_length=225, label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'نام کاربری'}), required=True)
    phone_number = forms.CharField(max_length=11, label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'شماره تماس'}), required=True)
    my_email = forms.EmailField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'ایمیل'}), required=True)
    first_name = forms.CharField(max_length=225)
    last_name = forms.CharField(max_length=225)

    password = forms.CharField(widget=forms.PasswordInput, validators=[MinLengthValidator(8)])

    def __init__(self, *args, **kwargs):

        super(UserRegistrationForm, self).__init__(*args, **kwargs)

        self.fields['my_email'].widget.attrs['class'] = 'form-control'
        self.fields['my_email'].widget.attrs['placeholder'] = 'ایمیل'
        self.fields['my_email'].label = ''
        self.fields['my_email'].help_text = '<span class="form-text text-muted"><small></small></span>'

        self.fields['first_name'].widget.attrs['class'] = 'form-control'
        self.fields['first_name'].widget.attrs['placeholder'] = 'نام'
        self.fields['first_name'].label = ''
        self.fields['first_name'].help_text = '<span class="form-text text-muted"><small></small></span>'

        self.fields['last_name'].widget.attrs['class'] = 'form-control'
        self.fields['last_name'].widget.attrs['placeholder'] = 'نام خانوادگی'
        self.fields['last_name'].label = ''
        self.fields['last_name'].help_text = '<span class="form-text text-muted"><small></small></span>'

        self.fields['password'].widget.attrs['class'] = 'form-control'
        self.fields['password'].widget.attrs['placeholder'] = 'رمز'

        self.fields['password'].label = ''
        self.fields['password'].help_text = '<ul class="form-text text-muted small"><li>رمزتان نباید با سایر اطلاعات شما مشابه باشد</li><li>رمزتان باید حداقل دارای 8 کاراکتر باشد</li><li>رمزتان نباید رمز رایجی باشد</li><li>رمزتان نباید تماما عددی باشد</li></ul>'

    def clean_email(self):
        email = self.cleaned_data['email']
        user = User.objects.filter(email=email).exists()
        if user:
            raise ValidationError('This Email Already Exists')

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        user = User.objects.filter(phone_number=phone).exists()
        if user:
            raise ValidationError("Phone Number Already Exists")

    def clean_username(self):
        username = self.cleaned_data['username']
        user = User.objects.filter(username=username).exists()
        if user:
            raise ValidationError("Username Already Exists")


class VerifyCodeForm(forms.Form):
    code = forms.IntegerField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Verify Code'}), required=True)


# class ProfileExploreForm(forms.Form):
#     username = forms.CharField(max_length=225, label="explore", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'profile, category or event'}), required=True)

class ProfileExploreForm(forms.Form):
    query = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Search people, events, categories...',
            'class': 'search-input'
        })
    )

from django import forms
from django.contrib.auth.models import User
from .models import Profile


class ProfileUpdateForm(forms.ModelForm):
    # Extra field for username from User model
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Username'})
    )

    class Meta:
        model = Profile
        fields = ("profile_pic", "first_name", "last_name", "bio")
        widgets = {
            'profile_pic': forms.ClearableFileInput(attrs={'class': 'custom-file-input'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
            'bio': forms.Textarea(attrs={'placeholder': 'Bio', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        # Pass the user instance when initializing the form
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Pre-fill the username field if user exists
        if self.user:
            self.fields['username'].initial = self.user.username

    def save(self, commit=True):
        profile = super().save(commit=False)

        # Update the username in the related User model
        if self.user:
            self.user.username = self.cleaned_data['username']
            if commit:
                self.user.save()

        if commit:
            profile.save()
        return profile

