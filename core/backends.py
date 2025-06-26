from django.contrib.auth.backends import ModelBackend
from .models import UserProfile

class PhoneBackend(ModelBackend):
    def authenticate(self, request, phone=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(phone=phone)
            if user.check_password(password):
                return user
        except UserProfile.DoesNotExist:
            return None
