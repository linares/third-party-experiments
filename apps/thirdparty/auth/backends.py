'''
Created on Aug 5, 2012

@author: bigI
'''

from django.conf import settings
from django.contrib.auth.models import User
from apps.thirdparty.models import UserProfile

class TwitterAuthBackend(object):
    """
    Authenticates this Twitter User
    """

    def authenticate(self, username, password=None):
        try:
            user = User.objects.get(username=username)
            return user
        except User.DoesNotExist:
            return None
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None