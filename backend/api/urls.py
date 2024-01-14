from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (UserViewSet, UserMeViewSet, PasswordChangeViewSet,
                    SubscriptionsViewSet, SubscribeViewSet, TagViewSet,
                    IngredientViewSet, RecipeViewSet, FavoriteViewSet,
                    ShoppingCartViewSet)

app_name = 'api'

router = DefaultRouter()
router.register('users/me', UserMeViewSet, basename='me')
router.register('users/set_password',
                PasswordChangeViewSet, basename='passchange')
router.register('users/subscriptions',
                SubscriptionsViewSet, basename='subscriptions')
# router.register(r'users/(?P<id>\d+)/subscribe',
#                 SubscribeViewSet, basename='subscribe')
# router.register('users/<int:pk>/subscribe/',
#                 SubscribeViewSet.as_view(
#                     {'delete': 'destroy', 'post': 'create'}),
#                 basename='subscribe')
router.register('users', UserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
# router.register(r'recipes/(?P<id>\d+)/favorite',
#                 FavoriteViewSet, basename='favorite')
# router.register('recipes/download_shopping_cart/',
#                 DlShoppingCartViewSet,
#                 basename='dl_shopping_cart')
router.register('recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
    path('users/<int:pk>/subscribe/',
         SubscribeViewSet.as_view({'delete': 'destroy', 'post': 'create'}),
         name='subscribe'),
    path('recipes/<int:pk>/favorite/',
         FavoriteViewSet.as_view({'delete': 'destroy', 'post': 'create'}),
         name='favorite'),
    path('recipes/<int:pk>/shopping_cart/',
         ShoppingCartViewSet.as_view({'delete': 'destroy', 'post': 'create'}),
         name='shopping_cart'),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
