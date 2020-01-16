import json
import time

import requests
from django.http import HttpResponse
from django_filters import rest_framework
from rest_framework import filters
from rest_framework import generics
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from sts.sts import Sts

from wallpaper import models as model
from wallpaper import state
from wallpaper.permissions import IsOwnerOrReadOnly
from wallpaper.serializers import *
from wallpaper.sign import Sign
from wallpaper.state import CustomResponse

from django.core.cache import cache


class CustomReadOnlyModelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ''
    serializer_class = ''
    permission_classes = ()
    filter_fields = ()
    search_fields = ()
    filter_backends = (rest_framework.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse(data=serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return CustomResponse(data=serializer.data)


# 注册登录模块

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_user(request):
    phone = request.data.get('phone')
    if len(phone) != 11:
        return CustomResponse(code=state.STATE_PHONE_ERROR)
    # user = auth.authenticate(username=phone, password=password)
    if MicroUser.objects.filter(phone=phone).exists() is True:
        return CustomResponse(code=state.STATE_USER_EXIST)
    user = MicroUser.objects.create(username=phone, phone=phone, password='')
    user.save()
    return CustomResponse()


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_user(request):
    phone = request.POST.get('phone', '')
    if len(phone) != 11:
        return CustomResponse(code=state.STATE_PHONE_ERROR)
    if MicroUser.objects.filter(phone=phone).exists():
        user = MicroUser.objects.get(phone=phone)
    else:
        user = MicroUser.objects.create(username=phone, phone=phone, password='')
    # user = auth.authenticate(username=username, password=password)
    user.isLogin = True
    user.save()
    data = MicroUserSerializer(user).data
    data['token'] = Token.objects.get_or_create(user=user)[0].key
    return CustomResponse(data=data)


@api_view(['POST'])
def logout_user(request):
    # auth.logout(request)
    # print(request.META.get('HTTP_UID'))
    try:
        user = MicroUser.objects.get(id=request.META.get('HTTP_UID'))
    except MicroUser.DoesNotExist:
        return CustomResponse(code=state.STATE_USER_NOT_EXIST)
    user.isLogin = False
    user.save()
    return CustomResponse()


# 获取Cos临时密钥
@api_view(['GET'])
def get_temp_secret_key(request):
    config = {
        # 临时密钥有效时长，单位是秒
        'duration_seconds': 1800,
        # 固定密钥
        'secret_id': model.secret_id,
        # 固定密钥
        'secret_key': model.secret_key,
        # 换成你的 bucket
        'bucket': 'wallpager-1251812446',
        # 换成 bucket 所在地区
        'region': 'ap-beijing',
        # 这里改成允许的路径前缀，可以根据自己网站的用户登录态判断允许上传的具体路径
        # 例子： a.jpg 或者 a/* 或者 * (使用通配符*存在重大安全风险, 请谨慎评估使用)
        'allow_prefix': 'avatar/*',
        # 密钥的权限列表。简单上传和分片需要以下的权限，其他权限列表请看 https://cloud.tencent.com/document/product/436/31923
        'allow_actions': [
            # 简单上传
            'name/cos:PutObject',
        ]
    }

    sts = Sts(config)
    response = sts.get_credential()
    # return CustomResponse(data=json.loads(json.dumps(response)))
    # print(json.loads(json.dumps(response)))
    return Response(response)


# 基础类的只读路由
class WallPapersViewSet(CustomReadOnlyModelViewSet):
    # permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)
    queryset = Wallpaper.objects.all()
    serializer_class = WallPaperSerializer
    filter_fields = ('subject_id', 'category_id', 'banner_id')

    # 筛选用户收藏
    def filter_queryset(self, queryset):
        uid = self.request.query_params.get('uid')
        if uid is None or uid == -1:
            return super().filter_queryset(queryset)
        try:
            user = MicroUser.objects.get(id=uid)
        except MicroUser.DoesNotExist:
            return super().filter_queryset(queryset)
        return user.collects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        users = MicroUser.objects.filter(id=request.META.get('HTTP_UID'))
        if users.exists():
            user = users.first()
            for paper in page:
                paper.collected = user.collects.filter(id=paper.id).exists()
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse(data=serializer.data)


class GetPaperComments(generics.ListAPIView):
    serializer_class = CommentSerializer
    lookup_field = 'paper_id'
    queryset = Comment.objects.all()

    def filter_queryset(self, queryset):
        paper_id = self.request.query_params.get('paper_id')
        print(paper_id)
        return queryset.filter(paper_id=paper_id)


@api_view(['POST'])
def add_paper_comment(request):
    uid = request.META.get('HTTP_UID')
    pid = request.POST.get('pid')
    content = request.POST.get('content')
    if uid is None or pid is None or content is None or MicroUser.objects.filter(id=uid).exists() is False \
            or Wallpaper.objects.filter(id=pid).exists() is False:
        return CustomResponse(data=state.STATE_ERROR)
    comment = Comment(content=content, paper_id=pid, user_id=uid)
    comment.save()
    paper = Wallpaper.objects.get(id=pid)
    paper.comment_num += 1
    paper.save()
    return CustomResponse(CommentSerializer(comment).data)


class GetMyCollect(generics.ListAPIView):
    serializer_class = WallPaperSerializer

    def get_queryset(self):
        uid = self.request.META.get('HTTP_UID')
        if uid is None:
            return None
        return MicroUser.objects.get(id=uid).collects.all()


@api_view(['POST'])
def add_collect(request, pid):
    try:
        paper = Wallpaper.objects.get(id=pid)
    except Wallpaper.DoesNotExist:
        return CustomResponse(code=state.STATE_WALLPAPER_NOT_EXIST)
    try:
        user = MicroUser.objects.get(id=request.META.get('HTTP_UID'))
    except MicroUser.DoesNotExist:
        return CustomResponse(code=state.STATE_USER_NOT_EXIST)
    if paper.users.filter(id=user.id).exists():
        return CustomResponse()
    if paper.collect_num >= 300:
        return CustomResponse(code=state.STATE_COLLECT_OVER)
    user.collects.add(paper)
    paper.collect_num = paper.collect_num + 1
    paper.save()
    user.save()
    cache.set('COLLECT:PAPER:' + str(paper.id) + ":UID:" + str(request.META.get('HTTP_UID')), True)
    return CustomResponse()


@api_view(['POST'])
def del_collect(request):
    ids = json.loads(request.body.decode(encoding='utf-8')).get('ids')
    try:
        user = MicroUser.objects.get(id=request.META.get('HTTP_UID'))
    except MicroUser.DoesNotExist:
        return CustomResponse(code=state.STATE_USER_NOT_EXIST)
    papers = []
    for pid in ids:
        try:
            paper = Wallpaper.objects.get(id=pid)
            papers.append(paper)
        except Wallpaper.DoesNotExist:
            return CustomResponse(code=state.STATE_WALLPAPER_NOT_EXIST)
        try:
            user.collects.remove(paper)
        except KeyError:
            return CustomResponse(code=state.STATE_ERROR)
        paper.collect_num = paper.collect_num - 1
    for paper in papers:
        paper.save()
    user.save()
    return CustomResponse()


@api_view(['POST'])
def buy_paper(request, pk):
    try:
        user = MicroUser.objects.get(id=request.META.get('HTTP_UID'))
    except MicroUser.DoesNotExist:
        return CustomResponse(code=state.STATE_USER_NOT_EXIST)
    try:
        paper = Wallpaper.objects.get(id=pk)
    except Wallpaper.DoesNotExist:
        return CustomResponse(code=state.STATE_WALLPAPER_NOT_EXIST)
    download_type = int(request.query_params.get('type'))
    if download_type != 1 and download_type != 2:
        return CustomResponse(code=state.STATE_ERROR)
    # if user.buys.filter(id=paper.id).exists():
    #     return CustomResponse(code=state.STATE_HAS_BUY)
    resume = (3 if (download_type == 2) else 1)
    if user.pea < resume:
        return CustomResponse(code=state.STATE_PEA_NOT_ENOUGH)
    user.pea = user.pea - resume
    # user.buys.add(paper)
    user.save()
    return CustomResponse(data=resume)


class CategoryViewSet(CustomReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class WallPaperDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)
    queryset = Wallpaper.objects.all()
    serializer_class = WallPaperSerializer


# 依照type筛选数据
class SubjectViewSet(CustomReadOnlyModelViewSet):
    lookup_field = 'id'
    serializer_class = SubjectSerializer
    search_fields = ('id', 'name', 'description',)
    queryset = Subject.objects.all()

    def get_queryset(self):
        key = self.request.query_params.get('key')
        if key is None:
            return Subject.objects.all()
        else:
            return Subject.objects.filter(name__contains=key)


# 更新Category封面
@api_view(['POST'])
def update_category_cover(request):
    cid = request.POST.get('cid')
    if cid is None or Category.objects.filter(id=cid).exists() is False:
        return CustomResponse(code=state.STATE_CATEGORY_NOT_EXIST)
    logo = request.POST.get('logo')
    if logo is None or len(logo) < 1:
        return CustomResponse(code=state.STATE_INVALID_URL)
    category = Category.objects.get(id=cid)
    category.logo = logo
    category.save()
    return CustomResponse()


# 设置Cos所属Banner
@api_view(['POST'])
def set_wallpaper_banner(request):
    try:
        paper = Wallpaper.objects.get(id=request.POST.get('pid'))
        paper.banner_id = request.POST.get('bid')
        paper.save()
    except Wallpaper.DoesNotExist as e:
        print(e)
        return CustomResponse(data=False)
    return CustomResponse(True)


# 获取所有分类
class CategoryList(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    # def perform_create(self, serializer):
    #     serializer.save(owner=self.request.user)


# 获取启动页数据
class GetSplash(generics.RetrieveAPIView):
    serializer_class = SplashSerializer
    queryset = Splash.objects.all().order_by('-id')

    def get_object(self):
        return self.queryset[0]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return CustomResponse(serializer.data)


class GetRandomRecommend(generics.ListAPIView):
    serializer_class = WallPaperSerializer
    queryset = Wallpaper.objects.all().order_by('?').distinct()

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        for paper in args[0]:
            collect_key = 'COLLECT:PAPER:' + str(paper.id) + ":UID:" + self.request.META.get('HTTP_UID')
            if collect_key in cache:
                paper.collected = cache.get(collect_key)
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)


class GetNewWallpapers(generics.ListAPIView):
    serializer_class = WallPaperSerializer
    queryset = Wallpaper.objects.all().order_by("-created")


class BannerViewSet(CustomReadOnlyModelViewSet):
    serializer_class = BannerSerializer
    queryset = Banner.objects.order_by('-created')


class UserUpdate(generics.UpdateAPIView):
    serializer_class = MicroUserSerializer
    queryset = MicroUser.objects.all()


@api_view(['GET'])
def get_update_info(request):
    if Update.objects.count() < 1:
        update = Update(versionCode=0)
    else:
        update = Update.objects.order_by('-id')[0]
    return CustomResponse(data=UpdateSerializer(update).data)


@api_view(['GET'])
def get_is_sign(request):
    try:
        user = MicroUser.objects.get(id=request.META.get('HTTP_UID'))
    except MicroUser.DoesNotExist:
        return CustomResponse(code=state.STATE_USER_NOT_EXIST)
    if timezone.now().date() == user.last_sign.date():
        return CustomResponse(code=state.STATE_TODAY_HAS_SIGN)
    user.last_sign = timezone.now()
    reward = 30 if user.vip else 10
    user.pea += reward
    user.save()
    return CustomResponse(data=reward)


# 获取带有Subject信息的Paper
@api_view(['GET'])
def get_paper_for_web(request, pk):
    paper = Wallpaper.objects.get(id=pk)
    result = json.loads(json.dumps(WallPaperSerializer(paper).data))
    result['description'] = paper.subject.description
    result['title'] = paper.subject.name
    return CustomResponse(data=result)


@api_view(['GET'])
def check_gzh_signature(request):
    print(request.GET['echostr'])
    return HttpResponse(request.GET['echostr'], content_type="text/plain")


@api_view(['GET'])
def get_wx_js_signature(request):
    access_token = cache.get('GZH:ACCESS_TOKEN')
    if access_token is None:
        res = requests.get(
            "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=wxeb10ca693233a27c&secret"
            "=69a3bde51f96b3d335c0a1eeeabb7c99")
        access_token = res.json().get('access_token')
        cache.set('GZH:ACCESS_TOKEN', access_token, ex=res.json().get('expires_in'))
    js_ticket = cache.get('GZH:JS_TICKET')
    if js_ticket is None:
        res = requests.get(
            'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=' + access_token + '&type=jsapi')
        js_ticket = res.json().get('ticket')
        cache.set('GZH:JS_TICKET', js_ticket, ex=res.json().get('expires_in'))
    sign = Sign(js_ticket, request.GET.get('url'))
    return CustomResponse(data=sign.sign())


@api_view(['POST'])
def update_share_num(request):
    pid = str(request.POST.get('pid'))
    paper = Wallpaper.objects.get(id=pid)
    paper.share_num += 1
    paper.save()
    return CustomResponse(data=state.STATE_SUCCESS)
