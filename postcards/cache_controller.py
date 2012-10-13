from django.db.models import signals
from django.dispatch import receiver

from locast.api import cache

from models import Postcard

POSTCARD_GET_GROUP = 'postcard_get'

@receiver(signals.post_save, sender=Postcard)
@receiver(signals.post_delete, sender=Postcard)
def _clear_postcard_get_cache(sender, **kwargs):
    cache.incr_group(POSTCARD_GET_GROUP)
