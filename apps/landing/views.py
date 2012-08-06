# Create your views here.
from django.http import HttpResponse
import oauth2 as oauth
from django.shortcuts import redirect
from django.template import Context, loader
import twitter
import settings

def home(request):
    
    if request.user.is_authenticated():
        uprofile = request.user.get_profile()
        
        api = twitter.Api(consumer_key=settings.TWITTER_CONSUMER_KEY,
                          consumer_secret=settings.TWITTER_CONSUMER_SECRET, 
                          access_token_key=uprofile.twitter_access_token, 
                          access_token_secret=uprofile.twitter_access_token_secret)
        
        print 'got api'
        
        timeline = []
        
        statuses = api.GetHomeTimeline(count=50)
        
        print 'got statuses'
        
        for status in statuses:
            timeline.append({
                                'created_at' : status.created_at,
                                'text' : status.text,
                                'user' : { 
                                            'name' : status.user.screen_name,
                                            'profile_image_url' : status.user.profile_image_url
                                          } 
                             })
        
        t = loader.get_template('main/main_page.html')
        c = Context({
                        'timeline' : timeline
                     })
        return HttpResponse(t.render(c))
                
    else :
        return redirect('/landing')
    



def signin(request):
    
    if request.user.is_authenticated():
        return redirect('/')        
    else :
        t = loader.get_template('landing/landing_page.html')
        c = Context({
        })
        return HttpResponse(t.render(c))
    