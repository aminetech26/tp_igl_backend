# Generated by Django 5.0 on 2023-12-27 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Articles', '0005_alter_uploadedarticle_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadedarticle',
            name='file',
            field=models.FileField(upload_to='./'),
        ),
    ]