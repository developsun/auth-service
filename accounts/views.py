import datetime
import json

from django.shortcuts import render
from cryptography.fernet import Fernet
from main.settings import FERNET_KEY
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from accounts.permissions import AnonymousUserOnlyPermission
User = get_user_model()


def reset_password_view(request, creds):

    fernet = Fernet(FERNET_KEY)
    creds_data = creds.split("'")
    try:
        creds_data = fernet.decrypt(creds_data[1].encode('utf-8')).decode()
        creds_data = json.loads(creds_data)
        expiry = creds_data['expiry']
        if datetime.datetime.now() < datetime.datetime.fromtimestamp(int(expiry)):
            user = User.objects.filter(phone_number=creds_data['phone_number']).first()
            return render(request, "reset_password.html", {
                "phone_number": creds_data['phone_number'],
                "name": user.full_name,
                "expiry": datetime.datetime.fromtimestamp(int(expiry)),
                "creds": creds
            })
        else:
            return render(request, "reset_password_error.html", {})
    except:
        return render(request, "reset_password_error.html", {})


def verify_phone_view(request, creds):
    fernet = Fernet(FERNET_KEY)
    creds_data = creds.split("'")
    try:
        creds_data = fernet.decrypt(creds_data[1].encode('utf-8')).decode()
        creds_data = json.loads(creds_data)
        expiry = creds_data['expiry']
        user = User.objects.filter(phone_number=creds_data['phone_number']).first()
        if datetime.datetime.now() < datetime.datetime.fromtimestamp(int(expiry)):
            user.is_phone_number_verified=True
            user.save()
            return render(request, "phone_number_verified.html", {
                "phone_number": creds_data['phone_number'],
                "name": user.full_name,
                "error": "0"
            })
        else:
            return render(request, "phone_number_verified.html", {
                "error": "1",
            })
    except:
        return render(request, "phone_number_verified.html", {
            "error": "1"
        })


def verify_email_view(request, creds):
    fernet = Fernet(FERNET_KEY)
    creds_data = creds.split("'")
    try:
        creds_data = fernet.decrypt(creds_data[1].encode('utf-8')).decode()
        creds_data = json.loads(creds_data)
        expiry = creds_data['expiry']
        user = User.objects.filter(email=creds_data['email']).first()
        if datetime.datetime.now() < datetime.datetime.fromtimestamp(int(expiry)):
            user.is_email_verified = True
            user.save()
            return render(request, "email_verified.html", {
                "name": user.full_name,
                "error": "0"
            })
        else:
            return render(request, "email_verified.html", {
                "error": "1",
            })
    except:
        return render(request, "email_verified.html", {
            "error": "1"
        })



@api_view(['POST'])
@permission_classes([AnonymousUserOnlyPermission])
def set_password_endpoint(request):

    fernet = Fernet(FERNET_KEY)
    creds = request.POST.get('creds', '')
    password = request.POST.get('password', '')
    confirm_password = request.POST.get('confirm_password', '')
    if not (password == confirm_password and password != ''):
        return Response({"status": "failed", "message": "Password and Confirm Password has not matched."}, status=400)

    creds = creds.split("'")
    try:
        creds = fernet.decrypt(creds[1].encode('utf-8')).decode()
        creds = json.loads(creds)
        expiry = creds['expiry']
        if datetime.datetime.now() < datetime.datetime.fromtimestamp(int(expiry)):
            user = User.objects.filter(phone_number=creds['phone_number']).first()
            user.set_password("password")
        else:
            raise Exception("Invalid token.")
    except:
        return Response({"status": "failed", "message": "Token has expired."}, status=403)

    return Response({"status": "successful", "message": "Password has been changed successfully."})
