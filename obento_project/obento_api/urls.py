# api_endpoints/urls.py

from django import urls
from django.urls import include, path
from rest_framework import routers
from . import views
from obento_api.views import RegisterView, LogoutAllView, LogoutView
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

router = routers.DefaultRouter()

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('ingredients', views.ingredients_list),
    path('recipes', views.recipes_list),
    path('recipes/<int:recipe_id>', views.get_delete_recipe)
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('logout/', LogoutView.as_view(), name='auth_logout'),
    path('logout_all/', LogoutAllView.as_view(), name='auth_logout_all'),
]