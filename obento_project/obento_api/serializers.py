# serializers.py

from re import I
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

from .models import *


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
                  'cooking_time',
                  'is_lunch',
                  'image_path',
                  'servings',
                  'user')

    def create(self, validated_data, image, ext):
        ingredients_data = validated_data.pop('ingredients')
        recipe_category = RecipeCategory.objects.get(
            pk=validated_data['category'])

        validated_data['category'] = recipe_category
        recipe = Recipe.objects.create(**validated_data)

        try:
            for ingredient_data in ingredients_data:
                ingredient = Ingredient.objects.get(
                    pk=ingredient_data['ingredient_id'])
                Compound.objects.create(recipe=recipe, ingredient=ingredient,
                                        quantity=ingredient_data['quantity'])
        except:
            recipe.delete()
            return 'Ingredient {} doesnt\'t exist.'.format(ingredient_data['ingredient_id'])

        user_id = validated_data['user']
        filename = f'{user_id}_{recipe.id}.{ext}'
        recipe.image_path.save(filename, image, save=True)
        return recipe.id


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id',
                  'name',
                  'category',
                  'unit',
                  'unitary_price',
                  'kcalories',
                  'icon_name')


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ('password', 'email', 'first_name')
        extra_kwargs = {
            'username': {'required': True},
            'first_name': {'required': True}
        }

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['email'],
            first_name=validated_data['first_name']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ('id',
                  'user',
                  'date',
                  'is_lunch',
                  'recipe',)

    def save(self, validated_data, date, recipe, is_lunch):
        object, created = Schedule.objects.update_or_create(user=validated_data['user'], date=date,
                                           is_lunch=is_lunch, defaults={'recipe_id': recipe.id})
        return object.id


class RecipeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeCategory
        fields = ('id',
                  'description')


class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = ('id',
                  'user',
                  'recipe',
                  'num_stars')

    def create(self, validated_data):
        recipe = Recipe.objects.get(pk=validated_data['recipe'])
        recipe.total_stars += validated_data['num_stars']
        recipe.num_scores += 1
        recipe.save()
        score = Score.objects.create(user=validated_data['user'], recipe=recipe,
                                     num_stars=validated_data['num_stars'])

        return score.id
