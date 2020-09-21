import sys

from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles
from django.contrib.auth.models import AbstractUser
import random
from qcloud_cos import CosConfig, CosS3Client, CosClientError, CosServiceError
import logging

# python manage.py makemigrations TestModel  # 让 Django 知道我们在我们的模型有一些变更
# python manage.py migrate TestModel   # 创建表结构
from rest_framework.authtoken.models import Token

from MicroWeb import settings

LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
STYLE_CHOICES = sorted((item, item) for item in get_all_styles())
TYPE_COS = 0
TYPE_ANIM = 1
TYPE_MM = 2
CHOICE_TYPE = [(TYPE_COS, "Cos"), (TYPE_ANIM, "动漫"), (TYPE_MM, "写真")]
BASE_AVATAR = "	http://wallpager-1251812446.cosbj.myqcloud.com/avatar/"

# 腾讯云存储
base_cos_url = "https://wallpager-1251812446.cos.ap-beijing.myqcloud.com/"

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
secret_id = 'AKIDFqlUxBi0JOTN3VnGVYLlCSWN5aFhlQu9'
secret_key = 'WZSAVSXT9oRqngmdFdq8E8WkmYUBdojD'
region = 'ap-beijing'
config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
# 2. 获取客户端对象
client = CosS3Client(config)


class Category(models.Model):
    name = models.CharField(default="", max_length=20)
    description = models.TextField(max_length=300, default="", null=True, blank=True)
    logo = models.URLField(default="", blank=True, null=True)
    created = models.DateTimeField(verbose_name='创建日期', default=timezone.now)
    type = models.SmallIntegerField(verbose_name='类型', choices=CHOICE_TYPE, default=TYPE_COS)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.name


class Subject(models.Model):
    owner = models.ForeignKey(to='MicroUser', default=1, on_delete=models.CASCADE, related_name='subject_owner')
    name = models.CharField(default="", max_length=120, blank=True)
    type = models.SmallIntegerField(verbose_name='类型', choices=CHOICE_TYPE, default=TYPE_COS)
    description = models.TextField(max_length=300, default="", blank=True, null=True)
    cover = models.URLField(default="", blank=True)
    cover_1 = models.URLField(default="", blank=True)
    cover_2 = models.URLField(default="", blank=True)
    tag = models.CharField(max_length=60, default="", blank=True)
    created = models.DateTimeField(verbose_name='创建日期', default=timezone.now)
    # 魅族、半次元、 MM131
    source = models.CharField(default="", max_length=60)
    # 数据来源id
    source_id = models.CharField(max_length=30, default="", blank=True)
    # # 点赞&收藏
    # support_people = models.ManyToManyField(to='MicroUser', on_delete=models.CASCADE, related_name='subject_support',
    #                                         blank=True)
    supported = models.BooleanField(default=False)

    # bcy_id = models.CharField(max_length=30, default="", blank=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.name


class Wallpaper(models.Model):
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, blank=True, null=True)
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE, blank=True, null=True)
    banner = models.ForeignKey('Banner', on_delete=models.SET_NULL, blank=True, null=True)
    url = models.URLField(default="")
    origin_url = models.URLField(default="")
    sw = models.IntegerField(default=0, blank=True)
    sh = models.IntegerField(default=0, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    type = models.SmallIntegerField(verbose_name='类型', choices=CHOICE_TYPE, default=TYPE_COS)
    # 魅族、半次元、 MM131
    source = models.CharField(verbose_name='来源', default="", max_length=60)
    # 数据来源id
    source_id = models.CharField(max_length=30, default="", blank=True)
    collect_num = models.IntegerField(default=0)
    comment_num = models.IntegerField(default=0)
    share_num = models.IntegerField(default=0)
    download_num = models.IntegerField(default=0)
    collected = models.BooleanField(default=False)

    class Meta:
        ordering = ('id',)

    # def __str__(self):
    #     return self.name


@receiver(post_delete, sender=Wallpaper)
def delete_cos_picture(sender, instance, **kwargs):
    picture_url = getattr(instance, 'url', '')
    if not picture_url:
        return
    client.delete_object(
        Bucket='wallpager-1251812446',
        Key=str(picture_url).replace(base_cos_url, '')
    )


# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def create_auth_token(sender, instance=None, created=False, **kwargs):
#     if created:
#         Token.objects.create(user=instance)


class Splash(models.Model):
    duration = models.IntegerField(default=0)
    name = models.CharField(default="", max_length=30, blank=True)
    cover_url = models.URLField(default="")
    link_url = models.URLField(default="", blank=True, )
    created = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=20)


class Banner(models.Model):
    subject_id = models.IntegerField()
    image_url = models.URLField()
    url = models.URLField(blank=True)
    type = models.SmallIntegerField()
    title = models.CharField(max_length=36, blank=True)
    desc = models.TextField(max_length=300, blank=True)
    color = models.CharField(max_length=10, blank=True)
    created = models.DateTimeField(auto_now_add=True)


class MicroUser(AbstractUser):
    uuid = models.CharField(max_length=30, blank=True, null=True)
    nickname = models.CharField(max_length=30, blank=True, default="微梦用户")
    phone = models.CharField(max_length=11, blank=True, null=True)
    signature = models.TextField(max_length=200, blank=True)
    sex = models.SmallIntegerField(default=0)
    avatar = models.URLField(default="")
    last_sign = models.DateTimeField(default=timezone.now)
    pea = models.IntegerField(default=10)
    vip = models.BooleanField(default=False)

    class Meta(AbstractUser.Meta):
        pass


class UserCollectPaper(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(MicroUser, on_delete=models.DO_NOTHING)
    paper = models.ForeignKey(Wallpaper, on_delete=models.DO_NOTHING)
    date = models.DateTimeField(verbose_name='添加日期', default=timezone.now)


class Update(models.Model):
    id = models.AutoField(primary_key=True)
    appUrl = models.URLField(default="")
    updateInfo = models.CharField(max_length=120)
    isForce = models.BooleanField(default=False)
    versionCode = models.SmallIntegerField()
    versionName = models.CharField(max_length=12)


class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    content = models.TextField()
    paper = models.ForeignKey(Wallpaper, models.CASCADE)
    user = models.ForeignKey(MicroUser, models.SET_NULL, null=True)
    created = models.DateTimeField(auto_now_add=True)


class Config(models.Model):
    newest_version = models.IntegerField(verbose_name='版本号', default=100, help_text='当前App最新的版本号')
