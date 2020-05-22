from django.contrib import admin

from .models import *


class MicroUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'nickname', 'phone', 'date_joined', 'last_login', 'pea', 'vip')
    raw_id_fields = ['buys', 'collects']


# Register your models here.
class WallpaperAdmin(admin.ModelAdmin):
    fields = ['banner', 'category', 'url', 'origin_url']
    list_display = ('id', 'category', 'subject', 'created')
    list_filter = ('category', 'subject')


class SubjectAdmin(admin.ModelAdmin):
    fields = ['name', 'description', 'cover', 'cover_1', 'cover_2']
    list_display = ('id', 'name', 'description', 'tag', 'created')
    search_fields = ('name', 'description',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')


class SplashAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'duration')


class BannerAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'subject_id', 'title', 'created')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'content', 'user_id', 'created')


admin.site.register(MicroUser, MicroUserAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Wallpaper, WallpaperAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Splash, SplashAdmin)
admin.site.register(Banner, BannerAdmin)
admin.site.register(Comment, CommentAdmin)
