# Generated by Django 3.2.16 on 2022-11-16 14:29

import django.db.models.expressions
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20221116_1712'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subscription',
            options={'verbose_name': 'Подписка', 'verbose_name_plural': 'Подписки'},
        ),
        migrations.RemoveConstraint(
            model_name='subscription',
            name='follower_author_unique',
        ),
        migrations.AddConstraint(
            model_name='subscription',
            constraint=models.CheckConstraint(check=models.Q(('follower', django.db.models.expressions.F('author')), _negated=True), name='Нельзя'),
        ),
    ]
