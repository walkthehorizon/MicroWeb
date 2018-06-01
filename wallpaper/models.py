from django.db import models
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles
from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import HtmlFormatter
from pygments import highlight

# python manage.py makemigrations TestModel  # 让 Django 知道我们在我们的模型有一些变更
# python manage.py migrate TestModel   # 创建表结构

LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
STYLE_CHOICES = sorted((item, item) for item in get_all_styles())
CATEGORY_CHOICES = ((0, '风景风光'), (1, '动漫游戏'), (2, '美丽文字'), (3, '萌娃萌宠'), (4, '文化节日'), (5, '美食天下'))


# Create your models here.
# class WallPager(models.Model):
#     name = models.CharField(max_length=12, default="")
#     describe = models.TextField(null=True, default="")
#     url = models.TextField(default="")

class Wallpaper(models.Model):
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='wallpaper', default="")
    created = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=20, default="")
    describe = models.TextField(max_length=300, default="")
    url = models.CharField(max_length=50, default="")
    category = models.IntegerField(choices=CATEGORY_CHOICES, default=0)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return self.name


class Snippet(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True, default='')
    code = models.TextField()
    linenos = models.BooleanField(default=False)
    language = models.CharField(choices=LANGUAGE_CHOICES, default='python', max_length=100)
    style = models.CharField(choices=STYLE_CHOICES, default='friendly', max_length=100)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return self.title
