# Generated by Django 2.1.7 on 2019-07-31 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallpaper', '0044_auto_20190729_1911'),
    ]

    operations = [
        migrations.AddField(
            model_name='wallpaper',
            name='collected',
            field=models.BooleanField(default=False),
        ),
    ]
