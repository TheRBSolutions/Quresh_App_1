# Generated by Django 3.2.23 on 2024-09-30 19:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('excel_editor', '0002_exceldata_extracted_images'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='exceldata',
            name='data',
        ),
        migrations.RemoveField(
            model_name='exceldata',
            name='extracted_images',
        ),
        migrations.CreateModel(
            name='ExcelImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField()),
                ('image', models.BinaryField()),
                ('excel_data', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='excel_editor.exceldata')),
            ],
            options={
                'ordering': ['number'],
            },
        ),
    ]
