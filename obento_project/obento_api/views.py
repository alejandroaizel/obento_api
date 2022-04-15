# views.py

from unicodedata import category
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
from django.db.models import Q, F
import datetime
import base64
from django.core.files.base import ContentFile

@api_view(['GET', 'POST'])
def recipes_list(request):
    """
    List all recipes or create a new recipe
    """

    if request.method == 'GET':
        try:
            recipe_data = JSONParser().parse(request)
        except:
            return JsonResponse({'message': 'Invalid body.'}, status=status.HTTP_400_BAD_REQUEST)

        q = Q()
        if 'category' in recipe_data:
            q &= Q(category=recipe_data['category'])

        recipes = Recipe.objects.filter(q)
        result = []

        for recipe in recipes:
            recipe_data = get_compound(recipe)
            result.append(recipe_data)

        return JsonResponse(result, status=status.HTTP_200_OK, safe=False)
    elif request.method == 'POST':
        try:
            recipe_data = JSONParser().parse(request)
        except:
            return JsonResponse({'message': 'Invalid body.'}, status=status.HTTP_400_BAD_REQUEST)

        if 'steps' in recipe_data:
            steps = recipe_data['steps']
            recipe_data['steps'] = '||'.join(steps)

        image, ext = base64_to_image(recipe_data['image_path'])
        recipe_data.pop('image_path')
        recipe_serializer = RecipeSerializer(data=recipe_data)

        message = {}

        if 'category' not in recipe_data:
            message['category'] = ["This field is required."]

        if 'ingredients' not in recipe_data:
            message['ingredients'] = ["This field is required."]

        if recipe_serializer.is_valid() and not message:
            recipe_id = recipe_serializer.create(recipe_data, image, ext)

            if not recipe_id:
                return JsonResponse({'message': recipe_id}, status=status.HTTP_400_BAD_REQUEST)
            else:
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
            return JsonResponse({'message': f'Recipe {recipe_id} doesn\'t exist.'}, status=status.HTTP_404_BAD_REQUEST)
    elif request.method == 'DELETE':
        try:
            recipe = Recipe.objects.get(pk=recipe_id)
            recipe.delete()
            return JsonResponse({'message': f'Recipe {recipe_id} deleted.'}, status=status.HTTP_200_OK)
        except Recipe.DoesNotExist:
            return JsonResponse({'message': f'Recipe {recipe_id} doesn\'t exist.'}, status=status.HTTP_404_BAD_REQUEST)


class UserRecipeList(APIView):
    """
    Retrieve user recipes
    """

    def get(self, request, user_id, format=None):
        recipes = Recipe.objects.filter(user=user_id)
        result = []

        for recipe in recipes:
            recipe_data = get_compound(recipe)
            result.append(recipe_data)

        return JsonResponse(result, status=status.HTTP_200_OK, safe=False)


class RecipeCategoryList(APIView):
    """
    Retrieve recipe categories
    """

    def get(self, request, format=None):
        recipe_categories = RecipeCategory.objects.all()
        recipe_categories_serializer = RecipeCategorySerializer(
            recipe_categories, many=True)
        return JsonResponse(recipe_categories_serializer.data, status=status.HTTP_200_OK, safe=False)


@api_view(['GET'])
def ingredients_list(request):
    """
    Retrieve ingredients
    """

    if request.method == 'GET':
        ingredients = Ingredient.objects.all()
        ingredients_serializer = IngredientSerializer(ingredients, many=True)
        return JsonResponse(ingredients_serializer.data, status=status.HTTP_200_OK, safe=False)


def get_compound(recipe):
    """
    Retrieve ingredients of a recipe
    """

    recipe_serializer = RecipeSerializer(recipe)
    recipe_data = recipe_serializer.data
    kcalories = 0.0
    estimated_cost = 0.0
    compounds = []

    recipe_data['category'] = recipe.category.description
    recipe_data['steps'] = recipe_data['steps'].split('||')

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
        estimated_cost += compound_dict['unitary_price'] * \
            compound_dict['quantity']

    recipe_data['kcalories'] = kcalories
    recipe_data['estimated_cost'] = estimated_cost
    recipe_data['ingredients'] = compounds

    recipe_data['num_stars'] = 0.0
    if recipe.num_scores != 0:
        recipe_data['num_stars'] = recipe.total_stars / recipe.num_scores

    return recipe_data

