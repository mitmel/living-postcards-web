from django.http import Http404

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from locast import get_model

from postcards.models import Postcard

def home(request):
    fragment = request.GET.get('_escaped_fragment_')
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
        og_image = postcard.gif_preview.url
        return render_to_response('content_page.django.html', locals(), context_instance = RequestContext(request))

    return render_to_response('home.django.html', locals(), context_instance = RequestContext(request))

def context_js(request):
    return render_to_response('context.django.js', locals(), context_instance = RequestContext(request), mimetype='text/javascript')
