# -*- coding=utf-8
import requests
import socket
import json
import os
import django
from qiniu import Auth, put_file, etag
import qiniu.config
import base64
from Cryptodome.Cipher import AES
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import logging
import time
import tinify

# 本虫使用方法，首先通过半次元日榜排行查看你需要的数据，以排名为准输入其排名,传递一个tuple即可，入口方法：start_bcy_spider
# 已上传日期记录[0817,0825]
# 腾讯云存储
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
secret_id = 'AKIDc8TgYF5ANO5h8BkwWv89nHajgWCha73n'  # 替换为用户的 secretId
secret_key = 'hLsEOPFuOkxzqVyHOK4d1DF6mGYfsxrZ'  # 替换为用户的 secretKey
region = 'ap-beijing'  # 替换为用户的 Region
config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
# 2. 获取客户端对象
client = CosS3Client(config)

# tiny压缩
tinify.key = "9HsFvbIYmXf8ykQrVdcDTBiikR1AStww"

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MicroWeb.settings')
    django.setup()

from wallpaper.models import *

# data真实内容  {"date":"20180719","grid_type":"timeline","token":"4b98b48cb5b20e72","p":"1","type":"week"}

# 半次元万能Post地址
bcy_detail_url = "https://api.bcy.net/api/item/detail/"
bcy_list_url = "https://api.bcy.net/api/coser/topList/"
bcy_collect_url = "https://api.bcy.net/api/space/getUserLikeTimeline"
headers = {'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 8.0.0; BKL-AL20 Build/HUAWEIBKL-AL20)',
           'X-BCY-Version': 'Android-4.1.2', 'Content-Type': 'application/x-www-form-urlencoded',
           'Host': 'api.bcy.net'}
query_data = {'iid': '36046028020', 'device_id': '46019894537', 'ac': 'wifi', 'channel': 'huawei', 'aid': '1250',
              'app_name': 'banciyuan', 'version_code': '412', 'version_name': '4.1.2', 'device_platform': 'android',
              'ssmix': 'a', 'device_type': 'BKL-AL20', 'device_brand': 'HONOR', 'language': 'zh', 'os_api': '26',
              'os_version': '8.0.0', 'uuid': '866953034499460', 'openudid': '56028d53b0cb3095',
              'manifest_version_code': '20180605', 'resolution': '1080*2160', 'dpi': '480',
              'update_version_code': '412', '_rticket': str(int(time.time()))}

base_image_cloud_path = 'http://wallpager-1251812446.cosbj.myqcloud.com/image'


# str不是16的倍数那就补足为16的倍数
def add_to_16(text, escape):
    while len(text) % 16 != 0:
        text += escape  # 详情是04,排行是05
    return str.encode(text)  # 返回bytes


def add_escape(text, escape):
    i = 16
    while i != 0:
        i = i - 1
        text += escape
    # print(len(text))
    return str.encode(text)


def generate_encrypt_data(dict1, escape):
    key = 'com_banciyuan_AI'
    # print(dict1)
    data_json = json.dumps(dict1).replace(' ', '')  # 移除多余的空格
    # print(data_json + "\n")
    # print(list(data_json))
    cipher = AES.new(add_to_16(key, '\x05'), AES.MODE_ECB)
    # print(add_escape(data_json, escape))
    if escape == '\x10':
        encrypted_text = str(base64.encodebytes(cipher.encrypt(add_escape(data_json, escape))),
                             encoding='utf8').replace('\n', '')
    else:
        encrypted_text = str(base64.encodebytes(cipher.encrypt(add_to_16(data_json, escape))), encoding='utf8').replace(
            '\n', '')
    print(encrypted_text)
    # print(len(encrypted_text))
    # encrypted_text = "ZUF3b+KH7Q/4/fUehqr0f+8chio5X2Byih1jgOFGieQG18gdrghcz7UvY+gWEtE0PtCMYvsmev07\ngpxKbwumvA=="
    # text_decrypted = str(cipher.decrypt(base64.decodebytes(bytes(encrypted_text, encoding='utf8'))).rstrip(b'\x05').decode("utf8"))  # 解密
    # print(encrypted_text)
    # print(len(encrypted_text))
    # print(text_decrypted)
    # print(list(text_decrypted))
    return encrypted_text


# def get_cos_play_subject_by_id(item_id, rank_pos):
#     dict_data = {"token": "3e6ac2ddeb8064ac", "item_id": item_id}
#     query_data['data'] = generate_encrypt_data(dict_data, '\x04')
#     detail_data = requests.post(bcy_detail_url, headers=headers, data=query_data)
#     print(detail_data.text)
#     detail_json = detail_data.json()["data"]
#     # print(detail_json)
#     return
#     multi_pic = detail_json['multi']
#     tag = detail_json['work']
#     desc = detail_json['plain']
#     name = tag
#     print(tag)
#     subject = Subject(owner_id=1, name=name, description=desc, tag=name, type=2)
#     subject.save()
#     i = 1
#     for pic in multi_pic:
#         path = pic['path'].replace('/w650', '')
#         dir_name = 'id_' + str(subject.id) + '_' + 'type_2' + '_' + date + '_' + str(rank_pos)
#         file_name = str(i) + '.jpg'
#         cloud_image_path = base_image_cloud_path + '/' + dir_name + '/' + file_name
#         if i == 1:
#             subject.cover = cloud_image_path.replace('cosbj', 'picbj')
#             subject.save()
#         create_new_wallpaper(subject.id, cloud_image_path, pic['w'], pic['h'])
#         i = i + 1
#         save_pic_to_disk(path, file_name, dir_name)
#     print("\n#################" + item_id + " 抓取完成")


