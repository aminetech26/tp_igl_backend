from django.db.models.signals import post_save
from django.dispatch import receiver
from .scrapper import Scrapper
from .models import UploadedArticle


@receiver(post_save, sender=UploadedArticle)
def run_scrapper_on_file_upload(sender,instance,**kwargs):
    scrapper = Scrapper(instance.file)
    scrapper.run()