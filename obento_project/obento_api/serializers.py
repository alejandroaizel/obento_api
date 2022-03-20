# serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

from .models import Recipe, Ingredient, Compound, RecipeCategory, Schedule


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
                  'image_path')

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        recipe_category = RecipeCategory.objects.get(
            pk=validated_data['category'])
        validated_data['category'] = recipe_category
        recipe = Recipe.objects.create(**validated_data)

        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.get(
                pk=ingredient_data['ingredient_id'])
            Compound.objects.create(
                recipe=recipe, ingredient=ingredient, quantity=ingredient_data['quantity'])
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

    def create(self, validated_data, date, recipe, is_lunch):
        schedule = Schedule.objects.create(user=validated_data['user'], recipe=recipe, date=date,
                                        is_lunch=is_lunch)
        return schedule.id
