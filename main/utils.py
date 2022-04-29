import pycountry
from django.utils.deconstruct import deconstructible
import os
from uuid import uuid4
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from botocore.exceptions import ClientError
import urllib.request
import urllib.parse

def country_choicer():
    """
    Helper to get all countries
    """
    for country in pycountry.countries:
        yield (country.alpha_2, country.name)


def language_choicer():
    """
    Helper to get all languages
    """
    for language in [lang for lang in pycountry.languages if hasattr(lang, 'alpha_2')]:
        yield (language.alpha_2, language.name)
        
@deconstructible
class UploadToPathAndRename(object):
    """
    Custom object to pass to `upload_to` for ImageField
    to autorename files
    """

    def __init__(self, path):
        self.sub_path = path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        filename = '{}.{}'.format(uuid4().hex, ext)
        # return the whole path to the file
        return os.path.join(self.sub_path, filename)

def sendSMS(apikey, numbers, sender, message):
    return True
 
