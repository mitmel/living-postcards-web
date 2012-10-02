import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from datetime import datetime

from locast.models.modelbases import LocastContent

from postcards.models import Postcard

def process_postcards():

    ps = Postcard.objects.filter(content_state=LocastContent.STATE_COMPLETE)
    
    if ps.count():
        print str(datetime.now()) + ' =======  running process_postcards ======'

    for p in ps:
        # This is done in order to make sure the object is up to date with the database
        p = Postcard.objects.get(id=p.id)
        if p.content_state == LocastContent.STATE_COMPLETE:
            print ' - processing postcard ' + str(p.id)
            p.process(verbose=True)

if __name__ == '__main__':
    process_postcards()
