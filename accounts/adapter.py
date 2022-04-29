"""
Custom `django-allauth` adapter
-------------------------------
"""
from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter as OriginalDefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.models import EmailAddress
from django.utils.crypto import get_random_string
from django.utils.encoding import force_text


class DefaultAccountAdapter(OriginalDefaultAccountAdapter):
    """
    Custom allauth.account.adapter.DefaultAccountAdapter
    """
    def get_from_email(self):
        """
        This is a hook that can be overridden to programatically
        set the 'from' email address for sending emails
        """
        return settings.DEFAULT_FROM_EMAIL

    def format_email_subject(self, subject):
        """
        Overriding method to change email subject
        """
        return force_text(subject)

    def send_mail(self, template_prefix, email, context):
        """
        Overriding method to patch `activate_url`
        """
        if email.split('@')[1] != 'localhost':
            if 'activate_url' in context:
                context['activate_url'] = "{frontend_url}/email-verification?key={key}" \
                    .format(
                        frontend_url=settings.FRONTEND_URL,

                        key=context['key'],
                    )
            if 'password_reset_url' in context:
                key = context['password_reset_url'].split('/')[-2]
                context['password_reset_url'] = "{frontend_url}/new-password?key={key}" \
                    .format(
                    frontend_url=settings.FRONTEND_URL,
                    key=key,
                )
            super().send_mail(template_prefix, email, context)


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom allauth.socialaccount.adapter.DefaultSocialAccountAdapter
    """
    def save_user(self, request, sociallogin, form=None):
        """
        Override the method to not send a letter to verify the email
        """
        user = super().save_user(request, sociallogin, form=None)
        if user.email.split('@')[1] != 'localhost':
            email = EmailAddress.objects.get(user=user)
            email.verified = True
            email.save()
        return user

    def populate_user(self, request, sociallogin, data):
        """
        Override the method for generating a user's temporary mail
        """
        user = super().populate_user(request, sociallogin, data)
        if not user.email:
            user.email = '%s@localhost' % get_random_string(length=12)
        return user
