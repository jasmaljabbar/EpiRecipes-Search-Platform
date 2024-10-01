from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RecipeSerializer
from opensearch_utils.search import search_recipes, get_recipe

class SearchView(APIView):
    def get(self, request):
        query = request.query_params.get('q', '')
        page = int(request.query_params.get('page', 1))
        size = int(request.query_params.get('size', 10))
        
        filters = {}
        for key, value in request.query_params.items():
            if key not in ['q', 'page', 'size']:
                filters[key] = value

        recipes, total = search_recipes(query, filters, page, size)
        serializer = RecipeSerializer(recipes, many=True)
        
        return Response({
            'results': serializer.data,
            'total': total,
            'page': page,
            'size': size
        })

class RecipeDetailView(APIView):
    def get(self, request, recipe_id):
        recipe = get_recipe(recipe_id)
        if recipe:
            serializer = RecipeSerializer(recipe)
            return Response(serializer.data)
        return Response({"error": "Recipe not found"}, status=status.HTTP_404_NOT_FOUND)