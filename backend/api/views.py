import logging
from functools import wraps
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from .serializers import RecipeSerializer

from opensearch_utils.search import search_recipes, get_recipe

logger = logging.getLogger(__name__)

def cache_on_auth(timeout):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(view_instance, request, *args, **kwargs):
            return cache_page(timeout)(view_func)(view_instance, request, *args, **kwargs)
        return _wrapped_view
    return decorator

class SearchView(APIView):
    @method_decorator(cache_page(60 * 15))
    def get(self, request):
        try:
            query = request.query_params.get('q', '')
            page = int(request.query_params.get('page', 1))
            size = int(request.query_params.get('size', 10))
            sort_by = request.query_params.get('sort_by')
            
            filters = {}
            for key, value in request.query_params.items():
                if key not in ['q', 'page', 'size', 'sort_by']:
                    if key in ['calories', 'rating']:
                        filters[key] = {}
                        if 'min' in value:
                            filters[key]['min'] = value.split(',')[0]
                        if 'max' in value:
                            filters[key]['max'] = value.split(',')[-1]
                    else:
                        filters[key] = value

            logger.info(f"Searching recipes with query: {query}, filters: {filters}, page: {page}, size: {size}, sort_by: {sort_by}")
            
            recipes, total = search_recipes(query, filters, page, size, sort_by)
            serializer = RecipeSerializer(recipes, many=True)
            
            logger.info(f"Search completed. Found {total} results.")
            
            return Response({
                'results': serializer.data,
                'total': total,
                'page': page,
                'size': size
            })
        except Exception as e:
            logger.error(f"Error in SearchView: {str(e)}", exc_info=True)
            return Response({"error": "An unexpected error occurred during search."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RecipeDetailView(APIView):
    @method_decorator(cache_page(60 * 60))
    def get(self, request, recipe_id):
        try:
            logger.info(f"Fetching recipe with id: {recipe_id}")
            recipe = get_recipe(recipe_id)
            if recipe:
                serializer = RecipeSerializer(recipe)
                logger.info(f"Successfully fetched recipe with id: {recipe_id}")
                return Response(serializer.data)
            logger.warning(f"Recipe not found with id: {recipe_id}")
            return Response({"error": "Recipe not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in RecipeDetailView: {str(e)}", exc_info=True)
            return Response({"error": "An unexpected error occurred while fetching the recipe."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)