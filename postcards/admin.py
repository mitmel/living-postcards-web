from django.contrib.gis import admin

from postcards import models

class MapAdmin(admin.OSMGeoAdmin):
    default_lon = 41.0128
    default_lat = 28.9744
    default_zoom = 6

class PhotoInline(admin.TabularInline):
    model = models.Photo
    fields = ('author', 'file')

class PostcardAdmin(MapAdmin):
    inlines = [PhotoInline]

class PhotoAdmin(MapAdmin):  
    fields = ('file','postcard')

admin.site.register(models.Postcard, PostcardAdmin)
admin.site.register(models.Photo, PhotoAdmin)

admin.site.register(models.PostcardUser, admin.ModelAdmin)

