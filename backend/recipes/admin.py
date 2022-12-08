from django.contrib import admin
from rest_framework.authtoken.admin import TokenAdmin

from .models import Cart, Favorite, Ingredient, Recipe, RecipeIngredient, Tag

TokenAdmin.raw_id_fields = ['user']


class IngredientInLine(admin.TabularInline):
    model = RecipeIngredient
    extra = 2


@admin.register(RecipeIngredient)
class LinksAdmin(admin.ModelAdmin):
    pass


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'favorites')
    search_fields = ('name', 'author__username')
    list_filter = ('tags',)
    inlines = (IngredientInLine,)

    def favorites(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'color', 'slug')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'user__email')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'user__email')
