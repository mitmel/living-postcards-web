import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from datetime import datetime

from locast.models.modelbases import LocastContent

from postcards.models import Postcard

def process_postcards():

    ps = Postcard.objects.filter(content_state=LocastContent.STATE_COMPLETE)

    for p in ps:
        # This is done in order to make sure the object is up to date with the database
        p = Postcard.objects.get(id=p.id)
        if p.content_state == LocastContent.STATE_COMPLETE:
            p.process(verbose=True)

if __name__ == '__main__':
    print str(datetime.now()) + ' =======  running process_postcards ======'
    process_postcards()
