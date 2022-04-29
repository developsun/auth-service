from django.contrib.auth import authenticate
from rest_framework import serializers, exceptions
from django.contrib.auth import get_user_model

from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)

            if user:
                if not user.is_active:
                    msg = 'User account is disabled.'
                    raise exceptions.ValidationError(msg)
                if not user.is_email_verified:
                    msg = 'Email Address is not verified.'
                    raise exceptions.ValidationError(msg)
                if not user.is_phone_number_verified:
                    msg = 'Phone Number is not verified.'
                    raise exceptions.ValidationError(msg)
            else:
                msg = 'The password or email you entered is incorrect. ' 'Try again, or choose another login option.'
                raise exceptions.ValidationError(msg)
        else:
            msg = 'Must include "email" and "password".'
            raise exceptions.ValidationError(msg)

        data['user'] = user
        return data


class AuthTokenMobileSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, data):
        phone_number = data.get('phone_number')
        password = data.get('password')

        if phone_number and password:
            get_email = User.objects.filter(phone_number=phone_number).first()
            user = authenticate(email=get_email, password=password)

            if user:
                if not user.is_active:
                    msg = 'User account is disabled.'
                    raise exceptions.ValidationError(msg)
                if not user.is_email_verified:
                    msg = 'Email Address is not verified.'
                    raise exceptions.ValidationError(msg)
                if not user.is_phone_number_verified:
                    msg = 'Phone Number is not verified.'
                    raise exceptions.ValidationError(msg)
            else:
                msg = 'The password or email you entered is incorrect. ' 'Try again, or choose another login option.'
                raise exceptions.ValidationError(msg)
        else:
            msg = 'Must include "phone number" and "password".'
            raise exceptions.ValidationError(msg)

        data['user'] = user
        return data

class UserMeSerializer(serializers.ModelSerializer):
    """
    Serializer to represent current user
    """

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'date_of_birth','phone_number' ,'gender', 'avatar', 'email']
        depth = 2


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer to represent user to be added
    """

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'gender', 'avatar', 'date_of_birth']
        depth = 1


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email','country', 'phone_number', 'first_name', 'last_name', 'password', 'password2')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        if len(attrs['phone_number']) != 10 and attrs['country'] == 'IN':
            raise serializers.ValidationError({"phone_number": "Phone number field cannot be greater than 10."})
        if User.objects.filter(email=attrs['email'], is_email_verified=True, is_phone_number_verified=True):
            raise serializers.ValidationError({"email_address": "An user with this email address already exists."})
        if User.objects.filter(phone_number=attrs['phone_number'], is_email_verified=True, is_phone_number_verified=True):
            raise serializers.ValidationError({"phone_number": "An user with this phone number already exists."})

        return attrs

    def create(self, validated_data):
        if User.objects.filter(email=validated_data['email']).count() > 0:
            User.objects.filter(email=validated_data['email']).all().delete()
        if User.objects.filter(phone_number=validated_data['phone_number']).count() > 0:
            User.objects.filter(phone_number=validated_data['phone_number']).all().delete()

        user = User.objects.create(
            phone_number=validated_data['phone_number'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            country=validated_data['country']
        )

        user.set_password(validated_data['password'])
        user.save()
        user.verify_id_details()

        return user
