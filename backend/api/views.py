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
from .mixins import CustomMixin
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
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return CreateRecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context


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


class FavoriteView(CustomMixin, APIView):
    """ Добавить/удалить рецепт из избранного. """
    permission_classes = [IsAuthenticated, ]
    serializer_class = FavoriteSerializer
    model_class = Favorite


class CartView(CustomMixin, APIView):
    """ Добавить/удалить рецепт из списка покупок. """
    permission_classes = [IsAuthenticated, ]
    serializer_class = CartSerializer
    model_class = Cart


@api_view(['GET'])
def download_shopping_cart(request):
    ingredient_list = "Cписок покупок:"
    ingredients = RecipeIngredient.objects.filter(
        recipe__cart__user=request.user
    ).values(
        'ingredient__name',
        'ingredient__measurement_unit'
    ).annotate(total=Sum('amount')).order_by('ingredient__name')
    for ingredient in ingredients:
        ingredient_list += (
          f"\n{ingredient['ingredient__name']} - "
          f"{ingredient['total']} {ingredient['ingredient__measurement_unit']}"
        )
    file = 'shopping_list.txt'
    response = HttpResponse(ingredient_list, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename={file}'
    return response
