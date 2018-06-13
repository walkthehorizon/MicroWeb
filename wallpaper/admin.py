from django.contrib import admin
from .models import *


class MicroUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'nickname', 'avatar', 'phone', 'email', 'signature', 'date_joined', 'last_login')


# Register your models here.
class WallpaperAdmin(admin.ModelAdmin):
    # fields = ['name', 'describe', 'category', 'url']
    list_display = ('id', 'name', 'describe', 'created', 'owner', 'category', 'subject')
    list_filter = ('category', 'owner', 'subject')


class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'owner', 'type', 'created')
    search_fields = ('name',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')


class SplashAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'duration')


admin.site.register(MicroUser, MicroUserAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Wallpaper, WallpaperAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Splash, SplashAdmin)
