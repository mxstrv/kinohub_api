from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, GenreViewSet, TitleViewSet,
                    ProfileViewSet, ReviewViewSet, CommentViewSet,
                    SignUpView, TokenReceiveView, )


v1_router = DefaultRouter()
v1_router.register('categories', CategoryViewSet, basename='category')
v1_router.register('genres', GenreViewSet, basename='genre')
v1_router.register('titles', TitleViewSet, basename='title')
v1_router.register('users', ProfileViewSet, basename='users')
v1_router.register(
    r'titles/(?P<title_id>[\d]+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
v1_router.register(
    r'titles/(?P<title_id>[\d]+)/reviews/(?P<review_id>[\d]+)/comments',
    CommentViewSet,
    basename='comments',
)

auth_patterns = [
    path('signup/', SignUpView.as_view(), name='user_create'),
    path('token/', TokenReceiveView.as_view(), name='token_receive'),
]

urlpatterns = [
    path('v1/', include(v1_router.urls)),
    path('v1/auth/', include(auth_patterns)),
]
