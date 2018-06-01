from django.contrib import admin
from .models import Snippet
from .models import Wallpaper


# Register your models here.
class WallpaperAdmin(admin.ModelAdmin):
    # fields = ['name', 'describe', 'category', 'url']
    list_display = ('name', 'category', 'describe', 'created', 'owner')
    list_filter = ('category', 'owner')


admin.site.register(Snippet)
admin.site.register(Wallpaper, WallpaperAdmin)
