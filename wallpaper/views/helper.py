# 请求是否来自客户端最新版本
from wallpaper.state import NEWEST_APP_VERSION


# 请求是否来自客户端最新版本
def is_newest_version(request):
    return request.META.get('HTTP_VERSION_NAME') == NEWEST_APP_VERSION


# 获取请求中的uid
def get_uid(request):
    return request.META.get('HTTP_UID')
