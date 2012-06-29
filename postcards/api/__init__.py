from django.views.decorators.csrf import csrf_exempt

from locast.api import *

from postcards import forms

@csrf_exempt
def register(request):
    data = {}
    data.update(get_json(request.raw_post_data))

    user = form_validate(forms.RegisterForm, data)

    return APIResponseOK(content=api_serialize(user))

