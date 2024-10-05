from django.contrib import admin
from .models import Recipe

# Customize the Recipe model display in the admin interface
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'categories', 'calories', 'rating', 'prep_time', 'cook_time')
    search_fields = ('title', 'categories')  # Enable search by title and categories
    list_filter = ('categories', 'rating')   # Add filters for categories and rating
    ordering = ('title',)  # Default ordering by title

# Register the Recipe model and its custom admin settings
admin.site.register(Recipe, RecipeAdmin)
