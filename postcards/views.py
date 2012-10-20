import settings

from django.contrib.flatpages.models import FlatPage
from django.http import Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from locast import get_model

from postcards.models import Postcard

def home(request):
    fragment = request.GET.get('_escaped_fragment_')

    # Javascript template "flatpages"
    locale = ''
    # If the locale is same as the request language, just use default flatpage
    if settings.LANGUAGE_CODE and not (request.LANGUAGE_CODE == settings.LANGUAGE_CODE):
        # Otherwise, grab the one that is /url-{locale}/
        locale = request.LANGUAGE_CODE

    home_page = _get_js_flatpage('home', locale)
    about_page = _get_js_flatpage('about', locale)
    competition_page = _get_js_flatpage('competition', locale)

    if fragment:
        fragments = fragment.split('/');
        # splits like this: ''/postcard/id/''
        if len(fragments) < 3:
            raise Http404

        model = get_model(fragments[1])
        if not model or (not model == Postcard):
            raise Http404

        try:
            id = int(fragments[2])
        except ValueError:
            raise Http404

        postcard = get_object_or_404(model, id=id)
        og_title = postcard.title
        og_image = postcard.animated_render.url
        og_author = postcard.author.display_name
        og_description = postcard.description

        return render_to_response('content_page.django.html', locals(), context_instance = RequestContext(request))

    return render_to_response('home.django.html', locals(), context_instance = RequestContext(request))

def context_js(request):
    return render_to_response('context.django.js', locals(), context_instance = RequestContext(request), mimetype='text/javascript')

# see: https://developers.facebook.com/docs/reference/javascript/
# 60*60*24*365 seconds
@cache_page(31536000)
def facebook_channel_html(request):
    response = render_to_response('facebook_channel.django.html', locals(), context_instance = RequestContext(request))

    response['Pragma'] = 'public'
    return response

def _get_js_flatpage(url, locale):
    content = ''
    if locale:
        locale = '-' + locale
    try:
        content = FlatPage.objects.get(url='/' + url + locale + '/').content
    except FlatPage.DoesNotExist:
        try:
            content = FlatPage.objects.get(url='/' + url + '/').content
        except FlatPage.DoesNotExist:
            pass
 
    return content
