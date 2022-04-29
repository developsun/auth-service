import json

from rest_framework.authtoken.models import Token
from accounts.permissions import AnonymousUserOnlyPermission
from rest_framework import generics
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from accounts.api import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.throttling import UserRateThrottle
from main.utils import sendSMS
from rest_framework import status
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.db.models import Q
import redis



class OncePerDayUserThrottle(UserRateThrottle):
    rate = '100/day'


User = get_user_model()


class AuthTokenView(generics.GenericAPIView):
    """
    Endpoint to obtain access token  from email creds to perform actions that requires authorization
    """

    permission_classes = (AnonymousUserOnlyPermission,)
    serializer_class = serializers.AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.set(token.key, json.dumps({"name": user.full_name,
                          "email": user.email,
                          "phone_number": user.phone_number}))
        return Response({'key': token.key})


class MobileAuthTokenView(generics.GenericAPIView):
    """
    Endpoint to obtain access token from mobile creds to perform actions that requires authorization
    """

    permission_classes = (AnonymousUserOnlyPermission,)
    serializer_class = serializers.AuthTokenMobileSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        #Save data in redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.set(token.key, user.id)
        return Response({'key': token.key})


@api_view(['GET'])
@throttle_classes([OncePerDayUserThrottle])
@permission_classes([AnonymousUserOnlyPermission])
def reset_password(request):
    '''
    Parameters
    phone_number:GET [MANDATORY]
    '''

    phone_number = request.GET.get('phone_number')
    email = request.GET.get('email')
    if phone_number is None and email is None:
        return Response({"error": "Phone number or Email field cannot be blank."}, status=400)

    user = User.objects.filter(phone_number=phone_number).first() if phone_number is not None else User.objects.filter(email=email).first()
    if user is not None:
        user.reset_password()
        return Response({"status": "ok", "message": "SMS & E-Mail has been sent."})
    else:
        return Response({"status": "failed", "message": "This phone number / email does not exists."})


@api_view(['GET'])
def logout(request):
    """
    Logout API - Endpoint to delete token on API token based authentication
    Allowed only for authorized user
    """
    try:
        # Remove token from redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.delete(str(request.user.auth_token))

        request.user.auth_token.delete()
        return Response({"status": "ok", "message": "User token has been deactivated."}, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({"status": "failed", "message": "User token is invalid."}, status=401)


class UserMeEndpoint(generics.RetrieveAPIView, generics.GenericAPIView):
    """
    Endpoint returns one's profile for read
    Allowed only for authorized user
    """

    serializer_class = serializers.UserMeSerializer
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        self.serializer_class = serializers.UserMeSerializer
        return super().get(request, *args, **kwargs)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['full_name'] = getattr(user, 'full_name', '')
        token['email'] = getattr(user, 'email', '')
        # ...

        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AnonymousUserOnlyPermission,)
    serializer_class = serializers.RegisterSerializer


@api_view(['GET'])
@permission_classes([AnonymousUserOnlyPermission])
def request_mobile_verification(request):
    '''
        Parameters
        phone_number:GET [MANDATORY]
    '''

    phone_number = request.GET.get('phone_number')
    try:
        User.objects.filter(phone_number=phone_number).verify_id_details(email_verify=False)
        return Response({"status": "ok", "message": "Verification link will be sent shortly."}, status=status.HTTP_200_OK)
    except:
        return Response({"status": "failed", "message": "System has faced some error"}, status=500)


@api_view(['GET'])
@permission_classes([AnonymousUserOnlyPermission])
def request_email_verification(request):
    '''
        Parameters
        email:GET [MANDATORY]
    '''

    email = request.GET.get('email')
    try:
        User.objects.filter(email=email).verify_id_details(phone_verify=False)
        return Response({"status": "ok", "message": "Verification link will be sent shortly."}, status=status.HTTP_200_OK)
    except:
        return Response({"status": "failed", "message": "System has faced some error"}, status=500)