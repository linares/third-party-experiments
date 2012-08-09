# Create your views here.
from django.http import HttpResponse, HttpResponseForbidden
import oauth2 as oauth
from django.shortcuts import redirect
from django.template import Context, loader
import twitter
import settings
from django.template.context import RequestContext

def home(request):
    
    if request.user.is_authenticated():
        timeline = getStatusesForRequest(request)
        
        t = loader.get_template('main/main_page.html')
        c = RequestContext(request, {
                        'timeline' : timeline
                     })
        return HttpResponse(t.render(c))
                
    else :
        return redirect('/landing')
    

def getTwitterApiForRequest(request):
    uprofile = request.user.get_profile()
        
    api = twitter.Api(consumer_key=settings.TWITTER_CONSUMER_KEY,
                      consumer_secret=settings.TWITTER_CONSUMER_SECRET, 
                      access_token_key=uprofile.twitter_access_token, 
                      access_token_secret=uprofile.twitter_access_token_secret)

    return api



def getStatusesForRequest(request, max_id=None):
    api = getTwitterApiForRequest(request)
       
    print max_id
    
    timeline = []
    if max_id == None :
        statuses = api.GetHomeTimeline(count=75)
    else :
        statuses = api.GetHomeTimeline(count=50, max_id=max_id)
    
    for status in statuses:
        timeline.append({
                            'created_at' : status.created_at,
                            'text' : status.text,
                            'user' : { 
                                        'name' : status.user.screen_name,
                                        'profile_image_url' : status.user.profile_image_url
                                      } 
                         })
    
    setLastStatusId(request, statuses)
    return timeline

def setLastStatusId(request, statuses):
    request.session['last_status_id'] = statuses[len(statuses)-1].id

def getLastStatusId(request):
    return request.session['last_status_id'] 

def signin(request):
    
    if request.user.is_authenticated():
        return redirect('/')        
    else :
        t = loader.get_template('landing/landing_page.html')
        c = Context({
        })
        return HttpResponse(t.render(c))


def page(request, page_id):
    if request.user.is_authenticated():        
        timeline = getStatusesForRequest(request, getLastStatusId(request))
        
        t = loader.get_template('main/main_page.html')
        c = RequestContext(request, {
                        'timeline' : timeline
                     })
        return HttpResponse(t.render(c))
    else:
        return HttpResponseForbidden()
    
    
