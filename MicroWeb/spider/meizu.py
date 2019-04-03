from urllib import request
from urllib import error
from urllib import parse
import socket
import json
import os
import django

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MicroWeb.settings')
    django.setup()

from wallpaper.models import *

#
# for data in Wallpaper.objects.all():
#     print('id', 'subjectId', data.id, data.subject_id)
#     data.category_id = data.subject_id
#     data.save()
category_list = {9000: 8, 9013: 7, 9008: 6, 9009: 5, 9015: 4, 9014: 3, 9012: 2}
base_api = 'http://api-theme.meizu.com'
meizu_subject = '/wallpapers/public/v4.1/special/layout'
meizu_category = '/wallpapers/public/v6.0/category/layout'


def save_category_detail():
    data = bytes(parse.urlencode({'mzos': '6.0', 'screen_size': '1080x1920'}),
                 encoding='UTF-8')
    try:
        response = request.urlopen(base_api + meizu_category, data=data)
        data = json.loads(response.read().decode('utf-8'))['value']['blocks'][0]['data']
        for category in data:
            local_category_id = category_list.get(category['id'])
            if local_category_id is None:
                continue
            category_url = category['url']
            print("开始获取分类：" + category_url)
            get_real_category_url(category_url, local_category_id)
    except error as e:
        print("获取分类错误", e)


def get_real_category_url(category_url, local_category_id):
    data = bytes(parse.urlencode({'mzos': '6.0', 'screen_size': '1080x1920'}),
                 encoding='UTF-8')
    try:
        response = request.urlopen(base_api + category_url, data=data)
        category_real_url = json.loads(response.read().decode('utf-8'))['value']['blocks'][0]['url']
        print("获取到真实分类：" + category_real_url)
        save_picture_from_category(category_real_url, local_category_id)
    except error as e:
        print("获取真正的分类错误", e)


def save_picture_from_category(category_detail_url, local_category_id):
    data = bytes(parse.urlencode({'mzos': '6.0', 'screen_size': '1080x1920', 'start': '0', 'max': '500'}),
                 encoding='UTF-8')
    try:
        response = request.urlopen(base_api + category_detail_url, data=data)
        data = json.loads(response.read().decode('utf-8'))['value']['data']
        for paper in data:
            picture = Wallpaper(source=paper.get('cp_name'), small_url=paper.get('small_pap_address'),
                                big_url=paper.get('big_pap_address'), category_id=local_category_id,
                                owner_id=1)
            picture.save()
            print(str(paper.get('id')) + " 保存成功")
    except error.URLError as e:
        if isinstance(e.reason, socket.timeout):
            print("获取魅族主题超时")


def save_subject():
    try:
        data = bytes(parse.urlencode({'mzos': '6.0', 'screen_size': '1080x1920', 'start': '0', 'max': '300'}),
                     encoding='UTF-8')
        response = request.urlopen(base_api + meizu_subject, data=data)
        blocks_list = json.loads(response.read().decode('utf-8'))['value']['blocks']
        i = 0
        for special in blocks_list:
            i += 1
            subject_data = special['data'][0]
            print(i, subject_data['id'])
            if is_exist_subject(subject_data['logo']):
                continue
            subject = Subject(name=subject_data['name'], cover=subject_data['logo'],
                              description=subject_data['description'])
            subject.save()
            list_url = base_api + subject_data['url']
            save_subject_paper(list_url, subject.id)

    except error as e:
        print(e)


def save_subject_paper(url, subject_id):
    try:
        data = bytes(parse.urlencode({'mzos': '6.0', 'screen_size': '1080x1920', 'start': '0', 'max': '500'}),
                     encoding='UTF-8')
        response = request.urlopen(url, data=data)
        wallpaper_list = json.loads(response.read().decode('utf-8'))['value']['wallpapers']
        for picture in wallpaper_list:
            wallpaper = Wallpaper(owner=MicroUser.objects.all().get(username="shentu"), subject_id=subject_id,
                                  small_url=picture['small_pap_address'], category=None,
                                  big_url=picture['big_pap_address']
                                  , name=picture['cp_name'])
            wallpaper.save()
    except error as e:
        print(e)


def is_exist_subject(logo):
    for s in Subject.objects.all():
        if s.cover == logo:
            return True
    return False


# save_category_detail()
from wallpaper.models import Wallpaper

wallpapers = Wallpaper.objects.all()
for item in wallpapers:
    item.url = item.url.replace("wallpager-1251812446.file.myqcloud.com", "wallpager-1251812446.cos.ap-beijing.myqcloud.com")
    item.save()
