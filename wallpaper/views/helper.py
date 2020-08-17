# 请求是否来自客户端最新版本
def is_old_version(request):
    version_code = request.META.get('HTTP_VERSION_CODE')
    return False if version_code is None else int(version_code) < 110


# 获取请求中的uid
def get_uid(request):
    return request.META.get('HTTP_UID')
