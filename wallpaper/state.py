from django.http import JsonResponse
import json

# 登陆注册模块
STATE_SUCCESS = 1
STATE_USER_EXIST = 1000
STATE_PASSWORD_ERROR = 1001
STATE_PHONE_ERROR = 1002
STATE_USER_NOT_EXIST = 1003
STATE_INVALID_USER = 1100
STATE_SUBJECT_NOT_EXIST = 1101

state_dict = {
    STATE_SUCCESS: '请求成功',
    STATE_USER_EXIST: '用户已存在',
    STATE_PASSWORD_ERROR: '密码错误',
    STATE_PHONE_ERROR: '手机号错误',
    STATE_USER_NOT_EXIST: '用户不存在',
    STATE_INVALID_USER: '无效用户',
    STATE_SUBJECT_NOT_EXIST: '专题不存在',
}


def generate_result_json(state_code=STATE_SUCCESS, data=''):
    return JsonResponse({'result': state_dict.get(state_code), 'state': state_code, 'data': data})


def dump_result_json(state_code=STATE_SUCCESS, data=''):
    return json.dumps({'result': state_dict.get(state_code), 'state': state_code, 'data': data})
