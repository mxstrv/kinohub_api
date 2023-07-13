from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.models import CustomUser
from .validators import year_validator


class Category(models.Model):
    name = models.CharField(max_length=256,
                            verbose_name='Название',
                            help_text='Название категории', )
    slug = models.SlugField(max_length=50,
                            unique=True,
                            verbose_name='Уникальная строка-индификатор',
                            help_text='Уникальная строка категории', )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Категория произведения'
        verbose_name_plural = 'Категории произведений'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=256,
                            verbose_name='Название',
                            help_text='Название жанра', )
    slug = models.SlugField(max_length=50,
                            unique=True,
                            verbose_name='Уникальная строка-индификатор',
                            help_text='Уникальная строка жанра', )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Жанр произведения'
        verbose_name_plural = 'Жанры произведений'

    def __str__(self):
        return self.name


class Title(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='categories',
        verbose_name='Категория',
        help_text='категории произведения',
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанры',
        help_text='жанры произведения',

    )
    name = models.CharField(
        max_length=256,
        db_index=True,
        verbose_name='Название',
        help_text='Название произведения',
    )
    year = models.IntegerField(
        validators=[year_validator],
        db_index=True,
        verbose_name='Год',
        help_text='год создания произведения',
    )
    description = models.TextField(
        null=True,
        verbose_name='Описание',
        help_text='описание создания произведения',
    )
    rating = models.FloatField(
        null=True,
        default=None,
        verbose_name='Средняя оценка',
        help_text='Средняя оценка',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def get_genre(self):
        return ', '.join([genre.name for genre in self.genre.all()])

    get_genre.short_description = 'Жанры'

    def __str__(self):
        return self.name


class Review(models.Model):
    """
    Отзыв на конкретное произведение.
    Оценка: от 1 до 10.
    Рейтинг: ср.арифм. поставленных оценок.
    Отзыв может быть только один от одного автора.
    При удалении пользователя удаляются все отзывы этого пользователя.
    При удалении произведения удаляются все отзывы к нему.
    """
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение',
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор обзора',
    )
    text = models.TextField()
    score = models.IntegerField(
        'Оценка',
        null=False,
        validators=[
            MaxValueValidator(
                settings.MAX_VAL_SCORE,
                f'Оценка не должна быть больше {settings.MAX_VAL_SCORE}'
            ),
            MinValueValidator(
                settings.MIN_VAL_SCORE,
                f'Оценка не должна быть меньше {settings.MIN_VAL_SCORE}'
            )
        ],
    )

    pub_date = models.DateTimeField(
        'Дата публикации отзыва',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ['-pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'], name="unique_review")
        ]
        verbose_name = 'Обзор',
        verbose_name_plural = 'Обзоры'


class Comment(models.Model):
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        blank=True,
        verbose_name='Обзор',
    )
    text = models.TextField(
        verbose_name='Текст комментария',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата добавления',
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
