# views.py

from ast import Return
from django.http import JsonResponse
from rest_framework import viewsets

from .models import Compound, Ingredient
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework import status

from obento_api.models import Recipe
from obento_api.serializers import RecipeSerializer, IngredientSerializer
import json


@api_view(['GET', 'POST'])
def recipes_list(request):
    if request.method == 'GET':
        recipes = Recipe.objects.all()
        result = []

        for recipe in recipes:
            recipe_data = get_compound(recipe)
            result.append(recipe_data)

        return JsonResponse(result, status=status.HTTP_200_OK, safe=False)
    elif request.method == 'POST':
        recipe_data = JSONParser().parse(request)
        recipe_serializer = RecipeSerializer(data=recipe_data)

        message = {}

        if 'category' not in recipe_data:
            message['category'] = ["This field is required."]
        
        if 'ingredients' not in recipe_data:
            message['ingredients'] = ["This field is required."]


        if recipe_serializer.is_valid() and not message:
            recipe_id = recipe_serializer.create(validated_data=recipe_data)
            return JsonResponse({'id': recipe_id}, status=status.HTTP_201_CREATED)

        message.update(recipe_serializer.errors)
        return JsonResponse(message, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'DELETE'])
def get_delete_recipe(request, recipe_id):
    if request.method == 'GET':
        try:
            recipe = Recipe.objects.get(pk=recipe_id)
            recipe_data = get_compound(recipe)
            return JsonResponse(recipe_data)
        except Recipe.DoesNotExist:
            return JsonResponse({'message': f'User {recipe_id} doesn\'t exist.'}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        try:
            recipe = Recipe.objects.get(pk=recipe_id)
            recipe.delete()    
            return JsonResponse({'message': f'User {recipe_id} deleted.'}, status=status.HTTP_200_OK)
        except Recipe.DoesNotExist:
            return JsonResponse({'message': f'User {recipe_id} doesn\'t exist.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def ingredients_list(request):
    if request.method == 'GET':
        ingredients = Ingredient.objects.all()
        ingredients_serializer = IngredientSerializer(ingredients, many=True)
        return JsonResponse(ingredients_serializer.data, status=status.HTTP_200_OK, safe=False)

def get_compound(recipe):
    recipe_serializer = RecipeSerializer(recipe)
    recipe_data = recipe_serializer.data
    kcalories = 0.0
    estimated_cost = 0.0
    compounds = []

    recipe_data['category'] = recipe.category.description

    for compound in Compound.objects.raw('''SELECT COMPOUND.id, ingredient_id, quantity, name, 
                                            category, unit, unitary_price, kcalories,
                                            icon_name FROM compound AS COMPOUND
                                            INNER JOIN ingredient AS INGREDIENT
                                            ON COMPOUND.ingredient_id=INGREDIENT.id AND
                                            COMPOUND.recipe_id = %s''', [recipe.id]):
        compound_dict = vars(compound)
        compound_dict.pop('_state')
        compound_dict.pop('id')
        compounds.append(compound_dict)
        kcalories += compound_dict['kcalories'] * compound_dict['quantity']
        estimated_cost += compound_dict['unitary_price'] * compound_dict['quantity']
    
    recipe_data['kcalories'] = kcalories
    recipe_data['estimated_cost'] = estimated_cost
    recipe_data['ingredients'] = compounds

    return recipe_data


