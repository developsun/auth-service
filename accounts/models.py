from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone
from main.utils import country_choicer,UploadToPathAndRename
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser,PermissionsMixin
)
from cryptography.fernet import Fernet
from main.settings import FERNET_KEY
import datetime
import json
from kafka import KafkaProducer


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=300, default=None, null=True, blank=True)
    last_name = models.CharField(max_length=300, default=None, null=True, blank=True)
    date_of_birth = models.DateField('Date of Birth', default=None, null=True, blank=True)
    phone_number = models.CharField(max_length=20, default=None, null=True, blank=True)
    is_phone_number_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    avatar = models.ImageField(
        'Avatar',
        blank=True,
        null=True,
        upload_to=UploadToPathAndRename('users/avatars')
    )
    
    SEX_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('others', 'Others')
    )

    gender = models.CharField(
        'Gender',
        choices=SEX_CHOICES,
        max_length=6,
        null=True,
        blank=True
    )

    country = models.CharField(
        'Country',
        max_length=2,
        choices=country_choicer(),
        blank=True
    )
    state = models.CharField('State', max_length=254, blank=True)
    city = models.CharField('City', max_length=254, blank=True)
    date_joined = models.DateTimeField('date joined', default=timezone.now)
    is_active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)  # An admin user; non super-user
    admin = models.BooleanField(default=False)  # A superuser
    # notice the absence of a "Password field", that is built in.
    objects = UserManager()

    username = None

    USERNAME_FIELD = 'email'
    
    REQUIRED_FIELDS = []  # Email & Password are required by default.
    
    @property
    def full_name(self):
        if self.first_name is not None and self.last_name is not None:
            return self.first_name+" "+self.last_name
        else:
            return self.first_name if self.first_name is not None else "User"

    @property
    def short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):              # __unicode__ on Python 2
        return self.email

    @property
    def is_staff(self):
        """Is the user a member of staff?"""
        return self.staff

    @property
    def is_admin(self):
        """Is the user a admin member?"""
        return self.admin

    @property
    def is_superuser(self):
        """Is the user active?"""
        return self.admin

    def reset_password(self):
        reset_password_cred_obj = {
            "phone_number": self.phone_number,
            "expiry": int(datetime.datetime.now().timestamp()+360)
        }

        fernet = Fernet(FERNET_KEY)
        enc_message = fernet.encrypt(json.dumps(reset_password_cred_obj).encode())
        producer = KafkaProducer(bootstrap_servers='localhost:9093', value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        data = {
            "email": self.email,
            "url": f'http://localhost:8000/verify_email/{enc_message}'
        }
        producer.send('reset_password__requests', value=data)

        with open('reset password strings.txt', 'a') as f:
            f.write(f"[{self.phone_number or self.email}]\thttp://localhost:8000/reset_password/{enc_message} \n")

    def verify_id_details(self, phone_verify=True, email_verify=True):
        fernet = Fernet(FERNET_KEY)

        if phone_verify:
            phone_verification = {
                "phone_number": self.phone_number,
                "expiry": int(datetime.datetime.now().timestamp()+360)
            }
            phone_verification_message = fernet.encrypt(json.dumps(phone_verification).encode())
            with open('verification strings.txt', 'a') as f:
                f.write(
                    f"Phone Verification | [{self.phone_number or self.email}]\thttp://localhost:8000/verify_phone/{phone_verification_message} \n")
                f.close()

        if email_verify:
            email_verification = {
                "email": self.email,
                "expiry": int(datetime.datetime.now().timestamp() + 360)
            }
            email_verification_message = fernet.encrypt(json.dumps(email_verification).encode())
            with open('verification strings.txt', 'a') as f:
                f.write(
                    f"Email Verification | [{self.phone_number or self.email}]\thttp://localhost:8000/verify_email/{email_verification_message} \n")
                f.close()


