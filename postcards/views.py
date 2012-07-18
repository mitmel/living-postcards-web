from django.shortcuts import render_to_response
from django.template import RequestContext

def home(request):
    return render_to_response('home.django.html', locals(), context_instance = RequestContext(request))

def context_js(request):
    return render_to_response('context.django.js', locals(), context_instance = RequestContext(request), mimetype='text/javascript')
