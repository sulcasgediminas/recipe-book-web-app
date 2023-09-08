from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=255)

class Cuisine(models.Model):
    name = models.CharField(max_length=255)

class Ingredient(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

class Recipe(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True)
    instructions = models.TextField(null=True)
    cooking_time = models.DurationField(null=True, blank=True)
    difficulty_levels = (
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    )
    difficulty_level = models.CharField(max_length=10, choices=difficulty_levels)
    servings = models.CharField(max_length=255, null=True, blank=True)
    preparation_time = models.CharField(max_length=255, null=True, blank=True)
    total_time = models.DurationField(null=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField(Category)
    cuisines = models.ManyToManyField(Cuisine)

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_of_measurement = models.CharField(max_length=50)

class Image(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    image_file = models.ImageField(upload_to='', blank=True, null=True)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='media/profiles/', blank=True, null=True)
    bio = models.TextField(null=True, blank=True)
    social_links = models.JSONField(null=True, blank=True)

class Review(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.DecimalField(max_digits=3, decimal_places=2)
    review_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Favorite(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Tag(models.Model):
    name = models.CharField(max_length=255)

class RecipeTag(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

class Allergen(models.Model):
    name = models.CharField(max_length=255)

class RecipeAllergen(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    allergen = models.ForeignKey(Allergen, on_delete=models.CASCADE)

class NutritionalInformation(models.Model):
    recipe = models.OneToOneField(Recipe, on_delete=models.CASCADE)
    calories = models.DecimalField(max_digits=6, decimal_places=2)
    protein = models.DecimalField(max_digits=6, decimal_places=2)
    carbohydrates = models.DecimalField(max_digits=6, decimal_places=2)
    fats = models.DecimalField(max_digits=6, decimal_places=2)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
