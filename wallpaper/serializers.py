from rest_framework import serializers
from wallpaper.models import *


class MicroUserSerializer(serializers.ModelSerializer):
    # "id": 1,
    # "last_login": "2018-07-03T09:17:28.915275Z",
    # "username": "shentu",
    # "email": "1308311472@qq.com",
    # "date_joined": "2018-07-02T10:05:53.214821Z",
    # "nickname": "神荼",
    # "phone": "18519118029",
    # "signature": "微梦官方编辑&程序&产品！",
    class Meta:
        model = MicroUser
        fields = ('id', 'nickname', 'avatar', 'phone', 'email', 'sex', 'signature', 'pea', 'vip')


class WallPaperSerializer(serializers.ModelSerializer):
    created = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    def to_representation(self, instance):
        paper = super().to_representation(instance)
        paper['subjectId'] = instance.subject.id
        paper['categoryId'] = instance.category.id if instance.category is not None else -1
        paper['originUrl'] = instance.origin_url
        paper['collectNum'] = instance.collect_num
        paper['commentNum'] = instance.comment_num
        paper['shareNum'] = instance.share_num
        paper['downloadNum'] = instance.download_num
        return paper

    class Meta:
        model = Wallpaper
        fields = ['id', 'url', 'collected', 'created']


class SubjectSerializer(serializers.ModelSerializer):
    # wallpaper = serializers.HyperlinkedRelatedField(
    #     many=True,
    #     queryset=Wallpaper.objects.all(),
    #     view_name="wallpaper-detail")

    # owner = MicroUserSerializer()
    created = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = Subject
        fields = ('id', 'name', 'cover', 'cover_1', 'cover_2', 'description', 'tag', 'created')
        # depth = 1


class CategorySerializer(serializers.ModelSerializer):
    created = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = Category
        fields = ('id', 'name', 'logo', 'description', 'created')


class SplashSerializer(serializers.ModelSerializer):
    class Meta:
        model = Splash
        get_latest_by = 'id'
        fields = ('name', 'duration', 'cover_url', 'link_url')


class BannerSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        banner = super().to_representation(instance)
        banner['imageUrl'] = instance.image_url
        return banner

    class Meta:
        model = Banner
        fields = ('id', 'url', 'type', 'color', 'title', 'desc')


class UpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Update
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    created = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    def to_representation(self, instance):
        user_dict = super().to_representation(instance)
        user_dict['nickname'] = instance.user.nickname
        user_dict['avatar'] = instance.user.avatar
        return user_dict

    class Meta:
        model = Comment
        fields = ('content', 'created',)
