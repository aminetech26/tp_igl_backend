from django.contrib import admin

from django.contrib import admin

from .models import Auteur,Institution,MotCle,ReferenceBibliographique, Article


admin.site.register(Auteur)
admin.site.register(Institution)
admin.site.register(MotCle)
admin.site.register(ReferenceBibliographique)
admin.site.register(Article)
