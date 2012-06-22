from django.contrib.gis import admin

from postcards import models

class PhotoInline(admin.TabularInline):
    model = models.Photo

class PostcardAdmin(admin.ModelAdmin):
    inlines = [PhotoInline]

admin.site.register(models.Postcard, PostcardAdmin)
