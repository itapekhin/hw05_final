# Generated by Django 2.2.16 on 2021-12-24 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0022_auto_20211224_2018'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='follow',
            name='one_love',
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('user', 'author'), name='one_following1'),
        ),
    ]
