import json

from django.db.models import Q
from django_filters import rest_framework
from rest_framework import filters
from rest_framework import generics
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.decorators import api_view
from sts.sts import Sts

from wallpaper import models as model
from wallpaper import state
from wallpaper.permissions import IsOwnerOrReadOnly
from wallpaper.serializers import *
from wallpaper.state import CustomResponse
from rest_framework.response import Response
from django_redis import get_redis_connection

con = get_redis_connection("default")


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
def register_user(request):
    # print(request)
    # print(request.data)
    phone = request.data.get('phone')
    if len(phone) != 11:
        return CustomResponse(code=state.STATE_PHONE_ERROR)
    # user = auth.authenticate(username=phone, password=password)
    if MicroUser.objects.exists(phone=phone) is True:
        return CustomResponse(code=state.STATE_USER_EXIST)
    user = MicroUser.objects.create(username=phone, phone=phone, password='')
    user.save()
    return CustomResponse()


@api_view(['POST'])
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
    return CustomResponse(data=MicroUserSerializer(user).data)
    # if user.password == password:
    #     # Correct password, and the user is marked "active"
    #     # auth.login(request, user)
    # else:
    #     # Show an error page
    #     return CustomResponse(code=state.STATE_PASSWORD_ERROR)


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
    policy = {'version': '2.0', 'statement': [{'action': ['name/cos:PutObject'], 'effect': 'allow',
                                               'resource': [
                                                   'qcs::cos:ap-beijing:uid/1251812446:wallpager-1251812446/*']}]}
    config = {
        # 临时密钥有效时长，单位是秒
        'duration_seconds': 1800,
        # 固定密钥
        'secret_id': model.secret_id,
        # 固定密钥
        'secret_key': model.secret_key,
        # 设置 策略 policy, 可通过 get_policy(list)获取
        'policy': policy
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
    filter_fields = ('subject_id', 'category_id')

    # def perform_create(self, serializer):
    #     serializer.save(owner=self.request.user)


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
        paper = Wallpaper.objects.filter(id=pid)
    except Wallpaper.DoesNotExist:
        return CustomResponse(code=state.STATE_WALLPAPER_NOT_EXIST)
    try:
        user = MicroUser.objects.get(id=request.META.get('HTTP_UID'))
    except MicroUser.DoesNotExist:
        return CustomResponse(code=state.STATE_USER_NOT_EXIST)
    if user.collects.filter(id=paper.id).exists():
        return CustomResponse()
    user.collects.add(wallpaper_id=pid)
    user.save()
    # print(str("collect_num:" + str(con.hincrby("wallpaper:" + str(pid), "collect_num"))))
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
    pea = int(request.query_params.get('pea'))
    if pea < 1 or pea > 3:
        return CustomResponse(code=state.STATE_ERROR)
    if user.pea < pea:
        return CustomResponse(code=state.STATE_PEA_NOT_ENOUGH)
    if user.buys.filter(id=paper.id).exists():
        return CustomResponse()
    user.pea = user.pea - pea
    user.buys.add(paper)
    user.save()
    return CustomResponse()


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
            return Subject.objects.filter(Q(name__contains=key) | Q(description__contains=key))


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


class GetPictureByCategoryId(generics.ListAPIView):
    serializer_class = WallPaperSerializer
    lookup_field = 'id'

    def get_queryset(self):
        # print(self.request.query_params.keys())
        return Wallpaper.objects.filter(category_id=self.kwargs.get('id'))


class GetSubjectWallpaper(generics.ListAPIView):
    serializer_class = WallPaperSerializer
    lookup_field = 'id'

    def get_queryset(self):
        # print(self.request.query_params.keys())
        return Wallpaper.objects.filter(subject_id=self.kwargs.get('pk'))


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


class BannerViewSet(CustomReadOnlyModelViewSet):
    serializer_class = BannerSerializer
    queryset = Banner.objects.order_by('-created')


class UserUpdate(generics.UpdateAPIView):
    serializer_class = MicroUserSerializer
    queryset = MicroUser.objects.all()

# @api_view(['PUT'])
# def put_subject_support(request):
#     user = request.user
#     if user is None or not user.is_active:
#         return generate_result_json(state_code=state.STATE_INVALID_USER)
#     subject_id = request.data.get('subjectId')
#     support_type = request.data.get('type')
#     subject = Subject.objects.get(id=subject_id)
#     if subject is None:
#         return generate_result_json(state_code=state.STATE_SUBJECT_NOT_EXIST)
#     if support_type == '1':
#         subject.support_people.add(user)
#     if support_type == '-1':
#         subject.support_people.remove(user)
#     # print(subject.support_people.all())
#     return generate_result_json(state_code=state.STATE_SUCCESS)
#
#
# @api_view(['GET'])
# def get_subject_support_count(request):
#     lookup_field = 'subjectId'
#     return generate_result_json(state_code=state.STATE_SUCCESS)
#     # subject_id = request.GET.get('subjectId', '2853')
#     # subject = Subject.objects.get(id=subject_id)
#     # if subject is None:
#     #     return generate_result_json(state_code=state.STATE_SUBJECT_NOT_EXIST)
#     # return generate_result_json(state_code=state.STATE_SUCCESS, data=str(len(subject.support_people.all())))
#
#
# class GetSubjectSupportCount(generics.GenericAPIView):
#     lookup_field = 'subjectId'
#
#     def get(self, request, subjectId):
#         try:
#             subject = Subject.objects.get(id=subjectId)
#         except Subject.DoesNotExist:
#             return Response(generate_result_json(state_code=state.STATE_SUBJECT_NOT_EXIST).content)
#         return Response(dump_result_json(state_code=state.STATE_SUCCESS, data=len(subject.support_people.all())))
