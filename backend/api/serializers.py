from rest_framework import serializers

class RecipeSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    title = serializers.CharField(max_length=255)
    ingredients = serializers.ListField(child=serializers.CharField())
    directions = serializers.ListField(child=serializers.CharField())
    calories = serializers.IntegerField(required=False)
    rating = serializers.FloatField(required=False)
    protein = serializers.FloatField(required=False)
    fat = serializers.FloatField(required=False)
    sodium = serializers.FloatField(required=False)
    # Add more fields as needed based on your EpiRecipes dataset

    def to_representation(self, instance):
        """
        Custom representation to handle potential differences between
        OpenSearch documents and Python objects.
        """
        data = super().to_representation(instance)
        
        # Convert ingredients and directions to lists if they're strings
        for field in ['ingredients', 'directions']:
            if isinstance(data.get(field), str):
                data[field] = data[field].split(',')
        
        return data

    def create(self, validated_data):
        """
        Create and return a new `Recipe` instance, given the validated data.
        """
        # This method would be used if you're creating new recipes
        # For now, we'll just return the validated data as we're not saving to a database
        return validated_data

    def update(self, instance, validated_data):
        """
        Update and return an existing `Recipe` instance, given the validated data.
        """
        # This method would be used if you're updating existing recipes
        # For now, we'll just return the instance as we're not saving to a database
        return instance