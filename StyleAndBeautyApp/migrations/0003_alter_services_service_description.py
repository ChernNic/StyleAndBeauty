# Generated by Django 5.0.2 on 2024-02-20 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('StyleAndBeautyApp', '0002_services_service_description_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='services',
            name='service_description',
            field=models.TextField(null=True),
        ),
    ]
