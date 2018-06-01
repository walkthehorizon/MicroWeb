from rest_framework import serializers
from wallpaper.models import Snippet, Wallpaper
from django.contrib.auth.models import User


class SnippetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Snippet
        fields = ('id', 'title', 'code', 'linenos', 'language', 'style')


class WallPagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallpaper
        fields = ('id', 'name', 'describe', 'url', 'category', 'created')
        owner = serializers.ReadOnlyField(source='owner.username')


class UserSerializer(serializers.ModelSerializer):
    wallpaper = serializers.PrimaryKeyRelatedField(many=True, queryset=Wallpaper.objects.all())

    class Meta:
        model = User
        fields = ('id', 'username', 'wallpaper')
