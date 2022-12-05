from django.db.models import F
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Cart, Favorite, Ingredient, Recipe,
                            RecipeIngredient, Tag)
from users.models import Subscription, User


class TagSerializer(serializers.ModelSerializer):
    """ Сериализатор тэгов. """
    name = serializers.CharField(source='title')

    class Meta:
        model = Tag
        fields = [
            'id',
            'name',
            'color',
            'slug',
        ]


class UserSerializer(serializers.ModelSerializer):
    """ Сериализатор пользователей. """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'password',
        ]
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ('is_subscribed',)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            follower=request.user, author=obj
        ).exists()


class ShowFavoriteSerializer(serializers.ModelSerializer):
    """ Сериализатор для отображения избранных рецептов. """
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class FavoriteSerializer(serializers.ModelSerializer):
    """ Сериализатор избранных рецептов. """
    class Meta:
        model = Favorite
        fields = ['user', 'recipe']

    def validate(self, data):
        if Favorite.objects.filter(
                user=self.context['request'].user,
                recipe=data['recipe']):
            raise serializers.ValidationError({
                'errors': 'Рецепт уже в избранном.'
            })
        return data

    def to_representation(self, instance):
        return ShowFavoriteSerializer(instance.recipe, context={
            'request': self.context.get('request')
        }).data


class CartSerializer(serializers.ModelSerializer):
    """ Сериализатор списка покупок. """
    class Meta:
        model = Cart
        fields = ['user', 'recipe']

    def validate(self, data):
        if Cart.objects.filter(
                user=self.context['request'].user,
                recipe=data['recipe']):
            raise serializers.ValidationError({
                'errors': 'Рецепт уже есть в списке покупок.'
            })
        return data

    def to_representation(self, instance):
        return ShowFavoriteSerializer(instance.recipe, context={
            'request': self.context.get('request')
        }).data


class ShowSubscriptionsSerializer(serializers.ModelSerializer):
    """ Сериализатор для отображения подписок пользователя. """
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        ]

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            follower=request.user, author=obj).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipes = Recipe.objects.filter(author=obj)
        limit = request.query_params.get('recipes_limit')
        if limit:
            recipes = recipes[:int(limit)]
        return ShowFavoriteSerializer(
            recipes, many=True, context={'request': request}).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class SubscriptionSerializer(serializers.ModelSerializer):
    """ Сериализатор подписок. """
    class Meta:
        model = Subscription
        fields = ['follower', 'author']

    def validate(self, data):
        if self.context['request'].user == data['author']:
            raise serializers.ValidationError({
                'errors': 'Нельзя подписаться на самого себя.'
            })
        if Subscription.objects.filter(
                follower=self.context['request'].user,
                author=data['author']):
            raise serializers.ValidationError({
                'errors': 'Вы уже подписаны на данного автора.'
            })
        return data

    def to_representation(self, instance):
        return ShowSubscriptionsSerializer(
            instance.author,
            context={'request': self.context.get('request')}
        ).data


class IngredientSerializer(serializers.ModelSerializer):
    """ Сериализатор ингредиентов. """
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """ Сериализатор ингредиентов в рецептах. """
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'measurement_unit', 'amount']


class AddIngredientRecipeSerializer(serializers.ModelSerializer):
    """ Сериализатор для добавления ингредиентов в рецепт. """
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']


class RecipeSerializer(serializers.ModelSerializer):
    """ Сериализатор рецептов. """
    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart'
        ]

    def get_ingredients(self, obj):
        ingredients = obj.ingredients.values(
            'id', 'name', 'measurement_unit', amount=F('ingredient__amount')
        )
        return ingredients

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user, recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Cart.objects.filter(
            user=request.user, recipe=obj
        ).exists()


class CreateRecipeSerializer(serializers.ModelSerializer):
    """ Сериализатор для создания рецепта. """
    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    ingredients = AddIngredientRecipeSerializer(many=True, source='recipe')
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = [
            'id',
            'author',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        ]

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        list = []
        for i in ingredients:
            amount = i['amount']
            if type(amount) != int:
                raise serializers.ValidationError({
                   'amount': 'Значение должно быть целым числом.'
                })
            if int(amount) < 1:
                raise serializers.ValidationError({
                   'amount': 'Убедитесь, что это значение больше либо равно 1.'
                })
            if i['id'] in list:
                raise serializers.ValidationError({
                   'ingredient': 'Ингредиенты должны быть уникальными!'
                })
            list.append(i['id'])
        return data

    def create_ingredients(self, ingredients, recipe):
        for i in ingredients:
            ingredient = Ingredient.objects.get(id=i['id'])
            RecipeIngredient.objects.create(
                ingredient=ingredient, recipe=recipe, amount=i['amount']
            )

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        ingredients = validated_data.pop('recipe')
        tags = validated_data.pop('tags')
        new_recipe = Recipe.objects.create(**validated_data)
        self.create_ingredients(ingredients, new_recipe)
        new_recipe.tags.set(tags)
        return new_recipe

    def update(self, recipe, validated_data):
        tags = validated_data.get('tags')
        ingredients = validated_data.get('recipe')
        recipe.image = validated_data.get('image', recipe.image)
        recipe.name = validated_data.get('name', recipe.name)
        recipe.text = validated_data.get('text', recipe.text)
        recipe.cooking_time = validated_data.get(
            'cooking_time', recipe.cooking_time)
        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)
        if ingredients:
            recipe.ingredients.clear()
            self.create_ingredients(ingredients, recipe)
        recipe.save()
        return recipe

    def to_representation(self, instance):
        return RecipeSerializer(instance, context={
            'request': self.context.get('request')
        }).data
