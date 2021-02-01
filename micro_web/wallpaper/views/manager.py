import os

from rest_framework.decorators import api_view, permission_classes

from wallpaper import state
from wallpaper.models import Subject, Wallpaper, CHOICE_TYPE, TYPE_ANIM
from wallpaper.serializers import SubjectSerializer
from wallpaper.state import CustomResponse
from rest_framework import permissions, generics
import tinify
from qcloud_cos import CosConfig, CosServiceError
from qcloud_cos import CosS3Client
import sys
import logging
import hashlib

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
secret_id = 'AKIDFqlUxBi0JOTN3VnGVYLlCSWN5aFhlQu9'  # 替换为用户的 secretId
secret_key = 'WZSAVSXT9oRqngmdFdq8E8WkmYUBdojD'  # 替换为用户的 secretKey
region = 'ap-beijing'  # 替换为用户的 Region
config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
client = CosS3Client(config)

tinify.key = "FQU0jxywTfb0VB2xdWD05HqlqBYntdYC"  # 配置tiny key
optimized_path = "optimized.jpg"  # tiny优化后的本地路径


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


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def upload_paper(request):
    url = request.POST.get('url')
    category_id = request.POST.get('categoryId')
    if url is None or category_id is None:
        return CustomResponse(code=state.STATE_ERROR)
    if Wallpaper.objects.filter(origin_url=url).exists():
        return CustomResponse()
    try:
        source = tinify.tinify.from_url(url)
        source.to_file(optimized_path)
    except Exception as e:
        print(e)
        return CustomResponse(code=state.STATE_ERROR)
    paper = Wallpaper.objects.create(origin_url=url, type=TYPE_ANIM, category_id=category_id)
    md5 = hashlib.md5()
    md5.update(url.encode('utf-8'))
    dest_path = '/image/' + str(paper.id) + '/' + md5.hexdigest() + '.jpg'
    upload_to_cos(optimized_path, dest_path)
    paper.url = "https://wallpager-1251812446.cos.ap-beijing.myqcloud.com" + dest_path
    paper.save()
    # 删除本地临时文件
    if os.path.exists(optimized_path):
        os.remove(optimized_path)
    return CustomResponse()


def upload_to_cos(local_path, dest_path):
    # 高级上传接口（推荐）
    # 根据文件大小自动选择简单上传或分块上传，分块上传具备断点续传功能。
    try:
        response = client.upload_file(
            Bucket='wallpager-1251812446',
            LocalFilePath=local_path,
            Key=dest_path,
            PartSize=1,
            MAXThread=10,
            EnableMD5=False
        )
        # print(response)
        # print(response['ETag'])
    except CosServiceError as e:
        print(e)

