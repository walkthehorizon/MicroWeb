# Generated by Django 2.0.5 on 2019-04-16 10:49

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('wallpaper', '0030_auto_20190109_1624'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建日期'),
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AlterField(
            model_name='microuser',
            name='avatar',
            field=models.URLField(blank=True, default='\thttp://wallpager-1251812446.cosbj.myqcloud.com/avatar/default_avatar_3.025788195490962.jpg'),
        ),
    ]