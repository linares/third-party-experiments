from django.db import models
from django.db.models.signals import post_save

# Create your models here.
from django.contrib.auth.models import User

class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(User)

    #twitter identity
    twitter_id = models.CharField(max_length=200, null=False, blank=False)
    twitter_screen_name = models.CharField(max_length=200, null=False, blank=False)
    twitter_profile_img =models.CharField(max_length=200, null=False, blank=False)
    
    
    
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)