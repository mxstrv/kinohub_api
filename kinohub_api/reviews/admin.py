from django.contrib import admin

from .models import Category, Comment, Genre, Review, Title


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    search_fields = ('slug', 'name')
    ordering = ('pk', 'name', 'slug')


class GenreAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    search_fields = ('slug', 'name')
    ordering = ('pk', 'name', 'slug')


class TitleAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'category', 'get_genre', 'year', 'rating')
    search_fields = ('name', 'category__name', 'genre__name', 'year')
    list_filter = ('category', 'genre')
    ordering = ('name', 'year', 'rating')
    raw_id_fields = ('category', 'genre')


class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'score',
        'pub_date',
        'author',
        'title'
    )
    search_fields = ('text', 'pub_date', 'author', 'score')
    list_filter = ('pub_date', 'score')
    empty_value_display = '-пусто-'


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'review',
        'author',
        'text',
        'pub_date'
    )
    list_display_links = ('text',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Category, CategoryAdmin)
