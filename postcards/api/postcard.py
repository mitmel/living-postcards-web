from django.views.decorators.csrf import csrf_exempt

from locast.api import *
from locast.api import rest, qstranslate, exceptions
from locast.auth.decorators import optional_http_auth, require_http_auth
from locast.models.modelbases import LocastContent

from postcards import forms, models

ruleset = {
    # Authorable
    'author'        :    { 'type': 'int' },
    'title'         :    { 'type': 'string' },
    'description'   :    { 'type': 'string' },
    'created'       :    { 'type': 'datetime' },
    'modified'      :    { 'type': 'datetime' },

    # Privately Authorable
    'privacy'       :    { 'type': 'string' },

    # Taggable
    'tags'          :    { 'type': 'list' },

    # Locatable
    'dist'          :    { 'type': 'geo_distance', 'alias': 'location__distance_lte' },
    'within'        :    { 'type': 'geo_polygon', 'alias': 'location__within' },

    # Favoritable
    'favorited_by'  :    { 'type': 'int' },

    # 
    'popularity'  :    { 'type': 'int', 'alias': 'facebook_likes' },
}

@csrf_exempt
class PostcardAPI(rest.ResourceView):

    @optional_http_auth
    def get(request, postcard_id=None, coll_id=None, format='.json'):

        # single postcard
        if postcard_id:
            postcard = get_object(models.Postcard, id=postcard_id)

            if not postcard.allowed_access(request.user):
                raise exceptions.APIForbidden
                
            postcard_dict = api_serialize(postcard, request)
            return APIResponseOK(content=postcard_dict, total=1)

        # multiple postcards
        else:
            base_query = models.Postcard.get_privacy_q(request) & \
               Q(content_state=4) 
            q = qstranslate.QueryTranslator(models.Postcard, ruleset, base_query)
            query = request.GET.copy()
            objs = total = pg = None
            try:
                objs = q.filter(query)
                objs, total, pg = paginate(objs, request.GET)
            except qstranslate.InvalidParameterException, e:
                raise exceptions.APIBadRequest(e.message)

            postcard_arr = []
            for p in objs:
                postcard_arr.append(api_serialize(p, request))

            return APIResponseOK(content=postcard_arr, total=total, pg=pg)

    @require_http_auth
    def post(request):
        postcard = postcard_from_post(request)
        postcard.save()
        # models.UserActivity.objects.create_activity(request.user, cast, 'created')

        return APIResponseCreated(content=api_serialize(postcard, request), location=postcard.get_api_uri())

    @require_http_auth
    def put(request, postcard_id = None):
        if not postcard_id:
            pass

        postcard = get_object(models.Postcard, postcard_id)

        if not postcard.allowed_edit(request.user):
            raise exceptions.APIForbidden

        postcard = postcard_from_post(request, postcard)
        postcard.save()

        return APIResponseOK(content=api_serialize(postcard, request))

    @require_http_auth
    def delete(request, postcard_id):

        postcard = get_object(models.Postcard, postcard_id)

        if not postcard.allowed_edit(request.user):
            raise exceptions.APIForbidden

        postcard.delete()

        return APIResponseOK(content='success')

    @optional_http_auth
    def get_photo(request, postcard_id, photo_id = None):
        if photo_id:
            photo = get_object(models.Photo, photo_id)
            check_postcard_photo(postcard_id, photo_id)

            return APIResponseOK(content=api_serialize(photo.contentmodel))

        else:
            postcard = get_object(models.Postcard, postcard_id)

            if not postcard.allowed_access(request.user):
                raise exceptions.APIForbidden

            photo_dicts = []
            for p in postcard.postcardcontent_set.all():
                photo_dicts.append(api_serialize(p, request))

        return APIResponseOK(content=photo_dicts)

    @require_http_auth
    def post_photo(request, postcard_id, photo_id = None):

        # If there is a photo_id, posting raw photo data to a photo
        if photo_id:
            photo = get_object(models.Photo, id = photo_id)
            check_postcard_photo(postcard_id, photo_id)

            content_type = get_param(request.META, 'CONTENT_TYPE')
            mime_type = content_type.split(';')[0]

            if not mime_type:
                raise exceptions.APIBadRequest('Invalid file type!')

            try:
                photo.create_file_from_data(request.raw_post_data, mime_type)
            except LocastContent.InvalidMimeType:
                raise exceptions.APIBadRequest('Invalid file type!')

            # Set the postcard as complete because it needs to be reprocessed
            postcard = get_object(models.Postcard, postcard_id)
            postcard.content_state = LocastContent.STATE_COMPLETE
            postcard.save()

            return APIResponseOK(content=api_serialize(photo.contentmodel))

        # If there is not, posting a new photo object
        else:
            photo = photo_from_post(request, postcard_id)
            photo.save()

            return APIResponseCreated(content=api_serialize(photo.contentmodel, request), location=photo.get_api_uri())

    @optional_http_auth
    def get_authors(request, postcard_id):
        pass


def check_postcard_photo(postcard_id, photo_id):
    postcard = get_object(models.Postcard, id=postcard_id)
    try:
        postcard.postcardcontent_set.get(id=photo_id)
    except models.PostcardContent.DoesNotExist:
        raise exceptions.APIBadRequest('Photo is not part of this postcard')
    return postcard


def get_geofeatures(request):
    bounds_param = get_param(request.GET, 'within')
    query = request.GET.copy()

    base_query = Q()

    if bounds_param:
        del query['within']
        base_query = base_query & get_polygon_bounds_query(bounds_param, 'location') 

    # postcard within bounds
    base_query = models.Postcard.get_privacy_q(request) & base_query

    q = qstranslate.QueryTranslator(models.Postcard, ruleset, base_query)
    postcards = q.filter(query)

    postcard_arr = []
    for p in postcards:
        if p.location:
            postcard_arr.append(geojson_serialize(p, p.location, request))

    return APIResponseOK(content=dict(type='FeatureCollection', features=postcard_arr))


@csrf_exempt
def update_facebook_likes(request):
    p_id = int(request.POST.get('id', None))
    postcard = get_object(models.Postcard, id=p_id)
    postcard.update_facebook_likes()

    return APIResponseOK(content=api_serialize(postcard))


def postcard_from_post(request, postcard = None):
    data = {}

    if postcard:
        data = api_serialize(postcard)

    data.update(get_json(request.raw_post_data))

    location = None
    if 'location' in data:
        location = data['location']

    if not postcard:
        data['author'] = request.user.id
    else:
        data['author'] = postcard.author.id

    # Modified and created cannot be set
    if 'modified' in data: del data['modified']
    if 'created' in data: del data['created']

    if 'privacy' in data: 
        data['privacy'] = models.Postcard.get_privacy_value(data['privacy'])

    postcard = form_validate(forms.PostcardAPIForm, data, instance = postcard)

    if location:
        postcard.set_location(location[0], location[1])
    
    return postcard


def photo_from_post(request, postcard_id, photo = None):
    data = {}
    if photo:
        data = api_serialize(photo)

    data.update(get_json(request.raw_post_data))

    data['postcard'] = postcard_id

    location = None
    if 'location' in data:
        location = data['location']

    if not photo:
        data['author'] = request.user.id
    else:
        data['author'] = photo.author.id

    # Modified and created cannot be set
    if 'modified' in data: del data['modified']
    if 'created' in data: del data['created']

    photo = form_validate(forms.PhotoAPIForm, data, instance = photo)

    if location:
        photo.set_location(location[0], location[1])
    
    return photo
