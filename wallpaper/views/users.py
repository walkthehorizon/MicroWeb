from rest_framework import permissions, generics
from rest_framework.decorators import api_view, permission_classes

from wallpaper import state
from wallpaper.models import MicroUser, Comment, Wallpaper
from wallpaper.serializers import MicroUserSerializer, Token, CommentSerializer
from wallpaper.state import CustomResponse

Download_Normal_Price = 0
Download_Origin_Price = 1


# 用户模块

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_account_info(request):
    uuid = request.GET.get('uuid', '')
    if not MicroUser.objects.filter(uuid=uuid).exists():
        user = MicroUser(uuid=uuid)
        user.save()
    user = MicroUser.objects.get(uuid=uuid)
    data = MicroUserSerializer(user).data
    data['token'] = Token.objects.get_or_create(user=user)[0].key
    data['nPrice'] = Download_Normal_Price
    data['oPrice'] = Download_Origin_Price
    data['showDonateInterval'] = 24*60*60*1000
    return CustomResponse(data=data)


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
