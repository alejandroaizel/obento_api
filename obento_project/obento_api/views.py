# views.py

from ast import Return
from django.http import JsonResponse
from django.contrib.auth.models import User

from rest_framework import viewsets
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework import viewsets, generics, status


from obento_api.models import *
from obento_api.serializers import *
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


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class LogoutAllView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        tokens = OutstandingToken.objects.filter(user_id=request.user.id)
        for token in tokens:
            t, _ = BlacklistedToken.objects.get_or_create(token=token)

        return Response(status=status.HTTP_205_RESET_CONTENT)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class MenuView():
    """
    Retrieve, post or delete a Menu.
    """
    def get_object(self, pk):
        try:
            return Schedule.objects.get(pk=pk)
        except Snippet.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = SnippetSerializer(snippet)
        return Response(serializer.data)

    def post(self, request, format=None):
        menu_data = JSONParser().parse(request)
        menu_serializer = ScheduleSerializer(data=menu_data)

        message = {}

        if 'recipe_id' not in menu_data:
            message['recipe_id'] = ["This field is required."]

        if menu_serializer.is_valid() and not message:
            menu = menu_serializer.create(validated_data=menu_data)
            return JsonResponse(menu, status=status.HTTP_201_CREATED)

        message.update(menu_serializer.errors)
        return JsonResponse(message, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        snippet = self.get_object(pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)