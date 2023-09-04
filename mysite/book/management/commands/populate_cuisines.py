from book.models import Cuisine
from django.core.management.base import BaseCommand
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Generate a cuisines'

    def handle(self, *args, **options):
        # Set up Django settings module
        settings_module = settings.SETTINGS_MODULE
        if not settings_module:
            settings_module = 'mysite.settings'  # Replace 'mysite' with the actual name of your Django project
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

        popular_cuisines = [
            'Italian',
            'Chinese',
            'Mexican',
            'Indian',
            'Japanese',
            'Thai',
            'French',
            'Spanish',
            'Greek',
            'Lebanese',
            'Turkish',
            'Moroccan',
            'Vietnamese',
            'Korean',
            'Brazilian',
            'American',
            'British',
            'German',
            'Swedish',
            'Russian',
            'Cuban',
            'Peruvian',
            'Argentinian',
            'Australian',
            'Indonesian',
            'Malaysian',
            'Filipino',
            'Portuguese',
            'Egyptian',
            'Ethiopian',
            'South African',
            'Nigerian',
            'Kenyan',
            'Mediterranean',
            'Caribbean',
            'Israeli',
            'Irish',
            'Scottish',
            'Mexican-American',
            'Chinese-American',
            'Indian-American',
            'Japanese-American',
            'Italian-American',
            'Greek-American',
            'Middle Eastern',
            'Latin American',
            'Scandinavian',
            'Polish',
            'Swiss',
            'Ukrainian',
            'Hawaiian',
        ]


        for cuisine_name in popular_cuisines:
            Cuisine.objects.create(name=cuisine_name)

        self.stdout.write(self.style.SUCCESS('Successfully populated cuisines.'))
