from django.db import models

# Create your models here.

class Recipe(models.Model):
    title = models.CharField(max_length=200)
    ingredients = models.TextField()
    directions = models.TextField()
    categories = models.CharField(max_length=200)
    calories = models.FloatField()
    rating = models.FloatField()
    prep_time = models.IntegerField()
    cook_time = models.IntegerField()
