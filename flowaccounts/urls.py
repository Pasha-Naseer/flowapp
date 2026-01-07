from django.urls import path
from . import views

app_name = 'flowaccounts'
urlpatterns = [
    path("login/", views.UserLoginView.as_view(), name='login'),
    path("logout/", views.user_logout, name='logout'),
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('verify/', views.UserRegisterVerifyCodeView.as_view(), name='verify_code'),
    path('update/', views.user_update, name='update'),
    path('update_password', views.update_password, name='update_password'),
]