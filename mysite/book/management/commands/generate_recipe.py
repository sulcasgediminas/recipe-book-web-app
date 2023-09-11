##############################################
# Import necessary modules
##############################################

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

############################################################################################
# dotenv_path = os.path.join(os.path.dirname(__file__), 'project_recipes/.env')
############################################################################################

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

        print(recipe_text)

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
            temperature=0.8,
            n=1
        )
        description = response.choices[0].text.strip()


############################################################################################
# Use OpenAI API to process the text and extract description
############################################################################################

        response = openai.Completion.create(
            engine='text-davinci-003',
            prompt=f"Extract full instruction of recipe's preparation from the following text:\n\n{recipe_text}\n. Do not include or do not add 'Instructions' at the beginning. (I will set up Instructions block manully)",
            max_tokens=500,
            temperature=0.4,
            n=1
        )
        instruction = response.choices[0].text.strip()





        response = openai.Completion.create(
            engine='text-davinci-003',
            prompt=f"## Generate Recipe Difficulty Level:\n\nUse this text to generate difficulty: {recipe_text}\n",
            max_tokens=128,
            temperature=0.2,
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
            prompt=f"Generate recipe's preparation time from description: {recipe_text}. Provide me only integer/number in minutes",
            max_tokens=32,
            temperature=0.1,
            n=1
        )
        preparation_time = response.choices[0].text.strip()


        response = openai.Completion.create(
            engine='text-davinci-003',
            prompt=f"## Generate Tags for recipe From: {recipe_text}. Add '#' before every tag.\n",
            max_tokens=128,
            temperature=0.3,
            n=1
        )
        tags = response.choices[0].text.strip()
        

        response = openai.Completion.create(
            engine='text-davinci-003',
            prompt=f"## Generate Recipe Total Time:\n\nInstructions: {recipe_text}\n",
            max_tokens=128,
            temperature=0.3,
            n=1
        )
        total_time = response.choices[0].text.strip()







        # Use OpenAI API to process the text and extract ingredients
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Extract a list of ingredients from the following text:\n\n{recipe_text}\n. Do not add any additional information such as measurement or condition",
            max_tokens=128,
            temperature=0.1,
            n=1,
            # stop=["-"],  # Stop generation after "-" to capture each ingredient line
        )

        # Extract the generated text from the response
        extracted_ingredients = response.choices[0].text.strip()

        # Split the extracted text into a list of ingredients
        ingredient_list = [line.strip() for line in extracted_ingredients.split("\n") if line.strip()]

                # Print the list of pure ingredients
        if not ingredient_list:
            print("No ingredients extracted.")
        else:
            print("Extracted ingredients:")
            for ingredient_text in ingredient_list:
                print(f"Ingredient: '{ingredient_text}'")

        # # Create a new recipe instance
        recipe = Recipe.objects.create(
            title=title,
            description=description,
            instructions=instruction,
            # cooking_time=None,
            # difficulty_level=difficulty_level,
            # servings=servings,
            preparation_time=preparation_time,
            # total_time=total_time
        )
        recipe.cuisines.set([cuisine])

                # Print the number of ingredients found
        print(f"Number of extracted ingredients: {len(ingredient_list)}")


        # recipe.save()

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









        # Generate the image using the OpenAI API
        response = openai.Image.create(
            prompt=f'Portrait of michelin-star {title}. Tasty, incredibly detailed, sharpen, professional food lighting. Professional food photography, captivating, rule of thirds, majestic, octane render.',
            size="512x512",
            n=1,
        )

        # Extract the generated image URL from the response
        image_file = response['data'][0]['url']
        image_response = requests.get(image_file, verify=False)
        image_content = image_response.content
        image_base64 = base64.b64encode(image_content).decode("utf-8")



        # # Create a new recipe instance
        # recipe = Recipe.objects.create(
        #     title=title,
        #     description=description,
        #     instructions=recipe_text,
        #     # cooking_time=None,
        #     # difficulty_level=difficulty_level,
        #     # servings=servings,
        #     preparation_time=preparation_time,
        #     # total_time=total_time
        # )
        # recipe.cuisines.set([cuisine])

        # Create a RecipeTag instance for the generated Tag and associate it with the Recipe
        tag_obj, created = Tag.objects.get_or_create(name=tags)
        tags = RecipeTag.objects.create(recipe=recipe, tag=tag_obj)

       

        # After generating the image URL using the OpenAI API
        image = Image.objects.create(recipe=recipe)

        image.image_file.save(f"{title}.jpg", ContentFile(image_content))

        # After the code execution is complete, you can print a success message if desired
        self.stdout.write(self.style.SUCCESS('Recipe generated successfully'))
