# Generated by Django 2.2.16 on 2021-12-24 16:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0017_auto_20211224_1929'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(help_text='Введите текст статьи', verbose_name='Содержание статьи'),
        ),
    ]