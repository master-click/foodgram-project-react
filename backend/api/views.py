from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Cart, Favorite, Ingredient, Recipe, Tag
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import Subscription, User

from .filters import IngredientFilter, RecipeFilter
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

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return CreateRecipeSerializer


class UserViewSet(viewsets.ModelViewSet):
    """ Отображение пользователей. Регистрация нового пользователя. """
    permission_classes = [AllowAny, ]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class TagViewSet(viewsets.ModelViewSet):
    """ Отображение тэгов. """
    permission_classes = [AdminOrReadOnly, ]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    """ Отображение ингредиентов. """
    permission_classes = [AdminOrReadOnly, ]
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
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
        if not Favorite.objects.filter(
           user=request.user, recipe__id=id).exists():
            serializer = FavoriteSerializer(
                data=data, context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED)
        return Response('HTTP_400_BAD_REQUEST',
                        status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        if Favorite.objects.filter(
           user=request.user, recipe=recipe).exists():
            Favorite.objects.filter(user=request.user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response('HTTP_400_BAD_REQUEST',
                        status=status.HTTP_400_BAD_REQUEST)


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
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        author = get_object_or_404(User, id=id)
        if Subscription.objects.filter(
           follower=request.user, author=author).exists():
            subscription = get_object_or_404(
                Subscription, follower=request.user, author=author
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class ShowSubscriptionsView(ListAPIView):
    """ Отображение подписок. """

    permission_classes = [IsAuthenticated, ]

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
        recipe = get_object_or_404(Recipe, id=id)
        if not Cart.objects.filter(user=request.user, recipe=recipe).exists():
            serializer = CartSerializer(data=data,
                                        context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(data=serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = CartSerializer(
            data=data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        if Cart.objects.filter(user=request.user, recipe=recipe).exists():
            Cart.objects.filter(user=request.user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


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
