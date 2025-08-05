from django.urls import path
from authentication import views

urlpatterns = [
    path('', views.UserAPIView.as_view(), name='user'),
    path('/login', views.LoginAPIView.as_view(), name='login'),
    # path('/token', views.RefreshTokenAPIView.as_view(), name='refresh_token'),
    path('/register', views.RegisterAPIView.as_view(), name='register'),
    # path('/verify', views.VerifyPhoneNumberAPIView.as_view(), name='verify'),
    # path('/forget', views.ForgotPasswordView.as_view(), name='forget_pass_request'),
    # path('/forget/<str:key>', views.ForgotVerifyAPIView.as_view(), name='forget_pass_verify'),
    # path('/user/<str:username>', views.GetUserInfoView.as_view(), name='get-user-with-username'),

]