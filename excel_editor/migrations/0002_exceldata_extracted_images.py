# Generated by Django 3.2.23 on 2024-09-30 18:11

from django.db import migrations
import djongo.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('excel_editor', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='exceldata',
            name='extracted_images',
            field=djongo.models.fields.JSONField(default=list),
        ),
    ]
