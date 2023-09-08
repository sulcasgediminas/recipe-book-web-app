from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Recipe, RecipeTag


def index(request):
    num_recipes = Recipe.objects.all().count()

    context = {
        'num_recipes': num_recipes,
    }

    return render(request, 'index.html', context=context)


class RecipeListView(ListView):
    model = Recipe
    template_name = 'recipe_list.html'
    context_object_name = 'recipes'

    def get_queryset(self):
        # Include related Image objects using prefetch_related
        return Recipe.objects.prefetch_related('image_set')


class RecipeDetailView(DetailView):
    model = Recipe
    template_name = 'recipe_detail.html'
    context_object_name = 'recipe'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recipe = self.get_object()
        image = recipe.image_set.first()  # Get the first associated Image object
        ingredients_used = recipe.recipeingredient_set.all()
        tags = recipe.recipetag_set.all()  # Fetch tags associated with the recipe


        context['image'] = image
        context['ingredients_used'] = ingredients_used
        context['tags'] = tags # Include tags in the context
        return context