# Create your views here.
from django.http import HttpResponse
import oauth2 as oauth
from django.shortcuts import redirect
from django.template import Context, loader

def home(request):
    
    if request.user.is_authenticated():
        return HttpResponse("Home")        
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
    