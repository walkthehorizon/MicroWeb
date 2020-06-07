from rest_framework.decorators import api_view, permission_classes

from wallpaper import state
from wallpaper.models import Subject
from wallpaper.serializers import SubjectSerializer
from wallpaper.state import CustomResponse
from rest_framework import permissions, generics


# 管理模块
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def delete_subject(request):
    sid = request.POST.get('sid')
    if sid is None or Subject.objects.filter(id=sid).exists() is False:
        return CustomResponse(code=state.STATE_SUBJECT_NOT_EXIST)
    subject = Subject.objects.get(id=sid)
    subject.delete()
    return CustomResponse()


class GetSubjects(generics.ListAPIView):
    serializer_class = SubjectSerializer
    queryset = Subject.objects.order_by("-id")
