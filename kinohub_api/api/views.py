import secrets

from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, filters, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from reviews.models import Category, Genre, Review, Title
from users.models import CustomUser
from .filters import TitleFilter
from .permissions import (IsAdminOrReadOnly, IsAdminOrSuperUser,
                          IsAuthorOrStaffOrReadOnly,
                          IsModeratorOrAuthorOrAuthenticated)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ProfileSerializer,
                          ReviewSerializer, SignUpSerializer,
                          TitlePostSerializer, TitleSerializer,
                          TokenReceiveSerializer, UserMeSerializer)


class SignUpView(generics.CreateAPIView):

    def post(self, request, *args, **kwargs):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        try:
            user, _ = CustomUser.objects.get_or_create(
                username=username,
                email=email)
        except IntegrityError:
            return Response(
                'Данный e-mail или username уже используется!',
                status=status.HTTP_400_BAD_REQUEST)

        confirmation_code = secrets.token_hex(32)
        user.confirmation_code = str(confirmation_code)
        user.save()

        send_mail(
            subject='Ваш код подтверждения',
            message=f'Ваш код для регистрации: {confirmation_code}',
            from_email=settings.DOMAIN_NAME,
            recipient_list=[email],
            fail_silently=False,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenReceiveView(generics.CreateAPIView):

    def post(self, request, *args, **kwargs):
        serializer = TokenReceiveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            CustomUser,
            username=request.data.get('username')
        )
        refresh = RefreshToken.for_user(user)

        if user.confirmation_code != request.data.get('confirmation_code'):
            return Response(
                'Неверный код подтверждения',
                status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'token': str(refresh.access_token)
        }, status=status.HTTP_200_OK)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = (IsAdminOrSuperUser,)
    serializer_class = ProfileSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=username',)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_object(self):
        # Для GET запроса по юзернейму
        return get_object_or_404(CustomUser,
                                 username=self.kwargs.get('pk'))

    def create(self, request, *args, **kwargs):
        serializer = ProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = CustomUser.objects.create(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email'])

        user.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False,
            methods=('GET', 'PATCH'),
            permission_classes=(IsAuthenticated,))
    # Для работы с эндопоинтом /me/
    def me(self, request):
        if request.method == 'GET':
            user_info = get_object_or_404(CustomUser, username=request.user)
            serializer = self.get_serializer(user_info)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            serializer = UserMeSerializer(
                request.user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    http_method_names = ['get', 'post', 'delete']
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED,
                        data='Запрос не допустим')


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    http_method_names = ['get', 'post', 'delete']
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED,
                        data='Запрос не допустим')


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method == 'GET':
            return TitleSerializer
        return TitlePostSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (
        IsModeratorOrAuthorOrAuthenticated | IsAuthorOrStaffOrReadOnly,)

    def get_queryset(self):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        from django.db.models import Avg
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id'))
        title.rating = title.reviews.aggregate(Avg('score'))['score__avg']
        title.save()
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (
        IsModeratorOrAuthorOrAuthenticated | IsAuthorOrStaffOrReadOnly,)

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)
