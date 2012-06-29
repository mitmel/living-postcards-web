from django.contrib.gis import admin

from postcards import models

class PhotoInline(admin.TabularInline):
    model = models.Photo
    fields = ('title', 'file')

class PostcardAdmin(admin.ModelAdmin):
    inlines = [PhotoInline]

class PhotoAdmin(admin.ModelAdmin): pass 

admin.site.register(models.Postcard, PostcardAdmin)
admin.site.register(models.Photo, PhotoAdmin)

admin.site.register(models.PostcardUser, admin.ModelAdmin)

