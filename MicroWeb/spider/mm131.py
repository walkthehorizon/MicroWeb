# 抓取mm131美女图片

from bs4 import BeautifulSoup
import requests
import os
import django

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MicroWeb.settings')
    django.setup()
from wallpaper.models import Wallpaper, Subject

base_index = "http://www.mm131.com/"
xinggan_index = base_index + "xinggan/"

start_index = xinggan_index


# 抓取起点
def get_all_subject(page_url):
    page_data = requests.get(page_url)
    page_data.encoding = 'gb2312'
    page_soup = BeautifulSoup(page_data.text, 'lxml')
    for dd in page_soup.find(class_="list-left public-box").find_all(name='dd'):
        if len(dd.attrs) > 0:  # 分页数据
            page_data = dd.find_all(name='a')
            next_page_url = xinggan_index + page_data[len(page_data) - 2]['href']
            if next_page_url == xinggan_index + "list_6_141.html":
                break
            print(next_page_url)
            get_all_subject(next_page_url)
            break
        # print(dd.a)
        sub_url = dd.a['href']
        sub_title = dd.a.img['alt']
        subject = Subject(owner_id=1, name=sub_title, type=3)
        subject.save()
        print(sub_title + "存储成功")
        get_wallpaper_by_url(sub_url, subject.id)


def get_wallpaper_by_url(pic_url, sub_id):
    pic_data = requests.get(pic_url)
    pic_data.encoding = 'gb2312'
    soup = BeautifulSoup(pic_data.text, 'lxml')
    # print(soup.prettify())
    content_pic = soup.find(name='div', class_='content-pic')
    try:
        cur_pic_url = content_pic.img['src']
        if cur_pic_url.find('/1.jpg') != -1:
            print(cur_pic_url)
            subject = Subject.objects.get(id=sub_id)
            subject.cover = cur_pic_url
            subject.save()
        paper = Wallpaper(owner_id=1, category_id=9, subject_id=sub_id, small_url=cur_pic_url)
        paper.save()
    except AttributeError:
        print('当前主题pic读取完毕')
    short_pic_url = content_pic.a['href']
    if short_pic_url.find('http', 0, len(short_pic_url)) != -1:
        return
    next_pic_url = xinggan_index + short_pic_url
    # print(next_pic_url)
    get_wallpaper_by_url(next_pic_url, sub_id)


def create_wallpaper():
    pass


get_all_subject(xinggan_index)
