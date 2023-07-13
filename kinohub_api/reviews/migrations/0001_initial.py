# Generated by Django 3.2 on 2023-03-22 18:47

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import reviews.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Название категории', max_length=256, verbose_name='Название')),
                ('slug', models.SlugField(help_text='Уникальная строка категории', unique=True, verbose_name='Уникальная строка-индификатор')),
            ],
            options={
                'verbose_name': 'Категория произведения',
                'verbose_name_plural': 'Категории произведений',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Текст комментария')),
                ('pub_date', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата публикации комментария')),
            ],
            options={
                'verbose_name': 'Комментарий',
                'verbose_name_plural': 'Комментарии',
                'ordering': ['-pub_date'],
            },
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Название жанра', max_length=256, verbose_name='Название')),
                ('slug', models.SlugField(help_text='Уникальная строка жанра', unique=True, verbose_name='Уникальная строка-индификатор')),
            ],
            options={
                'verbose_name': 'Жанр произведения',
                'verbose_name_plural': 'Жанры произведений',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('score', models.IntegerField(validators=[django.core.validators.MaxValueValidator(10, 'Оценка не должна быть больше 10'), django.core.validators.MinValueValidator(1, 'Оценка не должна быть меньше 1')], verbose_name='Оценка')),
                ('pub_date', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата публикации отзыва')),
            ],
            options={
                'verbose_name': ('Обзор',),
                'verbose_name_plural': 'Обзоры',
                'ordering': ['-pub_date'],
            },
        ),
        migrations.CreateModel(
            name='Title',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, help_text='Название произведения', max_length=256, verbose_name='Название')),
                ('year', models.IntegerField(db_index=True, help_text='год создания произведения', validators=[reviews.validators.year_validator], verbose_name='Год')),
                ('description', models.TextField(help_text='описание создания произведения', null=True, verbose_name='Описание')),
                ('rating', models.FloatField(default=None, help_text='Средняя оценка', null=True, verbose_name='Средняя оценка')),
                ('category', models.ForeignKey(help_text='категории произведения', on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='reviews.category', verbose_name='Категория')),
                ('genre', models.ManyToManyField(help_text='жанры произведения', to='reviews.Genre')),
            ],
            options={
                'verbose_name': 'Произведение',
                'verbose_name_plural': 'Произведения',
                'ordering': ['-id'],
            },
        ),
    ]