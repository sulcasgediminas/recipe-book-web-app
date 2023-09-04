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

        # Rest of your code goes here
        # Randomly select a few ingredients
        ingredients = list(Ingredient.objects.order_by('?')[:3])  # Replace '3' with the desired number of ingredients

        # Randomly select one cuisine
        cuisine = random.choice(Cuisine.objects.all())

        prompt = f"## Generate Food Recipe\n\nIngredients: {', '.join(ingredient.name for ingredient in ingredients)} plus add as many ingredients so dish would be deliciuos\n\nCuisine: {cuisine.name}\n\nInstructions:"
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

        # Generate dynamic values using OpenAI API
        response = openai.Completion.create(
            engine='text-davinci-003',
            prompt=f"## Generate Recipe Title:\n\nUse this text to generate recipe's title: {recipe_text}\n",
            max_tokens=100,
            temperature=0.5,
            n=1
        )
        title = response.choices[0].text.strip().replace('"', '')

        response = openai.Completion.create(
            engine='text-davinci-003',
            prompt=f"## Generate Recipe Description:\n\nUse this text to generate Description (Description is few sentences about recipe. How recipe was inspired. Who might like it, etc.): {recipe_text}\n",
            max_tokens=500,
            temperature=0.7,
            n=1
        )
        description = response.choices[0].text.strip()

        response = openai.Completion.create(
            engine='text-davinci-003',
            prompt=f"## Generate Recipe Difficulty Level:\n\nUse this text to generate difficulty: {recipe_text}\n",
            max_tokens=128,
            temperature=0.3,
            n=1
        )
        difficulty_level = response.choices[0].text.strip()

        response = openai.Completion.create(
            engine='text-davinci-003',
            prompt=f"## Generate Recipe Servings:\n\nUse this text to generate Servings: {recipe_text}\n",
            max_tokens=128,
            temperature=0.2,
            n=1
        )
        servings = response.choices[0].text.strip()


        response = openai.Completion.create(
            engine='text-davinci-003',
            prompt=f"## Generate Recipe Preparation Time:\n\nInstructions: {recipe_text}\n",
            max_tokens=128,
            temperature=0.3,
            n=1
        )
        preparation_time = response.choices[0].text.strip()

        response = openai.Completion.create(
            engine='text-davinci-003',
            prompt=f"## Generate Recipe Total Time:\n\nInstructions: {recipe_text}\n",
            max_tokens=128,
            temperature=0.3,
            n=1
        )
        total_time = response.choices[0].text.strip()

        response = openai.Completion.create(
            engine='text-davinci-003',
            prompt=f"## Generate ingredients used in recipe:\n\nInstructions: {recipe_text}\n",
            max_tokens=256,
            temperature=0.3,
            n=1
        )
        ingredients_used = response.choices[0].text.strip()

        # Generate the image using the OpenAI API
        response = openai.Image.create(
            prompt=f'Generate an image of {title}.',
            size="256x256",
            n=1,
        )

        # Extract the generated image URL from the response
        image_file = response['data'][0]['url']
        image_response = requests.get(image_file, verify=False)
        image_content = image_response.content
        image_base64 = base64.b64encode(image_content).decode("utf-8")

        # Create a new recipe instance
        recipe = Recipe.objects.create(
            title=title,
            description=description,
            instructions=recipe_text,
            # cooking_time=None,
            # difficulty_level=difficulty_level,
            # servings=servings,
            # preparation_time=preparation_time,
            # total_time=total_time
        )
        recipe.cuisines.set([cuisine])

        # Create a ingredients_used instance
        # ingredients_used = RecipeIngredient.objects.create(ingredient=ingredients_used)

        # After generating the image URL using the OpenAI API
        image = Image.objects.create(recipe=recipe)

        image.image_file.save(f"{title}.jpg", ContentFile(image_content))

        # After the code execution is complete, you can print a success message if desired
        self.stdout.write(self.style.SUCCESS('Recipe generated successfully'))
