# Generated by Django 3.2.16 on 2022-11-27 13:30

import django.contrib.auth.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_auto_20221119_1233'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=150, unique=True, validators=[django.contrib.auth.validators.ASCIIUsernameValidator], verbose_name='Логин'),
        ),
    ]
