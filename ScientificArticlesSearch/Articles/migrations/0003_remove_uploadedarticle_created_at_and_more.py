# Generated by Django 5.0 on 2023-12-24 19:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Articles', '0002_uploadedarticle_article_is_validated'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='uploadedarticle',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='uploadedarticle',
            name='updated_at',
        ),
    ]