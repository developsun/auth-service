from django.urls import path
from accounts.api import endpoints
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    path('token/email/', endpoints.AuthTokenView.as_view(), name='obtain_token'),
    path('token/mobile/', endpoints.MobileAuthTokenView.as_view(), name='mobile_token'),
    path('me/', endpoints.UserMeEndpoint.as_view(), name='fetch_me'),
    path('jwt/create/', endpoints.MyTokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('jwt/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('reset_password/', endpoints.reset_password, name='reset_password'),
    path('logout/', endpoints.logout, name='logout'),
    path('register/', endpoints.RegisterView.as_view(), name='register'),
    path('verify/mobile/', endpoints.request_mobile_verification, name='request_mobile_verification'),
    path('verify/email/', endpoints.request_email_verification, name='request_email_verification'),
]