def get_user_ingredients(user):
    total_price = 0.0
    ingredients = []

    for ingredient in Add.objects.raw('''SELECT A.id, A.ingredient_id, A.quantity,
                                         INGREDIENT.name, INGREDIENT.unitary_price
                                         FROM `add` AS A
                                         INNER JOIN ingredient AS INGREDIENT
                                         ON A.ingredient_id = INGREDIENT.id
                                         WHERE A.`user` = %s
                                      ''', [user]):
        ingredient_dict = vars(ingredient)
        ingredient_dict.pop('_state')
        ingredient_dict.pop('id')
        ingredient_dict['price'] = ingredient_dict['quantity'] * ingredient_dict['unitary_price']
        total_price += ingredient_dict['price']
        ingredients.append(ingredient_dict)

    return {'ingredients': ingredients, 'total_price': total_price}


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
    List all schedules or create a new schedule
    """

    RECIPES_PER_DAY = 2

    def get(self, request):

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
            start_date = datetime.datetime.strptime(
                schedule_data['start_date'], '%d-%m-%y')
            q &= Q(date__gte=start_date)

        if 'end_date' in schedule_data:
            end_date = datetime.datetime.strptime(
                schedule_data['end_date'], '%d-%m-%y')
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

    def post(self, request):

        try:
            schedule_data = JSONParser().parse(request)
        except:
            return JsonResponse({'message': 'Invalid body.'}, status=status.HTTP_400_BAD_REQUEST)

        message = {}

        if 'date' not in schedule_data:
            message['date'] = ["This field is required."]
            return JsonResponse(message, status=status.HTTP_400_BAD_REQUEST)

        dates_str = schedule_data['date'].split("|")
        start_date = datetime.datetime.strptime(dates_str[0], '%d-%m-%y')
        end_date = datetime.datetime.strptime(dates_str[1], '%d-%m-%y')
        schedule_data['date'] = start_date
        schedule_serializer = ScheduleSerializer(data=schedule_data)

        if schedule_serializer.is_valid():
            delta = datetime.date(end_date.year, end_date.month, end_date.day) - \
                datetime.date(start_date.year,
                                start_date.month, start_date.day)

            q = Q()
            if 'is_lunch' in schedule_data:
                q &= Q(is_lunch=schedule_data['is_lunch'])

            # if "ingredients_blacklist" in schedule_data:
                # TODO: Retrieve user blacklist and discard the ingredients

            if 'discarded_ingredients' in schedule_data:
                q &= ~Q(ingredients__in=schedule_data['discarded_ingredients'])

            num_recipes = (delta.days + 1) * self.RECIPES_PER_DAY
            recipes = Recipe.objects.filter(q).order_by('?').distinct()[:num_recipes]

            result = []

            i = 1
            is_lunch = True
            for recipe in recipes:
                menu_id = schedule_serializer.save(schedule_data, start_date,
                                                    recipe, is_lunch)

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
    Retrieve or delete a schedule by ID
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
            return JsonResponse({'message': f'Menu {menu_id} doesn\'t exist.'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, menu_id):
        try:
            schedule = Schedule.objects.get(pk=menu_id)
            schedule.delete()
            return Response({'message': f'Menu {menu_id} deleted.'}, status=status.HTTP_204_NO_CONTENT)
        except Schedule.DoesNotExist:
            return JsonResponse({'message': f'Menu {menu_id} doesn\'t exist.'}, status=status.HTTP_404_NOT_FOUND)


class UserScheduleList(APIView):
    """
    Retrieve user recipes
    """

    def get(self, request, user_id):

        try:
            schedule_data = JSONParser().parse(request)
            schedule_data['user'] = user_id
        except:
            return JsonResponse({'message': 'Invalid body.'}, status=status.HTTP_400_BAD_REQUEST)

        message = {}

        if 'date' not in schedule_data:
            message['date'] = ["This field is required."]

        if 'is_lunch' not in schedule_data:
            message['is_lunch'] = ["This field is required."]

        if not message:
            try:
                date = datetime.datetime.strptime(
                    schedule_data['date'], '%d-%m-%y')
                schedule = Schedule.objects.filter(
                    user=schedule_data['user'], date=date, is_lunch=schedule_data['is_lunch'])
            except Schedule.DoesNotExist:
                return JsonResponse({'message': f'Menu doesn\'t exist.'}, status=status.HTTP_404_NOT_FOUND)

            if len(schedule) == 1:
                schedule_serializer = ScheduleSerializer(schedule[0])
                schedule_data = schedule_serializer.data
                schedule_data['recipe'] = get_compound(schedule[0].recipe)
                return JsonResponse(schedule_data, status=status.HTTP_200_OK, safe=False)
            elif len(schedule) == 0:
                return JsonResponse({'message': f'Menu doesn\'t exist.'}, status=status.HTTP_404_NOT_FOUND)

        return JsonResponse(message, status=status.HTTP_400_BAD_REQUEST)

class UserScheduleList(APIView):
    """
    Retrieve user recipes
    """

    def get(self, request, user_id):

        try:
            schedule_data = JSONParser().parse(request)
            schedule_data['user'] = user_id
        except:
            return JsonResponse({'message': 'Invalid body.'}, status=status.HTTP_400_BAD_REQUEST)

        message = {}

        if 'date' not in schedule_data:
            message['date'] = ["This field is required."]

        if 'is_lunch' not in schedule_data:
            message['is_lunch'] = ["This field is required."]

        if not message:
            try:
                date = datetime.datetime.strptime(
                    schedule_data['date'], '%d-%m-%y')
                schedule = Schedule.objects.filter(
                    user=schedule_data['user'], date=date, is_lunch=schedule_data['is_lunch'])
            except Schedule.DoesNotExist:
                return JsonResponse({'message': f'Menu doesn\'t exist.'}, status=status.HTTP_404_NOT_FOUND)

            if len(schedule) == 1:
                schedule_serializer = ScheduleSerializer(schedule[0])
                schedule_data = schedule_serializer.data
                schedule_data['recipe'] = get_compound(schedule[0].recipe)
                return JsonResponse(schedule_data, status=status.HTTP_200_OK, safe=False)
            elif len(schedule) == 0:
                return JsonResponse({'message': f'Menu doesn\'t exist.'}, status=status.HTTP_404_NOT_FOUND)

        return JsonResponse(message, status=status.HTTP_400_BAD_REQUEST)

class ScoreList(APIView):
    """
    List all scores filter by user_id, recipe_id or num_stars
    """

    def get(self, request):

        try:
            score_data = JSONParser().parse(request)
        except:
            return JsonResponse({'message': 'Invalid body.'}, status=status.HTTP_400_BAD_REQUEST)

        q = Q()
        if 'user_id' in score_data:
            q &= Q(user=score_data['user_id'])

        if 'recipe_id' in score_data:
            q &= Q(recipe=score_data['recipe_id'])

        if 'num_stars' in score_data:
            q &= Q(num_stars=score_data['num_stars'])

        if 'order_by' in score_data:
            scores = Score.objects.filter(q).order_by(
                '-'+score_data['order_by'])[:10]
        else:
            scores = Score.objects.filter(q)

        scores_data = []

        for score in scores:
            score_serializer = ScoreSerializer(score)
            score_data = score_serializer.data
            scores_data.append(score_data)

        return JsonResponse(scores_data, status=status.HTTP_200_OK, safe=False)


class ScoreCreate(APIView):
    """
    Create and update a score
    """

    def post(self, request, user_id, recipe_id):
        try:
            score_data = JSONParser().parse(request)
            score_data['recipe'] = recipe_id
            score_data['user'] = user_id
        except:
            return JsonResponse({'message': 'Invalid body.'}, status=status.HTTP_400_BAD_REQUEST)

        score_serializer = ScoreSerializer(data=score_data)

        if score_serializer.is_valid():
            if score_data['num_stars'] < 0 or score_data['num_stars'] > 5:
                return JsonResponse({'message': 'Score must be a positive number between 0 and 5.'}, status=status.HTTP_400_BAD_REQUEST)
            score_id = score_serializer.create(score_data)
            return Response({'id': score_id}, status=status.HTTP_201_CREATED)

        return Response(score_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, user_id, recipe_id):
        try:
            score_data = JSONParser().parse(request)
            score_data['recipe'] = recipe_id
            score_data['user'] = user_id
        except:
            return JsonResponse({'message': 'Invalid body.'}, status=status.HTTP_400_BAD_REQUEST)

        message = {}

        if not "num_stars" in score_data:
            message['num_stars'] = ["This field is required."]
        else:
            if type(score_data['num_stars']) == str:
                return JsonResponse({'message': 'A valid number is required.'}, status=status.HTTP_400_BAD_REQUEST)
            if score_data['num_stars'] < 0 or score_data['num_stars'] > 5:
                return JsonResponse({'message': 'Score must be a positive number between 0 and 5.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            score = Score.objects.filter(user=user_id, recipe=recipe_id)
            recipe = Recipe.objects.filter(id=score_data['recipe']).update(total_stars=F('total_stars')
                                                                        - score[0].num_stars
                                                                        + score_data['num_stars'])
            score.update(num_stars=score_data['num_stars'])
        except:
            return JsonResponse({'message': 'Invalid user_id or recipe_id.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': f'Score {score[0].id} updated.'}, status=status.HTTP_200_OK)


def base64_to_image(image_base64):
    format, imgstr = image_base64.split(';base64,')
    ext = format.split('/')[-1]
    image = ContentFile(base64.b64decode(imgstr))

    return image, ext
class ShoppingList(APIView):
    """
    Retrieves and updates the shopping list according to the recipes or menus
    """

    def get(self, request, user_id, format=None):
        result = get_user_ingredients(user_id)
        return JsonResponse(result, status=status.HTTP_200_OK, safe=False)

    def put(self, request, user_id, format=None):
        try:
                recipe_ingredient_data = JSONParser().parse(request)
        except:
            return JsonResponse({'message': 'Invalid body.'}, status=status.HTTP_400_BAD_REQUEST)

        shopping_list = get_user_ingredients(user_id)
        user_ingredients = shopping_list['ingredients']

        if 'recipe_id' in recipe_ingredient_data:
            recipe_id = recipe_ingredient_data['recipe_id']
            recipe = Recipe.objects.get(id=recipe_id)
            compound_recipe = get_compound(recipe)
            recipe_ingredients = compound_recipe['ingredients']
            for recipe_ingredient in recipe_ingredients:
                if not any(ingredient['ingredient_id'] == recipe_ingredient['ingredient_id'] for ingredient in user_ingredients):
                    user_ingredient = Add.objects.create(
                        user = user_id,
                        ingredient_id = recipe_ingredient['ingredient_id'],
                        quantity = recipe_ingredient['quantity']
                    )
                    user_ingredient.save()
                else:
                    Add.objects.filter(user=user_id, ingredient_id=recipe_ingredient['ingredient_id'])\
                               .update(quantity=F('quantity') + recipe_ingredient['quantity'])
            return Response(status=status.HTTP_204_NO_CONTENT)
        elif 'ingredient_id' and 'quantity' in recipe_ingredient_data:
            print(user_ingredients)
            if not any(ingredient['ingredient_id'] == recipe_ingredient_data['ingredient_id'] for ingredient in user_ingredients):
                print("NO EXISTE y SE CREA")
                user_ingredient = Add.objects.create(
                        user = user_id,
                        ingredient_id = recipe_ingredient_data['ingredient_id'],
                        quantity = recipe_ingredient_data['quantity']
                    )
                user_ingredient.save()
            else:
                print("EXISTE y SE ACTUALIZA")
                Add.objects.filter(user=user_id, ingredient_id=recipe_ingredient_data['ingredient_id'])\
                           .update(quantity=F('quantity') + recipe_ingredient_data['quantity'])
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            message = {}
            message['recipe_id'] = ["This field is required."]
            message['ingredient_id'] = ["This field is required."]
            message['quantity'] = ["This field is required."]
            return JsonResponse(message, status=status.HTTP_400_BAD_REQUEST)
