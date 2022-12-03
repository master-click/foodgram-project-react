from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import CheckConstraint, F, Q


class User(AbstractUser):
    email = models.EmailField('email',
                              max_length=254,
                              unique=True,
                              )
    username = models.CharField('Логин',
                                max_length=150,
                                unique=True,
                                validators=[RegexValidator(
                                    regex=r"^[\w.@+-]+\Z")]
                                )
    first_name = models.CharField('Имя',
                                  max_length=150,
                                  blank=False,
                                  )
    last_name = models.CharField('Фамилия',
                                 max_length=150,
                                 blank=False,
                                 )
    password = models.CharField('Пароль',
                                max_length=150,
                                blank=False,
                                )
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']
    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return f'{self.username}: {self.email}'


class Subscription(models.Model):
    follower = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        related_name='author',
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            CheckConstraint(check=~Q(follower=F('author')),
                            name='no_self_subscribe')
        ]
