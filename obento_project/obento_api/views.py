# views.py

from ast import Return
from django.http import JsonResponse
from rest_framework import viewsets

from .serializers import HeroSerializer
from .models import Hero, Ingredient
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework import status

from obento_api.models import Recipe
from obento_api.serializers import RecipeSerializer, IngredientSerializer

class HeroViewSet(viewsets.ModelViewSet):
    queryset = Hero.objects.all().order_by('name')
    serializer_class = HeroSerializer

@api_view(['GET', 'POST'])
def recipes_list(request):
    if request.method == 'GET':
        recipes = Recipe.objects.all()
        recipes_serializer = RecipeSerializer(recipes, many=True)
        return JsonResponse(recipes_serializer.data, safe=False)
    elif request.method == 'POST':
        recipe_data = JSONParser().parse(request)
        recipe_serializer = RecipeSerializer(data=recipe_data)

        if recipe_serializer.is_valid():
            recipe_serializer.save()
            return JsonResponse(recipe_serializer.data, status=status.HTTP_201_CREATED)
        
        return JsonResponse(recipe_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def ingredients_list(request):
    if request.method == 'GET':
        ingredients = Ingredient.objects.all()
        ingredients_serializer = IngredientSerializer(ingredients, many=True)
        return JsonResponse(ingredients_serializer.data, safe=False)