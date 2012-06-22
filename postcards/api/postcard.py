from postcards import models

from locast.api import *
from locast.api import rest, qstranslate, exceptions

class PostcardAPI(rest.ResourceView):

    ruleset = {
        # Authorable
        'author'        :    { 'type' : 'int' },
        'title'         :    { 'type' : 'string' },
        'description'   :    { 'type' : 'string' },
        'created'       :    { 'type' : 'datetime' },
        'modified'      :    { 'type' : 'datetime' },

        # Privately Authorable
        'privacy'       :    { 'type' : 'string' },

        # Taggable
        'tags'          :    { 'type' : 'list' },

        # Locatable
        'dist'          :    { 'type': 'geo_distance', 'alias' : 'location__distance_lte' },
        'within'        :    { 'type': 'geo_polygon', 'alias' : 'location__within' },

        # Favoritable
        'favorited_by'  :    { 'type': 'int' },
    }

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
            base_query = models.Postcard.get_privacy_q(request)
            q = qstranslate.QueryTranslator(models.Postcard, PostcardAPI.ruleset, base_query)
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

