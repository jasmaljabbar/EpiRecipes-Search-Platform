from django.urls import path
from .views import SearchView, RecipeDetailView

urlpatterns = [
    path('search/', SearchView.as_view(), name='search'),
    path('recipe/<str:recipe_id>/', RecipeDetailView.as_view(), name='recipe-detail'),
]