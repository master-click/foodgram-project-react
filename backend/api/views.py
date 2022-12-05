from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import Cart, Favorite, Ingredient, Recipe, Tag
from users.models import Subscription, User

from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import AdminOrReadOnly
from .serializers import (CartSerializer, CreateRecipeSerializer,
                          FavoriteSerializer, IngredientSerializer,
                          RecipeIngredient, RecipeSerializer,
                          ShowSubscriptionsSerializer, SubscriptionSerializer,
                          TagSerializer, UserSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    """ Отображение рецептов. """
    permission_classes = [AllowAny, ]
    queryset = Recipe.objects.all().order_by('-pub_date')
    serializer_class = RecipeSerializer
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = RecipeFilter
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return CreateRecipeSerializer


class UserViewSet(viewsets.ModelViewSet):
    """ Отображение пользователей. Регистрация нового пользователя. """
    permission_classes = [AllowAny, ]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination


class TagViewSet(viewsets.ModelViewSet):
    """ Отображение тэгов. """
    permission_classes = [AdminOrReadOnly, ]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    """ Отображение ингредиентов. """
    permission_classes = [AdminOrReadOnly, ]
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [IngredientFilter, ]
    search_fields = ['^name', ]


class FavoriteView(APIView):
    """ Добавление/удаление рецепта из избранного. """
    permission_classes = [IsAuthenticated, ]

    def post(self, request, id):
        data = {
            'user': request.user.id,
            'recipe': id
        }
        serializer = FavoriteSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        Favorite.objects.filter(user=request.user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscribeView(APIView):
    """ Операция подписки/отписки. """
    permission_classes = [IsAuthenticated, ]

    def post(self, request, id):
        data = {
            'follower': request.user.id,
            'author': id
        }
        serializer = SubscriptionSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        author = get_object_or_404(User, id=id)
        subscription = get_object_or_404(
                Subscription, follower=request.user, author=author
            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShowSubscriptionsView(ListAPIView):
    """ Отображение подписок. """
    permission_classes = [IsAuthenticated, ]
    pagination_class = CustomPagination

    def get(self, request):
        follower = request.user
        queryset = User.objects.filter(author__follower=follower)
        page = self.paginate_queryset(queryset)
        serializer = ShowSubscriptionsSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class CartView(APIView):
    """ Добавить/удалить рецепт в список покупок. """
    permission_classes = [IsAuthenticated, ]

    def post(self, request, id):
        data = {
            'user': request.user.id,
            'recipe': id
        }
        serializer = CartSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        Cart.objects.filter(user=request.user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def download_shopping_cart(request):
    ingredient_list = "Cписок покупок:"
    ingredients = RecipeIngredient.objects.filter(
        recipe__cart__user=request.user
    ).values(
        'ingredient__name',
        'ingredient__measurement_unit'
    ).annotate(total=Sum('amount')).order_by('ingredient__name')
    for i in ingredients:
        ingredient_list += (
            f"\n{i['ingredient__name']} - "
            f"{i['total']} {i['ingredient__measurement_unit']}"
        )
    file = 'shopping_list.txt'
    response = HttpResponse(ingredient_list, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename={file}'
    return response
