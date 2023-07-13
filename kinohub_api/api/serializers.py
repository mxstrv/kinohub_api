from django.conf import settings

from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db.models import Avg
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import CustomUser


class SignUpSerializer(serializers.Serializer):
    """Cериализатор для регистрации пользователя."""
    email = serializers.EmailField(
        required=True,
        max_length=254,
    )
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+',
                message='Неподходящий формат имени пользователя'), ])
    first_name = serializers.CharField(
        max_length=150,
        required=False)
    last_name = serializers.CharField(
        max_length=150,
        required=False)
    role = serializers.CharField(
        required=False)
    bio = serializers.CharField(
        required=False)

    class Meta:
        fields = '__all__'
        model = CustomUser

    def validate(self, attrs):
        if attrs.get('username') == 'me':
            raise serializers.ValidationError(
                'Запрещено использовать юзернейм "me"')
        return attrs

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get(
            'first_name', instance.first_name)
        instance.last_name = validated_data.get(
            'last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.bio = validated_data.get('bio', instance.bio)
        instance.role = validated_data.get('role', instance.role)
        if instance.role not in ('user', 'moderator', 'admin'):
            raise serializers.ValidationError()
        instance.save()
        return instance


class ProfileSerializer(SignUpSerializer):
    """Cериализатор для работы с пользователем."""
    email = serializers.EmailField(
        required=True,
        max_length=254,
        validators=[UniqueValidator(queryset=CustomUser.objects.all()), ]
    )
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+',
                message='Неподходящий формат имени пользователя'),
            UniqueValidator(queryset=CustomUser.objects.all()), ]
    )

    class Meta:
        fields = '__all__'
        model = CustomUser


class UserMeSerializer(serializers.ModelSerializer):
    """Cериализатор для работы с эндпоинтом /me/."""
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+',
                message='Неподходящий формат имени пользователя'),
            UniqueValidator(queryset=CustomUser.objects.all()), ])

    class Meta:
        fields = '__all__'
        model = CustomUser
        read_only_fields = ['role']


class TokenReceiveSerializer(serializers.Serializer):
    """Cериализатор для работы с токеном."""
    username = serializers.CharField(
        required=True,
        max_length=150, )
    confirmation_code = serializers.CharField(
        required=True, )

    class Meta:
        fields = '__all__'
        model = CustomUser


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        exclude = ('id',)


class TitleSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Title
        fields = '__all__'


class TitlePostSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug',
    )

    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True,
    )

    class Meta:
        model = Title
        fields = '__all__'

    def get_rating(self, obj):
        rating = obj.reviews.aggregate(
            Avg('score')).get('score__avg')
        return round(rating, 2) if rating else rating


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    score = serializers.IntegerField(
        validators=[
            MinValueValidator(
                settings.MIN_VAL_SCORE, 'Оценка не должна быть меньше 1'),
            MaxValueValidator(
                settings.MAX_VAL_SCORE, 'Оценка не должна быть больше 10')]
    )
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )

    class Meta:
        fields = '__all__'
        model = Review

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data

        title_id = self.context['view'].kwargs.get('title_id')
        author = self.context['request'].user
        if Review.objects.filter(
                author=author, title=title_id).exists():
            raise serializers.ValidationError(
                'Нельзя оставить отзыв на одно произведение дважды'
            )
        return data

    def validate_rate(self, rate):
        return (rate if (settings.MIN_VAL_SCORE <= rate
                         <= settings.MAX_VAL_SCORE)
                else serializers.ValidationError(
                f'Рейтинг произведения должен быть от'
                f' {settings.MIN_VAL_SCORE} до {settings.MAX_VAL_SCORE}'))


class CommentSerializer(serializers.ModelSerializer):
    """Комментарии на отзывы"""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        validators=[UniqueValidator(queryset=Comment.objects.all())]
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment
