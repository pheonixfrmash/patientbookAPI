from django.urls import path,include
from pbusers.views import (
    registration_view,
    update_PbUser_view,
    PbUser_properties_view,
    logout_view,
    update_password_view,
    auth_token_view,
    reset_password,
    request_password,
)
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_jwt import views as jwt_views

urlpatterns = [
    path('register/',registration_view, name='register'),
    path('update_password/',update_password_view, name='update_password'),
    path('reset_password/',reset_password, name='reset_password'),
    path('login/',jwt_views.ObtainJSONWebToken.as_view(), name='login'),
    path('logout/',logout_view, name='logout'),
    path('properties/',PbUser_properties_view, name='properties'),
    path('properties/update',update_PbUser_view, name='update'),
    path('token/',auth_token_view, name='token'), 
    path('user/login/refresh' ,jwt_views.RefreshJSONWebToken.as_view(), name='user-login-refresh'),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('users/', include('djoser.urls.jwt')),
    path('request_password/',request_password,name='request_password'),
]