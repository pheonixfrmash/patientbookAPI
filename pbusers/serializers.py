from rest_framework import serializers
# from django.conf import settings
from pbusers.models import PbUser
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth.tokens import default_token_generator
from templated_mail.mail import BaseEmailMessage
from djoser import utils
from djoser.conf import settings


class RegistrationSerializer(serializers.ModelSerializer):
    
    password2 = serializers.CharField(style={'input_type':'password'}, write_only=True)
    
    class Meta:
        model = PbUser
        fields= ['email','password','password2','date_of_birth','gender','first_name','last_name',]
        extra_kwargs ={
            
            'password': {'write_only' : True},
        }
    def save(self):
        User = PbUser(
            email=self.validated_data['email'],
            date_of_birth=self.validated_data['date_of_birth'],
            first_name=self.validated_data['first_name'],
            last_name=self.validated_data['last_name'],
            gender=self.validated_data['gender'],
             )
        password = self.validated_data['password']
        password2 =self.validated_data['password2']
        
        if password!=password2:
            raise serializers.DjangoValidationError({'password': 'Passwords must match'})
        User.set_password(password)
        User.save()
        return User
    
        

class PbUserPropertiesSerializer(serializers.ModelSerializer):
    
	class Meta:
		model = PbUser
		fields = ['pk', 'email', 'date_of_birth','gender',]



class ChangePasswordSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(style={'input_type':'password'}, write_only=True)
    confirm_password = serializers.CharField(style={'input_type':'password'}, write_only=True)
    class Meta:
        model = PbUser
        fields = ['pk','email','first_name','date_of_birth','gender','last_name','password','new_password','confirm_password']
        read_only_fields = ['email','first_name','date_of_birth','gender','last_name',]

        extra_kwargs ={
            'password': {'write_only' : True},
        }
        
    def partial_update(self, instance, validated_data):
        instance.password = self.validated_data['new_password']
        instance.set_password(instance.password)
        instance.save()
        return instance

class ObtainExpiringAuthToken(ObtainAuthToken):
    def post(self, request):
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid():
            token, created =  Token.objects.get_or_create(user=serializer.object['user'])

            if not created:
                # update the created time of the token to keep it valid
                token.created = datetime.datetime.utcnow().replace(tzinfo=utc)
                token.save()

            return Response({'token': token.key})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserCreatePasswordRetypeSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(style={'input_type':'password'}, write_only=True)
    confirm_password = serializers.CharField(style={'input_type':'password'}, write_only=True)
    class Meta:
        model = PbUser
        fields = ['new_password','confirm_password']
        
    default_error_messages = {
        "password_mismatch": "Both Passwords must be same"
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["new_password"] = serializers.CharField(
            style={"input_type": "password"}
        )

    def validate(self, attrs):
        self.fields.pop("new_password", None)
        re_password = attrs.pop("new_password")
        attrs = super().validate(attrs)
        if attrs["confirm_password"] == re_password:
            return attrs
        else:
            self.fail("password_mismatch")
            
    def partial_update(self, instance, validated_data):
        instance.password = self.validated_data['confirm_password']
        instance.set_password(instance.password)
        instance.save()
        return instance

class PasswordResetEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PbUser
        fields = ['email']
        
    default_error_messages = {
        "email": "Email invalid"
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"] = serializers.EmailField(style={"input_type": "text"})

    
    def get_context_data(self):
        # PasswordResetEmail can be deleted
        context = super().get_context_data()
        print (context)
        print("\n")
        user = context.get("user")
        print(user)
        print("\n")
        context["uid"] = utils.encode_uid(user.pk)
        context["token"] = default_token_generator.make_token(user)
        context["url"] = settings.PASSWORD_RESET_CONFIRM_URL.format(**context)
        return context
    


class PasswordChangedConfirmationEmailSerializer(BaseEmailMessage):
    template_name = "email/password_changed_confirmation.html"