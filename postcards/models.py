import subprocess

from django.contrib.gis.db.models.manager import GeoManager
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from locast.api import datetostr
from locast.models import ModelBase, modelbases, interfaces, managers

class Postcard(ModelBase,
    interfaces.PrivatelyAuthorable,
    interfaces.Titled,
    interfaces.Locatable):

    class Meta:
        verbose_name = _('postcard')

    @models.permalink
    def get_api_uri(self):
        return ('postcard_single_api', [str(self.id)])

    #def get_absolute_url(self):
    #    return reverse('frontpage') + '#!cast/' + str(self.id) + '/'

    def __unicode__(self):
        return u'%s (id: %s)' % (self.title, str(self.id))

    objects = GeoManager()

    gif_preview = models.FileField(
            upload_to='derivatives/%Y/%m/%d/', 
            blank=True,
            help_text=_('Created automatically.'))

    def api_serialize(self, request):
        d = {}
        d['photos'] = reverse('postcard_photo_api', kwargs={'postcard_id':self.id})
        return d

    def process(self):
        if self.postcardcontent_set.count():
            self.create_animated_gif()

    def create_animated_gif(self):
        filename = 'animated_%s.gif' % self.id
        self.gif_preview.save(filename, ContentFile(''), False)
        images_to_gif_args = ['lcvideo_images_to_gif', self.gif_preview.path]
        for i in self.postcardcontent_set.all():
            if i.content.file:
                images_to_gif_args.append(i.content.file.path)

        subprocess.call(images_to_gif_args)

# Generic holder for media content.
class PostcardContent(modelbases.LocastContent):

    objects = models.Manager()

    postcard = models.ForeignKey(Postcard)

class Photo(PostcardContent,
        interfaces.Authorable,
        interfaces.Locatable,
        interfaces.Titled,
        modelbases.ImageContent):

    class Meta:
        verbose_name = _('photo')

    @models.permalink
    def get_api_uri(self):
        return ('postcard_photo_single_api', [str(self.postcard.id), str(self.id)])

    def __unicode__(self):
        return u'%s (id: %s, postcard: %s)' % (self.title, str(self.id), self.postcard.title)

    def api_serialize(self, request):
        d = {}
        if self.file:
            d['primary'] = modelbases.LocastContent.serialize_resource(self.file.url)

        return d

class PostcardUserManager(managers.LocastUserManager): pass

class UserActivity(modelbases.UserActivity): pass

class PostcardUser(modelbases.LocastUser):

    #@models.permalink
    #def get_api_uri(self):
    #    return ('user_api_single', [str(self.id)])

    def __unicode__(self):
        if self.email:
            return u'%s' % self.email
        else:
            return u'%s' % self.username

    def api_serialize(self, request):
        d = {'joined' : datetostr(self.date_joined)}
        profile = None
        try:
            profile = self.get_profile()
        except ObjectDoesNotExist:
            pass

        if ( profile ):
            d['profile'] = profile.api_serialize(request)

        return d

    def generate_display_name(self):
        self.display_name = self.username


class PostcardUserProfile(ModelBase):
    user = models.OneToOneField(PostcardUser)

#    user_image = models.ImageField(upload_to='user_images/%Y/%m/', null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    personal_url = models.URLField(null=True, blank=True)
    hometown = models.CharField(max_length=128, null=True, blank=True)

#    @property
#    def user_image_small(self):
#        if self.user_image:
#            return get_thumbnail(self.user_image, '150', quality=75)

    def api_serialize(self, request):
        d = {}
#        if self.user_image:
#            d['user_image'] = self.user_image.url
#            d['user_image_small'] = self.user_image_small.url

        if self.bio:
            d['bio'] = self.bio

        if self.personal_url:
            d['personal_url'] = self.personal_url

        if self.hometown:
            d['hometown'] = self.hometown

        return d

