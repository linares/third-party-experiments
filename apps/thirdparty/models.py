from django.contrib.auth.models import User
from django.db.models.signals import post_save

from django.db import models
import datetime

import twitter

class UserProfile(models.Model):
    
    # This field is required.
    user = models.OneToOneField(User)

    #twitter identity
    twitter_id = models.CharField(max_length=200, null=False, blank=False, unique=True)
    twitter_screen_name = models.CharField(max_length=200, null=False, blank=False, unique=True)
    twitter_profile_img = models.CharField(max_length=200, null=False, blank=False)
    twitter_access_token = models.CharField(max_length=200, null=False, blank=False, default='')
    twitter_access_token_secret = models.CharField(max_length=200, null=False, blank=False, default='')
    
    def set_twitter_info(self, twitter_user, access_token_key, access_token_secret):
        self.twitter_id = twitter_user.GetId()
        self.twitter_screen_name = twitter_user.GetScreenName()
        self.twitter_profile_img = twitter_user.GetProfileImageUrl()
        self.twitter_access_token = access_token_key
        self.twitter_access_token_secret = access_token_secret

   
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)