# Generated by Django 4.2.4 on 2023-08-08 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='image_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
