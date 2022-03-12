# serializers.py

from rest_framework import serializers

from .models import Recipe, Ingredient, Compound


class CompoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compound
        fields = ('id',
                  'recipe_id',
                  'ingredient_id',
                  'quantity',
                  'name')


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id',
                  'name',
                  'description',
                  'category',
                  'steps',
                  'estimated_cost',
                  'is_lunch',
                  'image_path')
        
    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)

        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.get(pk=ingredient_data['ingredient_id'])
            Compound.objects.create(recipe=recipe, ingredient=ingredient, quantity=ingredient_data['quantity'])
            
        return recipe.id


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