def create_new_wallpaper(subject_id, pic_url, sw, sh):
    wallpaper = Wallpaper(small_url=pic_url.replace('cosbj', 'picbj') + "!w650", sw=sw, sh=sh, big_url=pic_url,
                          category_id=1, subject_id=subject_id,
                          owner_id=1)
    wallpaper.save()
    print("\n数据库对象存储成功：" + str(wallpaper.id))


def save_pic_to_disk(url, file_name, dir_name):
    dir_path = "S://bcy/" + dir_name
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    file_path = dir_path + "/" + file_name
    try:
        print("开始tiny压缩：" + url)
        source = tinify.from_url(url)
        source.to_file(file_path)
        print("压缩完成：" + file_path + " tiny已用次数：%s", tinify.compression_count)
        save_pic_to_txcloud(dir_name + '/' + file_name, file_path)
    except tinify.ClientError as e:
        print(url + "  " + e.message)
    except tinify.ServerError as e:
        print(url + "  " + e.message)
        save_pic_to_disk(url, file_name, dir_name)
    except tinify.ConnectionError as e:
        print(url + "  " + e.message)
        save_pic_to_disk(url, file_name, dir_name)
    except tinify.AccountError as e:
        print(url + "  " + e.message)
    # print("请求写入图片：" + url)
    # r = requests.post(url)
    # with open(file_path, 'wb+') as f:
    #     f.write(r.content)
    # print("写入完成：" + file_path)


def save_pic_to_txcloud(file_name, localfile):
    print("开始上传到腾讯云Cos")
    # key上传到七牛后保存的文件名
    try:
        response = client.put_object_from_local_file(
            Bucket='wallpager-1251812446',
            LocalFilePath=localfile,
            Key="image/" + file_name,
        )
        print("上传完成：" + response['ETag'])
    except FileNotFoundError as e:
        print("文件不存在，上传失败" + localfile)


#
def get_detail_encrypt():
    dict_data = {"token": "3e6ac2ddeb8064ac", "item_id": '6588244326256476429'}
    generate_encrypt_data(dict_data, '\x04')


# 获取Cos日榜数据
def get_rank_encrypt_data():
    dict_data = {"date": "20180813", "grid_type": "timeline", "token": "3e6ac2ddeb8064ac", "p": "1", "type": "lastday"}
    generate_encrypt_data(dict_data, '\x02')

get_detail_encrypt()
get_rank_encrypt_data()


# # 通过日排行进行爬取
# def get_cos_rank_list(rank, page, date):
#     if len(rank) == 0:
#         return
#     dict_data = {"date": date, "grid_type": "timeline", "token": "3e6ac2ddeb8064ac", "p": str(page),
#                  "type": "lastday"}
#     query_data['data'] = generate_encrypt_data(dict_data, '\x02')
#     rank_data = requests.post(bcy_list_url, headers=headers, data=query_data).json()['data']
#     for i in rank:
#         item_id = rank_data[i]['item_detail']['item_id']
#         pos = (page - 1) * 20 + i + 1
#         print("开始抓取第" + str(pos) + "个，id：" + item_id + "#################")
#         get_cos_play_subject_by_id(item_id, pos)


# def start_bcy_spider(rank_tuple, date):
#     list1 = []
#     list2 = []
#     list3 = []
#     for i in rank_tuple:
#         if i <= 20:
#             list1.append(i - 1)
#         if 20 < i <= 40:
#             list2.append(i % 20 - 1)
#         if i > 40:
#             list3.append(i % 20 - 1)
#     get_cos_rank_list(list1, 1, date)
#     get_cos_rank_list(list2, 2, date)
#     get_cos_rank_list(list3, 3, date)


def get_cosplay_subject_by_id(item_id):
    dict_data = {"token": "3e6ac2ddeb8064ac", "item_id": item_id}
    query_data['data'] = generate_encrypt_data(dict_data, '\x04')
    detail_data = requests.post(bcy_detail_url, headers=headers, data=query_data)
    print(detail_data.text)
    detail_json = detail_data.json()["data"]
    # print(detail_json)
    multi_pic = detail_json['multi']
    if 'work' in detail_json:
        tag = detail_json['work']
    else:
        tag = ''
    desc = detail_json['plain']
    name = tag
    # print(tag)
    subject = Subject(owner_id=1, name=name, description=desc, tag=name, type=2)
    subject.save()
    i = 1
    for pic in multi_pic:
        path = pic['path'].replace('/w650', '')
        dir_name = 'id_' + str(subject.id) + '_' + 'type_2'
        file_name = str(i) + '.jpg'
        cloud_image_path = base_image_cloud_path + '/' + dir_name + '/' + file_name
        if i == 1:
            subject.cover = cloud_image_path.replace('cosbj', 'picbj')
            subject.save()
        create_new_wallpaper(subject.id, cloud_image_path, pic['w'], pic['h'])
        i = i + 1
        save_pic_to_disk(path, file_name, dir_name)
    print("\n#################" + item_id + " 抓取完成")


def get_cos_by_collect():
    dict_data = {'uid': '4084938', 'since': '0', 'grid_type': 'grid'}
    query_data['data'] = generate_encrypt_data(dict_data, '\x10')
    collect_data = requests.post(bcy_collect_url, headers=headers, data=query_data).json()['data']
    # print(json.dumps(collect_data))
    for pic_subject in collect_data:
        # print(pic_subject)
        item_detail = pic_subject['item_detail']
        item_id = item_detail['item_id']
        if len(Subject.objects.filter(bcy_id=item_id)) > 0:
            print(item_id + "已存在，跳过下载")
            continue
        if 'work' in item_detail:
            work = item_detail['work']
        else:
            work = ''
        # pos = (page - 1) * 20 + i + 1
        print("开始抓取" + work + ",id：" + item_id + "#################")
        get_cosplay_subject_by_id(item_id)
