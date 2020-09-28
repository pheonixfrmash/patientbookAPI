from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import render,redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import login,authenticate , logout
from rest_framework_jwt import views as jwt_views
from django.conf import settings
import requests
from pbusers.models import PbUser
from pbusers.serializers import (RegistrationSerializer,PbUserPropertiesSerializer,ChangePasswordSerializer,UserCreatePasswordRetypeSerializer,PasswordResetEmailSerializer,PasswordChangedConfirmationEmailSerializer)
from rest_framework.authtoken.models import Token


@api_view(['POST',])
def registration_view(request):
    if request.method == 'POST':
        serializer = RegistrationSerializer(data=request.data)
        data={}
        if serializer.is_valid():
            PbUser = serializer.save()
            data['response'] = "successfully registered user"
            data['email'] = PbUser.email
        else:
            data =serializer.errors
        return Response(data)

@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def logout_view(request):
    try:
        logout(request)
        return Response({"data": ("Successfully logged out.")},status=status.HTTP_200_OK)
    except (AttributeError, request.user.DoesNotExist):
        pass
        return Response({"data": ("Unable to log out as user does not exist.")},status=status.HTTP_200_OK)

@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def PbUser_properties_view(request):
    try:
        PbUser=request.user
    except PbUser.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = PbUserPropertiesSerializer(PbUser)
        return Response(serializer.data)


@api_view(['PUT',])
@permission_classes((IsAuthenticated,))
def update_PbUser_view(request):
    try:
        PbUser=request.user
    except PbUser.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'PUT':
        serializer = PbUserPropertiesSerializer(PbUser,data=request.data)
        data ={}
        if serializer.is_valid():
            serializer.save()
            data['response'] = " PbUser updated succesfully"
            return Response(data = data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['PUT',])
@permission_classes((IsAuthenticated,))
def update_password_view(request):
    try:
        PbUser=request.user
    except PbUser.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'PUT':
        serializer = ChangePasswordSerializer(PbUser,data=request.data)
        data ={}
        if serializer.is_valid():
            User = serializer.partial_update(PbUser,(request.data))
            data['response'] = " PbUser updated succesfully"
            return Response(data = data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST',])
def auth_token_view(request):
    try:
        PbUser=request.user
    except PbUser.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'POST':
        serializer = ObtainExpiringAuthToken(PbUser.get_token())
        data ={}
        if serializer.is_valid():
            PbUser = serializer.post(PbUser.get_token())
            data['response'] = " Token authentication succesful"
            return Response(data = data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'],)
# @permission_classes((IsAuthenticated,))
def reset_password(request):
        # serializer = self.get_serializer(data=request.data)
        serializer = UserCreatePasswordRetypeSerializer(data=request.data)
        data ={}
        if serializer.is_valid():
            user = request.user
            User = serializer.partial_update(user,(request.data))
            if user:
                context = {"user": user}
                to = [user]
                # settings.EMAIL.password_reset(self.request, context).send(to)
                data['response'] = " Password reset succesful"
                return Response(data = data)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
@api_view(['POST'],)
def request_password(request):
        serializer = PasswordResetEmailSerializer(data=request.data)
        data2 ={}
        if serializer.is_valid():
            user = request.data 
            user_details = PbUserPropertiesSerializer(user.get('email')) 
            if user_details:
                context = {"user": user_details}
                to = user.get('email')
                headers = {
                      'api_key': 'db29e9ccd68726555b0c469cf2dcf670',
                      'content-type': 'application/json',
                        }
                
                # data = '{"personalizations":[{"recipient":"glowdermadeveloper@gmail.com"}],"from":{"fromEmail":"glowdermadeveloper@pepisandbox.com","fromName":"glowdermadeveloper"},"subject":"Password Reset Details","content":"Hi, Please find the password reset link below"}'
                data = '{"personalizations":[{"recipient":"glowdermadeveloper@gmail.com","attributes":{"NAME":"Mike"},"from":{"fromEmail":"glowdermadeveloper@pepisandbox.com","fromName":"glowdermadeveloper"},"subject":"Welcome to Pepipost","content":"Hi [%NAME%], this is my first trial mail","templateId":20521,"settings":{"footer":1,"clicktrack":0,"opentrack":1,"unsubscribe":0}}'

                response = requests.post('https://api.pepipost.com/v2/sendEmail', headers=headers, data=data)
                print(response.headers,response.elapsed,response.status_code,response.history,response.reason)
                if(response.status_code==202):
                 data2['response'] = " Password reset Mail sent succesful"
                 return Response(data = data2)
        return Response(status=status.HTTP_204_NO_CONTENT)