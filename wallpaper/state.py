import json
from collections import OrderedDict

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from django.utils import six
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import exception_handler
from rest_framework import status

# 登陆注册模块
STATE_SUCCESS = 0
STATE_ERROR = -1
STATE_USER_EXIST = 1000
STATE_PASSWORD_ERROR = 1001
STATE_PHONE_ERROR = 1002
STATE_USER_NOT_EXIST = 1003
STATE_INVALID_USER = 1100
STATE_SUBJECT_NOT_EXIST = 1101
STATE_WALLPAPER_NOT_EXIST = 1200
STATE_CATEGORY_NOT_EXIST = 1300
STATE_INVALID_URL = 1301
STATE_HAS_BUY = 1401
STATE_PEA_NOT_ENOUGH = 1402
STATE_COLLECT_OVER = 1403
STATE_TODAY_HAS_SIGN = 1500

state_dict = {
    STATE_SUCCESS: '请求成功',
    STATE_ERROR: '请求异常',
    STATE_USER_EXIST: '用户已存在',
    STATE_PASSWORD_ERROR: '密码错误',
    STATE_PHONE_ERROR: '手机号错误',
    STATE_USER_NOT_EXIST: '用户不存在',
    STATE_INVALID_USER: '无效用户',
    STATE_SUBJECT_NOT_EXIST: '专题不存在',
    STATE_WALLPAPER_NOT_EXIST: '图片不存在',
    STATE_CATEGORY_NOT_EXIST: '分类不存在',
    STATE_INVALID_URL: '无效的url',
    STATE_HAS_BUY: '已购买',
    STATE_PEA_NOT_ENOUGH: '看豆不足',
    STATE_COLLECT_OVER: '可收藏量已满额，请移除部分后重试',
    STATE_TODAY_HAS_SIGN: '今日已签到',
}


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data['code'] = response.status_code
        response.data['message'] = response.data['detail']
        del response.data['detail']

    return response


class CustomResponse(Response):
    """
    An HttpResponse that allows its data to be rendered into
    arbitrary media types.
    """

    def __init__(self, data=None, code=STATE_SUCCESS,
                 status=None,
                 template_name=None, headers=None,
                 exception=False, content_type=None):
        msg = state_dict[code]
        """
        Alters the init arguments slightly.
        For example, drop 'template_name', and instead use 'data'.
        Setting 'renderer' and 'media_type' will typically be deferred,
        For example being set automatically by the `APIView`.
        """
        super(Response, self).__init__(None, status=status)

        if isinstance(data, Serializer):
            msg = (
                'You passed a Serializer instance as data, but '
                'probably meant to pass serialized `.data` or '
                '`.error`. representation.'
            )
            raise AssertionError(msg)

        self.data = {"code": code, "message": msg, "data": data}
        self.template_name = template_name
        self.exception = exception
        self.content_type = content_type

        if headers:
            for name, value in six.iteritems(headers):
                self[name] = value


class CustomPagePagination(LimitOffsetPagination):
    def get_paginated_response(self, data):
        return CustomResponse(OrderedDict([
            ('count', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('content', data)
        ]))


# 需要定制列表返回格式通过这个
class CustomPageResponse(Response):
    """
    An HttpResponse that allows its data to be rendered into
    arbitrary media types.
    """

    def __init__(self, data=None, code=None, msg=None, count=None, next=None, previous=None,
                 status=None,
                 template_name=None, headers=None,
                 exception=False, content_type=None):
        """
        Alters the init arguments slightly.
        For example, drop 'template_name', and instead use 'data'.
        Setting 'renderer' and 'media_type' will typically be deferred,
        For example being set automatically by the `APIView`.
        """
        super(Response, self).__init__(None, status=status)

        if isinstance(data, Serializer):
            msg = (
                'You passed a Serializer instance as data, but '
                'probably meant to pass serialized `.data` or '
                '`.error`. representation.'
            )
            raise AssertionError(msg)

        self.data = {"code": code, "message": msg, "data": {"count"}}
        self.template_name = template_name
        self.exception = exception
        self.content_type = content_type

        if headers:
            for name, value in six.iteritems(headers):
                self[name] = value
