from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UploadedArticle
from automated_scrap import *

@receiver(post_save, sender=UploadedArticle)
def run_scrapper_on_file_upload(sender,instance,**kwargs):
    run_scrapper