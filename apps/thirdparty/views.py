from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect

import settings

from urlparse import parse_qs
import twitter
import oauth2 as oauth
from models import UserProfile
from settings import TWITTER_CONSUMER_SECRET


def home(request):
            
    return HttpResponse("Signed IN Home")

def oauth_req(request):
    
    consumer = oauth.Consumer(key=settings.TWITTER_CONSUMER_KEY, secret=settings.TWITTER_CONSUMER_SECRET)
    request_token_url = settings.TWITTER_OAUTH_REQUEST_TOKEN_URL
    
    client = oauth.Client(consumer)
    resp, content = client.request(request_token_url, "GET")
    
    request.session['request_token'] = parse_qs(content)['oauth_token'][0]
    request.session['request_token_secret'] = parse_qs(content)['oauth_token_secret'][0]
    
    return redirect(settings.TWITTER_OAUTH_PERMS_REDIRECT_URL + parse_qs(content)['oauth_token'][0])
    
    
def twitter_signed_in(request):
    print request
    
    consumer = oauth.Consumer(key=settings.TWITTER_CONSUMER_KEY, secret=settings.TWITTER_CONSUMER_SECRET)
    access_token_url = settings.TWITTER_OAUTH_REQUEST_TOKEN_EXCHANGE
    print request.GET['oauth_verifier']
    
    token = oauth.Token(request.session['request_token'], request.session['request_token_secret'])
    
    client = oauth.Client(consumer, token)
    resp, content = client.request(access_token_url, "POST", body='oauth_verifier=%s' % request.GET['oauth_verifier'])
    
    print content 
    
    access_token = parse_qs(content)['oauth_token'][0]
    access_token_secret = parse_qs(content)['oauth_token_secret'][0]
    user_id = parse_qs(content)['user_id'][0]
    screen_name = parse_qs(content)['screen_name'][0]
    
    api = twitter.Api(consumer_key=settings.TWITTER_CONSUMER_KEY,consumer_secret=TWITTER_CONSUMER_SECRET, access_token_key=access_token, access_token_secret=access_token_secret)
    twitter_user = api.GetUser(user_id)
    
    try:
        user = User.objects.get(username__exact=screen_name)
    except User.DoesNotExist:
        user = None
    
    if user == None :
        #we've got a new user
        user = User.objects.create_user(username=screen_name, email='none@socialchew.com', password=None)
        user.save()
        
        print 'first time user'
        
        
    #now update the profile for this user with twitter information
    twitter_profile = user.get_profile()
    twitter_profile.set_twitter_info(twitter_user, access_token, access_token_secret)
    twitter_profile.save()

    print 'updated user\'s twitter profile'
    
    #now authenticate the user and log them in
    user = authenticate(username=user)
    print user
    
    login(request, user)
    
    print 'user should now be authenticated and logged in'
    
    
    return HttpResponse("Welcome, ")