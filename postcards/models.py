import settings
import subprocess
import urllib2

from django.contrib.gis.db.models.manager import GeoManager
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import simplejson as json
from django.utils.translation import ugettext_lazy as _

from locast.api import datetostr
from locast.models import ModelBase, modelbases, interfaces, managers
from locast.models.modelbases import LocastContent

from sorl.thumbnail import get_thumbnail

class Postcard(ModelBase,
    interfaces.UUID,
    interfaces.PrivatelyAuthorable,
    interfaces.Titled,
    interfaces.Locatable):

    class Meta:
        verbose_name = _('postcard')

    @models.permalink
    def get_api_uri(self):
        return ('postcard_single_api', [str(self.id)])

    def get_absolute_url(self):
        return reverse('home') + '#!/postcard/' + str(self.id) + '/'

    def __unicode__(self):
        return u'%s (id: %s)' % (self.title, str(self.id))

    objects = GeoManager()

    content_state = models.PositiveSmallIntegerField(choices=LocastContent.STATE_CHOICES, default=LocastContent.STATE_INCOMPLETE, blank=True)

    # popularity
    # facebook_likes + favorited
    facebook_likes = models.PositiveIntegerField(default=0)

    animated_render = models.FileField(
            upload_to='derivatives/%Y/%m/%d/', 
            blank=True,
            help_text=_('Created automatically.'))

    frame_delay = models.IntegerField(default=300)

    @property
    def first_photo_model(self):
        if self.postcardcontent_set.count():
            content = self.postcardcontent_set.order_by('id')[0].content
            return content

        return None

    @property
    def cover_photo(self):
        if self.first_photo_model and self.first_photo_model.file:
            return get_thumbnail(self.first_photo_model.file, '640', quality=75)

        return None
            
    @property
    def thumbnail(self):
        if self.cover_photo:
            return get_thumbnail(self.cover_photo, '150', quality=75)

        return None

    # all users who contributed
    @property
    def authors(self):
        authors = [self.author]
        if self.postcardcontent_set.count():
            for p in self.postcardcontent_set.all():
                if not p.author in authors:
                    authors.append(p.author)

        return authors

    def api_serialize(self, request):
        d = {}
        resc = {}
        if self.cover_photo:
            resc['cover_photo'] = LocastContent.serialize_resource(self.cover_photo.url)
        if self.thumbnail:
            resc['thumbnail'] = LocastContent.serialize_resource(self.thumbnail.url)
        if self.animated_render:
            resc['animated_render'] = LocastContent.serialize_resource(self.animated_render.url)

        d['resources'] = resc
        d['frame_delay'] = self.frame_delay
        d['facebook_likes'] = self.facebook_likes
        d['photos'] = reverse('postcard_photo_api', kwargs={'postcard_id':self.id})
        d['authors'] = map(lambda a: a.username,  self.authors)

        return d

    def geojson_properties(self, request):
        d = {}
        d['id'] = self.id
        d['title'] = self.title

        return d

    def pre_save(self):
        # If it is marked as COMPLETE, it needs to be processed, double check
        # that it is still COMPLETE
        if (self.content_state == LocastContent.STATE_INCOMPLETE or \
            self.content_state == LocastContent.STATE_COMPLETE):

            # Check that there is at least one photo
            if self.first_photo_model and self.first_photo_model.file:
                self.content_state = LocastContent.STATE_COMPLETE            

    def process(self, verbose=False):
        if self.first_photo_model.file and self.content_state == LocastContent.STATE_COMPLETE:
            self.content_state = LocastContent.STATE_PROCESSING
            self.save()

            if verbose: print 'creating animated render...'
            self.create_animated_render(verbose=verbose)

            self.content_state = LocastContent.STATE_FINISHED
            if verbose: print 'finished processing.'
            self.save()

    def create_animated_render(self, verbose=False):

        # create a new file. Otherwise, it will be overwritten
        if not self.animated_render:
            filename = 'animated_%s.gif' % self.id
            self.animated_render.save(filename, ContentFile(''), False)

        actual_delay = int(self.frame_delay / 10)
        images_to_gif_args = ['lcvideo_images_to_gif', unicode(actual_delay), self.animated_render.path]

        photos = self.postcardcontent_set.order_by('created')
        if actual_delay < 0:
            photos.reverse()

        for i in photos:
            if i.content.file:
                images_to_gif_args.append(i.content.file.path)

        stdout = None
        if verbose:
            stdout = subprocess.PIPE

        subprocess.call(images_to_gif_args, stdout=stdout)

    def update_facebook_likes(self):
        # https://graph.facebook.com/?id=http://mel-pydev.mit.edu/avea/?_escaped_fragment_=/postcard/1/
        postcard_url = settings.HOST + self.get_absolute_url().replace('#!','?_escaped_fragment_=')
        url = 'https://graph.facebook.com/?id=' + postcard_url
        response = urllib2.urlopen(url)
        fb_data = json.loads(response.read())
        if 'shares' in fb_data:
            self.facebook_likes = fb_data['shares']
        else:
            self.facebook_likes = 0

        self.save()


# Generic holder for media content.
class PostcardContent(modelbases.LocastContent,
        interfaces.UUID,
        interfaces.Authorable,
        interfaces.Locatable):

    objects = models.Manager()

    postcard = models.ForeignKey(Postcard)


class Photo(PostcardContent,
        modelbases.ImageContent):

    class Meta:
        verbose_name = _('photo')

    @models.permalink
    def get_api_uri(self):
        return ('postcard_photo_single_api', [str(self.postcard.id), str(self.id)])

    def __unicode__(self):
        return u'id: %s, postcard: %s' % (str(self.id), self.postcard.id)

    @property
    def medium_file(self):
        return get_thumbnail(self.file, '320', quality=75)

    def content_api_serialize(self, request=None):
        d = {}
        if self.file:
            d['resources'] = {}
            d['resources']['primary'] = self.serialize_resource(self.file.url)
            d['resources']['medium'] = self.serialize_resource(self.medium_file.url)

        return d


class PostcardUserManager(managers.LocastUserManager): pass


class UserActivity(modelbases.UserActivity): pass


class PostcardUser(modelbases.LocastUser):

    @models.permalink
    def get_api_uri(self):
        return ('user_api_single', [str(self.id)])

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

    bio = models.TextField(null=True, blank=True)
    personal_url = models.URLField(null=True, blank=True)
    hometown = models.CharField(max_length=128, null=True, blank=True)

    def api_serialize(self, request):
        d = {}

        if self.bio:
            d['bio'] = self.bio

        if self.personal_url:
            d['personal_url'] = self.personal_url

        if self.hometown:
            d['hometown'] = self.hometown

        return d
