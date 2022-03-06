# serializers.py

from rest_framework import serializers

from .models import Hero, Recipe, Ingredient, Compound


class HeroSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Hero
        fields = ('name', 'alias')


class RecipeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id',
                  'name',
                  'description',
                  'category',
                  'steps',
                  'estimated_cost',
                  'is_launch',
                  'image_path',
                  'total_stars',
                  'num_scores')


class IngredientSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id',
                  'name',
                  'category',
                  'unit',
                  'unitary_price',
                  'kcalories',
                  'icon_name')


class CompoundSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Compound
        fields = ('recipe_id',
                  'ingredient_id',
                  'quantity')
