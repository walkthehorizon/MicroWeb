import json

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import generics
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from sts.sts import Sts

from wallpaper import models as model, state
from wallpaper.permissions import IsOwnerOrReadOnly
from wallpaper.serializers import *
from wallpaper.state import CustomResponse
import wallpaper.views.helper as util
from wallpaper.views.users import Download_Normal_Price, Download_Origin_Price


class CustomReadOnlyModelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ''
    serializer_class = ''
    permission_classes = ()
    filter_fields = ()
    search_fields = ()
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,)

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
        uid = request.META.get('HTTP_UID')
        for paper in page:
            paper.collected = UserCollectPaper.objects.filter(user_id=uid, paper_id=paper.id).exists()
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse(data=serializer.data)

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        uid = self.request.META.get('HTTP_UID')
        for paper in args[0]:
            paper.collected = UserCollectPaper.objects.filter(user_id=uid, paper_id=paper.id).exists()
        # if uid is not None:
        #     for paper in args[0]:
        #         collect_key = 'COLLECT:PAPER:' + str(paper.id) + ":UID:" + self.request.META.get('HTTP_UID')
        #         if collect_key in cache:
        #             paper.collected = cache.get(collect_key)
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)


# 获取我的收藏（按收藏时间倒序）
class GetMyCollect(generics.ListAPIView):
    serializer_class = WallPaperSerializer

    def get_queryset(self):
        uid = self.request.META.get('HTTP_UID')
        papers = []
        paper_type = model.TYPE_COS if (util.is_old_version(self.request)) else model.TYPE_ANIM
        for collect in UserCollectPaper.objects.filter(user_id=uid, paper__type=paper_type).order_by('-date'):
            papers.append(Wallpaper.objects.get(id=collect.paper_id))
        return papers


@api_view(['POST'])
def add_collect(request, pid):
    if Wallpaper.objects.filter(id=pid).exists() is False:
        return CustomResponse(code=state.STATE_WALLPAPER_NOT_EXIST)
    uid = request.META.get('HTTP_UID')
    if UserCollectPaper.objects.filter(user_id=uid, paper_id=pid).exists():
        return CustomResponse()
    if len(UserCollectPaper.objects.filter(user_id=uid)) >= 300:
        return CustomResponse(code=state.STATE_COLLECT_OVER)
    collect = UserCollectPaper(user_id=uid, paper_id=pid)
    collect.save()
    # cache.set('COLLECT:PAPER:' + str(paper.id) + ":UID:" + str(request.META.get('HTTP_UID')), True)
    return CustomResponse()


@api_view(['POST'])
def del_collect(request):
    ids = json.loads(request.body.decode(encoding='utf-8')).get('ids')
    for pid in ids:
        collect = UserCollectPaper.objects.get(user_id=util.get_uid(request), paper_id=pid)
        collect.delete()
    return CustomResponse()


@api_view(['POST'])
def buy_paper(request, pk):
    download_type = int(request.query_params.get('type'))
    resume = Download_Origin_Price if (download_type == 2) else Download_Normal_Price
    user = MicroUser.objects.get(id=util.get_uid(request))
    if user.pea < resume:
        return CustomResponse(code=state.STATE_PEA_NOT_ENOUGH)
    user.pea -= resume
    user.save()
    return CustomResponse(data=resume)


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
    if settings.DEBUG is False:
        return
    cid = request.POST.get('cid')
    return CustomResponse()
    # if cid is None or Category.objects.filter(id=cid).exists() is False:
    #     return CustomResponse(code=state.STATE_CATEGORY_NOT_EXIST)
    # logo = request.POST.get('logo')
    # if logo is None or len(logo) < 1:
    #     return CustomResponse(code=state.STATE_INVALID_URL)
    # category = Category.objects.get(id=cid)
    # category.logo = logo
    # category.save()
    # return CustomResponse()


# 设置Cos所属Banner
@api_view(['POST'])
def set_wallpaper_banner(request):
    try:
        paper = Wallpaper.objects.get(id=request.POST.get('pid'))
        paper.banner_id = request.POST.get('bid')
        paper.save()
    except Wallpaper.DoesNotExist as e:
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

    def get_queryset(self):
        if util.is_old_version(self.request):
            return Wallpaper.objects.all().filter(type=TYPE_COS).order_by('?').distinct()
        else:
            return Wallpaper.objects.all().filter(type=TYPE_ANIM).order_by('?').distinct()

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        uid = self.request.META.get('HTTP_UID')
        for paper in args[0]:
            paper.collected = UserCollectPaper.objects.filter(user_id=uid, paper_id=paper.id).exists()
            paper.collect_num = len(UserCollectPaper.objects.filter(paper_id=paper.id))

        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)


class GetNewWallpapers(generics.ListAPIView):
    serializer_class = WallPaperSerializer

    def get_queryset(self):

        if util.is_old_version(self.request):
            return Wallpaper.objects.all().filter(type=model.TYPE_COS).order_by("-created")
        else:
            return Wallpaper.objects.all().filter(type=model.TYPE_ANIM).order_by("-created")

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        uid = self.request.META.get('HTTP_UID')
        for paper in args[0]:
            paper.collected = UserCollectPaper.objects.filter(user_id=uid, paper_id=paper.id).exists()
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)


class GetRankPapers(generics.ListAPIView):
    serializer_class = WallPaperSerializer

    def get_queryset(self):
        if util.is_old_version(self.request):
            return Wallpaper.objects.all().filter(type=model.TYPE_COS).order_by("-collect_num")
        else:
            return Wallpaper.objects.all().filter(type=model.TYPE_ANIM).order_by("-collect_num")


class GetBanners(generics.ListAPIView):
    serializer_class = BannerSerializer

    def get_queryset(self):
        return Banner.objects.order_by('-created') if util.is_old_version(self.request) else []


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
    if paper.category is not None:
        result['description'] = paper.category.description
        result['title'] = paper.category.name
    if paper.subject is not None:
        result['description'] = paper.subject.description
        result['title'] = paper.subject.name
    return CustomResponse(data=result)


@api_view(['POST'])
def update_share_num(request):
    pid = str(request.POST.get('pid'))
    paper = Wallpaper.objects.get(id=pid)
    paper.share_num += 1
    paper.save()
    return CustomResponse(data=state.STATE_SUCCESS)
