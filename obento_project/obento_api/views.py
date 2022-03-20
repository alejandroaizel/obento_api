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

from django.db.models import Q

import datetime

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
            return JsonResponse({'message': f'Recipe {recipe_id} doesn\'t exist.'}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        try:
            recipe = Recipe.objects.get(pk=recipe_id)
            recipe.delete()
            return JsonResponse({'message': f'Recipe {recipe_id} deleted.'}, status=status.HTTP_200_OK)
        except Recipe.DoesNotExist:
            return JsonResponse({'message': f'Recipe {recipe_id} doesn\'t exist.'}, status=status.HTTP_400_BAD_REQUEST)


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


class ScheduleList(APIView):
    """
    List all schedules, or create a new schedule
    """

    RECIPES_PER_DAY = 2
  
    def get(self, request, format=None):

        try:
            schedule_data = JSONParser().parse(request)
        except:
            return JsonResponse({'message': 'Invalid body.'}, status=status.HTTP_400_BAD_REQUEST)

        q = Q()
        if 'user' in schedule_data:
            q &= Q(user=schedule_data['user'])
        else:
            message = {}
            message['user'] = ["This field is required."]
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        if 'start_date' in schedule_data:
            start_date = datetime.datetime.strptime(schedule_data['start_date'], '%d-%m-%y')
            q &= Q(date__gte=start_date)
        
        if 'end_date' in schedule_data:
            end_date = datetime.datetime.strptime(schedule_data['end_date'], '%d-%m-%y')
            q &= Q(date__lte=end_date)

        if 'is_lunch' in schedule_data:
            q &= Q(is_lunch=schedule_data['is_lunch'])

        schedules = Schedule.objects.filter(q)
        schedules_data = []
        
        for schedule in schedules:
            schedule_serializer = ScheduleSerializer(schedule)
            schedule_data = schedule_serializer.data
            schedule_data['recipe'] = get_compound(schedule.recipe)
            schedules_data.append(schedule_data)
        
        return JsonResponse(schedules_data, status=status.HTTP_200_OK, safe=False)


    def post(self, request, format=None):

        try:
            schedule_data = JSONParser().parse(request)
        except:
            return JsonResponse({'message': 'Invalid body.'}, status=status.HTTP_400_BAD_REQUEST)

        dates_str = schedule_data['date'].split("|")
        start_date = datetime.datetime.strptime(dates_str[0], '%d-%m-%y')
        end_date = datetime.datetime.strptime(dates_str[1], '%d-%m-%y')
        schedule_data['date'] = start_date
        schedule_serializer = ScheduleSerializer(data=schedule_data)

        if schedule_serializer.is_valid():
            delta = datetime.date(end_date.year, end_date.month, end_date.day) - datetime.date(start_date.year, start_date.month, start_date.day)
            print(delta.days)
            num_recipes = (delta.days + 1) * self.RECIPES_PER_DAY
            print(num_recipes)
            recipes = Recipe.objects.all().order_by('?')[:num_recipes]

            result = []

            i = 1
            is_lunch = True
            for recipe in recipes:
                menu_id = schedule_serializer.create(schedule_data, start_date, recipe, is_lunch)
                result.append(menu_id)

                is_lunch = False

                if i % 2 == 0:
                    start_date += datetime.timedelta(days=1)
                    is_lunch = True

                i += 1

            return Response({'id': result}, status=status.HTTP_201_CREATED)

        return Response(schedule_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ScheduleDetail(APIView):
    """
    Retrieve, update or delete a schedule
    """

    def get(self, request, menu_id):
        schedule = None

        try:
            schedule = Schedule.objects.get(pk=menu_id)
            schedule_serializer = ScheduleSerializer(schedule)
            schedule_data = schedule_serializer.data
            schedule_data['recipe'] = get_compound(schedule.recipe)
            return JsonResponse(schedule_data, status=status.HTTP_200_OK, safe=False)
        except Schedule.DoesNotExist:
            try:
                schedule_data = JSONParser().parse(request)
            except:
                return JsonResponse({'message': 'Invalid body.'}, status=status.HTTP_400_BAD_REQUEST)

            message = {}

            if 'user' not in schedule_data:
                message['user'] = ["This field is required."]

            if 'date' not in schedule_data:
                message['date'] = ["This field is required."]

            if 'is_lunch' not in schedule_data:
                message['is_lunch'] = ["This field is required."]
        
            if not message:
                try:
                    date = datetime.datetime.strptime(schedule_data['date'], '%d-%m-%y')
                    schedule = Schedule.objects.filter(user=schedule_data['user'], date=date, is_lunch=schedule_data['is_lunch'])
                except Schedule.DoesNotExist:
                    return JsonResponse({'message': f'Menu {menu_id} doesn\'t exist.'}, status=status.HTTP_404_NOT_FOUND)
            
                if len(schedule) == 1:
                    schedule_serializer = ScheduleSerializer(schedule[0])
                    schedule_data = schedule_serializer.data
                    schedule_data['recipe'] = get_compound(schedule[0].recipe)
                    return JsonResponse(schedule_data, status=status.HTTP_200_OK, safe=False)
                elif len(schedule) == 0:
                    return JsonResponse({'message': f'Menu doesn\'t exist.'}, status=status.HTTP_404_NOT_FOUND)

            return JsonResponse(message, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, menu_id):
        try:
            schedule = Schedule.objects.get(pk=menu_id)
            schedule.delete()
            return Response({'message': f'Menu {menu_id} deleted.'}, status=status.HTTP_204_NO_CONTENT)
        except Schedule.DoesNotExist:
            return JsonResponse({'message': f'Menu {menu_id} doesn\'t exist.'}, status=status.HTTP_404_NOT_FOUND)

