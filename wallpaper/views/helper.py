# 将要发布的最新版本
from wallpaper import models

NEWEST_VERSION = 100


# 请求是否来自客户端最新版本
def is_gentle_mode(request):
    content_mode = request.META.get('HTTP_CONTENT_MODE')
    # print(content_mode)
    return True if content_mode == str(models.TYPE_COS) else False


# 获取请求中的uid
def get_uid(request):
    return request.META.get('HTTP_UID')
