from django.urls import path
from . import views

urlpatterns = [
    path('authorize/', views.InputPhoneView.as_view(), name='authorize'),
    path('input_code/', views.VerifyCodeView.as_view(), name='verify_code'),
    path('profile/', views.ProfileView.as_view(), name='profile'),

]
