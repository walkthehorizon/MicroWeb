# Generated by Django 2.2.1 on 2020-07-01 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallpaper', '0003_auto_20200630_1740'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='type',
            field=models.SmallIntegerField(choices=[(0, '动漫'), (1, 'Cos'), (2, '写真')], default=1, verbose_name='类型'),
        ),
    ]
