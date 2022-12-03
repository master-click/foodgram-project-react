from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CartView, FavoriteView, IngredientViewSet, RecipeViewSet,
                    ShowSubscriptionsView, SubscribeView, TagViewSet,
                    UserViewSet, download_shopping_cart)

router = DefaultRouter()
router.register('recipes', RecipeViewSet)
router.register('users', UserViewSet)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)


urlpatterns = [
    path(
        'recipes/download_shopping_cart/',
        download_shopping_cart,
        name='download_shopping_cart'
    ),
    path(
        'recipes/<int:id>/favorite/',
        FavoriteView.as_view(),
        name='favorite'
    ),
    path(
        'users/<int:id>/subscribe/',
        SubscribeView.as_view(),
        name='subscribe'
    ),
    path(
        'recipes/<int:id>/shopping_cart/',
        CartView.as_view(),
        name='shopping_cart'
    ),
    path(
        'users/subscriptions/',
        ShowSubscriptionsView.as_view(),
        name='subscriptions'
    ),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
