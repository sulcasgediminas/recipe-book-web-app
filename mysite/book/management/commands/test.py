from django.conf import settings
import random
import openai
import os
import requests
import base64
from dotenv import load_dotenv
from book.models import Ingredient, Cuisine, Recipe, Image, RecipeTag, Tag, RecipeIngredient
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile

# dotenv_path = os.path.join(os.path.dirname(__file__), 'project_recipes/.env')
load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')


class Command(BaseCommand):
    help = 'Generate a new recipe'

    def handle(self, *args, **options):
        # Set up Django settings module
        settings_module = settings.SETTINGS_MODULE
        if not settings_module:
            settings_module = 'book.settings'  # Replace 'your_project' with the actual name of your Django project
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)


        # Randomly select a few ingredients
        ingredients = list(Ingredient.objects.order_by('?')[:3])  # Replace '3' with the desired number of ingredients

        # Randomly select one cuisine
        cuisine = random.choice(Cuisine.objects.all())

        prompt = f"## Generate Food Recipe\n\n Use ingredients: {', '.join(ingredient.name for ingredient in ingredients)} plus add as many ingredients so dish would be deliciuos\n\nInspired by Cuisine: {cuisine.name}\n\n"
        response = openai.Completion.create(
            engine='text-davinci-003',
            prompt=prompt,
            max_tokens=1024,  # Adjust the value as per your needs
            temperature=0.5,  # Adjust the value to control the randomness of the generated text
            n=1,  # Adjust the value to generate multiple completions and choose the best one
            stop=None,  # You can provide a stop sequence to limit the generated text
            timeout=10,  # Adjust the value as per your needs
        )
        recipe_text = response.choices[0].text.strip().replace('\n', ' ')


                # Input text containing ingredients and additional information
        input_text = """
        Ingredients: 
        - 2 cans of tuna, drained
        - 2 tablespoons ghee
        - 1 cup heavy cream
        - 2 tablespoons fish sauce
        - 2 tablespoons lime juice
        - 2 tablespoons brown sugar
        - 1 teaspoon freshly grated ginger
        - 2 cloves garlic, minced
        - 2 tablespoons fresh cilantro, chopped
        - 1 teaspoon red chili flakes
        - 2 tablespoons vegetable oil
        - 1 red bell pepper, diced
        - 1 cup coconut milk
        """

        # Use OpenAI API to process the text and extract ingredients
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Extract a list of ingredients from the following text:\n\n{input_text}\n. Do not add any additional information such as measurement or condition",
            max_tokens=128,
            temperature=0.1,
            n=1,
            # stop=["-"],  # Stop generation after "-" to capture each ingredient line
        )

        # Extract the generated text from the response
        extracted_ingredients = response.choices[0].text.strip()

        print(extracted_ingredients)

        # Split the extracted text into a list of ingredients
        ingredient_list = [line.strip() for line in extracted_ingredients.split("\n") if line.strip()]

                # Print the list of pure ingredients
        if not ingredient_list:
            print("No ingredients extracted.")
        else:
            print("Extracted ingredients:")
            for ingredient_text in ingredient_list:
                print(f"Ingredient: '{ingredient_text}'")

        # Create a new recipe instance
        recipe = Recipe.objects.create(
            instructions=recipe_text,
        )
        recipe.cuisines.set([cuisine])

                # Print the number of ingredients found
        print(f"Number of extracted ingredients: {len(ingredient_list)}")


        recipe.save()

        # Print the list of pure ingredients
        for ingredient_text in ingredient_list:

            ingredient_text = ingredient_text.replace("- ", "")
  
            ingredient_text = ingredient_text.title()


            matching_ingredients = Ingredient.objects.filter(name=ingredient_text)

            if matching_ingredients.exists():
                # If multiple matching ingredients are found, choose the first one
                ingredient_obj = matching_ingredients.first()
            else:
                # If no matching ingredient is found, create a new one
                ingredient_obj, created = Ingredient.objects.get_or_create(name=ingredient_text)


            # Create a RecipeIngredient instance to associate the ingredient with the recipe
            # You can adjust the quantity and unit_of_measurement as needed
            recipe_ingredient, created = RecipeIngredient.objects.get_or_create(
                recipe=recipe,
                ingredient=ingredient_obj,
                quantity=1,  # Adjust as needed
                unit_of_measurement='unit',  # Adjust as needed
            )

            # Print a message indicating the ingredient was added to the recipe (optional)
            if created:
                print(f"Added ingredient '{ingredient_text}' to the recipe.")

            # Now, the extracted ingredients are associated with the 'recipe' in the database
