from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (UserViewSet, UserMeViewSet, PasswordChangeViewSet,
                    SubscriptionsViewSet, SubscribeViewSet, TagViewSet,
                    IngredientViewSet)

app_name = 'api'

router = DefaultRouter()
router.register('users/me', UserMeViewSet, basename='me')
router.register('users/set_password',
                PasswordChangeViewSet, basename='passchange')
router.register('users/subscriptions',
                SubscriptionsViewSet, basename='subscriptions')
router.register('users', UserViewSet, basename='users')
router.register(r'users/(?P<id>\d+)/subscribe',
                SubscribeViewSet, basename='subscribe')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
